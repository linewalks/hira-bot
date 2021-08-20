import time
from typing import List
from datetime import timedelta, datetime
from selenium.common.exceptions import WebDriverException
from helper import count_down, send_message
from files.configs.nhiss_cfg import (
  OS,
  RESEARCH_NUMBER_XPATH,
  RESEARCH_CENTER_XPATH,
  CREDENTIAL_ID,
  CREDENTIAL_PWD,
  CREDENTIAL_NAME,
  RESEARCH_VISITER_LIST,
)
from nhiss_bot import NhissBot


def init_nhiss_bot():
  nhiss_bot = NhissBot(os=OS)
  nhiss_bot.setResearchNumberXpath(RESEARCH_NUMBER_XPATH)
  nhiss_bot.setResearchCenterXpath(RESEARCH_CENTER_XPATH)
  nhiss_bot.setCredential(
    id= CREDENTIAL_ID,
    pwd= CREDENTIAL_PWD,
    name=CREDENTIAL_NAME
  )
  nhiss_bot.setResearchVisiters(RESEARCH_VISITER_LIST)
  return nhiss_bot

def run_until_success(debug=True):
  start = time.time()
  # Nhiss Bot 설정.
  nhiss_bot = init_nhiss_bot()
  
  today = datetime.now()
  #TODO: Set date and time to login.
  # NHISS 로그인.
  nhiss_bot.login()
  # NHISS 예약 신청 작업 실행.
  nhiss_bot.selectReservationOptions()  
  reservation_result = nhiss_bot.selectReservationDate()
  current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  if reservation_result:
    if not debug:
      nhiss_bot.apply() # 예약 신청 버튼 클릭.
      nhiss_bot.quit()  # 브라우저를 종료.
    end = time.time()
    elapsed = end - start
    print("------------------------------------------------------------------ 성공 -------------------------")
    print(f"[HiraBot][DEBUG] Time elapsed: {int(elapsed)}s Current Time: {current_time}")
    return True
  else:
    nhiss_bot.quit()  # 브라우저를 종료.    
    end = time.time()
    elapsed = end - start
    print(f"[HiraBot][DEBUG] Time elapsed: {int(elapsed)}s Current Time: {current_time}")
    return False

def run_on_time(debug=True):
  start = time.time()
  # Nhiss Bot 설정.
  nhiss_bot = init_nhiss_bot()
  
  today = datetime.now()

  if not debug:
    #TODO: Set date and time to login.
    nhiss_bot.wait_until_kst(today.year, today.month, today.day, 23, 55, 0)

  nhiss_bot.login()
  nhiss_bot.selectReservationOptions()

  if not debug:
    #TODO: NHISS Bot을 실행시킬 시간(예약 실행 시간)을 설정.
    nhiss_bot.wait_until_kst(today.year, today.month, today.day + 1, 0, 0, 0)
  
  booking_success = nhiss_bot.selectReservationDate()

  if not debug:
    nhiss_bot.apply() # 예약 신청 버튼 클릭.
    nhiss_bot.quit()  # 브라우저를 종료.
  
  end = time.time()
  elapsed = end - start
  print(f"[HiraBot] Elapsed: {elapsed}")
  if booking_success:
    send_message("run_on_time 예약 성공하였습니다!")
  else:
    send_message("run_on_time 예약 실패하였습니다!")
  time.sleep(10)

def handle_exception():
  while True:
    try:
      result = run_until_success()
      if result:
        break
    except WebDriverException as e:
      print("!!!!!!!!!!!!!!!!!!!!!!!!!!! WebDriverException 발생 !!!!!!!!!!!!!!!!!!!!!!!!!!!")
      count_down(5)


if __name__ == "__main__":
  from argparse import ArgumentParser, RawTextHelpFormatter
  parser = ArgumentParser(
      description=
"""
공단 신청을 자동으로 실행하는 봇 프로그램 입니다.
  신청 실행 모드:
    1. run_on_time: 세팅한 날짜/시간에 2주 뒤 날짜를 예약 시도하는 모드. 단일 실행
    2. run_until_success: 세팅한 날짜/시간에 예약이 성공할 때까지 계속해서 시도하는 모드.

""",
      formatter_class=RawTextHelpFormatter)

  parser.add_argument(
      "--run_until_success",
      type=bool,
      required=False,
      default=False,
      help='예약이 성공할 때까지 계속해서 신청 하는 옵션 (사용하지 않으면 run_on_time 모드로 동작)'
  )

  args = parser.parse_args()
  print(args.run_until_success)
  # send_message("공단 예약 신청을 시작합니다.")
  # #TODO: 파이썬 실행 커맨드라인 옵션 추가
  # # run_on_time()
  # handle_exception()
