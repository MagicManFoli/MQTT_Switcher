#!/usr/bin/env python3
# author: MF
# listens to MQTT and switches 433MHz radio sockets

import paho.mqtt.client as mqtt
import subprocess

import logging

formatter = "[%(asctime)s][%(levelname)s]: %(message)s"

# DEFINE RADIO SOCKETS HERE
syscode = "01010"
radio_id = {"Lamp": 1}


def on_con(client, userdata, flags, rc):
    logging.info("Connected to MQTT-Broker with Code " + str(rc))

    # subscribe here to renew on connection reset
    client.subscribe("Switches/#", 2)


def on_msg(client, userdata, msg):
    logging.debug("msg received on topic <{}> with payload <{}>".format(msg.topic, msg.payload))
    subtopic = msg.topic.split("/")[1]
    state = msg.payload.decode("utf-8")

    logging.debug("Calling Socket for subtopic '{}' with state '{}'".format(subtopic, state))
    exec_send(radio_id[subtopic], state)


def exec_send(number, state):
    logging.info("sending state {} for device {} in system {} via 433MHz".format(state, number, syscode))

    # SEND
    try:
        bash_command = "/home/pi/raspberry-remote/send {} {} {}".format(syscode, number, state)
        subprocess.check_call(bash_command.split(), timeout=10)
    except subprocess.TimeoutExpired:
        logging.error("sending failed, timeout")
        return
    except subprocess.CalledProcessError:
        logging.error("sending failed, process return not null")
        return

    logging.debug("message was sent")


def main():
    print("---------------------------------------------------------------")
    print("Starting sub_Switch, a tool to transfer MQTT commands to 433MHz")

    logging.basicConfig(filename='/home/pi/MQTT_Switcher/MQTT_Switcher.log', filemode='a', level=logging.DEBUG, format=formatter)
    logging.info("Initialising... ")

    client = mqtt.Client()

    client.on_connect = on_con
    client.on_message = on_msg

    client.connect("192.168.178.101", 1883, 60)

    logging.info("starting server")
    # starting blocking execution
    client.loop_forever()

    print("main is done, this should never happen")

    # never getting here
    return 0


main()
