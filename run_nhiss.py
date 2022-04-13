import time
from typing import List
from datetime import timedelta, datetime
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
from nhiss.tasks.region_general import run_on_time, run_until_success
from nhiss.tasks.region_seoul import run_on_time_in_seoul, run_until_success_in_seoul

# nhiss 봇 초기화
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

# 예약 버튼 클릭
def click_reservation_button(bot, debug: bool = True):  
  try:
    is_click_success = bot.clickApplyButtonAndCheckSuccess()

    if is_click_success:
      print("================ 예약 신청 성공 =================")
      return is_click_success
  except Exception as e:
    print("================ 예약 신청 실패 =================")
    raise e

# 예약 정보 채우기
def reservation_content_fill(bot, target_day, check_date: bool = True):
  try:
    # NHISS 로그인.
    bot.login()

    # NHISS 예약 신청 작업 실행.
    bot.selectReservationOptions() 
    if check_date: 
      bot.selectReservationDate(target_day)
    reservation_research_name = bot.getResearchName()

    return {
      "reservation_research_name": reservation_research_name,
    }
  except WebDriverException as e:
    raise Exception("예약 정보 입력 실패!")
  except Exception as err:
    print(err)
    raise err

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
    "-seoul",
    type= str,
    help='서울 지역에서 신청하는 옵션 (사용하지 않으면 일반 지역 신청)'
  )

  parser.add_argument(
      "--headless",
      action="store_true",
      help='브라우져 없이 봇을 실행하는 옵션'
  )

  args = parser.parse_args()
  target_day = args.run_until_success
  seoul = args.seoul
  region = RESEARCH_CENTER_XPATH_MAP[RESEARCH_CENTER_XPATH] if seoul == None else '서울'
  
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
