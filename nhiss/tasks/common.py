from selenium.common.exceptions import WebDriverException
from nhiss.configs.nhiss_cfg import (
  OS,
  RESEARCH_NUMBER_XPATH,
  RESEARCH_CENTER_XPATH,
  CREDENTIAL_ID,
  CREDENTIAL_PWD,
  CREDENTIAL_NAME,
  RESEARCH_VISITER_LIST,
)
from nhiss.nhiss_bot import NhissBot


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


# 예약 정보 채우기
def reservation_content_fill(bot, target_day, is_register_am, is_seoul: bool = False, check_date: bool = True):
  try:
    # NHISS 로그인
    bot.login()

    # NHISS 예약 신청 작업 실행 (일반 / 서울)
    bot.selectReservationOptions('seoul' if is_seoul else 'general') 

    if check_date: 
      bot.selectReservationDate(target_day, is_register_am, is_seoul)
    reservation_research_name = bot.getResearchName()

    return {
      "reservation_research_name": reservation_research_name,
    }
  except WebDriverException:
    raise Exception("예약 정보 입력 실패!")
  except Exception as err:
    print(err)
    raise err

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
