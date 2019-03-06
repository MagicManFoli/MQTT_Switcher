# variable parts of Switcher
# MODIFY TO ADD ENTRIES!

# used to subscribe to MQTT
root_topic = "Switches/#"

mqtt_host = "192.168.178.100"
# def: 1883
mqtt_port = 1883


# first block is your address space, second your channel (A-E)
# Most remotes only have 4 buttons, which leaves a "secret" channel
topic_to_id = {"living": "01010 1", "office": "01010 2", "printer": "01010 5"}
