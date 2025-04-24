import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

def load_pickle_file(file_path):
    """
    加载单个 pickle 文件。
    Args:
        file_path (str): pickle 文件路径。
    Returns:
        dict: 加载的 pickle 数据。
    """
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def plot_2d_data_in_one_fig(PP1, PP1ref, PP2, PP2ref, title, save_path, x_range=(-50, 50), y_range=(-50, 50)):
    """
    绘制 PP1 和 PP1ref 以及 PP2 和 PP2ref 的二维图像，并保存到一个图像中。
    Args:
        PP1 (numpy.array): 形状为 (400, 3)，绘制的第一个二维图数据。
        PP1ref (numpy.array): 形状为 (400, 3)，PP1 的参考数据。
        PP2 (numpy.array): 形状为 (400, 3)，绘制的第二个二维图数据。
        PP2ref (numpy.array): 形状为 (400, 3)，PP2 的参考数据。
        title (str): 图像标题。
        save_path (str): 保存图像的路径。
        x_range (tuple): x 轴范围 (min, max)。
        y_range (tuple): y 轴范围 (min, max)。
    """
    if (PP1 is None or PP1.shape[1] < 2 or PP1ref is None or PP1ref.shape[1] < 2 or
        PP2 is None or PP2.shape[1] < 2 or PP2ref is None or PP2ref.shape[1] < 2):
        print("Invalid data for 2D plotting.")
        return

    # 创建一个图像，包含两个子图（1 行 2 列）
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 绘制第一个子图：PP1 和 PP1ref
    ax1 = axes[0]
    ax1.scatter(PP1ref[:, 0], PP1ref[:, 1], c='blue', s=10, alpha=0.7, label="PP1ref")  # 蓝色散点
    ax1.scatter(PP1[:, 0], PP1[:, 1], c='orange', s=10, alpha=0.7, label="PP1")  # 橙色散点
    ax1.set_xlim(x_range)
    ax1.set_ylim(y_range)
    ax1.set_xlabel('X Coordinate')
    ax1.set_ylabel('Y Coordinate')
    ax1.set_title("PP1 vs PP1ref")
    ax1.legend()
    ax1.grid(True)

    # 绘制第二个子图：PP2 和 PP2ref
    ax2 = axes[1]
    ax2.scatter(PP2ref[:, 0], PP2ref[:, 1], c='blue', s=10, alpha=0.7, label="PP2ref")  # 蓝色散点
    ax2.scatter(PP2[:, 0], PP2[:, 1], c='orange', s=10, alpha=0.7, label="PP2")  # 橙色散点
    ax2.set_xlim(x_range)
    ax2.set_ylim(y_range)
    ax2.set_xlabel('X Coordinate')
    ax2.set_ylabel('Y Coordinate')
    ax2.set_title("PP2 vs PP2ref")
    ax2.legend()
    ax2.grid(True)

    # 设置总标题
    fig.suptitle(title, fontsize=16)

    # 保存图像
    plt.savefig(save_path, dpi=300)
    print(f"Saved plot to {save_path}")
    plt.close()  # 关闭当前图像，释放内存

def process_and_plot(input_folder, output_folder, x_range=(-50, 50), y_range=(-50, 50)):
    """
    读取 pickle 文件，绘制 PP1 和 PP1ref 以及 PP2 和 PP2ref 的二维图像，并保存结果。
    Args:
        input_folder (str): 包含 pickle 文件的输入文件夹。
        output_folder (str): 保存绘图的输出文件夹。
        x_range (tuple): x 轴范围 (min, max)。
        y_range (tuple): y 轴范围 (min, max)。
    """
    # 获取目录中的所有 .pkl 文件，按文件名排序
    pickle_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.pkl')], 
                          key=lambda x: int(x.split('.')[0]))

    if not pickle_files:
        print("No pickle files found in the input folder.")
        return

    # 确保输出目录存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历每个文件
    for file_name in pickle_files:
        file_path = os.path.join(input_folder, file_name)
        data = load_pickle_file(file_path)

        # 检查是否有 PP1, PP1ref, PP2 和 PP2ref 数据
        if "PP1" not in data or "PP1ref" not in data or "PP2" not in data or "PP2ref" not in data:
            print(f"PP1, PP1ref, PP2, or PP2ref key not found in file: {file_path}")
            continue

        PP1 = data["PP1"]
        PP1ref = data["PP1ref"]
        PP2 = data["PP2"]
        PP2ref = data["PP2ref"]

        # 绘制并保存图像
        plot_title = f"2D Plot of PP1/PP1ref and PP2/PP2ref ({file_name})"
        save_path = os.path.join(output_folder, f"{file_name.split('.')[0]}.png")
        plot_2d_data_in_one_fig(PP1, PP1ref, PP2, PP2ref, plot_title, save_path, x_range, y_range)

if __name__ == "__main__":
    # 输入存放 pickle 文件的目录
    input_folder = "result/test3"

    # 输出保存绘图的目录
    output_folder = "result/deform3"

    # 固定 x 和 y 的范围
    x_range = (-15, 15)  # 根据数据范围设置
    y_range = (-15, 15)  # 根据数据范围设置

    # 处理并绘制数据
    process_and_plot(input_folder, output_folder, x_range, y_range)