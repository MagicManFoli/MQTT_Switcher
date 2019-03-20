#!python3
# author: Modisch Fabrications
# listens to MQTT events and switches 433MHz radio sockets

import logging
import re
import sys
import time
from logging.handlers import RotatingFileHandler

import Bridge
import mapping

if sys.version_info[1] < 6:
    raise EnvironmentError("Can't run in pre 3.6 Environments!")

formatter = "[%(asctime)s][%(levelname)s]: %(message)s"
rf_pattern = re.compile("[01]{5} [1-5]")

project_name = "MQTT_Switcher"
revision = 5


def main():
    logger = get_logger(project_name)
    logger.info(f" --- Starting {project_name} [v{revision}], a tool to transfer MQTT commands to 433MHz --- ")

    bridge = Bridge.Bridge(logger, mapping.topic_to_id, mapping.root_topic, mapping.mqtt_host, mapping.mqtt_port)

    # try multiple times, waiting for broker to get online
    for t_retry in mapping.restart_delays:
        try:
            # start blocking
            bridge.run()
            # non-blocking should `break` here
            raise RuntimeError("Reached unreachable code")
        except ConnectionRefusedError:
            logger.warning(f"Connection failed, trying again in {t_retry} seconds")
            # hibernate here until another try is due
            time.sleep(t_retry)
        except Exception as e:
            logger.exception(e)
            raise

    # give up
    raise ConnectionError(f"Unable to connect to service after {mapping.restart_delays} tries")


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
