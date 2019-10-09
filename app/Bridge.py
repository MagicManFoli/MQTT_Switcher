import re
import subprocess
import time
from logging import Logger
from typing import Dict, Tuple, Iterable

import paho.mqtt.client as mqtt

Address_Mapping = Dict[str, Tuple[str, str]]

system_code_pattern = re.compile("[01]{5}")
unit_code_pattern = re.compile("[1-5]")


class Bridge:
    # pass whole Dict (with useful subsection of attributes) to allow parts
    # per module without dependencies between them or for a central importer
    def __init__(self, logger: Logger, config: Dict):
        self._logger = logger

        self._topic_to_id: Address_Mapping = config["topic_to_id"]
        self._check_validity(self._topic_to_id)

        self._root_topic = config["mqtt_root_topic"]
        self._host = config["mqtt_address"]["host"]
        self._port = config["mqtt_address"]["port"]

        self._repetitions_number = config["repetitions"]["number"]
        self._repetitions_sleep__ms = config["repetitions"]["sleep__s"]

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
            for _ in range(self._repetitions_number):
                t_pre_send = time.perf_counter()
                return_value = subprocess.run(["/home/pi/raspberry-remote/send", system_code, unit_code, state],
                                              check=True, capture_output=True, text=True,
                                              timeout=10)
                self._logger.debug(subprocess.CompletedProcess)
                # sleep only the time left, sending could take a few milliseconds due to the timings used
                t_passed = time.perf_counter() - t_pre_send
                time.sleep(self._repetitions_sleep__ms - t_passed)

        except subprocess.TimeoutExpired:
            # don't want to throw exceptions in receiver thread
            self._logger.error("remote failed, timeout")
            return

        self._logger.debug("message was sent")

    def run(self, timeout_restart_delays: Iterable):
        """
        start message bridge, blocking execution forever
        :raises ConnectionError when no connection could be established
        """
        self._client.connect(self._host, self._port)

        self._logger.info("Starting bridge [blocking]")

        # try multiple times, waiting for broker to get online
        for t_retry in timeout_restart_delays:
            try:
                # start potentially blocking execution
                self._client.loop_forever()
                # non-blocking should `break` here
                raise RuntimeError("Reached unreachable code")
            except ConnectionRefusedError:
                self._logger.warning(f"Connection failed, trying again in {t_retry} seconds")
                # hibernate here until another try is due
                time.sleep(t_retry)
            except Exception as e:
                self._logger.exception(e)
                raise

        # okay fine, give up
        raise ConnectionError(f"Unable to connect to service after {timeout_restart_delays} tries")

    # TODO: run async
