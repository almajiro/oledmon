#from luma.core.interface.serial import i2c

from PIL import Image, ImageFont, ImageDraw, ImageSequence
from luma.core.interface.serial import ftdi_spi
from luma.core.render import canvas
from luma.oled.device import ssd1322
import time

# serial = i2c(port=1, address=0x3C)

serial = ftdi_spi(device='ftdi://ftdi:2232h/1', gpio_DC=5, gpio_RST=6, bus_speed_hz=20000000)
device = ssd1322(serial)

# Box and text rendered in portrait mode
#with canvas(device) as draw:
#    draw.rectangle(device.bounding_box, outline="white", fill="black")
#    draw.text((10, 40), "Hello World", fill="white")
#
#sleep(10)

gif = Image.open('gifs/kbyd.gif')

while True:
    for i, f in enumerate(ImageSequence.Iterator(gif)):
        img = Image.new('RGB', (256, 64), (0 ,0 ,0))
        img.paste(f.resize((256,64)), (0,0))
        time.sleep(0.005)

        device.display(img)
