# MQTT_Switcher
This short script is used to trigger 433MHz radio sockets from MQTT messages.


## Usage
This service is docker based and will only run on a Raspberry Pi or something similar enough that 
port mappings, GPIO access and libraries are equal. 

### Using a pre-build image

Have a look at docker-compose.yml and copy it to your own setup, I published a pre-build image to Docker Hub.
I would not advice starting this and every other service manually, just use compose.

Customize this to your specific setup by modifying `config.yml`. 
You will surely need to do that as most remote controlled sockets use different codes.

Start it using `docker-compose up -d` when ready.

### Building your own image (*not recommended*)

Clone this repository and build it by calling `docker-compose up --build -d`. 
Follow the recipe provided in the previous chapter to configure your system.

### Manual execution

You can execute it manually by cloning and following the developer hints below.
Don't do this if you are unsure or you will get conflicts with the python distribution 
provided by your OS.

## Hardware

Connect your transmitter module like described in many other guides:
1. Data: GPIO 0 (wiringpi) / Pin 11 / GPIO 17
2. 5V
3. GND

A receiver can be connected to sniff code from the remote control, the 
default pin is GPIO 2 / pin 13 / GPIO 27. 
This is necessary for the configuration, I have not found a way to calculate it yet, see [Code configurations].

See this image (not made by me, please don't sue me!):
![Pin Codes](https://pi4j.com/1.2/images/j8header-3b.png)

## Allow GPIO
*This is needed only once per system and might have ben done already.*

This script accesses GPIO (which can be used maliciously), you need to manually unlock it:
1. Allow yourself access to GPIOs with `usermod -aG gpio modischpi`
2. Relog/Restart (*yes I really mean that*) to update group policies for your account

You might get the message `RuntimeError: No access to /dev/mem.  Try running as root!`, 
this is an indicator that the previous step did not work (or you forgot to restart).
You can also try exposing only /dev/gpiomem instead, which is a usable subset of mem.

It might be necessary to configure your Pi to wait for network connections before starting this service.
This script makes several attempts to connect, but it's better to be on the safe side.
Example setup for raspbian-style systems:  
1. `sudo raspi-config` -> Boot -> Wait for Network at Boot  
1. `sudo reboot now`

----------------------------------------------

## Code configurations

You need to fill in the config and pass it to the container.

You have a few different options depending on your system:
1. Self-learning sockets: A
2. Selectable Codes: A or B

Solutions:  
A: Read it with a 433MHz receiver. Refer to rpi-rf for that (additional hardware needed!)  
B: Encode the switch positions you set. Needs a tool, see ![RC_Switch_Code_Converter](https://github.com/ModischFabrications/RC_Switch_Code_Converter)

## Developer hints

Be aware that you are unable to run it on a desktop as it depends on RPI's GPIOs.
YOu will probably need to comment out the import for that and set a breakpoint somewhere.

### Dependencies

paho-mqtt
![rpi-rf](https://github.com/milaq/rpi-rf)

### Test script manually without docker
Get it to your System:
1. `git clone ###`
2. `cd MQTT_Switcher`
4. `git checkout dockerize`
4. `chmod +x build.sh`

Update to newest version
1. `git reset --hard`
3. `git pull [origin dockerize]`
5. `pipenv update`
6. `pipenv shell`

Execute
1. `export PYTHONPATH=.`        -> enables relative imports from /app
2. `python3 app/main.py -f config.yaml`
3. send MQTT messages with the correct topics and watch for your sockets


