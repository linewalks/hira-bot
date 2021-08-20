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
  RESEARCH_VISITER_LIST
)
from nhiss_bot import NhissBot


def run_until_success():
  start = time.time()
  # Nhiss Bot 설정.
  nhiss_bot = NhissBot(os=OS)
  nhiss_bot.setResearchNumberXpath(RESEARCH_NUMBER_XPATH)
  nhiss_bot.setResearchCenterXpath(RESEARCH_CENTER_XPATH)
  nhiss_bot.setCredential(
    id= CREDENTIAL_ID,
    pwd= CREDENTIAL_PWD,
    name=CREDENTIAL_NAME
  )
  nhiss_bot.setResearchVisiters(RESEARCH_VISITER_LIST)
  
  today = datetime.now()
  #TODO: Set date and time to login.
  # NHISS 로그인.
  nhiss_bot.login()
  # NHISS 예약 신청 작업 실행.
  nhiss_bot.selectReservationOptions()  
  reservation_result = nhiss_bot.selectReservationDate()
  current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  if reservation_result:
    # nhiss_bot.apply() # 예약 신청 버튼 클릭.
    # nhiss_bot.quit()  # 브라우저를 종료.
    end = time.time()
    elapsed = end - start
    print("------------------------- 성공 !! -------------------------")
    print(f"[HiraBot] Reservation Success! Time elapsed: {int(elapsed)} Current Time: {current_time}")
    msg = f"[HiraBot] 예약 성공하였습니다!"
    # send_message(msg)
    return True
  else:
    nhiss_bot.quit()  # 브라우저를 종료.    
    end = time.time()
    elapsed = end - start
    print("------------------------- 실패 !! -------------------------")
    print(f"[HiraBot] Reservation Failed! Time elapsed: {int(elapsed)} Current Time: {current_time}")
    # count_down(int(abs( - elapsed)))
    return False

def run_on_time():
  start = time.time()
  # Nhiss Bot 설정.
  nhiss_bot = NhissBot(os=OS)
  nhiss_bot.setResearchNumberXpath(RESEARCH_NUMBER_XPATH)
  nhiss_bot.setResearchCenterXpath(RESEARCH_CENTER_XPATH)
  nhiss_bot.setCredential(
    id= CREDENTIAL_ID,
    pwd= CREDENTIAL_PWD,
    name=CREDENTIAL_NAME
  )
  nhiss_bot.setResearchVisiters(RESEARCH_VISITER_LIST)
  
  today = datetime.now()
  #TODO: Set date and time to login.
  # nhiss_bot.wait_until_kst(today.year, today.month, today.day, 23, 55, 0)
  # NHISS 로그인.
  nhiss_bot.login()
  # NHISS 예약 신청 작업 실행.
  nhiss_bot.selectReservationOptions()

  #TODO: NHISS Bot을 실행시킬 시간(예약 실행 시간)을 설정.
  
  # nhiss_bot.wait_until_kst(today.year, today.month, today.day + 1, 0, 0, 0)
  reservation_result = nhiss_bot.selectReservationDate()
  print("예약 신청 버튼 클릭!")
  #TODO: 실제 예약 진행시 아래의 코드를 Comment-out하여 실행해주세요.

  # nhiss_bot.apply() # 예약 신청 버튼 클릭.
  # nhiss_bot.quit()  # 브라우저를 종료.
  end = time.time()
  elapsed = end - start
  print(f"[HiraBot] Elapsed: {elapsed}")
  msg = f"[HiraBot] run_on_time 예약 성공하였습니다!"
  time.sleep(50)
  # send_message(msg)

def handle_exception():
  while True:
    try:
      result = run_until_success()
      if result:
        break
    except WebDriverException:
      print("------------------------- WebDriverException 발생 -------------------------")
      count_down(60)


if __name__ == "__main__":
  run_on_time()
  # send_message("[HiraBot] 공단 예약 신청을 시작합니다.")
  # handle_exception()
