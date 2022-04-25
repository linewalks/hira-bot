import datetime
import time
import requests
 
from json import dumps
from hira.helper import debug_print
from nhiss.configs.nhiss_cfg import (
    NOTIFICATION_FLAG
)

def get_seconds_pretty_string(seconds):
  return str(datetime.timedelta(seconds=seconds))


def count_down(time_to_wait_seconds):
  if time_to_wait_seconds <= 0:
    raise ValueError("cannot wait for negative seconds.")
  
  start = time.time()
  print(f"[HiraBot]    Waiting for {get_seconds_pretty_string(time_to_wait_seconds)}")
  time.sleep(time_to_wait_seconds)
  elapsed = time.time() - start
  current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  debug_print(f"현재시간: {current_time} 경과시간: {float(elapsed):.2f}초")
  print("\n")



def send_message(msg):
  if not NOTIFICATION_FLAG:
    print(f"[HiraBot][DEBUG] {msg}")
    return  
  # url = "https://chat.googleapis.com/v1/spaces/AAAAKAqJ-Ak/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=PSxTjn9nAy37ZYdANBKA2ErTXZCrpEvJcgikzYFQ0JQ%3D" # 건보 사이트 방문
  url = "https://chat.googleapis.com/v1/spaces/AAAAF4dc2k4/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=9TUu6SkDaU99NTXLn-Shnzgh_NvwD0OAgrSZAMBvuV4%3D"
  bot_message = {'text' : msg}

  message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

  http_obj = Http()

  response = requests.post(url, headers=message_headers, json=bot_message)


def validate(date_text):
  try:
      datetime.datetime.strptime(date_text, '%Y-%m-%d')
  except ValueError:
      raise ValueError(f"Incorrect data format, should be YYYY-MM-DD. Given date_test: {date_text}")

# 시작 시간부터 경과 시간 체크
def check_elapsed_time(start_time):
  current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  end_time = time.time()
  elapsed = end_time - start_time
  print(f"[Bot][DEBUG] Current Time: {current_time} Time elapsed (in seconds): {float(elapsed):.2f}")
