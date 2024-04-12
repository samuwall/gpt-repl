import re
import pyperclip

class CodeBlockManager:
  def __init__(self):
    self.code_blocks = []

  def parse(self, markdown_str: str):
    self.code_blocks.clear()  # Clear the previous code block list
    self.code_blocks = re.findall(r'```.*?\n(.*?)```', markdown_str, re.DOTALL) # breaks when code includes ```
    # could also parse line by line, and check if line starts with ```, if already in code block, end code block, if not, start code block
    # that would fix the problem with code that contains ```, since it checks at the START of the line

  def copy_code_block(self, code_block_index: int):
    if 1 <= code_block_index <= len(self.code_blocks):
      code_block = self.code_blocks[code_block_index - 1]
      pyperclip.copy(code_block)
      print(f"Code block {code_block_index} copied to clipboard")
    else:
      print(f"Invalid code block index. Please enter a number between 1 and {len(self.code_blocks)}.")