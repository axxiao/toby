"""
The Camera caputre images

__author__ = "Alex Xiao <http://www.alexxiao.me/>"
__date__ = "2018-04-07"
__version__ = "0.1"

    Version:
        0.1 (07/04/2017): implemented basic version


Classes:
    Camera - the main class
"""
import cv2
import time
from threading import Thread
from .log import get_logger


class Camera(Thread):
    def __init__(self, camera_id=0, logger_name='Camera'):
        self.camera_id = camera_id
        self.cam = None
        self.logger_name = logger_name
        self.logger = get_logger(logger_name)
        self.running = False

    def release(self):
        self.running = False
        # wait for 1/3 second
        time.sleep(0.3)
        if not self.cam.isOpened():
            self.cam.release()

    def run(self):
        try:
            self.running = True
            self.cam = cv2.VideoCapture(self.camera_id)
            while self.running:
                #keep capture
                ret, frame = self.cam.read()
        except:
            if self.cam is not None:
                if not cam.isOpened():
                    self.cam.release()
