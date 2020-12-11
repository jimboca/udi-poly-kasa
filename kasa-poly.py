#!/usr/bin/env python
"""
This is a TP-Link Kasa NodeServer for Polyglot v2 written in Python3
by JimBo jimboca3@gmail.com
"""

import sys
import polyinterface
import time
import warnings
from nodes import Controller

LOGGER = polyinterface.LOGGER

if __name__ == "__main__":
    # Some are getting unclosed socket warnings due to garbage collection?? no idea why, so just ignore them since we dont' care
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<socket.socket.*>")
    if sys.version_info < (3, 6):
        LOGGER.error("ERROR: Python 3.6 or greater is required not {}.{}".format(sys.version_info[0],sys.version_info[1]))
        sys.exit(1)
    try:
        polyglot = polyinterface.Interface('Kasa')
        """
        Instantiates the Interface to Polyglot.
        The name doesn't really matter unless you are starting it from the
        command line then you need a line TPLinkKasa=N
        where N is the slot number.
        """
        polyglot.start()
        """
        Starts MQTT and connects to Polyglot.
        """
        control = Controller(polyglot)
        """
        Creates the Controller Node and passes in the Interface
        """
        control.runForever()
        """
        Sits around and does nothing forever, keeping your program running.
        """
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        """
        Catch SIGTERM or Control-C and exit cleanly.
        """
