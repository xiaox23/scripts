import os
import pickle
import numpy as np

# 路径配置
vis_data_base_folder = "data_save/vis_data"  # 视觉数据基础路径
tac_data_base_folder = "data_save/tac_data"  # 触觉数据基础路径
traj_data_base_folder = "data_save/traj_data"  # 轨迹数据基础路径
output_base_folder = "data_save/combined_data"  # 输出数据基础路径
os.makedirs(output_base_folder, exist_ok=True)

# 时间戳匹配限差（单位：毫秒）
time_threshold = 100  # 允许的时间误差范围

def load_pickle_files(folder_path):
    """加载指定文件夹下所有的pickle文件，并根据时间戳排序"""
    pickle_files = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pkl'):
            file_path = os.path.join(folder_path, file_name)
            timestamp = int(file_name.split('.')[0])  # 从文件名中提取时间戳
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
            except:
                print(f"Error loading {file_path}")
            pickle_files.append((timestamp, data))
    # 按时间戳排序
    pickle_files.sort(key=lambda x: x[0])
    return pickle_files

def load_grasp_time(grasp_time_file):
    """加载 grasp_time.txt 中的时间戳"""
    try:
        with open(grasp_time_file, 'r') as f:
            lines = f.readlines()
        # 提取最后一行的时间戳（假设 grasp_time.txt 按时间顺序保存时间戳）
        grasp_time = int(lines[-1].strip())
        return grasp_time
    except Exception as e:
        print(f"无法读取文件 {grasp_time_file}：{e}")
        return None

def load_traj_data(traj_folder):
    """加载轨迹数据并提取时间戳和 O_T_EE 数据"""
    traj_data = []
    for file_name in os.listdir(traj_folder):
        if file_name.endswith('.pkl'):
            file_path = os.path.join(traj_folder, file_name)
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            # 提取时间戳和 O_T_EE
            if 0 in data and 'skill_state_dict' in data[0]:
                timestamps = list(map(int, data[0]['skill_state_dict']['time_since_skill_started']))
                otee = data[0]['skill_state_dict']['O_T_EE']
                for ts, pose in zip(timestamps, otee):
                    traj_data.append((ts, pose))
    # 按时间戳排序
    traj_data.sort(key=lambda x: x[0])
    return traj_data

def find_closest_match(vis_ts, data):
    """在数据中找到与视觉时间戳最接近的数据"""
    closest = None
    min_diff = float('inf')  # 初始化最小时间差为无穷大
    
    for ts, value in data:
        diff = abs(vis_ts - ts)
        if diff < min_diff:  # 更新最小时间差
            min_diff = diff
            closest = (ts, value)
    
    return closest if min_diff <= time_threshold else None

def combine_data(vis_data, tac_data, traj_data, output_folder):
    """根据时间戳匹配视觉、触觉和轨迹数据，并保存到新pickle文件中"""
    combined_count = 0
    for vis_ts, vis in vis_data:
        tac_match = find_closest_match(vis_ts, tac_data)
        traj_match = find_closest_match(vis_ts, traj_data)

        if tac_match and traj_match:
            _, tac = tac_match
            _, otee = traj_match
            combined_data = {
                "vis_timestamp": vis_ts,
                "depth_image": vis["depth_image"],
                "color_image": vis["color_image"],
                "tac_data": tac,
                "O_T_EE": otee
            }
            output_file = os.path.join(output_folder, f"{vis_ts}.pkl")
            with open(output_file, 'wb') as f:
                pickle.dump(combined_data, f)
            combined_count += 1
    print(f"完成组合数据，共生成 {combined_count} 个文件！")

def remove_files_below_threshold(output_folder, grasp_time):
    """删除文件名小于 grasp_time 的所有 .pkl 文件"""
    removed_count = 0
    for file_name in os.listdir(output_folder):
        if file_name.endswith('.pkl'):
            file_path = os.path.join(output_folder, file_name)
            timestamp = int(file_name.split('.')[0])  # 从文件名中提取时间戳
            if timestamp < grasp_time:
                os.remove(file_path)
                removed_count += 1
    print(f"删除了 {removed_count} 个小于 grasp_time ({grasp_time}) 的文件！")

if __name__ == "__main__":
    # 读取实验目录（假设视觉和触觉数据的子文件夹结构一致）
    vis_experiment_folders = sorted(os.listdir(vis_data_base_folder))
    tac_experiment_folders = sorted(os.listdir(tac_data_base_folder))
    traj_experiment_folders = sorted(os.listdir(traj_data_base_folder))

    # 遍历实验编号文件夹
    for exp_number in vis_experiment_folders:
        vis_folder = os.path.join(vis_data_base_folder, exp_number)
        tac_folder = os.path.join(tac_data_base_folder, exp_number)
        traj_folder = os.path.join(traj_data_base_folder, exp_number)
        output_folder = os.path.join(output_base_folder, exp_number)

        if not os.path.exists(tac_folder):
            print(f"实验 {exp_number} 缺少触觉数据，跳过...")
            continue

        grasp_time_file = os.path.join(tac_folder, "grasp_time.txt")
        if not os.path.exists(grasp_time_file):
            print(f"实验 {exp_number} 缺少 grasp_time.txt 文件，跳过...")
            continue

        grasp_time = load_grasp_time(grasp_time_file)
        if grasp_time is None:
            print(f"实验 {exp_number} 的 grasp_time 读取失败，跳过...")
            continue

        os.makedirs(output_folder, exist_ok=True)

        print(f"加载实验 {exp_number} 的视觉数据...")
        vis_data = load_pickle_files(vis_folder)
        print(f"视觉数据加载完成，共 {len(vis_data)} 帧！")

        print(f"加载实验 {exp_number} 的触觉数据...")
        tac_data = load_pickle_files(tac_folder)
        print(f"触觉数据加载完成，共 {len(tac_data)} 帧！")

        print(f"加载实验 {exp_number} 的轨迹数据...")
        traj_data = load_traj_data(traj_folder)
        print(f"轨迹数据加载完成，共 {len(traj_data)} 帧！")

        print(f"开始匹配并组合实验 {exp_number} 的数据...")
        combine_data(vis_data, tac_data, traj_data, output_folder)

        print(f"删除实验 {exp_number} 中小于 grasp_time 的文件...")
        remove_files_below_threshold(output_folder, grasp_time)

        print(f"实验 {exp_number} 的数据处理完成！")