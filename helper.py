import time
import sys
import datetime


def get_seconds_pretty_string(seconds):
  return str(datetime.timedelta(seconds=seconds))


def count_down(time_to_wait_seconds):
  if time_to_wait_seconds <= 0:
    raise ValueError("cannot wait for negative seconds.")
  print(f"[HiraBot] Waiting for {get_seconds_pretty_string(time_to_wait_seconds)}")
  for remaining in range(time_to_wait_seconds, 0, -1):
      dots = "." * (5 - remaining % 5)
      sys.stdout.write("\r")
      sys.stdout.write(f"[HiraBot] {get_seconds_pretty_string(remaining)} remaining{dots}")
      sys.stdout.flush()
      time.sleep(1)
  print("\n")
