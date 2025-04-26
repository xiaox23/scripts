#!/bin/bash

# Activate the Python virtual environment if required
# Uncomment and modify the following line if you're using a virtual environment
# source /path/to/your/virtualenv/bin/activate

# Run A02VisData.py and A01TacData.py simultaneously
echo "Starting A02VisData.py and A01TacData.py..."

gnome-terminal --title="vis" -- bash -c "python scripts/F02VisData.py --base_folder data_save/vis_data --exp_number 1"  &

# echo "The PID of the terminal is $!"

gnome-terminal  --title="tac" -- bash -c "python scripts/F01TacData.py --folder_path data_save/tac_data --exp_number 1" &

# echo "The PID of the terminal is $!"

# Wait for both scripts to finish (optional)
wait

echo "Both scripts have finished running."