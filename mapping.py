# variable parts of Switcher
# MODIFY TO ADD ENTRIES!

# used to subscribe to MQTT
root_topic = "Switches/#"

mqtt_host = "192.168.178.100"
# def: 1883
mqtt_port = 1883

restart_delays = (1, 60, 60 * 60)  # in seconds

# first block is your system-code (network-id), second your unit-code (device-id)
# Most remotes only have 4 buttons, which leaves a "secret" channel 5
topic_to_id = {"living": ["01010", 1], "office": ["01010", 2], "printer": ["01010", 5]}
