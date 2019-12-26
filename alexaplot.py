#!/usr/bin/env python3

# install --> (sudo) apt-get install python3-pip bluetooth libbluetooth-dev libudev-dev bluez-hcidump --> (sudo) pip3 install pillow python-ev3dev protobuf src
# depending on your version of EV3Dev, some of these might already be installed
# this is the program that you run to launch the printer system and connect to the Echo
# to run --> (sudo) python3 alexaplot.py

import os
import sys
import time
import logging
import json
import random
import threading
import printer

from enum import Enum
from agt import AlexaGadget



# Set the logging level to INFO to see messages from AlexaGadget
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
logger = logging.getLogger(__name__)


class Picture(Enum):
    """
    The list of directional commands and their variations.
    These variations correspond to the skill slot values.
    """
    TAJMAHAL = ['taj','taj mahal']
    SAINTLOUIS = ['city','saint louis']
    STATUEOFLIBERTY = ['liberty','statue','statue of liberty']
    ME = ['me','myself']


class MindstormsGadget(AlexaGadget):
    """
    A MINDSTORMS plotter that prints based on voice commands.
    """

    def __init__(self):
        """
        Performs Alexa Gadget initialization routines and ev3dev resource allocation.
        """
        super().__init__()

        # Gadget state
        # Start threads

    def on_connected(self, device_addr):
        """
        Gadget connected to the paired Echo device.
        :param device_addr: the address of the device we connected to
        """
        logger.info("{} connected to Echo device".format(self.friendly_name))

    def on_disconnected(self, device_addr):
        """
        Gadget disconnected from the paired Echo device.
        :param device_addr: the address of the device we disconnected from
        """
        logger.info("{} disconnected from Echo device".format(self.friendly_name))

    def on_custom_mindstorms_gadget_control(self, directive):
        """
        Handles the Custom.Mindstorms.Gadget control directive.
        Looks for the payload with the id 'picture'
        """
        try:
            payload = json.loads(directive.payload.decode("utf-8"))
            print("Control payload: {}".format(payload), file=sys.stderr)
            control_type = payload["type"]
            if control_type == "print":

                self._print(payload["picture"])

        except KeyError:
            print("Missing expected parameters: {}".format(directive), file=sys.stderr)

    def _print(self, picture):
        #Take in the payload with the name

        print("Print command: ({})".format(picture), file=sys.stderr)
        print("printing "+picture.lower().replace(" ", "")+".png")

        # conjoin words and make lowercase to match filename
        if picture.lower().replace(" ", "") == "custom":
            # if the print id is "custom" - take a picture using the webcam. Use imagemagick to do canny edge detection and various edits to optimize the picture for printing
            print("taking picture")
            os.system("fswebcam --no-banner -r 640x480 --jpeg 85 -D 1 web-cam-shot.jpg ; convert web-cam-shot.jpg -colorspace gray -canny 0x1+10%+10%  -negate -rotate -90 -posterize 3 -resize 120 -threshold 80% -monochrome custom.png")

        # call printer() from printer.py

        print("starting print")       
        printer.printer(picture.lower().replace(" ", "")+".png")



if __name__ == '__main__':

    gadget = MindstormsGadget()

    print("init alexa plotter")

    # initiate plotter
    gadget.main()

    print("terminate alexa plotter")


