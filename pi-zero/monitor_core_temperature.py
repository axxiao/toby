import psutil
import time
from datetime import datetime
import os
import math
import argparse


def main(average_mins=5, max_temp=90):
    """
    :param average_mins
    """
    # or command: vcgencmd measure_temp
    temps = []
    while True:
        temp = psutil.sensors_temperatures()['cpu-thermal']
        if temp[0].current > max_temp:
            print("FATAL!\nSystem temperature is {} C too HIGH!".format("{:.2f}".format(temp[0].current)))
            print("Will reboot NOW! @{} UTC".format(datetime.utcnow().isoformat()))
            time.sleep(1)
            os.system("sudo reboot") # end
        temps.append(temp[0].current)
        if len(temps) > (12 * average_mins):
            avg = sum(temps) / len(temps)
            print("The average tempature in past {} minutes was: "
                  "{} C, top was {} C @{} UTC".format(str(average_mins), "{:.2f}".format(avg), 
                                                      "{:.2f}".format(max(temps)),
                                                      datetime.utcnow().isoformat())
                    )
            temps = []       
        time.sleep(5)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--mins', type=int,
                        help='output evey x minutes')
    parser.add_argument('--max', type=int,
                        help='max temperature which will trigger reboot')
    args = parser.parse_args()
    main(args.mins, args.max)
