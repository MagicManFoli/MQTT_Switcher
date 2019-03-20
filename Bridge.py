import re
import subprocess
from logging import Logger
from typing import Dict, Tuple

import paho.mqtt.client as mqtt

Address_Mapping = Dict[str, Tuple[str, str]]

system_code_pattern = re.compile("[01]{5}")
unit_code_pattern = re.compile("[1-5]")


class Bridge:
    def __init__(self, logger: Logger, topic_to_id: Address_Mapping, root_topic, host="localhost", port=1883):
        self._logger = logger

        self._topic_to_id = topic_to_id
        self._check_validity(topic_to_id)

        self._root_topic = root_topic
        self._port = port
        self._host = host

        self._client = mqtt.Client()
        self._client.on_connect = self._on_con
        self._client.on_message = self._on_msg

    @staticmethod
    def _check_validity(mapping: Address_Mapping):
        """
        Used to prevent dict-key exploits when executing shell command
        """
        for system_code, unit_code in mapping.values():
            if system_code_pattern.match(system_code) is None:
                raise ValueError(f"Invalid systemCode: {system_code}")
            if unit_code_pattern.match(unit_code) is None:
                raise ValueError(f"Invalid unitCode: {unit_code}")

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
        self._exec_send(*self._topic_to_id[subtopic], state)  # * -> unpack

    def _exec_send(self, system_code: str, unit_code: int, state):
        self._logger.info(f"sending: systemCode={system_code}, unitCode={unit_code}, state={state}")

        try:
            # this is unsafe but I see no other "easy" way
            # this should eventually be replaced by "rpi-rf"
            return_value = subprocess.run(["/home/pi/raspberry-remote/send", system_code, unit_code, state],
                                          check=True, capture_output=True, text=True,
                                          timeout=10)
            self._logger.debug("STDOUT:" + return_value.stdout)
            self._logger.debug("STDERR:" + return_value.stderr)

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
