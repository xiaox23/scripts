import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import cv2

def load_pickle_file(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def process_and_plot_cal_data(input_base_folder, output_base_folder, x_range=(-50, 50), y_range=(-50, 50)):
    """
    读取 cal_data 文件夹中的数据，绘制并保存视觉图像、触觉图像，以及 PP1 和 PP2 的二维图像。
    Args:
        input_base_folder (str): 包含 cal_data 的输入文件夹。
        output_base_folder (str): 保存绘图的输出文件夹。
        x_range (tuple): x 轴范围 (min, max)。
        y_range (tuple): y 轴范围 (min, max)。
    """
    for exp_number in sorted(os.listdir(input_base_folder)):
        input_folder = os.path.join(input_base_folder, exp_number)
        output_folder = os.path.join(output_base_folder, exp_number)

        if not os.path.isdir(input_folder):
            continue

        os.makedirs(output_folder, exist_ok=True)

        pickle_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.pkl')], 
                              key=lambda x: int(x.split('.')[0]))

        if not pickle_files:
            print(f"No pickle files found in the input folder for experiment {exp_number}.")
            continue

        first_frame = True
        first_P1, first_P2 = None, None  # 存储第一帧的 P1 和 P2

        for idx, file_name in enumerate(pickle_files):
            file_path = os.path.join(input_folder, file_name)
            data = load_pickle_file(file_path)

            # 获取视觉数据：RGB 和深度图像
            depth_image = data.get("depth_image")
            color_image = data.get("color_image")
            depth_image515 = data.get("depth_image515")
            color_image515 = data.get("color_image515")

            # 获取触觉数据
            tac_data = data.get("tac_data", {})
            P1 = tac_data.get("P1")
            P2 = tac_data.get("P2")

            # 如果视觉或触觉数据缺失，跳过处理
            if depth_image is None or color_image is None or P1 is None:
                print(f"Skipping file {file_name} due to missing data.")
                continue

            # 存储第一帧的 P1 和 P2
            if first_frame:
                first_P1 = P1
                first_P2 = P2
                first_frame = False

            # 绘制视觉图像
            try:
                # 绘制原始视觉图像
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                combined_image = np.hstack((color_image, depth_colormap))
                combined_output_path = os.path.join(output_folder, f"{file_name}_combined_visual.png")
                cv2.imwrite(combined_output_path, combined_image)
                print(f"Saved combined visual image: {combined_output_path}")

                # 绘制515视觉图像
                depth_colormap515 = cv2.applyColorMap(cv2.convertScaleAbs(depth_image515, alpha=0.03), cv2.COLORMAP_JET)
                combined_image515 = np.hstack((color_image515, depth_colormap515))
                combined_output_path515 = os.path.join(output_folder, f"{file_name}_combined_visual515.png")
                cv2.imwrite(combined_output_path515, combined_image515)
                print(f"Saved combined visual image 515: {combined_output_path515}")

            except Exception as e:
                print(f"Error saving visual image for {file_name}: {e}")

            # 绘制触觉图像
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

            # 绘制并保存二维图像
            try:
                plot_title = f"2D Plot of PP1 and PP2 ({file_name})"
                save_path = os.path.join(output_folder, f"{file_name.split('.')[0]}_2d_plot.png")
                plot_2d_data_with_two_subplots(first_P1, first_P2, P1, P2, plot_title, save_path, x_range, y_range)
            except Exception as e:
                print(f"Error saving 2D plot for {file_name}: {e}")

def plot_2d_data_with_two_subplots(first_P1, first_P2, P1, P2, title, save_path, x_range=(-50, 50), y_range=(-50, 50)):
    if (P1 is None or P1.shape[1] < 2 or 
        P2 is None or P2.shape[1] < 2):
        print("Invalid data for 2D plotting.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 左侧子图：P1
    ax1 = axes[0]
    ax1.scatter(first_P1[:, 0], first_P1[:, 1], c='blue', s=10, alpha=0.7, label="First Frame P1")  # 蓝色点
    ax1.scatter(P1[:, 0], P1[:, 1], c='red', s=10, alpha=0.7, label="Current Frame P1")  # 红色点
    ax1.set_xlim(x_range)
    ax1.set_ylim(y_range)
    ax1.set_xlabel('X Coordinate')
    ax1.set_ylabel('Y Coordinate')
    ax1.set_title("First Frame Data")
    ax1.legend()
    ax1.grid(True)

    # 右侧子图：P2
    ax2 = axes[1]
    ax2.scatter(first_P2[:, 0], first_P2[:, 1], c='blue', s=10, alpha=0.7, label="First Frame P2")  # 蓝色点
    ax2.scatter(P2[:, 0], P2[:, 1], c='red', s=10, alpha=0.7, label="Current Frame P2")  # 红色点
    ax2.set_xlim(x_range)
    ax2.set_ylim(y_range)
    ax2.set_xlabel('X Coordinate')
    ax2.set_ylabel('Y Coordinate')
    ax2.set_title("Current Frame Data")
    ax2.legend()
    ax2.grid(True)

    # 设置总标题
    fig.suptitle(title, fontsize=16)

    plt.savefig(save_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    input_base_folder = "data_save/combined_data"
    output_base_folder = "data_save/cal_plots"
    x_range = (-15, 15)
    y_range = (-15, 15)

    process_and_plot_cal_data(input_base_folder, output_base_folder, x_range, y_range)