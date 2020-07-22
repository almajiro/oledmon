#from luma.core.interface.serial import i2c

from luma.core.interface.serial import ftdi_spi
from luma.core.render import canvas
from luma.oled.device import ssd1322
from time import sleep

# serial = i2c(port=1, address=0x3C)

serial = ftdi_spi(device='ftdi://ftdi:2232h/1', gpio_DC=5, gpio_RST=6)
device = ssd1322(serial)

# Box and text rendered in portrait mode
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((10, 40), "Hello World", fill="white")

sleep(10)
