### gpt-repl

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