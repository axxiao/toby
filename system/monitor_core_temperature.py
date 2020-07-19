import psutil
import time
from datetime import datetime
import os
import math
import argparse
import subprocess
from ax.log import build_logger


def tail(f, n=10, head=None):
    """
    use Unix command to get last n lines of a file
    and return first #[head] rows
    """
    head = head or n
    head = n if head > n else head
    proc = subprocess.Popen(['tail', '-n', str(n), f], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    return lines[:head]


def main(average_mins=10, max_temp=90, log_path='/tmp/', max_reboot=3, check_intevral=5):
    """
    Monitor tempature and reboot/ power off
    """
    # or command: vcgencmd measure_temp
    logger = build_logger('Monitor-Temperature', 'info')
    logger.info('Monitor Starting')
    temps = []
    while True:
        sensors = psutil.sensors_temperatures()
        temp = None
        current = max([v[0] for k, v in sensors.items() if 'thermal' in k]).current
        # temp = ['cpu-thermal'] for pi-zero
        if current > max_temp:
            logger.error("FATAL!\nSystem temperature is {} C too HIGH!".format("{:.2f}".format(current)))
            logger.error("Will reboot NOW! @{} UTC".format(datetime.utcnow().isoformat()))
            time.sleep(1)
            # check temp_critical.log
            cmd = 'reboot'
            os.system("sudo {}".format(cmd)) # end
        temps.append(current)
        if len(temps) > ((60 / check_intevral) * average_mins):
            avg = sum(temps) / len(temps)
            logger.info("The average tempature in past {} minutes was: "
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
    parser.add_argument('--max', type=int, default=90,
                        help='max temperature which will trigger reboot')
    parser.add_argument('--max_reboot', type=int, default=3,
                        help='max reboot times before swith off powers')
    parser.add_argument('--log_path', type=str,
                        default='/opt/workspace/logs/monitor',
                        help='max temperature which will trigger reboot')
    args = parser.parse_args()
    main(args.mins, args.max, args.log_path, args.max_reboot)
