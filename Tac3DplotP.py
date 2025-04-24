import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def load_pickle_files(folder_path):
    """
    从指定文件夹中加载所有 .pkl 文件。
    
    Args:
        folder_path (str): 存放 .pkl 文件的文件夹路径。
    
    Returns:
        list: 所有加载的 .pkl 文件内容（每个为一个字典）。
    """
    pickle_files = [f for f in os.listdir(folder_path) if f.endswith('.pkl')]
    data_list = []
    
    for file in sorted(pickle_files, key=lambda x: int(x.split('.')[0])):  # 按文件名数字排序
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            data_list.append(data)
    
    return data_list

def plot_3d_data(P, title="3D Plot of P"):
    """
    绘制三维图像。
    
    Args:
        P (numpy.array): 形状为 (400, 3) 的三维点数据。
        title (str): 图像标题。
    """
    if P is None or P.shape[1] != 3:
        print("Invalid data for 3D plotting.")
        return
    
    x = P[:, 0]
    y = P[:, 1]
    z = P[:, 2]
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c=z, cmap='viridis', marker='o')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)
    plt.show()

def process_and_plot(folder_path):
    """
    读取指定文件夹下的所有 .pkl 文件，并绘制 key 为 P 的三维图像。
    
    Args:
        folder_path (str): 存放 .pkl 文件的文件夹路径。
    """
    # 加载所有 pickle 文件
    data_list = load_pickle_files(folder_path)
    
    # 遍历所有数据，提取 key 为 P 的数据并绘制
    for i, data in enumerate(data_list):
        if "P1" in data:  # 假设 P1 是需要绘制的 key
            print(f"Plotting file {i}: {folder_path}/{i}.pkl")
            plot_3d_data(data["P1"], title=f"3D Plot of P1 (File {i})")
        else:
            print(f"No P1 data in file {i}: {folder_path}/{i}.pkl")

if __name__ == "__main__":
    # 指定存放 .pkl 文件的文件夹路径
    folder_path = "result/test3"
    
    # 读取所有 pickle 文件并绘制 P 的三维图像
    process_and_plot(folder_path)