import time
import sys


def parse_seconds(seconds):
  hours = int(seconds / 3600)
  mins = int(seconds / 60 - hours * 60)
  seconds = int(seconds % 60)
  return hours, mins, seconds

def get_seconds_pretty_string(seconds):
  hours, mins, seconds = parse_seconds(seconds)
  return f"{hours:02d}:{mins:02d}:{seconds:02d}"


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
