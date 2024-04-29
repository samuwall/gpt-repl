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
import re
import argparse
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings

from gpt_repl.config import get_config_path, open_conf_file, load_config
from gpt_repl.spinner import Spinner
from gpt_repl.code_clipboard import CodeBlockManager
from gpt_repl.help import help_runtime
from gpt_repl.render import print_rule, render, color_codes
from gpt_repl.chat import sel_chat, mkdir_new_chat, load_chat, print_chat, save_chat, save_system_prompt, load_system_prompt, remove_system_message
from gpt_repl.input import getch

# from rich.traceback import install
# install()


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
  ai_gen_chat_titles = config['settings']['ai_gen_chat_titles']


  vendor = ""
  if model.startswith("gpt"):
    from openai import OpenAI
    openai_client = OpenAI()
    vendor = "openai"
    color = "magenta" if re.match(r"^....4", model) else "green"
  elif model.startswith("claude"):
    from anthropic import Anthropic
    anthropic_client = Anthropic()
    vendor = "anthropic"
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

  if not selected_chat: # new chat
    is_new_chat = True
    print(f"\n\x1b[1m{color_codes[color]}{model}:\x1b[0m How can I help you today? \x1b[96m'q' to quit '-h' for help\x1b[0m")
    print_rule(color)

  else: # previous chat
    messages = load_chat(selected_chat)
    system_prompt = load_system_prompt(selected_chat)
    if vendor == "openai":
      # insert the system prompt into beginning of messages
      messages.insert(0, {"role": "system", "content": system_prompt})

    print_chat(selected_chat, renderer, color)

  assistant_response = ""
  prev_input = ""

  while 1:
    
    try:
      # save cursor position (for rewriting input)
      sys.stdout.write("\x1b[s")
      sys.stdout.flush()

      #-- get user input
      user_input = prompt(": ", key_bindings=bindings, default=prev_input)


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
        sys.stdout.write("\r\x1b[K")  # carriage return, clear confirmation line
        sys.stdout.flush()
        prev_input=""

      else:
        sys.stdout.write("\x1b[u")    # update current cursor position back to saved pos at beginning of prompt()
        sys.stdout.flush()            # text gets overwritten by prev_input prompt and allows user to edit input before submitting
        prev_input=user_input
        continue
    
    #-- ctrl-c, quit program
    except KeyboardInterrupt:
      break

    # user input is not a command and is not an accident
    #-- send to gpt API
    spinner.start()

    if is_new_chat:

      if vendor == "openai":

        messages = [{"role": "system", "content": system_prompt}]
        messages.append({"role": "user", "content": user_input})

        completion = openai_client.chat.completions.create(
          model=model,
          messages=messages
        )

        assistant_response = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_response})

        selected_chat = mkdir_new_chat(model, ai_gen_chat_titles, user_input, assistant_response, "openai", openai_client)

      elif vendor == "anthropic":

        messages = []
        messages.append({"role": "user", "content": user_input})

        completion = anthropic_client.messages.create(
          model=model,
          max_tokens=4096,
          system=system_prompt,
          messages=messages
        )

        assistant_response = completion.content[0].text
        messages.append({"role": "assistant", "content": assistant_response})

        selected_chat = mkdir_new_chat(model, ai_gen_chat_titles, user_input, assistant_response, "anthropic", anthropic_client)

      save_system_prompt(selected_chat, system_prompt)
      is_new_chat = False
      

    else:
      
      if vendor == "openai":
        messages.append({"role": "user", "content": user_input})

        completion = openai_client.chat.completions.create(
          model=model,
          messages=messages
        )
        assistant_response = completion.choices[0].message.content

        messages.append({"role": "assistant", "content": assistant_response})

      elif vendor == "anthropic":
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
  
