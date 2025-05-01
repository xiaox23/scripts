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
    def __init__(self, base_folder="data_save/vis_data", base_folder515="data_save/vis_data515", exp_number="0001"):
        # 初始化 RealSense 管道
        self.pipeline_list = []
        self.config_list = []
        self.connect_device = []

        # 连接设备并获取可用设备列表
        for d in rs.context().devices:
            if d.get_info(rs.camera_info.name).lower() != 'platform camera':
                self.connect_device.append(d.get_info(rs.camera_info.serial_number))

        # 确保至少有两个相机连接
        if len(self.connect_device) < 2:
            raise Exception("至少需要两个 RealSense 相机")

        # 设置数据保存路径
        self.base_folder = base_folder
        self.base_folder515 = base_folder515
        self.exp_number = exp_number.zfill(4)  # 实验编号格式化为四位
        self.data_folder = os.path.join(self.base_folder, self.exp_number)
        self.data_folder515 = os.path.join(self.base_folder515, self.exp_number)
        os.makedirs(self.data_folder, exist_ok=True)
        os.makedirs(self.data_folder515, exist_ok=True)

        # 配置每个相机
        for i in range(len(self.connect_device)):
            pipeline = rs.pipeline()
            config = rs.config()
            config.enable_device(self.connect_device[i])
            if i == 1:
                config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
            else:
                config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            
            self.pipeline_list.append(pipeline)
            self.config_list.append(config)
            # 启动管道
            pipeline.start(config)

        # 对齐对象
        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)

        self.running = True

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

    def save_data(self, depth_image, color_image, color_timestamp):
        # Prepare data dictionary
        data = {
            "depth_image": depth_image,
            "color_image": color_image,
        }
        
        # 使用 color_timestamp 作为文件名
        file_name = f"{color_timestamp}.pkl"
        file_path = os.path.join(self.data_folder, file_name)
        
        # 保存数据到文件
        with open(file_path, "wb") as f:
            pickle.dump(data, f)

    def save_data515(self, depth_image, color_image, color_timestamp):
        # Prepare data dictionary
        data = {
            "depth_image": depth_image,
            "color_image": color_image,
        }
        
        # 使用 color_timestamp 作为文件名
        file_name = f"{color_timestamp}.pkl"
        file_path = os.path.join(self.data_folder515, file_name)
        
        # 保存数据到文件
        with open(file_path, "wb") as f:
            pickle.dump(data, f)

    def run(self):
        # 在单独的线程中监听键盘输入
        stop_thread = threading.Thread(target=self.stop_on_keypress)
        stop_thread.daemon = True  # 设置为守护线程，确保主线程结束时它也会结束
        stop_thread.start()

        try:
            while self.running:
                for i, pipeline in enumerate(self.pipeline_list):
                    # 从每个相机获取颜色和深度帧
                    frames = pipeline.wait_for_frames()

                    # 对齐深度帧到颜色帧
                    aligned_frames = self.align.process(frames)

                    # 获取对齐的帧
                    aligned_depth_frame = aligned_frames.get_depth_frame()
                    color_frame = aligned_frames.get_color_frame()
                    

                    # 验证帧的有效性
                    if not aligned_depth_frame or not color_frame:
                        continue

                    # 获取时间戳
                    color_timestamp = str(int(round(time.time(),3)*1000))  # 颜色帧时间戳

                    # 转换数据为 NumPy 数组
                    depth_image = np.asanyarray(aligned_depth_frame.get_data())
                    color_image = np.asanyarray(color_frame.get_data())
                    
                    # 保存数据
                    if i == 0:
                        self.save_data(depth_image, color_image, color_timestamp)
                    elif i == 1:
                        self.save_data515(depth_image, color_image, color_timestamp)
                time.sleep(0.05)

        finally:
            self.running = False  # 确保停止运行
            for pipeline in self.pipeline_list:
                pipeline.stop()  # 停止每个相机的流
            print("All pipelines stopped.")

def main():
    # 使用 argparse 获取命令行参数
    parser = argparse.ArgumentParser(description="Run RealSense data collection.")
    parser.add_argument(
        "--base_folder", 
        type=str, 
        default="data_save/vis_data", 
        help="Path to the base folder where data will be saved."
    )
    parser.add_argument(
        "--base_folder515", 
        type=str, 
        default="data_save/vis_data515", 
        help="Path to the base folder for the second camera data."
    )
    parser.add_argument(
        "--exp_number",
        type=str,
        required=True,
        help="Experiment number (e.g., '0001', '0002')."
    )
    args = parser.parse_args()

    # 使用传入的文件夹路径和实验编号运行
    realsense = Realsense(base_folder=args.base_folder, base_folder515=args.base_folder515, exp_number=args.exp_number)
    realsense.run()

if __name__ == "__main__":
    main()

# python scripts/H02VisData.py --base_folder data_save/vis_data --base_folder515 data_save/vis_data515 --exp_number 1