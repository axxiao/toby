#!/bin/bash
export PYTHONPATH="$PYTHONPATH:/opt/workspace/toby/"
echo "Start Toby Temperature Monitor"
source /opt/pyenvs/toby/bin/activate
python /opt/workspace/toby/system/monitor_core_temperature.py --mins 3
