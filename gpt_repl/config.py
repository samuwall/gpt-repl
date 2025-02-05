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

  # if gpt.conf not already there, write default config to it
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
#   always_new_chat
#   ai_gen_chat_titles

# INITIAL SYSTEM PROMPT (only applies to new chats):
#system-prompt = You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture. Image input capabilities: Disabled. Tools: None.
system-prompt = You are a helpful assistant.
#system-prompt = You are Lebron James. You will respond only in the style of a Lebron James Instagram caption, complete with catchphrases and an overuse of emojis.

# GPT MODEL:
# uncomment the model you would like to use, or add a new one (chat models only)
# model = <provider_name>/<model_name>

model = openai/gpt-4o-mini
#model = openai/o1-mini
#model = anthropic/claude-3-5-haiku-latest

# DEFAULT TEXT RENDERER:
#renderer = rich
renderer = lite
#renderer = raw

# ALWAYS CREATE A NEW CHAT WITHOUT ASKING TO SELECT FROM PREV CHATS?:
# true or false
always_new_chat = false

# ENABLE/DISABLE AI GENERATED SAVED CHAT TITLES:
ai_gen_chat_titles = true

# AI CHAT TITLE GENERATION MODEL:
# select a cheap and fast model
#chat_title_gen_model = openai/gpt4o



"""