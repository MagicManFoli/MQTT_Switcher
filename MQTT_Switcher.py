#!python3
# author: Modisch Fabrications
# listens to MQTT events and switches 433MHz radio sockets

import subprocess
import re
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from typing import Dict
import sys

import paho.mqtt.client as mqtt

import mapping

if sys.version_info[1] < 6:
    raise EnvironmentError("Can't run in pre 3.6 Environments!")

formatter = "[%(asctime)s][%(levelname)s]: %(message)s"
rf_pattern = re.compile("[01]{5} [1-5]")

project_name = "MQTT_Switcher"
revision = 4


class Bridge:

    def __init__(self, logger: Logger, mapping: Dict[str, str], root_topic, host="localhost", port=1883):
        self._logger = logger

        self._mappings = mapping
        self.check_validity(mapping)

        self._root_topic = root_topic
        self._port = port
        self._host = host

        self._client = mqtt.Client()
        self._client.on_connect = self._on_con
        self._client.on_message = self._on_msg

    @staticmethod
    def check_validity(mapping: Dict[str, str]):
        """
        Used to prevent dict-key exploits when executing shell command
        """
        for value in mapping.values():
            if rf_pattern.match(value) is None:
                raise ValueError(value)

        # could be shorter but less comprehensible:
        # any(rf_pattern.match(v) is None for v in mappings.TtoID.values())

    def _on_con(self, client, userdata, flags, rc):
        self._logger.debug(f"Connected to MQTT-Broker with Code {rc}")

        # subscribe here to renew on connection reset
        client.subscribe(self._root_topic, 2)

    def _on_msg(self, client, userdata, msg):
        self._logger.debug(f"msg received on topic <{msg.topic}> with payload <{msg.payload}>")
        subtopic = msg.topic.split("/")[1]
        state = msg.payload.decode("utf-8")

        self._logger.debug(f"Subtopic '{subtopic}', state '{state}'")
        self._exec_send(self._mappings[subtopic], state)

    def _exec_send(self, rf_id, state):
        self._logger.info(f"sending state {state} for 433 MHz ID {rf_id}")

        try:
            # this is unsafe but I see no other "easy" way
            bash_command = f"/home/pi/raspberry-remote/send {rf_id} {state}"
            subprocess.check_call(bash_command.split(), timeout=10)
        except subprocess.TimeoutExpired:
            self._logger.error("sending failed, timeout")
            return
        except subprocess.CalledProcessError as e:
            self._logger.error(f"sending failed, process returned {e}")
            return

        self._logger.debug("message was sent")

    def start(self):
        self._client.connect(self._host, self._port, 60)

        self._logger.info("Starting bridge [blocking]")
        # starting blocking execution
        self._client.loop_forever()


def main():
    logger = get_logger(project_name)
    logger.info(f" --- Starting {project_name} [v{revision}], a tool to transfer MQTT commands to 433MHz --- ")

    bridge = Bridge(logger, mapping.topic_to_id, mapping.root_topic, mapping.mqtt_host, mapping.mqtt_port)
    # start [blocking]
    bridge.start()

    # never getting here
    raise RuntimeError("Unexpected termination")


def get_logger(name: str):
    """
    prepare logging to file & stream. Can be called multiple times .
    :return: logger object
    """

    # singleton, value only present if previously executed
    if "logger" in get_logger.__dict__:
        get_logger.logger.warning("Prevented double initialisation of logger")
        return get_logger.logger

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # minimum level

    # complete log in file
    fh = logging.handlers.RotatingFileHandler(f"{name}.log", maxBytes=1 * 1024 * 1024, backupCount=4)  # 1MB
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)

    # logging >=info to stdout
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

    get_logger.logger = logger

    return logger


if __name__ == '__main__':
    main()
