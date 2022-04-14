import time
from datetime import timedelta, datetime
from selenium.common.exceptions import WebDriverException
from utils.helper import count_down, send_message, check_elapsed_time
from utils.message import success_msg, failure_msg
from nhiss.configs.nhiss_cfg import (
  RESEARCH_CENTER_XPATH,
  CREDENTIAL_NAME,
)
from nhiss.tasks.common import init_nhiss_bot, click_reservation_button
from nhiss.nhiss_bot import RESEARCH_CENTER_XPATH_MAP

user_name = CREDENTIAL_NAME
region = RESEARCH_CENTER_XPATH_MAP[RESEARCH_CENTER_XPATH]


# 예약 정보 채우기
def reservation_content_fill(bot, target_day, check_date: bool = True):
  try:
    # NHISS 로그인
    bot.login()

    # NHISS 예약 신청 작업 실행
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

def run_on_time(target_day, headless: bool = False, debug: bool = True):
  start_time = time.time()
  today = datetime.now()
  next_day = today + timedelta(days = 1)

  bot = init_nhiss_bot(headless)

  try:
    if not debug:
      # TODO: Set date and time to login
      bot.wait_until_kst(today.year, today.month, today.day, 23, 55, 0)

    # 예약 신청 내용 입력
    result = reservation_content_fill(bot, target_day, False)

    if not debug:
      # TODO: NHISS Bot을 실행시킬 시간(예약 실행 시간)을 설정.
      bot.wait_until_kst(next_day.year, next_day.month, next_day.day, 0, 0, 0)

    bot.selectReservationDate()
    
    # 예약 신청 버튼 클릭
    is_reservation_success = click_reservation_button(bot, debug) 
    # TODO: 연구 과제 중복 신청 예외처리 필요 (현재 중복되어도 성공 출력)
    
    if is_reservation_success:
      send_message(success_msg(user_name, region, target_day, result['reservation_research_name']))

  except Exception as err:
    print(err)
    send_message(failure_msg(user_name, region, target_day))
  finally:
    check_elapsed_time(start_time)
    time.sleep(10)
    bot.quit()

def run_until_success(target_day, headless: bool = False):
  while True:
    bot = init_nhiss_bot(headless)
    start_time = time.time()

    try:
      # 예약 신청 내용 입력
      result = reservation_content_fill(bot, target_day)

      if result:
        # 예약 신청 버튼 클릭
        is_reservation_success = click_reservation_button(bot) 

        if is_reservation_success: 
          # TODO: 연구 과제 중복 신청 예외처리 필요 (현재 중복되어도 성공 출력)
          send_message(success_msg(user_name, region, target_day, result['reservation_research_name']))

    except Exception as err:
      print(err)
      count_down(5)
    finally:
      check_elapsed_time(start_time)
      time.sleep(1)
      bot.quit()
