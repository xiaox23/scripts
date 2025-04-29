import os
import time
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse

def load_latest_pickle(folder_path):
    """
    Load the latest pickle file from the specified folder.
    """
    files = [f for f in os.listdir(folder_path) if f.endswith('.pkl')]
    if not files:
        return None
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))
    file_path = os.path.join(folder_path, latest_file)
    
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    return data

def update(frame, folder_path, scatter, quiver):
    data = load_latest_pickle(folder_path)
    if data:
        P1 = data.get("P1", np.zeros((0, 3)))
        F1 = data.get("F1", np.zeros((0, 3)))

        if P1.size > 0 and F1.size > 0:
            scatter._offsets3d = (P1[:, 0], P1[:, 1], P1[:, 2])
            if quiver:
                quiver.remove()  # Remove previous quiver if it exists
            # Increase length, linewidth, and arrowhead size
            quiver = ax.quiver(P1[:, 0], P1[:, 1], P1[:, 2], F1[:, 0], F1[:, 1], F1[:, 2], 
                                length=10, color='r', normalize=False, linewidth=3, arrow_length_ratio=0.5)
    return scatter, quiver

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time 3D Visualization of Tac3D Data.")
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

    # Set up the figure and 3D axis
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Points and Vectors')

    # Initial scatter and quiver
    scatter = ax.scatter([], [], [])
    quiver = None  # Initialize quiver to None

    # Create animation
    ani = FuncAnimation(fig, update, fargs=(exp_folder_path, scatter, quiver), interval=1000)

    plt.show()

# python scripts/G07GUI.py --folder_path data_save/tac_data --exp_number 1