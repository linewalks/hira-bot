import time
from datetime import timedelta, datetime

from utils.helper import count_down, send_message, check_elapsed_time
from utils.message import success_msg, failure_msg
from nhiss.tasks.common import init_nhiss_bot, reservation_content_fill, click_reservation_button

def run_on_time(info, headless: bool = False, debug: bool = True):
  register_info = info.getInfo()

  start_time = time.time()
  today = datetime.now()
  next_day = today + timedelta(days = 1)

  bot = init_nhiss_bot(headless)

  try:
    if not debug:
      # TODO: Set date and time to login
      bot.wait_until_kst(today.year, today.month, today.day, 23, 55, 0)

    # 1. 예약 신청 내용 입력 (날짜 선택 x)
    result = reservation_content_fill(bot, register_info['target_day'], register_info['is_seoul'], check_date = False)

    if not debug:
      # TODO: NHISS Bot을 실행시킬 시간(예약 실행 시간)을 설정.
      bot.wait_until_kst(next_day.year, next_day.month, next_day.day, 0, 0, 0)

    # 2. 갱신된 날짜 테이블 내에서 선택
    bot.selectReservationDate(is_register_am = register_info['is_register_am'], is_seoul = register_info['is_seoul'])
    
    # 3. 예약 신청
    is_reservation_success = click_reservation_button(bot, debug) 
    # TODO: 연구 과제 중복 신청 예외처리 필요 (현재 중복되어도 성공 출력)
    
    if is_reservation_success:
      send_message(success_msg(register_info['user_name'], register_info['region'], register_info['target_day'], result['reservation_research_name']))

  except Exception as err:
    print(err)
    send_message(failure_msg(register_info['user_name'], register_info['region'], register_info['target_day']))
  finally:
    check_elapsed_time(start_time)
    time.sleep(10)
    bot.quit()


def run_until_success(info, headless: bool = False):
  register_info = info.getInfo()

  while True:
    bot = init_nhiss_bot(headless)
    start_time = time.time()

    try: 
      # 1. 예약 신청 내용 입력
      result = reservation_content_fill(bot, register_info['target_day'], register_info['is_register_am'], register_info['is_seoul'], check_date = True)

      if result:
        # 2. 예약 신청
        is_reservation_success = click_reservation_button(bot) 

        if is_reservation_success: 
          target_day = register_info['target_day']

          if register_info['is_seoul']:
            target_day += '(오전)' if register_info['is_register_am'] else '(오후)'

          # TODO: 연구 과제 중복 신청 예외처리 필요 (현재 중복되어도 성공 출력)
          send_message(success_msg(register_info['user_name'], register_info['region'], target_day, result['reservation_research_name']))
          break

    except Exception as err:
      print(err)
      count_down(5)
    finally:
      check_elapsed_time(start_time)
      time.sleep(1)
      bot.quit()
