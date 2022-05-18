import requests
from datetime import datetime, timedelta


region_list = [
    "원주 본부",
    "명동",
    "명동(리서치)",
    "경인",
    "대전",
    "광주",
    "대구",
    "부산",
    "전주",
    "청주",
    "일산병원"
]

region_dict = {
    resion: f"/html/body/div[6]/div/table/tbody/tr[{idx + 1}]/td[2]"
    for idx, resion in enumerate(region_list)
}


def get_research_number_xpath(number):
  return f"/html/body/div[5]/div/table/tbody/tr[{number + 1}]/td[2]"


def get_countdown():
  today = datetime.today()
  next_day = today + timedelta(days = 1)
  target_datetime = datetime(
      year=next_day.year, 
      month=next_day.month, 
      day=next_day.day, 
      hour=8, 
      minute=54, 
      second=30
  )
  cur_gmt_time = requests.get("https://nhiss.nhis.or.kr/bd/ay/bdaya001iv.do").headers["Date"]
  cur_gmt_time = datetime.strptime(cur_gmt_time, "%a, %d %b %Y %H:%M:%S %Z")
  cur_kst_time = cur_gmt_time + timedelta(hours=9)
  delta = target_datetime - cur_kst_time
  return int(delta.total_seconds())
