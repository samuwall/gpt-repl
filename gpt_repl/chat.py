#################################################
## file         : chat.py
## description  :
##
#################################################

import sys
import os
import json
from datetime import datetime
from gpt_repl.render import render, print_rule
from gpt_repl.input import getch

def sel_chat():
    chat_dirs = list_of_chat_paths()
    page_size = 5
    current_page = 0
    max_page = (len(chat_dirs) + page_size - 1) // page_size

    # save initial cursor pos
    sys.stdout.write("\x1b[s")
    sys.stdout.flush()

    while 1:
        start = current_page * page_size
        end = start + page_size
        displayed_chats = chat_dirs[start:end]

        # update cursor pos to initial pos, clear to end of screen
        sys.stdout.write("\x1b[u\x1b[J")
        sys.stdout.flush()

        print(f"\nSelect chat: (0-{page_size}, default: 0)")
        print("\n\x1b[96m\x1b[1m0. New Chat\x1b[0m")

        for i, chat in enumerate(displayed_chats, 1):
            title_file = os.path.join(chat, 'title.txt')
            if os.path.exists(title_file):
                with open(title_file, 'r') as file:
                    print(f"{i}. {file.read().strip()}")
            else:
                print(f"{i}. {os.path.basename(chat)}")

        print()
        
        if current_page + 1 < max_page:
            prompt_str = f"(Showing {start + 1}-{start + len(displayed_chats)}: n for next page, p for previous): "
        else:
            prompt_str = f"(Showing {start + 1}-{start + len(displayed_chats)}: p for previous): "
        sys.stdout.write(prompt_str)
        sys.stdout.flush()

        choice = getch().lower()

        if choice == '\n' or choice == '\r':
            sys.stdout.write("\x1b[u\x1b[J")
            sys.stdout.flush()
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
            sys.stdout.write("\x1b[u\x1b[J")
            sys.stdout.flush()
            return chat_dirs[start + int(choice) - 1]
        elif choice == '0':
            sys.stdout.write("\x1b[u\x1b[J")
            sys.stdout.flush()
            return None


def mkdir_new_chat(model: str, title_gen_model: str, user_input: str, assistant_response: str):

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

    if title_gen_model:

        from litellm import completion

        generated_title = ""
        chat_str = f"User: {user_input[:1000]}\nAssistant: {assistant_response[:1000]}"
        task = "Using a maximum of 4 words, generate a title which captures the main subject of the following trimmed conversation between User and Assistant. Return only the title, nothing else."
        prompt = f"{task}\n{chat_str}"

        response = completion(model=title_gen_model, messages=[{"role": "user", "content": prompt}], max_tokens=20)
        generated_title = response.choices[0].message.content

        # sanitize odd responses
        generated_title = generated_title[:30]
        generated_title = generated_title.replace('\t', ' ').replace('\n', ' ')
        chars_to_strip = ' .!?\t\n\'"'
        generated_title = f"{generated_title.strip(chars_to_strip)} [{model_name}]"

        # write title
        with open(os.path.join(chat_dir, "title.txt"), "w") as f:
            f.write(generated_title)

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

