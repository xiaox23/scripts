import pyrealsense2 as rs
import numpy as np
import os
import pickle
import time
import argparse
import threading
import sys
import select

class Realsense:
    def __init__(self, data_folder="data_save/vis_data"):
        # Initialize the Realsense pipeline
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # Get device information and configuration
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = self.config.resolve(pipeline_wrapper)
        self.device = pipeline_profile.get_device()
        device_product_line = str(self.device.get_info(rs.camera_info.product_line))

        found_rgb = False
        for s in self.device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            raise Exception("depth camera with rgb information is required")

        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

        # Start streaming
        self.profile = self.pipeline.start(self.config)
        self.camera_start_time = time.time()  # 相机启动时的系统时间

        # 获取第一帧的时间戳（校准时间偏移）
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        self.first_frame_timestamp = color_frame.get_timestamp() / 1000.0  # 转为秒

        # Get the depth scale of the depth sensor
        depth_sensor = self.profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()
        print("Depth scale: ", self.depth_scale)

        # Create an alignment object
        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)

        self.data_folder = data_folder
        print("data_folder: ")
        print(data_folder)
        os.makedirs(self.data_folder, exist_ok=True)
        self.frame_count = 0
        self.prev_time = time.time()

        # 控制运行状态的变量
        self.running = True

    def save_data(self, depth_image, color_image, color_timestamp):
        data = {
            "depth_image": depth_image,
            "color_image": color_image,
            "color_timestamp": color_timestamp
        }
        
        # 使用 color_timestamp 作为文件名
        file_name = f"{self.convert_to_system_time(color_timestamp)}.pkl"
        file_path = os.path.join(self.data_folder, file_name)
        
        # 保存数据到文件
        with open(file_path, "wb") as f:
            pickle.dump(data, f)

        self.frame_count += 1
    
    def calculate_fps(self):
        current_time = time.time()
        elapsed_time = current_time - self.prev_time
        fps = 1 / elapsed_time
        print(f"FPS: {fps:.2f}")
        self.prev_time = current_time

    def convert_to_system_time(self, color_timestamp):
        # 将相机时间戳转换为秒
        color_timestamp_seconds = color_timestamp / 1000.0

        # 转换为系统时间
        system_time = self.camera_start_time + (color_timestamp_seconds - self.first_frame_timestamp)

        # 转换为毫秒并取整
        system_time_milliseconds = int(system_time * 1000)
        return system_time_milliseconds

    def stop_on_keypress(self):
        """监听标准输入，当用户输入 's' 并按下回车时停止运行"""
        print("Press 's' and Enter to stop...")
        while self.running:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                user_input = sys.stdin.readline().strip()
                if user_input.lower() == 's':
                    print("Stopping RealSense...")
                    self.running = False  # 设置为 False，通知主线程停止
                    break

    def run(self):
        # 在单独的线程中监听键盘输入
        stop_thread = threading.Thread(target=self.stop_on_keypress)
        stop_thread.daemon = True  # 设置为守护线程，确保主线程结束时它也会结束
        stop_thread.start()

        try:
            while self.running:
                # Get color and depth frames
                frames = self.pipeline.wait_for_frames()

                # Align the depth frame to the color frame
                aligned_frames = self.align.process(frames)

                # Get the aligned frames
                aligned_depth_frame = aligned_frames.get_depth_frame()
                color_frame = aligned_frames.get_color_frame()

                # Verify if the frames are valid
                if not aligned_depth_frame or not color_frame:
                    continue

                # Get timestamps
                color_timestamp = color_frame.get_timestamp()  # Color frame timestamp

                depth_image = np.asanyarray(aligned_depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                self.save_data(depth_image, color_image, color_timestamp)

        finally:
            self.running = False  # 确保停止运行
            self.pipeline.stop()  # 停止相机流
            print("Pipeline stopped.")


def main():
    # 使用 argparse 获取命令行参数
    parser = argparse.ArgumentParser(description="Run RealSense data collection.")
    parser.add_argument(
        "--data_folder", 
        type=str, 
        default="data_save/vis_data", 
        help="Path to the folder where data will be saved."
    )
    args = parser.parse_args()

    # 使用传入的文件夹路径运行
    realsense = Realsense(data_folder=args.data_folder)
    realsense.run()

if __name__ == "__main__":
    main()

# python scripts/E02VisData.py --data_folder data_save/vis_data