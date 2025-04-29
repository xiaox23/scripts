import os
import pickle
import numpy as np

def load_pickle_file(file_path):
    """加载单个 pickle 文件"""
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def save_pickle_file(data, file_path):
    """保存数据到 pickle 文件"""
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)

def process_combined_data(input_folder, output_folder):
    """
    处理 combined_data 文件夹中的 pickle 文件，计算 PP1, PP2 及其参考值，并保存到 cal_data。
    Args:
        input_folder (str): 包含 combined_data 的输入文件夹。
        output_folder (str): 保存处理后数据的输出文件夹。
    """
    # 获取目录中的所有 .pkl 文件，按文件名排序
    pickle_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.pkl')], 
                          key=lambda x: int(x.split('.')[0]))

    if not pickle_files:
        print(f"No pickle files found in the input folder: {input_folder}")
        return

    # 加载第一个文件的 P1 和 P2
    first_file_path = os.path.join(input_folder, pickle_files[0])
    first_data = load_pickle_file(first_file_path)
    if "tac_data" not in first_data:
        print(f"'tac_data' key not found in the first file: {first_file_path}")
        return

    tac_data = first_data["tac_data"]
    if "P1" not in tac_data or "P2" not in tac_data:
        print(f"'P1' or 'P2' key not found in the first file: {first_file_path}")
        return

    # 保存第一个文件的 P1 和 P2
    P1 = tac_data["P1"]
    P2 = tac_data["P2"]

    # 遍历目录中的每个 pickle 文件
    for file_name in pickle_files:
        file_path = os.path.join(input_folder, file_name)
        data = load_pickle_file(file_path)

        # 检查是否存在 tac_data 和 D1, D2
        if "tac_data" not in data:
            print(f"'tac_data' key not found in file: {file_path}")
            continue

        tac_data = data["tac_data"]
        if "P1" not in tac_data or "P2" not in tac_data:
            print(f"'P1' or 'P2' key not found in file: {file_path}")
            continue

        # 读取 D1 和 D2
        PP1 = tac_data["P1"]
        PP2 = tac_data["P2"]

        # 保存计算结果到新数据字典中
        tac_data["PP1"] = PP1
        tac_data["PP1ref"] = P1
        tac_data["PP2"] = PP2
        tac_data["PP2ref"] = P2

        # 构造输出文件路径
        output_file = os.path.join(output_folder, file_name)

        # 保存处理后的数据到新文件
        save_pickle_file(data, output_file)
        print(f"Processed and saved file: {output_file}")

if __name__ == "__main__":
    # 输入存放 combined_data 的目录
    combined_data_base_folder = "data_save/combined_data"
    output_base_folder = "data_save/cal_data"

    # 遍历每个实验编号的文件夹
    for exp_number in sorted(os.listdir(combined_data_base_folder)):
        input_folder = os.path.join(combined_data_base_folder, exp_number)
        output_folder = os.path.join(output_base_folder, exp_number)

        # 跳过非目录项
        if not os.path.isdir(input_folder):
            continue

        # 创建输出文件夹
        os.makedirs(output_folder, exist_ok=True)

        print(f"Processing experiment: {exp_number}")
        process_combined_data(input_folder, output_folder)











##############################################
"""Contents of the pickle file:
vis_timestamp: <class 'int'>
  Value: 1745655532229
depth_image: <class 'numpy.ndarray'>
  Shape: (480, 640)
color_image: <class 'numpy.ndarray'>
  Shape: (480, 640, 3)
tac_data: <class 'dict'>
  Length: 16
  tac_data contents:
    pos: <class 'float'>
      Value: 33.25111770629883
    force: <class 'float'>
      Value: 4.998503684997559
    P1: <class 'numpy.ndarray'>
      Shape: (400, 3)
    D1: <class 'numpy.ndarray'>
      Shape: (400, 3)
    F1: <class 'numpy.ndarray'>
      Shape: (400, 3)
    Fr1: <class 'numpy.ndarray'>
      Shape: (1, 3)
    Mr1: <class 'numpy.ndarray'>
      Shape: (1, 3)
    P2: <class 'numpy.ndarray'>
      Shape: (400, 3)
    D2: <class 'numpy.ndarray'>
      Shape: (400, 3)
    F2: <class 'numpy.ndarray'>
      Shape: (400, 3)
    Fr2: <class 'numpy.ndarray'>
      Shape: (1, 3)
    Mr2: <class 'numpy.ndarray'>
      Shape: (1, 3)
    PP1: <class 'numpy.ndarray'>
      Shape: (400, 3)
    PP1ref: <class 'numpy.ndarray'>
      Shape: (400, 3)
    PP2: <class 'numpy.ndarray'>
      Shape: (400, 3)
    PP2ref: <class 'numpy.ndarray'>
      Shape: (400, 3)"""