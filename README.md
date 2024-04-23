> i mostly made this so that i can save battery (terminal vs. browser)
and use gpt-4-turbo and claude-3-opus in a chat-bot setting with saved chats and without expensive subscriptions
>> limited error handling, just for fun and for learning python

### gpt-repl

This Python script provides a terminal-based REPL (Read-Eval-Print Loop) interface for interacting with GPT chat models, such as OpenAI's GPT models (e.g., gpt-4-turbo) and Anthropic's Claude models.

Features:
- Load settings from a configuration file (gpt.conf)
- Chat with both OpenAI and Anthropic models
- Create new chats or load previous chats
- Multi-line inputs
- Render assistant responses using different rendering options (raw, lite, rich)
- Custom markdown renderer (lite)
- Copy code blocks to your clipboard
- Provide runtime help and commands for interacting with the chat
- Automatically save chat history and system prompts for future reference

To run the script, execute it from the command line. Use the '--config' flag to open the configuration file for editing. Press 'q' or 'quit' to exit the chat, and use '-h' or '--help' to display runtime help.

Note: Requires valid API keys for OpenAI and Anthropic to be set as environment variables.

Setup:
- `git clone`
- `cd path/to/gpt-repl`
- `pipx install .`
- `gpt --help`

Now you can enter the `gpt` command in any terminal and use gpt-repl. 
