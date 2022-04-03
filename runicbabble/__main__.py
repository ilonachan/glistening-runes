
import logging.config

import yaml

# Read the logger configuration from a config file
with open('logging.yaml', 'r') as lf:
    log_cfg = yaml.safe_load(lf.read())
logging.config.dictConfig(log_cfg)

from runicbabble import discord

discord.start()
