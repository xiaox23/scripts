import os
import cv2
import pickle
import numpy as np


def visualize_from_pickle(input_folder, output_folder):
    """
    Reads depth and RGB images from pickle files and saves visualized images.
    
    Args:
        input_folder (str): Folder containing the pickle files.
        output_folder (str): Folder to save the visualized images.
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each pickle file in the input folder
    for file_name in os.listdir(input_folder):
        if not file_name.endswith('.pkl'):
            continue  # Skip non-pickle files

        file_path = os.path.join(input_folder, file_name)

        # Load the pickle file
        with open(file_path, 'rb') as f:
            data = pickle.load(f)

        # Extract depth and color images
        depth_image = data.get("depth_image")
        color_image = data.get("color_image")

        # Skip if data is missing
        if depth_image is None or color_image is None:
            print(f"Skipping file {file_name} due to missing data.")
            continue

        # Visualize depth as a colormap
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack RGB and depth images for visualization
        combined_image = np.hstack((color_image, depth_colormap))

        # Save the visualized images
        base_name = os.path.splitext(file_name)[0]  # Get file name without extension
        rgb_output_path = os.path.join(output_folder, f"{base_name}_rgb.png")
        depth_output_path = os.path.join(output_folder, f"{base_name}_depth.png")
        combined_output_path = os.path.join(output_folder, f"{base_name}_combined.png")

        # Save individual and combined images
        cv2.imwrite(rgb_output_path, color_image)
        cv2.imwrite(depth_output_path, depth_colormap)
        cv2.imwrite(combined_output_path, combined_image)

        print(f"Processed and saved: {rgb_output_path}, {depth_output_path}, {combined_output_path}")


def main():
    # Define input folder containing pickle files and output folder for visualized images
    input_folder = "data_save/vis_data"  # Folder containing saved pickle files
    output_folder = "data_save/visualized_images"  # Folder to save visualized images

    # Run the visualization
    visualize_from_pickle(input_folder, output_folder)


if __name__ == "__main__":
    main()