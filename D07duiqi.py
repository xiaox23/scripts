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
            timestamps.append(int(file.split('.')[0]))  # 横坐标：文件名（时间戳，转换为整数）
            pos_values.append(data["pos"])  # 读取 pos
            force_values.append(data["force"])  # 读取 force
            P1_max_values.append(np.max(data["P1"]))  # 读取 P1 最大值

    # 转换为 numpy 数组以便绘图
    timestamps = np.array(timestamps)
    pos_values = np.array(pos_values)
    force_values = np.array(force_values)
    P1_max_values = np.array(P1_max_values)

    # 筛选横坐标范围 [1745576224874, 1745576234449]
    x_min, x_max = 1745576224874, 1745576234449
    mask = (timestamps >= x_min) & (timestamps <= x_max)
    timestamps = timestamps[mask]
    pos_values = pos_values[mask]
    force_values = force_values[mask]
    P1_max_values = P1_max_values[mask]

    # 时间延迟！！！100是自己调的。
    # P1_max_values 的横坐标减去 100
    P1_timestamps = timestamps - 100

    # 创建绘图窗口
    plt.figure(figsize=(12, 6))

    # 绘制 pos
    plt.plot(timestamps, pos_values, label="pos", color="blue", linewidth=2)
    # 绘制 force
    plt.plot(timestamps, force_values, label="force", color="green", linewidth=2)
    # 绘制 P1 最大值
    plt.plot(P1_timestamps, P1_max_values, label="P1 Max (adjusted x)", color="red", linewidth=2)

    # 绘制竖线
    plt.axvline(x=27485+1.7455762e12, color='black', linestyle='--', linewidth=1.5, label="x=27388")

    # 设置图例
    plt.legend(loc="upper right", fontsize=12)

    # 设置横纵坐标标签
    plt.xlabel("Timestamps (File Names)", fontsize=14)
    plt.ylabel("Values", fontsize=14)

    # 设置横坐标范围
    plt.xlim(min(timestamps), max(timestamps))

    # 设置更密集的横坐标刻度
    plt.xticks(
        ticks=np.linspace(min(timestamps), max(timestamps), 100, dtype=int),  # 现在的 10 倍密度
        rotation=45,
        fontsize=10
    )

    # 禁用科学计数法
    plt.ticklabel_format(style='plain', axis='x')

    # 添加网格
    plt.grid(alpha=0.4)

    # 设置标题
    plt.title("Variation of pos, force, and P1 Max with Adjusted Timestamps", fontsize=16)

    # 调整布局并显示图表
    plt.tight_layout()
    plt.show()

# 调用函数，传入保存 .pkl 文件的文件夹路径
folder_path = 'data_save/tac_data'  # 修改为实际的保存路径
read_and_plot(folder_path)