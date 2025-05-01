import pyrealsense2 as rs
import numpy as np
import cv2
import os
import time
import argparse


def capture_rgbd(save_dir):
    # 创建保存目录
    rgb_dir = save_dir + "/rgb"
    depth_dir = save_dir + "/depth"
    os.makedirs(rgb_dir, exist_ok=True)
    os.makedirs(depth_dir, exist_ok=True)

    # 配置 RealSense 管道
    pipeline = rs.pipeline()
    config = rs.config()

    # 启用 RGB 和深度流
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # 启动管道
    profile = pipeline.start(config)
    
    device = pipeline.get_active_profile().get_device()
    depth_sensor = device.first_depth_sensor()
    device = pipeline.get_active_profile().get_device()
    depth_sensor.set_option(rs.option.laser_power, 100)  # L515 的最大功率为 150
    # 设置最近距离为 0
    depth_sensor.set_option(rs.option.min_distance, 0)

    # 对齐深度到 RGB
    align_to = rs.stream.color
    align = rs.align(align_to)

    frame_count = 0
    fps = 3  # 目标帧率
    interval = 1.0 / fps  # 每帧间隔时间（秒）

    try:
        while True:
            start_time = time.time()

            # 获取对齐的帧
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)

            # 获取 RGB 和深度帧
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            if not color_frame or not depth_frame:
                continue

            # 转换图像格式
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())  # 16-bit 深度图
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

            # 生成文件名
            filename_rgb = os.path.join(rgb_dir, f"{frame_count:05d}.png")
            filename_depth = os.path.join(depth_dir, f"{frame_count:05d}.png")
            filename_depth_vis = os.path.join(depth_dir, f"depth_vis_{frame_count:05d}.png")

            # 保存 RGB 图像
            cv2.imwrite(filename_rgb, color_image)

            # 保存 16-bit 深度图（保留原始深度信息）
            cv2.imwrite(filename_depth, depth_image)

            # 保存伪彩色深度图（可视化用）
            # cv2.imwrite(filename_depth_vis, depth_colormap)

            print(f"Saved: {filename_rgb}, {filename_depth}")

            frame_count += 1

            # 控制帧率（每 200ms 采集一帧）
            elapsed_time = time.time() - start_time
            sleep_time = max(0, interval - elapsed_time)
            time.sleep(sleep_time)

            # 显示图像
            concat_image = np.concatenate((color_image,depth_colormap), axis=1)
            H, W = concat_image.shape[0], concat_image.shape[1]
            cv2.imshow('RGB Image', cv2.resize(concat_image, dsize=(W//2, H//2)))

            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


def view_intrinsic():
    # 初始化 RealSense 管道
    pipeline = rs.pipeline()
    config = rs.config()

    # 启用 RGB 和深度流
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # 启动相机
    profile = pipeline.start(config)

    # 获取 RGB 和深度相机的内参
    color_intrinsics = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    depth_intrinsics = profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()

    # 打印 RGB 相机内参
    print("RGB Camera Intrinsics:")
    print(f"Width: {color_intrinsics.width}, Height: {color_intrinsics.height}")
    print(f"fx: {color_intrinsics.fx}, fy: {color_intrinsics.fy}")
    print(f"cx: {color_intrinsics.ppx}, cy: {color_intrinsics.ppy}")
    print(f"Distortion Model: {color_intrinsics.model}")
    print(f"Distortion Coefficients: {color_intrinsics.coeffs}")
    
    
    print("Depth Camera Intrinsics:")
    print(f"Width: {depth_intrinsics.width}, Height: {depth_intrinsics.height}")
    print(f"fx: {depth_intrinsics.fx}, fy: {depth_intrinsics.fy}")
    print(f"cx: {depth_intrinsics.ppx}, cy: {depth_intrinsics.ppy}")
    print(f"Distortion Model: {depth_intrinsics.model}")
    print(f"Distortion Coefficients: {depth_intrinsics.coeffs}")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_dir', type=str)
    args   = parser.parse_args()
    capture_rgbd(args.save_dir) 
    # view_intrinsic()


'''
RGB Camera Intrinsics:
Width: 1280, Height: 720
fx: 905.9979858398438, fy: 905.8917846679688
cx: 651.4166870117188, cy: 360.7659912109375
Distortion Model: distortion.brown_conrady
Distortion Coefficients: [0.1650751829147339, -0.49894121289253235, -0.0007983257528394461, -1.9092254660790786e-05, 0.44926804304122925]
Depth Camera Intrinsics:
Width: 640, Height: 480
fx: 457.48046875, fy: 458.5078125
cx: 320.625, cy: 236.958984375
Distortion Model: distortion.none
Distortion Coefficients: [0.0, 0.0, 0.0, 0.0, 0.0]
'''


'''
Reproject Depth Intrinsic:
fx: 914.96
cx: 641.5
fy: 687.76
cy: 355.44
'''
