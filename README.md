# MQTT_Switcher
This short script is used to trigger 433MHz radio sockets from MQTT messages.
Customize this to your likings by modifying `mapping.py`
It would be nice to port this into a docker container but interfacing with GPIOs via raspberry-remote is easier when native.

## Hardware

Connect your transmitter module like described in many other guides:
1. Data: GPIO 0 (wiringpi) / Pin 11 / GPIO 17
2. 5V
3. GND

A receiver can be connected to sniff code from the remote control, 
default pin is GPIO 2 / pin 13 / GPIO 27.

See this image (not made by me, please don't sue me!):
![Pin Codes](https://pi4j.com/1.2/images/j8header-3b.png)

## Installation
1. Allow yourself access to GPIOs with `usermod -aG gpio modischpi`
2. Relog/Restart (*yes I really mean that*) to update group policies for your account



It might be necessary to configure your Pi to wait for network connections before starting this service.
Example setup for raspbian-style systems:  
1. `sudo raspi-config` -> Boot -> Wait for Network at Boot  
1. `sudo reboot now`

## Config
(default config)
["01010", "2"] true: 4477265 [pulselength 308, protocol 1]
-> 100 0100 0101 0001 0101 0001
["01010", "2"] false: 4477268 [pulselength 310, protocol 1]
-> 100 0100 0101 0001 0101 0100

["01010", "1"] true: 4474193 [pulselength 308, protocol 1]
-> 100 0100 0100 0101 0101 | 0001‬

["01010", "1"] false: 4474196
-> 100 0100 0100 0101 0101 0100


SYS, DEV        RECEIVED        REC (BIN)
"01011", 1" ON: 4457809     -> 100 0100 0000 0101 0101 0001‬ -> 440551
"01011", 1" OFF: 4457812    -> 100 0100 0000 0101 0101 0100 -> 440554

"01010", "1" ON: 4474193    -> 100 0100 0100 0101 0101 0001‬ -> 444551
"01010", "1" OFF: 4474196   -> 100 0100 0100 0101 0101 0100 -> 444554

"01010", "2" ON: 4477265    ->                              -> 445151
"01010", "2" OFF: 4477268   ->                              -> 445154

"11010", 1" ON: 279889      ->      100 0100 0101 0101 0001 -> 044551
"11010", 1" OFF: 279892     ->      100 0100 0101 0101 0100‬ -> 044554


https://github.com/HeptaSean/SocketPi/blob/master/socket_switch.py
https://github.com/sui77/rc-switch/blob/master/RCSwitch.cpp
https://github.com/r10r/rcswitch-pi/blob/master/RCSwitch.cpp
switchOn(SYS: str, DEV: int)     -> 

## Debugging

Test script manually with 
1. `export PYTHONPATH=.`        -> allow relative imports from /app
2. `python3 app/main.py -f config.yaml`
3. send MQTT messages with the correct topics

