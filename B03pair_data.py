import os
import pickle
import numpy as np

# 路径配置
vis_data_folder = "data_save/vis_data"  # 视觉数据路径
tac_data_folder = "data_save/tac_data"  # 触觉数据路径
output_folder = "data_save/combined_data"  # 输出数据路径
os.makedirs(output_folder, exist_ok=True)

# 时间戳匹配限差（单位：毫秒*1000）
time_threshold = 100000  # 允许的时间误差范围

def load_pickle_files(folder_path):
    """加载指定文件夹下所有的pickle文件，并根据时间戳排序"""
    pickle_files = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pkl'):
            file_path = os.path.join(folder_path, file_name)
            timestamp = int(file_name.split('.')[0])  # 从文件名中提取时间戳
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            pickle_files.append((timestamp, data))
    # 按时间戳排序
    pickle_files.sort(key=lambda x: x[0])
    return pickle_files

def find_closest_match(vis_ts, tac_data):
    """在触觉数据中找到与视觉时间戳最接近的数据"""
    closest_tac = None
    min_diff = float('inf')
    for tac_ts, tac in tac_data:
        diff = abs(vis_ts - tac_ts)
        if diff < min_diff:
            min_diff = diff
            closest_tac = (tac_ts, tac)
        if diff > time_threshold:  # 超过限差直接跳过
            break
    return closest_tac if min_diff <= time_threshold else None

def combine_data(vis_data, tac_data):
    """根据时间戳匹配视觉和触觉数据，并保存到新pickle文件中"""
    combined_count = 0
    for vis_ts, vis in vis_data:
        match = find_closest_match(vis_ts, tac_data)
        if match:
            tac_ts, tac = match
            combined_data = {
                "vis_timestamp": vis_ts,
                "tac_timestamp": tac_ts,
                "depth_image": vis["depth_image"],
                "color_image": vis["color_image"],
                "tac_data": tac
            }
            # 保存到新文件
            output_file = os.path.join(output_folder, f"{vis_ts}_{tac_ts}.pkl")
            with open(output_file, 'wb') as f:
                pickle.dump(combined_data, f)
            combined_count += 1
    print(f"完成组合数据，共生成 {combined_count} 个文件！")

if __name__ == "__main__":
    # 加载视觉和触觉数据
    print("加载视觉数据...")
    vis_data = load_pickle_files(vis_data_folder)
    print(f"视觉数据加载完成，共 {len(vis_data)} 帧！")

    print("加载触觉数据...")
    tac_data = load_pickle_files(tac_data_folder)
    print(f"触觉数据加载完成，共 {len(tac_data)} 帧！")

    # 组合数据
    print("开始匹配并组合数据...")
    combine_data(vis_data, tac_data)
    print("数据处理完成！")