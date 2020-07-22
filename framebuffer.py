from PIL import Image, ImageFont, ImageDraw, ImageSequence
import numpy as np
import serial
import time
import sys
import cv2
from mss import mss

import pyautogui

from luma.core.interface.serial import ftdi_spi
from luma.core.render import canvas
from luma.oled.device import ssd1322
from time import sleep

#serial = ftdi_spi(device='ftdi://ftdi:232h/', gpio_DC=5, gpio_RST=6)
#device = ssd1322(serial)

#mon = {'top': 200, 'left': 200, 'width': 1920, 'height': 1080}
#mon = {"top": 0, "left": 1080, "width": 160, "height": 135}
#mon = {"top": 1000, "left": 1000, "width": 800, "height": 640}
mon = {"top": 0, "left": 0, "width": 3000, "height": 3000}


sct = mss()

while True:
    sct_img = sct.grab(mon)


    #video = pyautogui.screenshot(region=(0, 0, 3000, 3000))
    video = Image.frombytes('RGB', sct_img.size, sct_img.bgra, "raw", "BGRX")

    #video = Image.open('/tmp/cover.jpg')
    #cv2.imshow('test', np.array(video))
    cv2.imshow('/tmp/cover.jpg', 0)
    cv2.waitKey(0)

    #mini_video = video.copy()

    #img = Image.new('RGB', (256, 64))
    #img.paste(mini_video.resize((256,64)), (0, 0))

    #device.display(img)

    #time.sleep(1)

