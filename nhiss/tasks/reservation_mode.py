import time
from datetime import datetime, timedelta
from utils.helper import get_run_on_time_work_date, count_down, send_message, check_elapsed_time
from utils.message import success_msg, failure_msg
from nhiss.tasks.common import init_nhiss_bot, reservation_content_fill, click_reservation_button
from nhiss.tasks.register_info import RegisterInfo
from nhiss.tasks.error import ForceQuit
from nhiss.configs.nhiss_cfg import (OS,
  RESEARCH_NUMBER_XPATH,
  RESEARCH_CENTER_XPATH,
  CREDENTIAL_ID,
  CREDENTIAL_PWD,
  CREDENTIAL_NAME,
  RESEARCH_VISITER_LIST
)
from background.nhiss import celery

# nhiss_cfg.py에서 기입하는 정보가 모두 채워졌는지 확인
def check_all_config_filled_up():
  if not all((OS,
  RESEARCH_NUMBER_XPATH,
  RESEARCH_CENTER_XPATH,
  CREDENTIAL_ID,
  CREDENTIAL_PWD,
  CREDENTIAL_NAME,
  RESEARCH_VISITER_LIST)):
    raise Exception('모든 정보를 기입해주세요.')

@celery.task(bind=True)
def run_on_time(self, info, headless: bool = False, debug: bool = True,  options={}):
  register_info = RegisterInfo(*info).getInfo()

  task_message = f"[Bot] {register_info['user_name']}님 {register_info['region']} 지역 task_id: {self.request.id}입니다. target day: {register_info['target_day']}"
  send_message(task_message)
  print(task_message)

  start_time = time.time()
  work_date = get_run_on_time_work_date()

  check_all_config_filled_up()
  bot = init_nhiss_bot(headless, options)

  try:
    if not debug:
      pre_work_date = work_date - timedelta(minutes = 5)

      # TODO: Set date and time to login
      bot.wait_until_kst(pre_work_date.year, pre_work_date.month, pre_work_date.day, pre_work_date.hour, pre_work_date.minute, pre_work_date.second)

    # 1. 예약 신청 내용 입력 (날짜 선택 x)
    result = reservation_content_fill(bot, register_info['target_day'], register_info['is_seoul'], check_date = False)

    if not debug:
      # TODO: NHISS Bot을 실행시킬 시간(예약 실행 시간)을 설정.
      bot.wait_until_kst(work_date.year, work_date.month, work_date.day, work_date.hour, work_date.minute, work_date.second)

    # 2. 갱신된 날짜 테이블 내에서 선택
    bot.selectReservationDate(register_info['target_day'], register_info['is_seoul'])
    
    # 3. 예약 신청
    is_reservation_success = click_reservation_button(bot, debug)     
    # TODO: 연구 과제 중복 신청 예외처리 필요 (현재 중복되어도 성공 출력)  <- 해결 확인 필요

        
    if is_reservation_success:
      send_message(success_msg(register_info['user_name'], register_info['region'], register_info['target_day'], result['reservation_research_name']))

  except Exception as err:
    print(err)
    send_message(failure_msg(register_info['user_name'], register_info['region'], register_info['target_day'], err))
  finally:
    check_elapsed_time(start_time)
    time.sleep(1)
    bot.quit()


@celery.task(bind=True)
def run_until_success(self, info, headless: bool = False, options={}):
  register_info = RegisterInfo(*info).getInfo()
  check_all_config_filled_up()

  task_message = f"[Bot] {register_info['user_name']}님 {register_info['region']} 지역 task_id: {self.request.id}입니다. target day: {register_info['target_day']}"
  send_message(task_message)
  print(task_message)

  while True:
    start_time = time.time()
    bot = init_nhiss_bot(headless, options)

    try: 
      if (datetime.now() > datetime.strptime(register_info['target_day'], "%Y-%m-%d")):
        send_message(failure_msg(register_info['user_name'], register_info['region'], register_info['target_day'], 'target_day가 오늘 날짜보다 앞에 있습니다.'))
        break

      # 1. 예약 신청 내용 입력
      result = reservation_content_fill(bot, register_info['target_day'], register_info['is_seoul'], check_date = True)

      if result:
        # 2. 예약 신청
        is_reservation_success = click_reservation_button(bot) 

        if is_reservation_success:
          # TODO: 연구 과제 중복 신청 예외처리 필요 (현재 중복되어도 성공 출력) <- 해결 확인 필요
          send_message(success_msg(register_info['user_name'], register_info['region'], register_info['target_day'], result['reservation_research_name']))
          break

    except ForceQuit as err:
      send_message(failure_msg(register_info['user_name'], register_info['region'], register_info['target_day'], err))
      break

    except Exception as err:
      print(err)
      count_down(5)

    finally:
      check_elapsed_time(start_time)
      time.sleep(1)
      bot.quit()
