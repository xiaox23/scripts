import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import cv2


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


def process_and_plot_cal_data(input_base_folder, output_base_folder, x_range=(-50, 50), y_range=(-50, 50)):
    """
    读取 cal_data 文件夹中的数据，绘制并保存视觉图像、触觉图像，以及 PP1 和 PP2 的二维图像。
    Args:
        input_base_folder (str): 包含 cal_data 的输入文件夹。
        output_base_folder (str): 保存绘图的输出文件夹。
        x_range (tuple): x 轴范围 (min, max)。
        y_range (tuple): y 轴范围 (min, max)。
    """
    # 遍历每个实验编号文件夹
    for exp_number in sorted(os.listdir(input_base_folder)):
        input_folder = os.path.join(input_base_folder, exp_number)
        output_folder = os.path.join(output_base_folder, exp_number)

        # 跳过非目录项
        if not os.path.isdir(input_folder):
            continue

        # 确保输出目录存在
        os.makedirs(output_folder, exist_ok=True)

        # 获取目录中的所有 .pkl 文件，按文件名排序
        pickle_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.pkl')], 
                              key=lambda x: int(x.split('.')[0]))

        if not pickle_files:
            print(f"No pickle files found in the input folder for experiment {exp_number}.")
            continue

        # 遍历每个文件
        for file_name in pickle_files:
            file_path = os.path.join(input_folder, file_name)
            data = load_pickle_file(file_path)

            # 获取视觉数据：RGB 和深度图像
            depth_image = data.get("depth_image")
            color_image = data.get("color_image")

            # 获取触觉数据
            tac_data = data.get("tac_data", {})
            P1 = tac_data.get("P1")
            PP1 = tac_data.get("PP1")
            PP1ref = tac_data.get("PP1ref")
            PP2 = tac_data.get("PP2")
            PP2ref = tac_data.get("PP2ref")

            # 如果视觉或触觉数据缺失，跳过处理
            if depth_image is None or color_image is None or P1 is None:
                print(f"Skipping file {file_name} due to missing data.")
                continue

            # ========== 绘制视觉图像 ==========
            try:
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                combined_image = np.hstack((color_image, depth_colormap))
                combined_output_path = os.path.join(output_folder, f"{file_name}_combined_visual.png")
                cv2.imwrite(combined_output_path, combined_image)
                print(f"Saved combined visual image: {combined_output_path}")
            except Exception as e:
                print(f"Error saving visual image for {file_name}: {e}")

            # ========== 绘制触觉图像 ==========
            try:
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                if P1.shape[1] == 3:  # 检查数据形状是否正确
                    x, y, z = P1[:, 0], P1[:, 1], P1[:, 2]
                    scatter = ax.scatter(x, y, z, c=z, cmap='viridis', marker='o')
                    ax.set_xlabel("X")
                    ax.set_ylabel("Y")
                    ax.set_zlabel("Z")
                    ax.set_title(f"3D Plot of P1 ({file_name})")
                    plt.colorbar(scatter, ax=ax, label="Z Value")
                    tactile_output_path = os.path.join(output_folder, f"{file_name}_tactile.png")
                    plt.savefig(tactile_output_path)
                    plt.close(fig)
                    print(f"Saved tactile image: {tactile_output_path}")
                else:
                    print(f"Invalid P1 shape in {file_name}. Skipping tactile visualization.")
                    plt.close(fig)
            except Exception as e:
                print(f"Error saving tactile image for {file_name}: {e}")

            # ========== 绘制并保存二维图像 ==========
            try:
                plot_title = f"2D Plot of PP1/PP1ref and PP2/PP2ref ({file_name})"
                save_path = os.path.join(output_folder, f"{file_name.split('.')[0]}_2d_plot.png")
                plot_2d_data_in_one_fig(PP1, PP1ref, PP2, PP2ref, plot_title, save_path, x_range, y_range)
            except Exception as e:
                print(f"Error saving 2D plot for {file_name}: {e}")


if __name__ == "__main__":
    # 输入存放 cal_data 的目录
    input_base_folder = "data_save/cal_data"

    # 输出保存绘图的目录
    output_base_folder = "data_save/cal_plots"

    # 固定 x 和 y 的范围
    x_range = (-15, 15)  # 根据数据范围设置
    y_range = (-15, 15)  # 根据数据范围设置

    # 处理并绘制数据
    process_and_plot_cal_data(input_base_folder, output_base_folder, x_range, y_range)