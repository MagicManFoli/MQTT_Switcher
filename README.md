# MQTT_Switcher
This short script is used to trigger 433MHz radio sockets from MQTT messages.
Customize this to your likings by modifying `mapping.py`
It would be nice to port this into a docker container but interfacing with GPIOs via raspberry-remote is easier when native.

## Hardware

Connect your transmitter module like described in many other guides:
1. Data: GPIO 0 (wiringpi) / Pin 11 / GPIO 17
2. 5V
3. GND

A receiver can be connected to sniff code from the remote control, the 
default pin is GPIO 2 / pin 13 / GPIO 27. 
This is necessary for the configuration, I have not found a way to calculate it yet.

See this image (not made by me, please don't sue me!):
![Pin Codes](https://pi4j.com/1.2/images/j8header-3b.png)

## Installation
Because this script accesses GPIO (which can be dangerous) you need to manually unlock it:
1. Allow yourself access to GPIOs with `usermod -aG gpio modischpi`
2. Relog/Restart (*yes I really mean that*) to update group policies for your account

It might be necessary to configure your Pi to wait for network connections before starting this service.
Example setup for raspbian-style systems:  
1. `sudo raspi-config` -> Boot -> Wait for Network at Boot  
1. `sudo reboot now`

## Code configurations

You need to fill in the config and pass it to the container.

### Trying to find the pattern between (system id + device id + state) and the rpi-rf code

Sockets: Brennenstuhl RCS 1000SN, very easy and generic device with DIPs for channel selection

#### Recordings (view as raw)
(default config, default pins)
["01010", "2"] true: 4477265 [pulselength 308, protocol 1]
-> 100 0100 0101 0001 0101 0001
["01010", "2"] false: 4477268 [pulselength 310, protocol 1]
-> 100 0100 0101 0001 0101 0100

["01010", "1"] true: 4474193 [pulselength 308, protocol 1]
-> 100 0100 0100 0101 0101 | 0001‬

["01010", "1"] false: 4474196
-> 100 0100 0100 0101 0101 0100


SYS, DEV        RECEIVED        REC (BIN)
"01011", 1" ON: 4457809     -> 0100 0100 0000 0101 0101 0001‬ -> 440551
"01011", 1" OFF: 4457812    -> 0100 0100 0000 0101 0101 0100 -> 440554

"01010", "1" ON: 4474193    -> 0100 0100 0100 0101 0101 0001‬ -> 444551
"01010", "1" OFF: 4474196   -> 0100 0100 0100 0101 0101 0100 -> 444554

"01010", "2" ON: 4477265    -> 0100 0100 0101 0001 0101 0001 -> 445151
"01010", "2" OFF: 4477268   -> 0100 0100 0101 0001 0101 0100 -> 445154

"11010", 1" ON: 279889      -> 0000 0100 0100 0101 0101 0001 -> 044551
"11010", 1" OFF: 279892     -> 0000 0100 0100 0101 0101 0100‬ -> 044554

"01010", 5" ON: ??          -> 0100 0100 XXXX XXXX 0101 0001
"01010", 5" OFF: ??         -> 0100 0100 XXXX XXXX 0101 0100


#### References

https://github.com/HeptaSean/SocketPi/blob/master/socket_switch.py

24 bits
every second bit is 0 and can be ignored -> [0, 1, 4, 5]

last block is on/off -> 1 is on, 4 is off

TODO: diff INPUT -> OUTPUT line by line to find corresponding bits

https://github.com/sui77/rc-switch/blob/master/RCSwitch.cpp
https://github.com/r10r/rcswitch-pi/blob/master/RCSwitch.cpp
switchOn(SYS: str, DEV: int)

## Developer hints

Be aware that you are unable to completely use it on a desktop as it depends on RPI's GPIOs.
YOu will probably need to comment out the import for that and set a breakpoint somewhere.

### Test script manually without docker
Get it to your System:
1. `git clone ###`
2. `cd MQTT_Switcher`
4. `git checkout dockerize`
4. `chmod +x build.sh`

Update to newest version
3. `git pull [origin dockerize]`
5. `pipenv update`
6. `pipenv shell`

Execute
1. `export PYTHONPATH=.`        -> enables relative imports from /app
2. `python3 app/main.py -f config.yaml`
3. send MQTT messages with the correct topics


