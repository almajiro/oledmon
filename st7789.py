from PIL import Image
import numbers

from pyftdi.spi import SpiController, SpiIOError
from pyftdi.gpio import GpioController
import time

import numpy as np

ST7789_NOP = 0x00
ST7789_SWRESET = 0x01
ST7789_RDDID = 0x04
ST7789_RDDST = 0x09

ST7789_SLPIN = 0x10
ST7789_SLPOUT = 0x11
ST7789_PTLON = 0x12
ST7789_NORON = 0x13

ST7789_INVOFF = 0x20
ST7789_INVON = 0x21
ST7789_DISPOFF = 0x28
ST7789_DISPON = 0x29

ST7789_CASET = 0x2A
ST7789_RASET = 0x2B
ST7789_RAMWR = 0x2C
ST7789_RAMRD = 0x2E

ST7789_PTLAR = 0x30
ST7789_MADCTL = 0x36
ST7789_COLMOD = 0x3A

ST7789_FRMCTR1 = 0xB1
ST7789_FRMCTR2 = 0xB2
ST7789_FRMCTR3 = 0xB3
ST7789_INVCTR = 0xB4
ST7789_DISSET5 = 0xB6

ST7789_GCTRL = 0xB7
ST7789_GTADJ = 0xB8
ST7789_VCOMS = 0xBB

ST7789_LCMCTRL = 0xC0
ST7789_IDSET = 0xC1
ST7789_VDVVRHEN = 0xC2
ST7789_VRHS = 0xC3
ST7789_VDVS = 0xC4
ST7789_VMCTR1 = 0xC5
ST7789_FRCTRL2 = 0xC6
ST7789_CABCCTRL = 0xC7

ST7789_RDID1 = 0xDA
ST7789_RDID2 = 0xDB
ST7789_RDID3 = 0xDC
ST7789_RDID4 = 0xDD

ST7789_GMCTRP1 = 0xE0
ST7789_GMCTRN1 = 0xE1

ST7789_PWCTR6 = 0xFC

_offset_left = 0
_offset_top = 0

_width = 240
_height = 240

spi = SpiController()
spi.configure('ftdi://ftdi:2232h/2')
tft = spi.get_port(cs=0, freq=24000000, mode=2)

#gpio = GpioController()
#gpio.configure('ftdi://ftdi:2232h/2', (gpio.direction & 0x0F) + 0xF0)

gpio = spi.get_gpio()
gpio.set_direction(0xF0, 0xFF)

# DCX command/data register 1=display data 0=command data
# RST reset is active low

def reset():
    gpio.write(0x40)
    time.sleep(0.5)
    gpio.write(0x00)
    time.sleep(0.5)
    gpio.write(0x40)
    time.sleep(0.5)

def send(data, is_data=True):
    if is_data:
        gpio.write(0x20 | 0x40)
    else:
        gpio.write(0x40)

    if isinstance(data, numbers.Number):
        data = [data & 0xFF]

    tft.write(data)

def command(data):
    send(data, False)

def data(data):
    send(data, True)

def init():
    command(ST7789_SWRESET)    # Software reset
    time.sleep(0.150)               # delay 150 ms

    command(ST7789_SLPOUT)
    time.sleep(0.500)

    command(ST7789_COLMOD)
    data(0x05)

    command(ST7789_MADCTL)
    data(0x00)

    command(ST7789_CASET)
    data(0x00)
    data(0x00)
    data((240 + 0) >> 8)
    data((240 + 0) & 0xFF)

    command(ST7789_RASET)
    data(0x00)
    data(0x00)
    data((240 + 0) >> 8)
    data((240 + 0) & 0xFF)

    command(ST7789_INVON)
    time.sleep(0.100)

    command(ST7789_NORON)
    time.sleep(0.100)

    command(ST7789_DISPON)
    time.sleep(0.500)

def set_window(x0=0, y0=0, x1=None, y1=None):
    if x1 is None:
        x1 = _width - 1

    if y1 is None:
        y1 = _height - 1

    y0 += _offset_top
    y1 += _offset_top

    x0 += _offset_left
    x1 += _offset_left

    command(ST7789_CASET)       # Column addr set
    data(x0 >> 8)
    data(x0 & 0xFF)             # XSTART
    data(x1 >> 8)
    data(x1 & 0xFF)             # XEND
    command(ST7789_RASET)       # Row addr set
    data(y0 >> 8)
    data(y0 & 0xFF)             # YSTART
    data(y1 >> 8)
    data(y1 & 0xFF)             # YEND
    command(ST7789_RAMWR)       # write to RAM

def image_to_data(image, rotation=0):
    pb = np.rot90(np.array(image.convert('RGB')), rotation // 90).astype('uint8')

    result = np.zeros((_width, _height, 2), dtype=np.uint8)
    result[..., [0]] = np.add(np.bitwise_and(pb[..., [0]], 0xF8), np.right_shift(pb[..., [1]], 5))
    result[..., [1]] = np.add(np.bitwise_and(np.left_shift(pb[..., [1]], 3), 0xE0), np.right_shift(pb[..., [2]], 3))
    return result.flatten().tolist()

def display( image):
    set_window()
    pixelbytes = list(image_to_data(image, 0))

    for i in range(0, len(pixelbytes), 4096):
        data(pixelbytes[i:i + 4096])

reset()
init()

print("st7789 initialized")

image = Image.open('cat.jpg')
image = image.resize((240, 240))

# Draw the image on the display hardware.
print('Drawing image')

#display(image)
