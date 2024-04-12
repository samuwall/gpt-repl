import sys
import os
import json
from datetime import datetime
from pathlib import Path
from .render import render, print_rule
# from input import getch

def clear_lines(num_lines: int):
  if num_lines > 0:
    sys.stdout.write(f"\x1b[{num_lines}A")    # move cursor up num_lines
    sys.stdout.write("\r\x1b[0J")             # clear from cursor to end of screen
    sys.stdout.flush()

def mkdir_new_chat(model: str):
   # Create chats directory if it doesn't exist
  chats = Path(__file__).resolve().parent.parent / "chats"
  chats.mkdir(exist_ok=True)
  
  # Create new chat directory with timestamp
  timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
  chat_dir = chats / f"{timestamp}_{model}"
  chat_dir.mkdir()

  # Initialize empty messages.json file
  messages_path = chat_dir / "messages.json"
  with open(messages_path, "w") as f:
    json.dump([], f)

  # Initialize empty chat.md file
  chat_path = chat_dir / "chat.md"
  open(chat_path, "w").close()

  return chat_dir

def save_system_prompt(chat_dir, system_prompt: str):
  # need this for anthropic client, bc sys_prompt cannot be part of conversation json 'messages'
  # so when loading previous claude chat, sys_prompt needs to be loaded from disk instead
  with open(os.path.join(chat_dir, "system.txt"), "w") as f:
    f.write(system_prompt)

def load_system_prompt(chat_dir):
  with open(os.path.join(chat_dir, "system.txt"), "r") as f:
    system_prompt = f.read()
  return system_prompt

def remove_system_message(messages):
  # return sliced copy of messages for use in save_chat()
  if messages and messages[0].get("role") == "system":
    return messages[1:]
  return messages[:]

def save_chat(chat_dir, messages, user_input: str, assistant_response: str):
  
  with open(os.path.join(chat_dir, "messages.json"), "w") as f:
    json.dump(messages, f, indent=2)

  with open(os.path.join(chat_dir, "chat.md"), "a") as f:
    f.write(f": {user_input}\n\n")
    f.write(f"{assistant_response}\n\n")

def list_of_chat_paths():
   # create chats directory if it doesn't exist
  chats = Path(__file__).resolve().parent.parent / "chats"
  chats.mkdir(exist_ok=True)

  chat_paths = sorted(chats.iterdir(), reverse=True)
  return chat_paths

def load_chat(chat_dir):
  with open(os.path.join(chat_dir, "messages.json"), "r") as f:
    messages = json.load(f)
  
  return messages

def print_chat(chat_dir, renderer: str, color: str):
  print(f"\n\x1b[1m{chat_dir.name}:\x1b[0m \x1b[96m'q' to quit '-h' for help\x1b[0m")
  print_rule(color)

  with open(os.path.join(chat_dir, "chat.md"), "r") as f:
    render(f.read().rstrip(), color, renderer) # .rstrip() removes trailing newlines

def sel_chat():
  chat_dirs = list_of_chat_paths()
  page_size = 5
  current_page = 0
  lines = 0
  max_page = (len(chat_dirs) + page_size - 1) // page_size

  while True:
    start = current_page * page_size
    end = start + page_size
    displayed_chats = chat_dirs[start:end]

    clear_lines(lines)

    print(f"\n\rSelect chat: (0-{page_size}, default: 0)")
    print("\n0. New Chat")
    lines = 4

    for i, chat in enumerate(displayed_chats, 1):
      print(f"{i}. {chat.name}")
      lines += 1

    if current_page + 1 < max_page:
      prompt_str = f"(Showing {start + 1}-{start + len(displayed_chats)}, n for next page, p for previous page): "
    else:
      prompt_str = f"(Showing {start + 1}-{start + len(displayed_chats)}, p for previous page): "
    sys.stdout.write(prompt_str)
    sys.stdout.flush()
    lines += 1

    try: 
      choice = input().strip().lower()
    except KeyboardInterrupt: 
      # clear ^C and greyout prompt
      sys.stdout.write("\r\033[K\033[90m" + prompt_str + "\033[0m\n")
      sys.stdout.flush()
      sys.exit()

    if choice == '':
      return None
    if choice == 'n' and current_page + 1 < max_page:
      current_page += 1
    elif choice == 'p' and current_page > 0:
      current_page -= 1
    elif choice.isdigit() and int(choice) > 0 and int(choice) <= len(displayed_chats):
      return chat_dirs[start + int(choice) - 1]
    elif choice == '0':
      return None