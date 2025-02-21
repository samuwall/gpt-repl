#################################################
## file         : main.py
## description  :
##
#################################################

import sys
import argparse
import threading
import importlib
from prompt_toolkit.key_binding import KeyBindings
from gpt_repl.config import get_config_path, open_conf_file, load_config
from gpt_repl.spinner import Spinner
from gpt_repl.code_clipboard import copy_code_block
from gpt_repl.help import help_runtime
from gpt_repl.render import print_rule, render, color_codes, provider_color_table
from gpt_repl.chat import sel_chat, mkdir_new_chat, load_chat, print_chat, save_chat
from gpt_repl.input import get_input

def main():

    load_thread = threading.Thread(target=importlib.import_module, args=("litellm",), daemon=True)
    load_thread.start()

    messages = []
    response = ""
    prev_input = ""

    ### get args ################################

    parser = argparse.ArgumentParser(description="Terminal-based REPL GPT Chat Bot")
    parser.add_argument("--config", action="store_true", help="open the config file")
    args = parser.parse_args()

    config_path = get_config_path("gpt.conf")
    if args.config:
        open_conf_file(config_path)
        sys.exit()

    ### initialize classes ######################

    spinner = Spinner(message="")
    bindings = KeyBindings()
    @bindings.add("c-n")
    def _(event):
        event.current_buffer.insert_text("\n")
    @bindings.add("c-r")
    def _(event):
        event.current_buffer.text = ""

    ### load configs ############################

    config = load_config(config_path)
    model = config['settings']['model']
    renderer = config['settings']['renderer']
    always_new_chat = config['settings']['always_new_chat']

    ### assign color ############################

    provider = model.split('/')[0]
    if provider not in provider_color_table:
        color = "green"
    else:
        color = provider_color_table[provider]

    ### select chat #############################

    is_new_chat = False

    if always_new_chat.lower() == 'true':
        selected_chat = None
    else:
        selected_chat = sel_chat()

    if selected_chat:
        messages = load_chat(selected_chat)
        print_chat(selected_chat, renderer, color)
    else:
        is_new_chat = True
        print(f"\n\x1b[1m{color_codes[color]}{model}:\x1b[0m How can I help you today? \x1b[96m'q' to quit '-h' for help\x1b[0m")
        print_rule(color)

    ### MAIN REPL LOOP ##########################

    while 1:

        ### get user prompt/command #############

        try:
            action, data = get_input(prev_input, bindings)
        except KeyboardInterrupt:
            break

        if action == 'quit':
            break
        elif action == 'help':
            help_runtime()
            continue
        elif action == 'copy_code':
            copy_code_block(response, data)
            continue
        elif action == 'render':
            render(response, color, data)
            continue
        elif action == 'invalid_command':
            print("invalid command\n")
            continue
        elif action == 'input':
            user_input = data
            prev_input = ""
        elif action == 'cancel':
            prev_input = data
            continue
        else:
            continue

        ### send prompt to API ##################

        spinner.start()
        load_thread.join()
        from litellm import completion

        messages.append({"role": "user", "content": user_input})
        response_obj = completion(model=model, messages=messages)
        response = response_obj.choices[0].message.content
        messages.append({"role": "assistant", "content": response})

        if is_new_chat:
            selected_chat = mkdir_new_chat(model, user_input)
            is_new_chat = False

        response = f"\x1b[1m{color_codes[color]}{model}:\x1b[0m {response}"
        save_chat(selected_chat, messages, user_input, response)

        spinner.stop()
        render(response, color, renderer)


if __name__ == "__main__":
    main()
