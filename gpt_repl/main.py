import sys
import re
import argparse
from litellm import completion
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from gpt_repl.config import get_config_path, open_conf_file, load_config
from gpt_repl.spinner import Spinner
from gpt_repl.code_clipboard import CodeBlockManager
from gpt_repl.help import help_runtime
from gpt_repl.render import print_rule, render, color_codes
from gpt_repl.chat import sel_chat, mkdir_new_chat, load_chat, print_chat, save_chat
from gpt_repl.input import getch

def main():

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
    code_block_manager = CodeBlockManager()

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
    ai_gen_chat_titles = config['settings']['ai_gen_chat_titles']

    ### assign color ############################

    color = "white"

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
        
        ### get prompt/command ##################

        try:
            
            # save cursor position (for rewriting input)
            sys.stdout.write("\x1b[s")
            sys.stdout.flush()

            # get user input
            user_input = prompt(": ", key_bindings=bindings, default=prev_input)

            # check if input is a command
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
                render(response, color, "raw")
                continue
            elif re.match(r"^--?p\s+lite$", normalized_input):
                render(response, color, "lite")
                continue
            elif re.match(r"^--?p\s+rich$", normalized_input):
                render(response, color, "rich")
                continue
            elif re.match(r"^--?[a-z]$", normalized_input) or re.match(r"^--?.\s", normalized_input):
                print(f"invalid command\n") # likely command attempt
                continue

            # valid prompt, confirm submission
            print("\rAre you sure you want to submit? \x1b[96m[y/n]\x1b[0m", end='')
            confirm = getch().lower()

            if confirm == 'y':
                sys.stdout.write("\r\x1b[K")  # clear confirmation msg
                sys.stdout.flush()
                prev_input=""

            else:
                sys.stdout.write("\x1b[u")  # update cursor back to pos before any user inputs
                sys.stdout.flush()
                prev_input=user_input       # save this input for further modification
                continue
            
        # ctrl-c
        except KeyboardInterrupt:
            break


        ### send prompt to API ##################

        spinner.start()

        messages.append({"role": "user", "content": user_input})
        response = completion(model=model, messages=messages)
        response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": response})

        if is_new_chat:
            selected_chat = mkdir_new_chat(model, ai_gen_chat_titles, user_input, response)
            is_new_chat = False

        code_block_manager.parse(response)
        response = f"\x1b[1m{color_codes[color]}{model}:\x1b[0m {response}"
        save_chat(selected_chat, messages, user_input, response)
        spinner.stop()

        render(response, color, renderer)


if __name__ == "__main__":
    main()

