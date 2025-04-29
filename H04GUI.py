import os
import time
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse

# Global variables to store P1 and P2 from the first pickle file
global_P1 = None
global_P2 = None

def load_first_pickle(folder_path):
    """
    Load the first pickle file from the specified folder.
    If no file is found, wait until one is available.
    """
    while True:
        if not os.path.exists(folder_path):
            print(f"Folder '{folder_path}' not found, waiting...")
            time.sleep(1)  # 等待1秒后再次检查
            continue

        files = [f for f in os.listdir(folder_path) if f.endswith('.pkl')]
        if files:
            first_file = min(files, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))
            file_path = os.path.join(folder_path, first_file)
            
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            return data.get("P1", np.zeros((0, 2))), data.get("P2", np.zeros((0, 2)))
        
        print("No files found, waiting...")
        time.sleep(1)  # 等待1秒后再次检查

def load_latest_pickle(folder_path):
    """
    Load the latest pickle file from the specified folder.
    If no file is found, wait until one is available.
    """
    while True:
        files = [f for f in os.listdir(folder_path) if f.endswith('.pkl')]
        if files:
            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))
            file_path = os.path.join(folder_path, latest_file)
            
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            return data.get("P1", np.zeros((0, 2))), data.get("P2", np.zeros((0, 2)))

        print("No files found, waiting...")
        time.sleep(1)  # 等待1秒后再次检查
def update(frame, folder_path, scatter_left, quiver_left, scatter_right, quiver_right):
    global global_P1, global_P2

    data = load_latest_pickle(folder_path)
    if data:
        P1, P2 = data  # 解包返回的元组

        delt_P1 = P1 - global_P1
        delt_P2 = P2 - global_P2

        # 更新左侧图的散点和箭头
        scatter_left.set_offsets(global_P1[:, :2])
        if quiver_left[0] is not None:
            quiver_left[0].remove()
        quiver_left[0] = ax_left.quiver(global_P1[:, 0], global_P1[:, 1], delt_P1[:, 0], delt_P1[:, 1],
                                         angles='xy', scale_units='xy', scale=1, color='r', linewidth=2)

        # 更新右侧图的散点和箭头
        scatter_right.set_offsets(global_P2[:, :2])
        if quiver_right[0] is not None:
            quiver_right[0].remove()
        quiver_right[0] = ax_right.quiver(global_P2[:, 0], global_P2[:, 1], delt_P2[:, 0], delt_P2[:, 1],
                                           angles='xy', scale_units='xy', scale=1, color='r', linewidth=2)

    return scatter_left, quiver_left, scatter_right, quiver_right

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time 2D Visualization of Tac3D Data.")
    parser.add_argument(
        '--folder_path',
        type=str,
        default='data_save/tac_data',
        help="Path to the folder where the data is saved."
    )
    parser.add_argument(
        '--exp_number',
        type=str,
        required=True,
        help="Experiment number (e.g., '0001', '0002')."
    )
    args = parser.parse_args()
    
    # Create the path to the specific experiment folder
    exp_folder_path = os.path.join(args.folder_path, args.exp_number.zfill(4))

    # Load the first P1 and F1
    global_P1, global_P2 = load_first_pickle(exp_folder_path)

    # 设置图形和两个子图
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(10, 5))

    # 设置左侧图的标签和标题
    ax_left.set_xlabel('X (P1)')
    ax_left.set_ylabel('Y (P1)')
    ax_left.set_title('Left Plot: P1')

    # 设置右侧图的标签和标题
    ax_right.set_xlabel('X (P2)')
    ax_right.set_ylabel('Y (P2)')
    ax_right.set_title('Right Plot: P2')

    # 初始化散点和箭头
    scatter_left = ax_left.scatter([], [])
    quiver_left = [None]  # Initialize quiver for left

    scatter_right = ax_right.scatter([], [])
    quiver_right = [None]  # Initialize quiver for right

    # 创建动画
    ani = FuncAnimation(fig, update, fargs=(exp_folder_path, scatter_left, quiver_left, scatter_right, quiver_right), interval=100)

    plt.show()
# python scripts/H07GUI.py --folder_path data_save/tac_data --exp_number 1