#!/bin/bash

# Activate the Python virtual environment if required
# Uncomment and modify the following line if you're using a virtual environment
# source /path/to/your/virtualenv/bin/activate

# Run A02VisData.py and A01TacData.py simultaneously
echo "Starting A02VisData.py and A01TacData.py..."

python3 scripts/A02VisData.py &
python3 scripts/A01TacData.py &

# Wait for both scripts to finish (optional)
wait

echo "Both scripts have finished running."