from os import environ
import sys
from pyftdi.gpio import GpioController, GpioException
from time import sleep
 
class GpioTest(object):
    """
    """
 
    def __init__(self):
        self._gpio = GpioController()
        self._state = 0  # SW cache of the GPIO output lines
 
    def open(self, out_pins):
        """Open a GPIO connection, defining which pins are configured as
           output and input"""
        out_pins &= 0xFF
        url = environ.get('FTDI_DEVICE', 'ftdi://ftdi:2232h/1')
        self._gpio.open_from_url(url, direction=out_pins)
 
    def close(self):
        """Close the GPIO connection"""
        self._gpio.close()
 
    def set_gpio(self, line, on):
        """Set the level of a GPIO ouput pin.
 
           :param line: specify which GPIO to madify.
           :param on: a boolean value, True for high-level, False for low-level
        """
        if on:
            state = self._state | (1 << line)
        else:
            state = self._state & ~(1 << line)
        self._commit_state(state)
 
    def get_gpio(self, line):
        """Retrieve the level of a GPIO input pin
 
           :param line: specify which GPIO to read out.
           :return: True for high-level, False for low-level
        """
        value = self._gpio.read_port()
        return bool(value & (1 << line))
 
    def _commit_state(self, state):
        """Update GPIO outputs
        """
        self._gpio.write_port(state)
        # do not update cache on error
        self._state = state
 
 
if __name__ == '__main__':
    gpio = GpioTest()
    # mask = 0x80  # AD7=Out
    mask = 0xFF
    gpio.open(mask)
    while True:
        gpio.set_gpio(0, True)
        sleep(0.2)
        gpio.set_gpio(0, False)
        sleep(0.2)
