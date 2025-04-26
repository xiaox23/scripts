#!/bin/bash

# Activate the Python virtual environment if required
# Uncomment and modify the following line if you're using a virtual environment
# source /path/to/your/virtualenv/bin/activate

# Run A02VisData.py and A01TacData.py simultaneously
echo "Starting A02VisData.py and A01TacData.py..."

gnome-terminal --title="vis" -- bash -c "python3 scripts/E02VisData.py --data_folder data_save/vis_data"  &

# echo "The PID of the terminal is $!"

gnome-terminal  --title="tac" -- bash -c "python3 scripts/E01TacData.py --folder_path data_save/tac_data" &

# echo "The PID of the terminal is $!"

# Wait for both scripts to finish (optional)
wait

echo "Both scripts have finished running."