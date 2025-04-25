#!/bin/bash

# Activate the Python virtual environment if required
# Uncomment and modify the following line if you're using a virtual environment
# source /path/to/your/virtualenv/bin/activate

# Run A02VisData.py and A01TacData.py simultaneously
echo "Starting A02VisData.py and A01TacData.py..."

python3 scripts/C01TacData.py --folder_path data_save/tac_data &
python3 scripts/C02VisData.py --data_folder data_save/vis_data

# Wait for both scripts to finish (optional)
wait

echo "Both scripts have finished running."