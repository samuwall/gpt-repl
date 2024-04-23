import sys
import time
import threading

class Spinner:
  def __init__(self, message="", delay=0.1):
    self.spinner = ['|', '/', '-', '\\']
    self.delay = delay
    self.message = message
    self.running = False
    self.spinner_thread = None

  def spin(self):
    sys.stdout.write('\n')
    sys.stdout.flush()
    while self.running:
      for cursor in self.spinner:
        sys.stdout.write(f'\r{self.message} {cursor}')
        sys.stdout.flush()
        time.sleep(self.delay)
        sys.stdout.write(f'\r{self.message} ')
        sys.stdout.flush()

  def start(self):
    self.running = True
    self.spinner_thread = threading.Thread(target=self.spin)
    self.spinner_thread.start()

  def stop(self):
    self.running = False
    self.spinner_thread.join()
    sys.stdout.write('\x1b[A')    # move up a line
    sys.stdout.write("\r\x1b[0J") # clear from cursor to end of screen
    sys.stdout.flush()