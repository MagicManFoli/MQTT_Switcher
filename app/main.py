#!python3
# author: Modisch Fabrications
# listens to MQTT events and switches 433MHz radio sockets
import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict

from ruamel.yaml import YAML

from app import Bridge

# pyYAML is dead! https://stackoverflow.com/questions/20805418/pyyaml-dump-format

if sys.version_info[1] < 6:
    raise EnvironmentError("Can't run in pre 3.6 environments!")

formatter = "[%(asctime)s][%(levelname)s]: %(message)s"

project_name = "MQTT_Switcher"
# SemVer, increment major on API changes
revision = 0.6


def main():
    logger = get_logger(f"../{project_name}.log")
    logger.info(f" --- Starting {project_name} [v{revision}], a tool to transfer MQTT commands to 433MHz --- ")

    config = get_args()
    logger.info(f"Config parameters: {config}")

    bridge = Bridge.Bridge(logger, config)
    try:
        # start blocking
        bridge.run(config["timeout_restart_delays__s"])
    except KeyboardInterrupt:
        logger.warning(f"Killed by CTRL+C, cleaning up")

    bridge.cleanup()

    logger.info(f"Everything done and cleaned up, Goodbye!")


def get_args() -> Dict:
    parser = argparse.ArgumentParser(project_name)
    parser.add_argument("-f", "--config_file",
                        type=Path, default=Path("./config.yml"),
                        help="Configuration file with mappings to local addresses",
                        required=True, dest="config_file")

    # will get shell args automatically
    args = parser.parse_args()

    config_file: Path = args.config_file
    if not config_file.is_file():
        raise FileNotFoundError(f"No config file found in {config_file.resolve()}!")

    # prevent weird expansion bombs and stuff without needing many restrictions
    yaml = YAML(typ='safe')
    data = yaml.load(config_file)
    return data


def get_logger(file_name: str) -> logging.Logger:
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
    fh = logging.handlers.RotatingFileHandler(file_name, maxBytes=1 * 1024 * 1024, backupCount=4)  # 1MB
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
