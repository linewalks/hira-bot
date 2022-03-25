import chromedriver_autoinstaller
import os
import time
from typing import List
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from utils.helper import count_down, send_message, validate
from nhiss.configs.nhiss_cfg import (
  OS,
  RESEARCH_NUMBER_XPATH,
  RESEARCH_CENTER_XPATH,
  CREDENTIAL_ID,
  CREDENTIAL_PWD,
  CREDENTIAL_NAME,
  RESEARCH_VISITER_LIST,
)
from nhiss.nhiss_bot import NhissBot, RESEARCH_CENTER_XPATH_MAP

def check_driver():
  chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
  driver_path = os.path.join(os.getcwd(), "files", "driver", OS)

  try:
    driver = webdriver.Chrome(f'{driver_path}/{chrome_ver}/chromedriver')   
  except:
    chromedriver_autoinstaller.install(path=driver_path)
    driver = webdriver.Chrome(f'{driver_path}/{chrome_ver}/chromedriver')
  
  driver.implicitly_wait(3)
  print("driver check 완료")


def init_nhiss_bot(headless: bool=False):
  nhiss_bot = NhissBot(operating_system=OS, headless=headless)
  nhiss_bot.setResearchNumberXpath(RESEARCH_NUMBER_XPATH)
  nhiss_bot.setResearchCenterXpath(RESEARCH_CENTER_XPATH)
  nhiss_bot.setCredential(
    id= CREDENTIAL_ID,
    pwd= CREDENTIAL_PWD,
    name=CREDENTIAL_NAME
  )
  nhiss_bot.setResearchVisiters(RESEARCH_VISITER_LIST)
  return nhiss_bot


def click_reservation_button(bot, debug):  
  is_click_success = bot.clickApplyButtonAndCheckSuccess()
  if is_click_success:
    print("================ 예약 신청 성공 =================")
  else:
    print("================ 예약 신청 실패 =================")
  return is_click_success


def run(target_day, headless: bool= False, debug: bool = True):
  start = time.time()

  # Nhiss Bot 설정.
  bot = init_nhiss_bot(headless)

  # NHISS 로그인.
  bot.login()
  # NHISS 예약 신청 작업 실행.
  bot.selectReservationOptions()  
  bot.selectReservationDate(target_day)
  current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  is_reservation_success = click_reservation_button(bot, debug)
  if is_reservation_success:
    result = True
  else:
    result = False

  time.sleep(1)
  bot.quit()

  elapsed = time.time() - start
  print(f"[Bot][DEBUG] Current Time: {current_time} Time elapsed (in seconds): {float(elapsed):.2f}")
  return result

# 예약 정보 채우기
def reservation_content_fill(target_day, headless: bool= False):
  try:
    # Nhiss Bot 설정.
    bot = init_nhiss_bot(headless)
    
    # NHISS 로그인.
    bot.login()
    # NHISS 예약 신청 작업 실행.
    bot.selectReservationOptions()  
    reservation_date = bot.selectReservationDate(target_day)
    reservation_research_name = bot.getResearchName()

    return {
      "reservation_research_name": reservation_research_name
    }
  except WebDriverException as e:
    raise Exception("예약 정보 입력 실패!")

def run_on_time(target_day, headless: bool = False, debug: bool = True):
  start = time.time()
  
  today = datetime.now()
  next_day = today + timedelta(days = 1)

  if not debug:
    #TODO: Set date and time to login.
    bot.wait_until_kst(today.year, today.month, today.day, 23, 55, 0)

  bot.login()
  bot.selectReservationOptions()

  if not debug:
    #TODO: NHISS Bot을 실행시킬 시간(예약 실행 시간)을 설정.
    bot.wait_until_kst(next_day.year, next_day.month, next_day.day, 0, 0, 0)

  bot.selectReservationDate(target_day)
  is_reservation_success = click_reservation_button(bot, debug)

  end = time.time()
  elapsed = end - start
  print(f"[Bot]] Elapsed: {elapsed}")
  if is_reservation_success:
    send_message(f"[Bot]{CREDENTIAL_NAME}님 {RESEARCH_CENTER_XPATH_MAP[RESEARCH_CENTER_XPATH]}지역 공단봇 예약 성공하였습니다! target day: {target_day}")
  if booking_success:
    send_message(f"[Bot] {CREDENTIAL_NAME}님 {RESEARCH_CENTER_XPATH_MAP[RESEARCH_CENTER_XPATH]}지역 공단봇 예약 성공하였습니다! target day: {target_day}")

  else:
    send_message(f"[Bot] {CREDENTIAL_NAME}님 {RESEARCH_CENTER_XPATH_MAP[RESEARCH_CENTER_XPATH]}지역 공단봇 예약 실패하였습니다! target day: {target_day}")
  time.sleep(10)
  bot.quit()


def run_until_success(target_day, headless: bool = False):
  while True:
    bot = None
    start = time.time()

    try:
      result = reservation_content_fill(target_day, headless)
      bot = result['bot']

      if result:
        bot.apply() # 예약 신청 버튼 클릭
        send_message(f"[Bot] {CREDENTIAL_NAME}님 {RESEARCH_CENTER_XPATH_MAP[RESEARCH_CENTER_XPATH]}지역 공단봇 예약 성공하였습니다! target day: {target_day}\n• 연구명: {result['reservation_research_name']}")

        # TODO: 연구 과제 중복 신청 예외처리 필요 (현재 중복되어도 성공 출력)
        print("------------------------------- 성공 -------------------------")
        break
    except WebDriverException as e:
      print("!!!!!!!!!!!!!!!!!!!!!!!!!!! WebDriverException 발생 !!!!!!!!!!!!!!!!!!!!!!!!!!!")
      count_down(5)
    except Exception as err:
      print(f"{str(err)}")
      count_down(5)
    finally:
      time.sleep(1)
      bot.quit()
    
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    elapsed = time.time() - start
    print(f"[Bot][DEBUG] Current Time: {current_time} Time elapsed (in seconds): {float(elapsed):.2f}")


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
      "-run_until_success",
      type= str,
      help='예약이 성공할 때까지 계속해서 신청 하는 옵션 (사용하지 않으면 run_on_time 모드로 동작) target day를 설정해주세요'
  )

  parser.add_argument(
      "--headless",
      action="store_true",
      help='브라우져 없이 봇을 실행하는 옵션'
  )

  args = parser.parse_args()
  target_day = args.run_until_success
  # chrome driver check
  check_driver()
  if target_day:
    try:
      validate(target_day)
    except ValueError as e:
      send_message(f"{e}")
      exit(1)
    send_message(f"[Bot]{CREDENTIAL_NAME}님 {RESEARCH_CENTER_XPATH_MAP[RESEARCH_CENTER_XPATH]}지역 공단봇 run_until_success 모드로 시작합니다. target day: {target_day}")
    run_until_success(target_day, args.headless)
  else:
    target_day = (datetime.now() + timedelta(days = 15)).strftime("%Y-%m-%d")
    send_message(f"[Bot]{CREDENTIAL_NAME}님 {RESEARCH_CENTER_XPATH_MAP[RESEARCH_CENTER_XPATH]}지역 공단봇 run_on_time 모드로 시작합니다. target day: {target_day}")
    run_on_time(target_day, args.headless, debug=False)
