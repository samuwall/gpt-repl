#################################################
## file         : chat.py
## description  :
##
#################################################

import sys
import os
import json
from datetime import datetime
from gpt_repl.render import render, print_rule, clear_lines, count_lines 
from gpt_repl.input import getch

def sel_chat():
    chat_dirs = list_of_chat_paths()
    page_size = 5
    current_page = 0
    max_page = (len(chat_dirs) + page_size - 1) // page_size
    num_lines = 0

    while 1:
        start = current_page * page_size
        end = start + page_size
        displayed_chats = chat_dirs[start:end]

        clear_lines(num_lines)
        output_str = f"\nSelect chat: (0-{page_size}, default: 0)\n\n"
        output_str += "\x1b[96m\x1b[1m0. New Chat\x1b[0m\n"

        for i, chat in enumerate(displayed_chats, 1):
            title_file = os.path.join(chat, 'title.txt')
            if os.path.exists(title_file):
                with open(title_file, 'r') as file:
                    chat_title = file.read().strip()
            else:
               chat_title = os.path.basename(chat)

            output_str += f"{i}. {chat_title}\n"

        output_str += "\n"
        
        if current_page == 0:
            prompt_str = f"(Showing {start + 1}-{start + len(displayed_chats)}: n for next page): "
        elif current_page + 1 < max_page:
            prompt_str = f"(Showing {start + 1}-{start + len(displayed_chats)}: n for next page, p for previous): "
        else:
            prompt_str = f"(Showing {start + 1}-{start + len(displayed_chats)}: p for previous): "

        output_str += prompt_str
        num_lines = count_lines(output_str) - 1

        sys.stdout.write(output_str)
        sys.stdout.flush

        choice = getch().lower()

        if choice == '\n' or choice == '\r':
            clear_lines(num_lines)
            return None
        elif choice == 'q' or choice == '\x03': # ctrl-c
            sys.stdout.write("\r\x1b[K")
            sys.stdout.write("\x1b[90m" + prompt_str + "\x1b[0m\n\n")
            sys.stdout.flush()
            sys.exit()
        elif choice == 'n' and current_page + 1 < max_page:
            current_page += 1
        elif choice == 'p' and current_page > 0:
            current_page -= 1
        elif choice.isdigit() and int(choice) > 0 and int(choice) <= len(displayed_chats):
            clear_lines(num_lines)
            return chat_dirs[start + int(choice) - 1]
        elif choice == '0':
            clear_lines(num_lines)
            return None


def mkdir_new_chat(model: str, user_input: str):

    # replace `/` with `_` so model can be used as a dir name
    model_dir = model.replace('/', '_')
    model_name = model.split('/')[1]

    # create chats directory if it doesn't exist
    chats = os.path.join(os.path.expanduser('~'), '.gpt-repl', 'chats')
    if not os.path.exists(chats):
        os.makedirs(chats)

    # create new chat directory with timestamp
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    chat_dir = os.path.join(chats, f"{timestamp}_{model_dir}")
    os.makedirs(chat_dir)

    # initialize empty messages.json file
    with open(os.path.join(chat_dir, 'messages.json'), "w") as f:
        json.dump([],f)

    # initialize empty chat.md file
    open(os.path.join(chat_dir, 'chat.md'), "w").close()

    chat_title = f"{user_input[:25]}.. [{model_name}]"

    # write title
    with open(os.path.join(chat_dir, "title.txt"), "w") as f:
        f.write(chat_title)

    return chat_dir


def save_system_prompt(chat_dir, system_prompt: str):
    # need this for anthropic client, bc sys_prompt cannot be part of conversation json 'messages'
    # so when loading previous claude chat, sys_prompt needs to be loaded from disk instead
    with open(os.path.join(chat_dir, "system.txt"), "w") as f:
        f.write(system_prompt.strip())


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
    chats = os.path.join(os.path.expanduser('~'), '.gpt-repl', 'chats')
    if not os.path.exists(chats):
        os.makedirs(chats)

    chat_paths = sorted([os.path.join(chats, file) for file in os.listdir(chats)], reverse=True)
    return chat_paths


def load_chat(chat_dir):
    with open(os.path.join(chat_dir, "messages.json"), "r") as f:
        messages = json.load(f)

    return messages


def print_chat(chat_dir, renderer: str, color: str):
    print(f"\n\x1b[1m{os.path.basename(chat_dir)}:\x1b[0m \x1b[96m'q' to quit '-h' for help\x1b[0m")
    print_rule(color)

    with open(os.path.join(chat_dir, "chat.md"), "r") as f:
        render(f.read().rstrip(), color, renderer) # .rstrip() removes trailing newlines

