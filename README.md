
[![Build Status](https://travis-ci.org/jimboca/udi-poly-kasa.svg?branch=master)](https://travis-ci.org/jimboca/udi-kasa)

# kasa-polyglot

This is the [TP Link Kasa](https://www.kasasmart.com/us) Poly for the [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)
(c) JimBoCA aka Jim Searle
MIT license.

This node server is intended to support all devices supported by the [pyHS100 Python Library](https://github.com/GadgetReactor/pyHS100/blob/master/README.md) but currently it only supports:
- PowerStrips
  - HS300
more will be added as requested, and time allows.  

This nodeserver relies on a mostly undocumented and officially supported local APO which TP-Link could break at any time.

## Installation

This nodeserver will only work on a machine running on your local network, it will not work with Polyglot Cloud until TP-Link releases a public API for their cloud interface.

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
4. Open the admin console (close and re-open if you had it open) and you should see a new node 'Kasa Controller'
5. The auto-discover should automatically run and find your devices and add them.  Verify by checking the nodeserver log
   * While this is running you can view the nodeserver log in the Polyglot UI to see what it's doing

## Usage

This node server makes every attempt to handle devices which are not responding for any reason, like they are unplugged or powered off.  When a device is Discovered, it is remembered, so if it doesn't respond on the next discovery it will still be an active device and when plugged back in it will be seen as connected.

The node server does not require that you reserve IP addresses for the devices, the device address is remembered based on it's MAC address, so if the IP address changes, it will be properly handled.

## Supported Kasa Devices

The known list of supported devices models are:
  1 HS100 (US)
  1 HS110 (US)
  1 HS300 (US)
  1 KL130 (US)
    * Currently limited to on/off. Can not set brightness, colors or temperature yet.
  1 KL110 (US)
    * Currently limited to on/off. Can not set brightness

### Unknown devices

Any unknown device model should show up as a default device but may not allow proper control.  Please submit an issue to [UDI Poly Kasa Issues](https://github.com/jimboca/udi-poly-kasa/issues) Feel free to Fork this repo and add support as you like and send me a pull request.

## Kasa Controller

This is the main node created by this nodeserver and manages the devices.

### Node Drivers
The settings for this node are

#### Node Server Connected
   * Status of nodeserver process, this should be monitored by a program if you want to know the status
#### TODO: Devices
   * The number of devices currently managed
#### TODO: Debug Mode
   * The debug printing mode
#### TODO: Short Poll
   * This is how often it will Poll the Devices to get status
#### Long Poll
   * Updates other device status like emeter.

### Node Commands

The commands for this node

#### Query
   * Poll's all devices and sets all status in the ISY
#### Discover
   * Run's the auto-discover to find your devices
#### Install Profile
   * This uploads the current profile into the ISY.
   * Typically this is not necessary, but sometimes the ISY needs the profile uploaded twice.

## Kasa Devices

The supported Kasa devices can have different status and commands, but these are the common ones.

### Node Drivers
The settings for this node are

#### Status (ST)
  * Status of device, on, off, or brightness.
#### Connected (GV0)
  * True if device is communicating

### Node Commands

The commands for these nodes

#### Query
  * Poll's all devices and sets all status in the ISY
#### On, Off
  * Turn device on or off

# Issues

If you have an issue where the nodes are not showing up properly, open the Polyglot UI and go to Kasa -> Details -> Log, and click 'Download Log Package' and send that to jimboca3@gmail.com as an email attachment, or send it in a PM [Universal Devices Forum](https://forum.universal-devices.com/messenger)

# Upgrading

Open the Polyglot web page, go to nodeserver store and click "Update" for "Kasa".

Then restart the Kasa nodeserver by selecting it in the Polyglot dashboard and select Control -> Restart, then watch the log to make sure everything goes well.

# Release Notes
- 2.1.0 09/21/2019
  - Merge changes from @eagleco to support plugs, thank you!
  - Fixed to work for those with emeter (HS110) and those without (HS100)
  - Adding support for SmartBulbs, only limited support currently.
- 2.0.3 04/21/2019
  - Fixed controller naming, sorry if you are using this you will need to:
    - Go to Polyglot Web page
    - Update the Nodeserver in the Store
    - Delete the Nodeserver
    - Add it again
- 2.0.2 03/29/2019
  - Fixed shortPoll to properly update
- 2.0.1 03/28/2019
  - Update ST on shortPoll, added heartbeat
- 2.0.0 03/27/2019
  - Initial version
