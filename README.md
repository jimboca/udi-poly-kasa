
[![Build Status](https://travis-ci.org/jimboca/udi-poly-kasa.svg?branch=master)](https://travis-ci.org/jimboca/udi-kasa)

# harmony-polyglot

This is the [TP Link Kasa](https://www.kasasmart.com/us) Poly for the [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with  [Polyglot V2](https://github.com/Einstein42/udi-polyglotv2)
(c) JimBoCA aka Jim Searle
MIT license.

This node server is intended to support all devices supported by the [pyHS100 Python Library](https://github.com/GadgetReactor/pyHS100/blob/master/README.md) but currently it only supports:
- PowerStrips
  - HS300
more will be added as requested, and time allows.  Feel free to Fork this repo and add support as you like and send me a pull request.

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
8. Once all nodes are added you will need to close and re-open the admin console the new custom profile is loaded.


## Kasa Controller

This is the main node created by this nodeserver and manages the hubs.

### Node Settings
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
   * Not currently used

### Node Commands

The commands for this node

#### Query
   * Poll's all devices and sets all status in the ISY
#### Discover
   * Run's the auto-discover to find your devices
#### Install Profile
   * This uploads the current profile into the ISY.
   * Typically this is not necessary, but sometimes the ISY needs the profile uploaded twice.


# Issues

If you have an issue where the nodes are not showing up properly, open the Polyglot UI and go to Kasa -> Details -> Log, and click 'Download Log Package' and send that to jimboca3@gmail.com as an email attachment, or send it in a PM [Universal Devices Forum](https://forum.universal-devices.com/messenger)

# Upgrading

Open the Polyglot web page, go to nodeserver store and click "Update" for "Kasa".

Then restart the Kasa nodeserver by selecting it in the Polyglot dashboard and select Control -> Restart, then watch the log to make sure everything goes well.

# Release Notes
- 2.0.0 03/27/2019
  - Initial version
