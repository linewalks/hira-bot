from hira.hira_bot import HiraBot
from hira.helper import debug_print
if __name__ == "__main__":
  hira_bot = HiraBot()
  success = hira_bot.run()
  debug_print(success)
