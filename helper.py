import datetime
import time
import sys
from httplib2 import Http
from json import dumps
from files.configs.nhiss_cfg import (
    NOTIFICATION_FLAG
)

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


def send_message(msg):
  if not NOTIFICATION_FLAG:
    print(f"[HiraBot][DEBUG] {msg}")
    return  
  url = 'https://chat.googleapis.com/v1/spaces/AAAARTaMFug/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=t-AsqJo52GoF0jiqVehUA1H5yojIRd0DbD8LSjdkuSg%3D'
  bot_message = {
      'text' : msg}

  message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

  http_obj = Http()

  response = http_obj.request(
      uri=url,
      method='POST',
      headers=message_headers,
      body=dumps(bot_message),
  )
