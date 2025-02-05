#################################################
## file         : code_clipboard.py
## description  :
##
#################################################

import re
import pyperclip

def copy_code_block(markdown_str: str, code_block_index: int):

    code_blocks = re.findall(r'^\s*```.*?\n(.*?)\n\s*```\s*$', markdown_str, re.DOTALL | re.MULTILINE)

    if 1 <= code_block_index <= len(code_blocks):
        code_block = code_blocks[code_block_index - 1]
        try:
            pyperclip.copy(code_block)
            print(f"Code block {code_block_index} copied to clipboard\n")
        except Exception as e:
            print(e)
    else:
        print(f"Invalid code block index. Please enter a number between 1 and {len(code_blocks)}.\n")