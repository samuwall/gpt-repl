#################################################
## file         : config.py
## description  :
##
#################################################

import os
import sys
import subprocess
from configparser import ConfigParser

def get_config_path(filename: str):

    config_dir = os.path.join(os.path.expanduser('~'), '.gpt-repl')

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    config_path = os.path.join(config_dir, filename)

    # if gpt.conf doesnt exist, write default config to it
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            f.write(conf_str)

    return config_path


def load_config(path: str):

    if not os.path.exists(path):
        print("config file not found")
        sys.exit(1)

    config = ConfigParser()
    config.read(path)
    return config

def open_conf_file(path: str):

    editor = os.environ.get("EDITOR", "nano")
    try:
        subprocess.run([editor, path])
    except subprocess.CalledProcessError as err:
        print(f"Failed to open the configuration file: {err}")


conf_str = """
[settings]

# settings:
#   system-prompt
#   model
#   renderer
#   stream
#   always_new_chat

# INITIAL SYSTEM PROMPT (only applies to new chats):
system-prompt = You are a helpful assistant.
#system-prompt = You are Lebron James. You will respond only in the style of a Lebron James Instagram caption, complete with catchphrases and an overuse of emojis.

# GPT MODEL (https://docs.litellm.ai/docs/providers):
#model = openai/gpt-4o-mini
model = openai/o1-mini
#model = anthropic/claude-3-5-haiku-latest

# DEFAULT TEXT RENDERER:
#renderer = raw
renderer = lite
#renderer = rich

# STREAM MODEL RESPONSE? (true/false)
stream = false

# ALWAYS CREATE A NEW CHAT WITHOUT ASKING TO SELECT FROM PREV CHATS? (true/false):
always_new_chat = false

"""
