#!/bin/bash

# Activate the Python virtual environment if required
# Uncomment and modify the following line if you're using a virtual environment
# source /path/to/your/virtualenv/bin/activate

echo "Starting A02VisData.py and A01TacData.py..."

gnome-terminal --title="vis" -- bash -c "python scripts/G02VisData.py --base_folder data_save/vis_data --exp_number 1"  &

gnome-terminal  --title="tac" -- bash -c "python scripts/G01TacData.py --folder_path data_save/tac_data --exp_number 1" &

gnome-terminal  --title="traj" -- bash -c "python scripts/G03TrajData.py --path data_save/traj_data --exp_number 1" &

gnome-terminal  --title="gui" -- bash -c  "python scripts/G07GUI.py --folder_path data_save/tac_data --exp_number 1" &

wait

echo "Both scripts have finished running."