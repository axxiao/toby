import os
import argparse
import time
from datetime import datetime

def main(args):
    name = os.path.join(args.target, args.file)
    print(f"Writing to {name}")
    while True:
        with open(name, 'a') as f:
            f.write(str(datetime.utcnow()) + '\n')
        time.sleep(args.intevral)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Write to disk every for a defined period')
    parser.add_argument('-t', '--target', type=str, required=True,
                        help='target folder (on the usb device)')
    parser.add_argument('-i', '--intevral', type=int, required=False,
                        default=120, help='Interval (seconds), default [120]s')
    parser.add_argument('-f', '--file', type=str, required=False,
                        default='alive.log', help='File name, default [alive.log]')
    main(parser.parse_args())
