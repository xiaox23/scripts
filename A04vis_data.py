import os
import pickle
import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def visualize_and_save(pickle_folder, output_folder):
    """
    从 pickle 文件中读取视觉和触觉数据，并绘制保存。
    
    Args:
        pickle_folder (str): 存放 pickle 文件的文件夹路径。
        output_folder (str): 保存绘制图像的文件夹路径。
    """
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 遍历每个 pickle 文件
    for file_name in os.listdir(pickle_folder):
        if not file_name.endswith(".pkl"):
            continue  # 跳过非 pickle 文件

        file_path = os.path.join(pickle_folder, file_name)

        # 加载 pickle 文件
        with open(file_path, 'rb') as f:
            data = pickle.load(f)

        # 获取视觉数据：RGB 和深度图像
        depth_image = data.get("depth_image")
        color_image = data.get("color_image")

        # 获取触觉数据：3D 点云（假设存储在 P1 中）
        P1 = data.get("tac_data", {}).get("P1")

        # 如果视觉或触觉数据缺失，跳过处理
        if depth_image is None or color_image is None or P1 is None:
            print(f"Skipping file {file_name} due to missing data.")
            continue

        # ========== 绘制视觉图像 ==========
        # 将深度图像转换为伪彩色图像
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # 保存单独的 RGB 图像
        rgb_output_path = os.path.join(output_folder, f"{file_name}_rgb.png")
        cv2.imwrite(rgb_output_path, color_image)

        # 保存单独的深度图像
        depth_output_path = os.path.join(output_folder, f"{file_name}_depth.png")
        cv2.imwrite(depth_output_path, depth_colormap)

        # 保存合并的视觉图像
        combined_image = np.hstack((color_image, depth_colormap))
        combined_output_path = os.path.join(output_folder, f"{file_name}_combined_visual.png")
        cv2.imwrite(combined_output_path, combined_image)
        print(f"Saved visual images: {rgb_output_path}, {depth_output_path}, {combined_output_path}")

        # ========== 绘制触觉图像 ==========
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
        else:
            print(f"Invalid shape for P1 in file {file_name}. Skipping tactile visualization.")
            plt.close(fig)
            continue

        # 保存触觉图像
        tactile_output_path = os.path.join(output_folder, f"{file_name}_tactile.png")
        plt.savefig(tactile_output_path)
        plt.close(fig)
        print(f"Saved tactile image: {tactile_output_path}")

if __name__ == "__main__":
    # 输入 pickle 文件夹路径
    pickle_folder = "data_save/combined_data"  # 存放保存的 pickle 文件
    output_folder = "data_save/visualized_combined"  # 输出图像保存路径

    # 执行可视化和保存
    visualize_and_save(pickle_folder, output_folder)