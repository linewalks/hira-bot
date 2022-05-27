import time
import requests

from datetime import timedelta, datetime
from json import dumps
from hira.helper import debug_print
from nhiss.configs.nhiss_cfg import (
    NOTIFICATION_FLAG
)

def get_seconds_pretty_string(seconds):
  return str(datetime.timedelta(seconds=seconds))

def get_run_on_time_target_day():
  today = datetime.now()
  target_time = datetime(today.year, today.month, today.day, 9, 0, 0)

  # 오늘 오전 9시 이전 : 예약 대기가 풀리는 오늘 기준 2주 뒤 예약
  if (today - target_time).total_seconds() < 0: 
    return today + timedelta(weeks = 2) 

  # 오늘 오전 9시 이후 : 예약 대기가 풀리는 내일 기준 2주 뒤 예약
  else:
    next_day = today + timedelta(days = 1)
    return next_day + timedelta(weeks = 2)


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
  url = "https://chat.googleapis.com/v1/spaces/AAAAKAqJ-Ak/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=PSxTjn9nAy37ZYdANBKA2ErTXZCrpEvJcgikzYFQ0JQ%3D" # 건보 사이트 방문

  bot_message = {'text' : msg}

  message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

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
