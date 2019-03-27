#!/usr/bin/env python3

import logging
from pyHS100 import Discover

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=10,
    format='%(levelname)s:\t%(name)s\t%(message)s'
)
logger.setLevel(logging.DEBUG) 
logging.getLogger('pyHS100.discover').setLevel(logging.DEBUG)

print("Starting discovery...")
for dev in Discover.discover().values():
    print("discover: Got Device\n\tAlias:{}\n\tModel:{}\n\tMac:{}\n\tHost:{}".
            format(dev.alias,dev.model,dev.mac,dev.host))
    cname = dev.__class__.__name__
    print("discover: {}".format(cname))
    if cname == 'SmartStrip':
        print("  Nice, it's a smart strip")
    else:
        print("What is this: {}".format(dev))

