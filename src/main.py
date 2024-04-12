"""
gpt-repl

This Python script provides a terminal-based REPL (Read-Eval-Print Loop) interface for interacting with GPT chat models, such as OpenAI's GPT models (e.g., gpt-3.5-turbo, gpt-4) and Anthropic's Claude models. It allows users to engage in conversational exchanges with the selected model through a command-line interface.

Features:
- Load settings from a configuration file (gpt.conf)
- Chat with both OpenAI and Anthropic models
- Create new chats or load previous chats
- Render assistant responses using different rendering options (raw, lite, rich)
- Copy code blocks to your clipboard
- Provide runtime help and commands for interacting with the chat
- Automatically save chat history and system prompts for future reference

To run the script, execute it from the command line. Use the '--config' flag to open the configuration file for editing. Press 'q' or 'quit' to exit the chat, and use '-h' or '--help' to display runtime help.

Note: Requires valid API keys for OpenAI and Anthropic to be set as environment variables.
"""

import sys
import os
import subprocess
import re
import argparse
from pathlib import Path
from configparser import ConfigParser
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings

from .spinner import Spinner
from .code_clipboard import CodeBlockManager
from .help import help_runtime
from .render import print_rule, render, color_codes
from .chat import sel_chat, mkdir_new_chat, load_chat, print_chat, save_chat, save_system_prompt, load_system_prompt, remove_system_message
from .input import getch

# from rich.traceback import install
# install()


def get_config_path(filename: str):
  return str(Path(__file__).resolve().parent.parent / filename)

# load .conf file settings using ConfigParser object
## return reference to populated ConfigParser object
def load_config(path: str):
  config = ConfigParser()
  config.read(path)
  return config

def open_conf_file(path: str):
  editor = os.environ.get("EDITOR", "nano")
  try:
    subprocess.run([editor, path])
  except subprocess.CalledProcessError as err:
    print(f"Failed to open the configuration file: {err}")


