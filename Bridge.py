import subprocess
from logging import Logger
from typing import Dict

import paho.mqtt.client as mqtt

from MQTT_Switcher import rf_pattern


class Bridge:
    def __init__(self, logger: Logger, mapping: Dict[str, str], root_topic, host="localhost", port=1883):
        self._logger = logger

        self._mappings = mapping
        self._check_validity(mapping)

        self._root_topic = root_topic
        self._port = port
        self._host = host

        self._client = mqtt.Client()
        self._client.on_connect = self._on_con
        self._client.on_message = self._on_msg

    @staticmethod
    def _check_validity(mapping: Dict[str, str]):
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

        # subscribe here instead of run to renew on connection reset
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
            # this should eventually be replaced by "rpi-rf"
            return_value = subprocess.run(["/home/pi/raspberry-remote/send", rf_id, state],
                                          check=True, capture_output=True,
                                          timeout=10)
            self._logger.debug("\t" + return_value.stdout)

        except subprocess.TimeoutExpired:
            self._logger.error("remote failed, timeout")
            return

        self._logger.debug("message was sent")

    def run(self):
        """
        start message bridge, blocking execution forever
        """
        self._client.connect(self._host, self._port)

        self._logger.info("Starting bridge [blocking]")
        # starting blocking execution
        self._client.loop_forever()

    # TODO: run async
