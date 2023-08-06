This project is a python module for woriking with NooLite USB stick (PC118, PC1116, PC1132).
Can be easy used for making a smarthome.
About NooLite: http://www.noo.com.by/

Author: Anton Balashov
E-mail: sicness(_at_)darklogic.ru
License: GPL v3
Site: https://github.com/Sicness/pyNooLite

Example:

  import noolite

  n = noolite.NooLite()
  n.on(0)       # Turn power on on first channel
  n.off(0)      # Turn power off on first channel
  n.set(1, 115) # Set 115 level on second channel
  n.bind(7)     # send "bind" signal on channel 8

Look at example.py for a extra example

Dependences:

* python module pyusb
For Ubuntu do: 
sudo apt-get install python-pip 
sudo pip install pyusb

* To have access to device from common user add rule to udev, for example to /etc/udev/rules.d/50-noolite.rules next line:
ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="05df", SUBSYSTEMS=="usb", ACTION=="add", MODE="0666", GROUP="dialout"
And add your user to dialout group:
sudo usermod <user> -a -G dialout

Forked from https://github.com/kyuri/nooLite commit 504b9bd7572ba8f5b337fbb27cd3343fcbbd8550
