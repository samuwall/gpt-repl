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
system-prompt = You are a helpful assistant.

# GPT MODEL:
# uncomment the model you would like to use, or add a new one (chat models only)
#-- openai models ( https://platform.openai.com/docs/models/overview )

# Dec. 2023 (currently points to gpt-4-turbo-2024-04-09
model = gpt-4-turbo

# Sep. 2021 (less expensive, faster)
#model = gpt-3.5-turbo-0125

#model = etc...

#-- anthropic models ( https://docs.anthropic.com/claude/docs/models-overview )

# Feb. 2024
#model = claude-3-opus-20240229

# Feb. 2024
#model = claude-3-sonnet-20240229

# Mar. 2024
#model = claude-3-haiku-20240307


# DEFAULT TEXT RENDERER:
#renderer = rich
renderer = lite
#renderer = raw


# ALWAYS CREATE A NEW CHAT WITHOUT ASKING TO SELECT FROM PREV CHATS?:
# true or false
always_new_chat = false

# ENABLE/DISABLE AI GENERATED SAVED CHAT TITLES:
ai_gen_chat_titles = true


"""