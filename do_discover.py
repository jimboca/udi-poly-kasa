#!/usr/bin/env python3

import logging,asyncio
from kasa import Discover

#logger = logging.getLogger(__name__)
#logging.basicConfig(
#    level=10,
#    format='%(levelname)s:\t%(name)s\t%(message)s'
#)
#logger.setLevel(logging.WARNING)
#logging.getLogger('kasa.discover').setLevel(logging.DEBUG)

async def print_device(dev):
    await dev.update()
    print("print_device:")
    print("print_device: Got Device\n\tAlias:{}\n\tModel:{}\n\tMac:{}\n\tHost:{}".
            format(dev.alias,dev.model,dev.mac,dev.host))
    if dev.is_bulb:
        print("print_device: it's a bulb")
    elif dev.is_strip:
        print("print_device: it's a smart strip")
    elif dev.is_plug:
        print("print_device: it's a plug")
    else:
        print("What is this: {}".format(dev))

devices = asyncio.run(Discover.discover(on_discovered=print_device))
