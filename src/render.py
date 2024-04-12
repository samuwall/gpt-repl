import os
import re
import textwrap
import ansiwrap
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_style_by_name

color_codes = {
  "red": "\x1b[91m",
  "green": "\x1b[92m",
  "yellow": "\x1b[93m",
  "blue": "\x1b[94m",
  "magenta": "\x1b[95m",
  "cyan": "\x1b[96m",
  "white": "\x1b[97m",
  "grey": "\x1b[37m",
  "orange3": "\x1b[38;5;208m",
  "reset": "\x1b[0m"
}

def render(markdown_str: str, color: str, renderer: str):
  if renderer == "raw":
    print(f"\n{markdown_str}")
    print_rule(color)
    print()

  elif renderer == "lite":
    print(f"\n{md2ansi(markdown_str)}\n")
    print_rule(color)
    #print()

  else:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    console = Console()
    md = Markdown(markdown_str)
    panel = Panel(md, border_style=color, padding=(1,2), expand=False)
    console.print(panel)
    print(f"\n")




def md2ansi(md: str):
  lines = md.split('\n')
  output = []
  width = os.get_terminal_size().columns
  
  in_code_block = False
  code_block_language = None
  code_block_content = []
  code_snippets = []
  style = get_style_by_name("monokai")
  
  for line in lines:
    if line.strip().startswith('```'):
      if in_code_block:
        # End of code block, process it
        try:
          lexer = get_lexer_by_name(code_block_language)
        except Exception:
          lexer = TextLexer()
        try:
          formatted_code = highlight('\n'.join(code_block_content), lexer, Terminal256Formatter(style=style))
          output.append(formatted_code)
        except Exception as e:
          print(f"Error formatting code block: {str(e)}")
          output.append('\n'.join(code_block_content))
        in_code_block = False
        code_block_language = None
        code_block_content = []
      else:
        # Start of code block
        in_code_block = True
        code_block_language = line.strip('` ') # removes all three backticks and any whitespace from beginning of string, leaving only language
      continue
    
    if in_code_block:
      code_block_content.append(line)
    else:
      # Process normal text

      # extract inline code, replace with placeholders
      code_snippets = re.findall(r'`(.*?)`', line)
      line = re.sub(r'`(.*?)`', '1NL1NECODE', line)
      
      line = re.sub(r'(\*\*|__)(.*?)\1', lambda m: f"\x1b[1m{m.group(2)}\x1b[0m", line)   # bold
      line = re.sub(r'(\*|_)(.*?)\1', lambda m: f"\x1b[3m{m.group(2)}\x1b[0m", line)      # italic
      line = re.sub(r'^(#{1,6})\s*(.*)', lambda m: f"\x1b[1;35m{' ' * len(m.group(1))} {m.group(2)}\x1b[0m", line)  # headers in magenta
      line = re.sub(r'^\s*([\*\-\+])\s+(.*)', lambda m: f"  \x1b[93m•\x1b[0m {m.group(2)}", line)        # unordered lists
      line = re.sub(r'^(\d+\.)\s+(.*)', lambda m: f" \x1b[93m{m.group(1)}\x1b[0m {m.group(2)}", line)   # ordered lists

      # replace all inline code placeholders in this line w/ real code
      for snippet in code_snippets:
        line = line.replace('1NL1NECODE', f"\x1b[1;36m{snippet}\x1b[0m", 1)

      try:
        wrapped_text = ansiwrap.fill(line, width=width, replace_whitespace=True, drop_whitespace=True, break_on_hyphens=False)
        output.append(wrapped_text)
      except Exception as e:
        print(f"Error wrapping text: {str(e)}")
        output.append(line)

  return '\n'.join(output) # join all members of list var into one big str, joined with newlines


def print_rule(color: str):

  if color not in color_codes:
    color = "green" # Default color if an invalid color is specified

  rule = "─" * os.get_terminal_size().columns
  colored_rule = color_codes[color] + rule + color_codes["reset"]
  print(colored_rule)
