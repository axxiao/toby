#!/usr/bin/env bash
source /opt/workspace/toby/set_variables.sh
gunicorn -b 192.168.1.100:12116 -w 4 --threads 8 toby:app
