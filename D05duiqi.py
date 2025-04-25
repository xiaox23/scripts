import os
import pickle
import matplotlib.pyplot as plt
import numpy as np

# 定义读取和绘图的函数
def read_and_plot(folder_path):
    # 获取文件夹中所有 .pkl 文件，按文件名排序
    files = sorted([f for f in os.listdir(folder_path) if f.endswith('.pkl')], key=lambda x: int(x.split('.')[0]))
    
    # 初始化存储数据的列表
    timestamps = []
    pos_values = []
    force_values = []
    P1_max_values = []

    # 遍历所有文件，读取数据
    for file in files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            timestamps.append(file.split('.')[0])  # 横坐标：文件名（时间戳）
            pos_values.append(data["pos"])  # 读取 pos
            force_values.append(data["force"])  # 读取 force
            P1_max_values.append(np.max(data["P1"]))  # 读取 P1 最大值

    # 转换为 numpy 数组以便绘图
    pos_values = np.array(pos_values)
    force_values = np.array(force_values)
    P1_max_values = np.array(P1_max_values)

    # 创建绘图窗口和子图
    fig, axs = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    # 绘制 pos
    axs[0].plot(timestamps, pos_values, label="pos", color="blue")
    axs[0].set_ylabel("Pos")
    axs[0].legend()
    axs[0].grid()

    # 绘制 force
    axs[1].plot(timestamps, force_values, label="force", color="green")
    axs[1].set_ylabel("Force")
    axs[1].legend()
    axs[1].grid()

    # 绘制 P1 最大值
    axs[2].plot(timestamps, P1_max_values, label="P1 Max", color="red")
    axs[2].set_ylabel("P1 Max")
    axs[2].legend()
    axs[2].grid()

    # 设置横坐标
    axs[2].set_xlabel("Timestamps (File Names)")

    # 调整布局
    plt.tight_layout()
    plt.show()

# 调用函数，传入保存 .pkl 文件的文件夹路径
folder_path = 'data_save/tac_data'  # 修改为实际的保存路径
read_and_plot(folder_path)