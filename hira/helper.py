from datetime import datetime
from logging import debug
from hira.config import priority_list
def debug_print(msg):
  print(f"[HiraBot][Debug]{msg}")

def validate_priority_list_dataformat():
  for p in priority_list:
    validate_priority_list_dataformat_helper(p[0])
    validate_priority_list_dataformat_helper(p[1])

def validate_priority_list_dataformat_helper(date):
  try:
    given_date = datetime.strptime(date, '%Y%m%d')
  except ValueError:
    raise ValueError(f"잘못된 날짜 데이터 형식입니다. 반드시 YYYYMMDD 형태로 수정해주세요.\n전달 받은 잘못된 날짜 데이터: {date}")
  
  if (given_date - datetime.now()).total_seconds() <= 0:
    raise ValueError(f"priority_list 중 과거의 날짜 발견. 미래의 날짜로 수정해주세요. 수정할 날짜: {date}")
