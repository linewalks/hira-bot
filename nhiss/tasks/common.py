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
def init_nhiss_bot(headless: bool=False, options={}):
  research_number_xpath = options.get("research_number_xpath", RESEARCH_NUMBER_XPATH)
  research_center_xpath = options.get("research_center_xpath", RESEARCH_CENTER_XPATH)
  name = options.get("name", CREDENTIAL_NAME)
  id = options.get("id", CREDENTIAL_ID)
  password = options.get("password", CREDENTIAL_PWD)
  research_visiter_list = options.get("research_visiter_list", RESEARCH_VISITER_LIST)

  nhiss_bot = NhissBot(operating_system=OS, headless=headless)
  nhiss_bot.setResearchNumberXpath(research_number_xpath)
  nhiss_bot.setResearchCenterXpath(research_center_xpath)
  nhiss_bot.setCredential(
      id=id,
      pwd=password,
      name=name
  )
  nhiss_bot.setResearchVisiters(research_visiter_list)
  return nhiss_bot


# 예약 정보 채우기
def reservation_content_fill(bot, target_day, is_seoul: bool = False, check_date: bool = True):
  try:
    # NHISS 로그인
    bot.login()

    # NHISS 예약 신청 작업 실행 (일반 / 서울)
    bot.selectReservationOptions('seoul' if is_seoul else 'general') 

    if check_date: 
      bot.selectReservationDate(target_day, is_seoul)
    reservation_research_name = bot.getResearchName()

    return {
      "reservation_research_name": reservation_research_name,
    }
  except WebDriverException:
    #TODO: 아이디, 비밀번호 오입력 시 run_until_success break 걸기
    # alert_text = e.alert_text
    # if '가입자 정보가 없습니다.' or '비밀번호를 확인해주세요' in alert_text:
    #   raise Exception(alert_text)
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
