# MQTT_Switcher
This short script is used to trigger 433MHz radio sockets from MQTT messages.

Stop running service:
"sudo systemctl stop MQTT_Switcher"

Change permissions:
sudo chmod ug+x ~/MQTT_Switcher/MQTT_Switcher.py

Copy service to systemd:
"sudo cp ~/MQTT_Switcher/MQTT_Switcher.service /etc/systemd/system"

Start Service:
"sudo systemctl start MQTT_Switcher"

Start Service:
"sudo systemctl enable MQTT_Switcher"

Check Status:
systemctl status MQTT_Switcher.service


