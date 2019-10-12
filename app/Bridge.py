import time
from logging import Logger
from typing import Dict, Tuple, Iterable

import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from rpi_rf import RFDevice

Address_Mapping = Dict[str, Tuple[int, int]]


class Bridge:
    # pass whole Dict (with useful subsection of attributes) to allow parts
    # per module without dependencies between them or for a central importer
    def __init__(self, logger: Logger, config: Dict):
        self._logger = logger

        self._topic_to_id: Address_Mapping = config["topic_to_rf_code"]

        self._root_topic = config["mqtt_root_topic"]
        self._host = config["mqtt_address"]["host"]
        self._port = config["mqtt_address"]["port"]

        self._repetitions_number = config["repetitions"]["number"]
        self._repetitions_sleep__ms = config["repetitions"]["sleep__s"]

        # init MQTT
        self._client = mqtt.Client()
        self._client.on_connect = self._on_con
        self._client.on_message = self._on_msg

        # init 433MHz
        self._rfdevice = RFDevice(config["rf_gpio"])
        self._rfdevice.enable_tx()

    def _on_con(self, client, userdata, flags, rc):
        self._logger.debug(f"Connected to MQTT-Broker with Code {rc}")

        # subscribe here instead of run to renew on connection reset
        client.subscribe(self._root_topic, 2)

    def _on_msg(self, client, userdata, msg):
        self._logger.debug(f"msg received on topic <{msg.topic}> with payload <{msg.payload}>")
        subtopic = msg.topic.split("/")[1]
        state = msg.payload.decode("utf-8")  # 0 or "0" or 1 or "1", the protocol is not that precise

        self._logger.debug(f"Subtopic '{subtopic}', state '{state}'")
        # # first code of tuple is off, second on (implicit mapping from position to state)
        self._exec_send(self._topic_to_id[subtopic][int(state)])

    def _exec_send(self, code: int):
        self._logger.info(f"sending Code={code}")

        for _ in range(self._repetitions_number):
            t_pre_send = time.perf_counter()
            success = self._rfdevice.tx_code(code)
            # sleep only the time left, sending could take a few milliseconds due to the timings used
            t_passed = time.perf_counter() - t_pre_send
            time.sleep(self._repetitions_sleep__ms - t_passed)

        self._logger.debug("code was sent successfully")

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

    # TODO: def run_async
    def cleanup(self):
        self._client.disconnect()

        # prevent "RuntimeWarning: This channel is already in use, continuing anyway.
        #  Use GPIO.setwarnings(False) to disable warnings."
        GPIO.cleanup()