def main():

  config_path = get_config_path("gpt.conf")

  #-- arg handling
  parser = argparse.ArgumentParser(description="Terminal-based REPL GPT Chat Bot")
  parser.add_argument("--config", action="store_true", help="open the config file")
  args = parser.parse_args()

  if args.config:
    open_conf_file(config_path)
    sys.exit()
  #----

  #-- initialize / load settings
  spinner = Spinner(message="")
  code_block_manager = CodeBlockManager()

  bindings = KeyBindings()
  @bindings.add("c-n")
  def _(event):
    event.current_buffer.insert_text("\n")
  @bindings.add("c-r")
  def _(event):
    event.current_buffer.text = ""

  config = load_config(config_path)
  system_prompt = config['settings']['system-prompt']
  model = config['settings']['model']
  renderer = config['settings']['renderer']
  always_new_chat = config['settings']['always_new_chat']

  is_openai = False
  is_anthropic = False
  if model.startswith("gpt"):
    from openai import OpenAI
    openai_client = OpenAI()
    is_openai = True
    color = "magenta" if re.match(r"^....4", model) else "green"
  elif model.startswith("claude"):
    from anthropic import Anthropic
    anthropic_client = Anthropic()
    is_anthropic = True
    color = "orange3"
  else:
    print("invalid model")
    sys.exit()
  #----


  is_new_chat = False

  if always_new_chat.lower() == 'true':
    selected_chat = None
  else: 
    selected_chat = sel_chat()

  if not selected_chat:
    is_new_chat = True
    if is_openai: 
      messages = [{"role": "system", "content": system_prompt}]
    if is_anthropic: 
      messages = []
    selected_chat = mkdir_new_chat(model)
    save_system_prompt(selected_chat, system_prompt)
    print(f"\n\x1b[1m{color_codes[color]}{model}:\x1b[0m How can I help you today? \x1b[96m'q' to quit '-h' for help\x1b[0m")
    print_rule(color)

  else: # previous chat
    messages = load_chat(selected_chat)
    system_prompt = load_system_prompt(selected_chat)
    if is_openai:
      # insert the system prompt into beginning of messages
      messages.insert(0, {"role": "system", "content": system_prompt})

    print_chat(selected_chat, renderer, color)


  prev_input = ""

  while 1:
    
    try:
      #-- get user input
      user_input = prompt(": ", key_bindings=bindings, default=prev_input)
      num_lines = user_input.count('\n') + 1

      #-- check if input is a command
      normalized_input = user_input.strip().lower()
      if normalized_input in ["q", "quit"]:
        break
      elif normalized_input in ["-h", "--h", "--help"]:
        help_runtime()
        continue
      elif re.match(r"^--?c \d+$", normalized_input):
        id = int(normalized_input.split()[1])
        code_block_manager.copy_code_block(id) # e.g., -c 2 or --c 2
        print()
        continue
      elif re.match(r"^--?p\s+raw$", normalized_input): 
        render(assistant_response, color, "raw")
        continue
      elif re.match(r"^--?p\s+lite$", normalized_input):
        render(assistant_response, color, "lite")
        continue
      elif re.match(r"^--?p\s+rich$", normalized_input):
        render(assistant_response, color, "rich")
        continue
      elif re.match(r"^--?[a-z]$", normalized_input) or re.match(r"^--?.\s", normalized_input):
        print(f"invalid command\n") # likely command attempt
        continue

      #-- not a command, confirm submission
      print("\rAre you sure you want to submit? \x1b[96m[y/n]\x1b[0m", end='') # for some reason, doesn't show up without carriage return, shud investigate (or not?)
      confirm = getch().lower()

      if confirm == 'y':
        sys.stdout.write("\r\x1b[K") # carriage return, clear line
        sys.stdout.flush()
        prev_input=""

      else:
        # clear_lines(num_lines)                  # actually clearing the lines creates a flashing effect

        sys.stdout.write(f"\r\x1b[{num_lines}A")  # just move up num_lines and let prev_input overwrite lines
        sys.stdout.flush()                        # need \r so that input gets overwritten from the start
        prev_input = user_input                   # they are the same size so nothing is left over
        continue                                  # note: this depends on prompt() clearing the confirmation line
    
    #-- ctrl-c, quit program
    except KeyboardInterrupt:
      break

    # user input is not a command and is not an accident
    #-- send to gpt API
    spinner.start()

    if is_new_chat:

      if is_openai:
        
        messages.append({"role": "user", "content": user_input})

        completion = openai_client.chat.completions.create(
          model=model,
          messages=messages
        )

        assistant_response = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_response})

      elif is_anthropic:
        messages.append({"role": "user", "content": user_input})

        completion = anthropic_client.messages.create(
          model=model,
          max_tokens=4096,
          system=system_prompt,
          messages=messages
        )

        assistant_response = completion.content[0].text
        messages.append({"role": "assistant", "content": assistant_response})

    else:
      
      if is_openai:
        messages.append({"role": "user", "content": user_input})

        completion = openai_client.chat.completions.create(
          model=model,
          messages=messages
        )
        assistant_response = completion.choices[0].message.content

        messages.append({"role": "assistant", "content": assistant_response})

      elif is_anthropic:
        messages.append({"role": "user", "content": user_input})

        completion = anthropic_client.messages.create(
          model=model,
          max_tokens=4096,
          system=system_prompt,
          messages=messages
        )

        assistant_response = completion.content[0].text
        messages.append({"role": "assistant", "content": assistant_response})


    code_block_manager.parse(assistant_response)

    assistant_response = f"\x1b[1m{color_codes[color]}{model}:\x1b[0m {assistant_response}"

    save_chat(selected_chat, remove_system_message(messages), user_input, assistant_response)

    spinner.stop()

    render(assistant_response, color, renderer)

    

if __name__ == "__main__":
  main()
  
