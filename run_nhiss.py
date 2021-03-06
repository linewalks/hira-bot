from datetime import datetime

from utils.helper import get_run_on_time_target_day, send_message, validate
from background.nhiss import celery
from nhiss.configs.nhiss_cfg import (
  RESEARCH_CENTER_XPATH,
  CREDENTIAL_NAME,
)   
from nhiss.nhiss_bot import RESEARCH_CENTER_XPATH_MAP
from nhiss.tasks.register_info import RegisterInfo
from nhiss.tasks.reservation_mode import run_on_time, run_until_success
from utils.message import failure_msg

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
      action="store_true",
      help='서울 지역에서 신청하는 옵션 (사용하지 않으면 일반 지역 신청)'
  )

  parser.add_argument(
      "--headless",
      action="store_true",
      help='브라우져 없이 봇을 실행하는 옵션'
  )

  args = parser.parse_args()
  target_day = args.run_until_success
  is_seoul = True if args.seoul else False

  user_name = CREDENTIAL_NAME
  region = '서울' if is_seoul else RESEARCH_CENTER_XPATH_MAP[RESEARCH_CENTER_XPATH]

  # run until success 모드
  if target_day:
    if (datetime.now() > datetime.strptime(target_day, "%Y-%m-%d")):
      send_message(failure_msg(user_name, region, target_day, 'target_day가 오늘 날짜보다 앞에 있습니다.'))
    else:
      try:
        validate(target_day)
      except ValueError as e:
        send_message(failure_msg(user_name, region, target_day, "올바른 형식의 target_day를 넣어 주세요 ex)xxxx-xx-xx"))
        exit(1)

      send_message(f"[Bot] {user_name}님 {region} 지역 공단봇 run_until_success 모드로 시작합니다. target day: {target_day}")
      run_until_success([user_name, target_day, region, is_seoul], args.headless)

  # run on time 모드
  else:
    target_day = get_run_on_time_target_day().strftime("%Y-%m-%d")

    send_message(f"[Bot] {user_name}님 {region} 지역 공단봇 run_on_time 모드로 시작합니다. target day: {target_day}")
    run_on_time([user_name, target_day, region, is_seoul], args.headless, debug=False)
