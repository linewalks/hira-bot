from hira.hira_bot import HiraBot
from hira.helper import debug_print, validate_priority_list_dataformat
from selenium.common.exceptions import TimeoutException
from datetime import datetime
from utils.helper import send_message
import time

def run_on_time():
  debug_print("run_on_time() 실행")
  hira_bot = HiraBot()
  try:
    start = time.time() 
    success = hira_bot.run_on_time()
    elapsed = time.time() - start
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    debug_print(f"[예약{'성공' if success else '실패'}] 현재시간: {current_time} 경과시간: {float(elapsed):.2f}초")
  except TimeoutException as e:
    debug_print("TimeoutException 발생!")


def run_until_success():
  debug_print("run_until_success() 실행")
  hira_bot = HiraBot()
  # success = hira_bot.run()
  # debug_print(f"성공 여부: ${success}")
  while True:
    start = time.time() 
    try:
      success = hira_bot.run_until_success()
      elapsed = time.time() - start
      current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
      debug_print(f"[예약{'성공' if success else '실패'}] 현재시간: {current_time} 경과시간: {float(elapsed):.2f}초")
      if success: break
    except TimeoutException as e:
      debug_print("TimeoutException 발생!")


if __name__ == "__main__":
  from argparse import ArgumentParser, RawTextHelpFormatter
  parser = ArgumentParser(
      description=
"""
심평원 센터별 신청을 자동으로 실행하는 봇 프로그램 입니다.
  신청 실행 모드:
    1. run_on_time(default mode): 설장한 시간까지 기다린 후에 신청 시도를 1회 실행합니다. 
    2. run_until_success: 예약이 성공할 때까지 즉시 계속해서 시도하는 모드.

""",
  formatter_class=RawTextHelpFormatter)
  parser.add_argument(
      "-run_until_success",
      action="store_true",
      help='예약이 성공할 때까지 계속해서 신청 하는 옵션 (사용하지 않으면 run_on_time 모드로 동작)'
  )
  args = parser.parse_args()  

  validate_priority_list_dataformat()


  if args.run_until_success:
    run_until_success()
  else:
    run_on_time()
