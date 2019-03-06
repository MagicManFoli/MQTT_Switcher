# MQTT_Switcher
This short script is used to trigger 433MHz radio sockets from MQTT messages.
Customize this to your likings by modifying `mapping.py`
It would be nice to port this into a docker container but interfacing with GPIOs via raspberry-remote is easier when native.

# Installation
It might be necessary to configure your Pi to wait for network connections before starting this service:  
1. `sudo raspi-config` -> Boot -> Wait for Network at Boot  
1. `sudo reboot now`

Make sure to have `raspberry-remote` installed in your home directory.


Start this with your system by using a few of these commands:
1. Stop running service: `sudo systemctl stop MQTT_Switcher`
1. Change permissions: `sudo chmod ug+x ~/MQTT_Switcher/MQTT_Switcher.py`
1. Copy service to systemd: `sudo cp ~/MQTT_Switcher/MQTT_Switcher.service /etc/systemd/system`
1. Start Service: `sudo systemctl start MQTT_Switcher`
1. Start Service: `sudo systemctl enable MQTT_Switcher`
1. Check Status: `systemctl status MQTT_Switcher.service`



