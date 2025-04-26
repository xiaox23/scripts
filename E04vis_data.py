# import os
# import pickle
# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from datetime import datetime

# def visualize_and_save(pickle_folder, output_folder, x_range=(-50, 50), y_range=(-50, 50)):
#     """
#     从 pickle 文件中读取视觉、触觉数据，同时绘制 marker flow，并保存结果到一个文件夹中。
    
#     Args:
#         pickle_folder (str): 存放 pickle 文件的文件夹路径。
#         output_folder (str): 保存所有图像的文件夹路径。
#         x_range (tuple): 绘制 marker flow 图像时的 x 轴范围 (min, max)。
#         y_range (tuple): 绘制 marker flow 图像时的 y 轴范围 (min, max)。
#     """
#     # 创建输出文件夹
#     os.makedirs(output_folder, exist_ok=True)

#     # 获取当前时间戳，用于文件命名
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

#     # 遍历每个 pickle 文件
#     for file_name in os.listdir(pickle_folder):
#         if not file_name.endswith(".pkl"):
#             continue  # 跳过非 pickle 文件

#         file_path = os.path.join(pickle_folder, file_name)

#         # 加载 pickle 文件
#         with open(file_path, 'rb') as f:
#             data = pickle.load(f)

#         # 获取视觉数据：RGB 和深度图像
#         depth_image = data.get("depth_image")
#         color_image = data.get("color_image")

#         # 获取触觉数据：从 tac_data 中提取
#         tac_data = data.get("tac_data", {})
#         P1 = tac_data.get("P1")
#         D1 = tac_data.get("D1")
#         F1 = tac_data.get("F1")
#         P2 = tac_data.get("P2")
#         D2 = tac_data.get("D2")
#         F2 = tac_data.get("F2")

#         # 如果视觉或触觉数据缺失，跳过处理
#         if depth_image is None or color_image is None or P1 is None or P2 is None:
#             print(f"Skipping file {file_name} due to missing visual or tactile data.")
#             continue

#         # 使用时间戳和文件名作为前缀
#         file_prefix = f"{timestamp}_{file_name.split('.')[0]}"

#         # ========== 绘制视觉图像 ==========
#         # 将深度图像转换为伪彩色图像
#         depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

#         # 保存合并的视觉图像
#         combined_image = np.hstack((color_image, depth_colormap))
#         combined_output_path = os.path.join(output_folder, f"{file_prefix}_combined_visual.png")
#         cv2.imwrite(combined_output_path, combined_image)

#         # ========== 绘制触觉点云图像 ==========
#         fig = plt.figure()
#         ax = fig.add_subplot(111, projection='3d')

#         # 绘制 P1 点云
#         if P1.shape[1] == 3:  # 检查 P1 是否为 3D 点云
#             x, y, z = P1[:, 0], P1[:, 1], P1[:, 2]
#             scatter = ax.scatter(x, y, z, c=z, cmap='viridis', marker='o')
#             ax.set_xlabel("X")
#             ax.set_ylabel("Y")
#             ax.set_zlabel("Z")
#             ax.set_title(f"3D Plot of P1 ({file_name})")
#             plt.colorbar(scatter, ax=ax, label="Z Value")
#         else:
#             print(f"Invalid shape for P1 in file {file_name}. Skipping tactile visualization.")
#             plt.close(fig)
#             continue

#         # 保存触觉点云图像
#         tactile_output_path = os.path.join(output_folder, f"{file_prefix}_tactile.png")
#         plt.savefig(tactile_output_path)
#         plt.close(fig)
#         print(f"Saved tactile image: {tactile_output_path}")

#         # ========== 绘制 marker flow 图像 ==========
#         # 绘制 P1 -> P2 的 marker flow
#         if P1.shape == P2.shape:  # 确保 P1 和 P2 的形状一致
#             fig, ax = plt.subplots(figsize=(8, 8))
#             ax.quiver(P1[:, 0], P1[:, 1], P2[:, 0] - P1[:, 0], P2[:, 1] - P1[:, 1],
#                       angles='xy', scale_units='xy', scale=1, color='blue', alpha=0.6)
#             ax.set_xlim(x_range)
#             ax.set_ylim(y_range)
#             ax.set_xlabel('X Coordinate')
#             ax.set_ylabel('Y Coordinate')
#             ax.set_title(f"Marker Flow (P1 -> P2) ({file_name})")
#             ax.grid(True)

#             # 保存 marker flow 图像
#             marker_output_path = os.path.join(output_folder, f"{file_prefix}_marker_flow.png")
#             plt.savefig(marker_output_path, dpi=300)
#             plt.close(fig)
#             print(f"Saved marker flow image: {marker_output_path}")
#         else:
#             print(f"P1 and P2 shapes do not match in file {file_name}. Skipping marker flow visualization.")

# if __name__ == "__main__":
#     # 输入 pickle 文件夹路径
#     pickle_folder = "data_save/combined_data"  # 存放保存的 pickle 文件
#     output_folder = "data_save/visualized_combined"  # 输出图像保存路径

#     # 固定 x 和 y 的范围
#     x_range = (-15, 15)  # 根据数据范围设置
#     y_range = (-15, 15)  # 根据数据范围设置

#     # 执行可视化和保存
#     visualize_and_save(pickle_folder, output_folder, x_range, y_range)

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

        # 保存合并的视觉图像
        combined_image = np.hstack((color_image, depth_colormap))
        combined_output_path = os.path.join(output_folder, f"{file_name}_combined_visual.png")
        cv2.imwrite(combined_output_path, combined_image)
        # print(f"Saved visual images: {rgb_output_path}, {depth_output_path}, {combined_output_path}")

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