
runtime_help_str = """
  Welcome to gpt-repl, a terminal-based gpt chat-bot!

### Available Runtime Commands

- `q` or `quit`: Exit the program.
- `-h` or `--help`: Display this help message.
- `-c <code_block_index>`: Copy a code block (1-N from top to bottom) to your clipboard. Only applies to most recent API response.
- `-p <renderer>`: Re-print the current API response with a different text renderer ('raw', 'lite', or 'rich')

### How to Use

1. Start the program. You'll be greeted with a prompt indicating the model's readiness to assist.
2. Type your question or command at the prompt and press Enter.
3. Use the available runtime commands as needed.

### Helpful Shortcuts for Writing Inputs

- Newline / line break: ctrl-n
- Clear current input buffer: ctrl-r
- Paste: ctrl-shift-v, shift-ins, right-click->paste (terminal emulators)
- Delete word: ctrl-w, ctrl-backspace
- Delete line: ctrl-u, ctrl-k
- Mover cursor one word: ctrl-leftarrow/rightarrow
- Move cursor to beginning of line: ctrl-a
- Move cursor to end of line: ctrl-e


  For command line arguments such as configuring the gpt model or system prompt, see `gpt-repl -h`

  """

def help_runtime():
  # print(md2ansi(runtime_help_str))
  print(runtime_help_str)