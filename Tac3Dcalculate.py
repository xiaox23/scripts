import os
import pickle
import numpy as np

def load_pickle_file(file_path):
    # 加载单个 pickle 文件。
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def save_pickle_file(data, file_path):
    # 保存数据到 pickle 文件。
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)

def process_pickle_files(input_folder):
    # input_folder (str): 包含 pickle 文件的输入文件夹。
    # 获取目录中的所有 .pkl 文件，按文件名排序
    pickle_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.pkl')], 
                        key=lambda x: int(x.split('.')[0]))

    if not pickle_files:
        print("No pickle files found in the input folder.")
        return

    # 加载第一个文件的 P1 P2
    first_file_path = os.path.join(input_folder, pickle_files[0])
    first_data = load_pickle_file(first_file_path)
    if "P1" not in first_data:
        print(f"P1 key not found in the first file: {first_file_path}")
        return
    if "P2" not in first_data:
        print(f"P2 key not found in the first file: {first_file_path}")
        return

    # 保存第一个文件的 P1 P2 到变量
    P1 = first_data["P1"]
    P2 = first_data["P2"]

    # 遍历每个 pickle 文件，计算 PP1 PP2 和 PP1ref PP2ref 并保存
    for file_name in pickle_files:
        file_path = os.path.join(input_folder, file_name)
        data = load_pickle_file(file_path)

        # 检查是否有 D1 D2数据
        if "D1" not in data:
            print(f"D1 key not found in file: {file_path}")
            continue
        if "D2" not in data:
            print(f"D2 key not found in file: {file_path}")
            continue

        D1 = data["D1"]
        D2 = data["D2"]

        # 计算 PP1 PP2
        PP1 = P1 + D1
        data["PP1"] = PP1  # 将 PP1 保存到数据字典中
        data["PP1ref"] = P1  # 将 P1 保存为 PPref
        PP2 = P2 + D2
        data["PP2"] = PP2  # 将 PP1 保存到数据字典中
        data["PP2ref"] = P2  # 将 P1 保存为 PPref

        # 更新 pickle 文件
        save_pickle_file(data, file_path)
        print(f"Updated file: {file_path}")

if __name__ == "__main__":
    # 输入存放 pickle 文件的目录
    input_folder = "result/test3"

    # 处理并保存数据
    process_pickle_files(input_folder)
