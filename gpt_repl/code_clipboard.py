#################################################
## file         : code_clipboard.py
## description  : 
##
#################################################

import re
import pyperclip

class CodeBlockManager:
  def __init__(self):
    self.code_blocks = []

  def parse(self, markdown_str: str):
    self.code_blocks.clear()  # Clear the previous code block list
    self.code_blocks = re.findall(r'^\s*```.*?\n(.*?)\n\s*```\s*$', markdown_str, re.DOTALL | re.MULTILINE)

  def copy_code_block(self, code_block_index: int):
    if 1 <= code_block_index <= len(self.code_blocks):
      code_block = self.code_blocks[code_block_index - 1]
      try:
        pyperclip.copy(code_block)
        print(f"Code block {code_block_index} copied to clipboard")
      except Exception as e:
        print(e)
    else:
      print(f"Invalid code block index. Please enter a number between 1 and {len(self.code_blocks)}.")