# Thanks to the following for contributions that made this file possible:
# - The Herd Of Kittens' gotemp-ldusb.py utility (2008)
#   http://www.thok.org/intranet/python/vernier/README.html
# - Scott Tsai's gotemp-lights.py utility (2010)
#   https://gitorious.org/scottt/gotemp
import os
import struct
import time
from constants import \
    CMD_PACKET_SIZE, CMD_ID_SET_LED_STATE, CMD_ID_GET_LED_STATE, \
    LED_BRIGHTNESS_MED, LED_BRIGHTNESS_MAX, LED_BRIGHTNESS_MIN, \
    LED_COLOR_RED, LED_COLOR_GREEN, LED_COLOR_ORANGE


class Device(object):
    def __init__(self, device, open=False):
        self.fd = None
        self.path = device

        if open:
            self.open()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, val, traceback):
        self.close()

    def open(self):
        if not self.fd:
            self.fd = os.open(self.path, os.O_RDWR)

    def close(self):
        if self.fd:
            os.close(self.fd)
            self.fd = None

    def send_cmd(self, cmd, *args):
        packet = [0] * CMD_PACKET_SIZE
        packet[0] = cmd

        p = 1
        for arg in args:
            packet[p] = arg
            p += 1

        bytes_written = os.write(self.fd,
                                 struct.pack(*(['BBBBBBBB'] + packet)))
        assert(bytes_written == CMD_PACKET_SIZE)

    def _set_led(self, color, brightness=LED_BRIGHTNESS_MED):
        if brightness < LED_BRIGHTNESS_MIN or LED_BRIGHTNESS_MAX < brightness:
            raise TypeError('LED brightness out of range')

        self.send_cmd(CMD_ID_SET_LED_STATE, color, brightness)

    def _get_led_state(self):
        self.send_cmd(CMD_ID_GET_LED_STATE)

    def set_color_red(self):
        self.set_led(LED_COLOR_RED)

    def set_color_green(self):
        self.set_led(LED_COLOR_GREEN)

    def set_color_orange(self):
        self.set_led(LED_COLOR_ORANGE)

    def test_leds(self):
        for color in [LED_COLOR_RED, LED_COLOR_GREEN, LED_COLOR_ORANGE]:
            for brightness in [LED_BRIGHTNESS_MIN, LED_BRIGHTNESS_MAX]:
                self._set_led(color, brightness)
                self._get_led_state()
                time.sleep(0.5)

    def get_reading(self):
        packet = os.read(self.fd, CMD_PACKET_SIZE)
        data = list(struct.unpack("<BBHHH", packet))

        num_samples = data.pop(0)
        seq_num = data.pop(0)  # NOQA

        deg_c = None
        deg_f = None
        for sample in range(num_samples):
            deg_c = data[sample] / 128.0
            deg_f = 9.0 / 5.0 * deg_c + 32

        return (deg_c, deg_f)
