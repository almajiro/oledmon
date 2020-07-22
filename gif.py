from PIL import Image, ImageFont, ImageDraw, ImageSequence
import numpy as np
import serial
import time
import sys


CONTROL_WORD = 0x04
COMMAND_WORD = 0x02
WRITE_START_WORD = 0xE0
WRITE_END_WORD = 0xF0

def send_byte(byte):
    device.write(bytes([byte & 0xFF]))

def send_data(byte):
#    send_byte(0xE4)
    send_byte(byte)
#    send_byte(WRITE_END_WORD)

def send_command(byte):
    send_byte(0x06)
    send_byte(byte)

def val_map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def sec_to_min(value):
    minute = 0
    while (value >= 60):
        value -= 60
        minute += 1
    return '{:02}'.format(minute) + ':' + '{:02}'.format(value)

def send_buffer(bitmap):
    send_byte(0xE4)
    
    for row in bitmap:
        for col in range(0, len(row), 2):
            data = 0x00
    
            if row[col]:
                data |= int(val_map(row[col], 0, 256, 0, 15))  << 4
    
            if row[col+1]:
                data |= int(val_map(row[col+1], 0, 256, 0, 15))
    
            send_data(data)

    #send_byte(0x06)

def grayscale(img):
    rgb = np.array(img, dtype="float32");
    
    rgbL = pow(rgb/255.0, 2.2)
    r, g, b = rgbL[:,:,0], rgbL[:,:,1], rgbL[:,:,2]
    grayL = 0.299 * r + 0.587 * g + 0.114 * b  # BT.601
    gray = pow(grayL, 1.0/2.2)*255

    return gray

device = serial.Serial('/dev/ttyUSB2', 1500000)

gif = Image.open('ab.gif')

while True:
    for i, f in enumerate(ImageSequence.Iterator(gif)):
        img = Image.new('RGB', (256, 64), (0 ,0 ,0))

        img.paste(f.resize((256,64)), (0,0))

        #time.sleep(0.0001)
        send_buffer(grayscale(img))

device.close()
