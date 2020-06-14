import psutil
import time
from datetime import datetime
import os
import math
import argparse
import logging
import subprocess


def tail(f, n, offset=0):
    proc = subprocess.Popen(['tail', '-n', n + offset, f], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    return lines[:, -offset]


def main(average_mins=10, max_temp=90, log_path='/tmp/', max_reboot=3, check_intevral=5):
    """
    Monitor tempature and reboot/ power off
    """
    # or command: vcgencmd measure_temp
    logger = logging.get_logger()
    logger.info('Monitor Starting")
    temps = []
    while True:
        temp = psutil.sensors_temperatures()['cpu-thermal']
        if temp[0].current > max_temp:
            logger.error("FATAL!\nSystem temperature is {} C too HIGH!".format("{:.2f}".format(temp[0].current)))
            logger.error("Will reboot NOW! @{} UTC".format(datetime.utcnow().isoformat()))
            time.sleep(1)
            # check temp_critical.log
            cmd = 'reboot'
            os.system("sudo {}".format(cmd)) # end
        temps.append(temp[0].current)
        if len(temps) > (12 * average_mins):
            avg = sum(temps) / len(temps)
            logger.info("The average tempature in past {} minutes was: " +
                        "{} C, top was {} C @{} UTC".format(str(average_mins), "{:.2f}".format(avg), 
                                                            "{:.2f}".format(max(temps)),
                                                            datetime.utcnow().isoformat())
                        )
            temps = []       
        time.sleep(check_intevral)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--mins', type=int, default=10,
                        help='output evey x minutes')
    parser.add_argument('--max', type=int, deafult=90,
                        help='max temperature which will trigger reboot')
    parser.add_argument('--max-reboot', type=int, default=5,
                        help='max reboot times before swith off powers')
    parser.add_argument('--log-path', type=str,
                        default='/opt/workspace/logs/monitor',
                        help='max temperature which will trigger reboot')
    args = parser.parse_args()
    main(args.mins, args.max, args.log-path, args.max-reboot)
