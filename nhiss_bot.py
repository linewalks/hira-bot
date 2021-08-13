import time
from typing import List
import requests
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from helper import count_down
from notification import send_message
from files.configs.nhiss_cfg import (
  OS,
  RESEARCH_NUMBER_XPATH,
  RESEARCH_CENTER_XPATH,
  CREDENTIAL_ID,
  CREDENTIAL_PWD,
  CREDENTIAL_NAME,
  RESEARCH_VISITER_LIST
)

def get_target_index_js(driver, target_day):
  return driver.execute_script("""
    var target_day =  arguments[0]
    var row_count = window[2].WShtAC_1.GetRowCount()
    var target_index = -1
    for (var i = 0; i < row_count; i++){
      var cur_row_date = window[2].WShtAC_1.GetGridCellText("RSVT_DT", i)  
      if (target_day == cur_row_date){
        target_index = i
        break;
      }   
    }
    return target_index
  """, target_day)


def select_target_day_with_index_js(driver, target_index):
  driver.execute_script("""
    var target_index =  arguments[0]
    window[2].WShtAC_1.SetGridCellText("CHK", target_index, 1)
    window[2].BTN_SELECT_Click()
  """, target_index)


def select_visitor_js(driver, visiter):
  driver.execute_script("""
    var target_user_name =  arguments[0]
    var row_count = window[2].WShtAC_1.GetRowCount()
    var target_index = -1
    for (var i = 0; i < row_count; i++){
      var cur_user_id = window[2].WShtAC_1.GetGridCellText("RSCHR_NM", i)  
      if (target_user_name == cur_user_id){
        target_index = i
        break;
      }   
    }

    if (target_index != -1){
      window[2].WShtAC_1.SetGridCellText("CHK", target_index, 1)
    }
  """, visiter)

class NhissBot:
  
  def __init__(self, os: str):
    self.os = os

    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    self.driver = webdriver.Chrome(executable_path=f'./files/driver/{self.os}/chromedriver', options=op)


  def wait_until_kst(
        self, 
        year, 
        month, 
        day, 
        hour=0, 
        minute=0, 
        second=0
    ):
    target_datetime = datetime(
      year=year, 
      month=month, 
      day=day, 
      hour=hour, 
      minute=minute, 
      second=second)
    print(f'[HiraBot] Target  Time (KST): {target_datetime}')
    time_diff = timedelta(hours=9) 
    format = "%a, %d %b %Y %H:%M:%S %Z"
    cur_gmt_time = requests.get('https://nhiss.nhis.or.kr/bd/ay/bdaya001iv.do').headers['Date']
    cur_gmt_time = datetime.strptime(cur_gmt_time, format)
    print(f'[HiraBot] Current Time (GMT): {cur_gmt_time}')
    cur_kst_time = cur_gmt_time + time_diff
    print(f'[HiraBot] Current Time (KST): {cur_kst_time}')
    delta = target_datetime - cur_kst_time
    # time_to_wait_sec = int(delta.total_seconds())
    time_to_wait_sec = float(delta.total_seconds())
    try:
      # count_down(time_to_wait_sec)
      time.sleep(time_to_wait_sec)
    except ValueError:
      print('[HiraBot][TargetTimeError] Target Time must be in the future')
      exit(1)
    print('[HiraBot] Time to activate HiraBot!')

  def setCredential(self, id, pwd, name):
    self.user_id = id
    self.user_pwd = pwd
    self.user_name = name

  def setResearchVisiters(self, visiters: List[str]):
    self.visiters = visiters

  def setResearchCenterXpath(self, research_center_xpath: str):
    self.research_center_xpath = research_center_xpath

  def setResearchNumberXpath(self, research_number_xpath: str):
    self.research_number_xpath = research_number_xpath

  def login(self):
    # print(f'[HiraBot] Log-in as \
    # \n    Id:{self.user_id}\n    Name:{self.user_name}')
    # 로그인 페이지 접속
    self.wait = WebDriverWait(self.driver, timeout=1)
    self.driver.get('https://nhiss.nhis.or.kr/bd/ay/bdaya003iv.do')
    # 로그인
    # TODO: 계정 정보 config 파일로 이동
    self.driver.find_element_by_id('j_username').send_keys(self.user_id)
    self.driver.find_element_by_id('j_password').send_keys(self.user_pwd + Keys.RETURN)
    time.sleep(1)
    # 로그인 후 팝업 닫기
    main = self.driver.window_handles 
    for handle in main: 
      if handle != main[0]: 
        self.driver.switch_to.window(handle) 
        self.driver.close() 
    self.driver.switch_to.window(self.driver.window_handles[0])
  
  def selectReservationOptions(self):
    # print('[HiraBot] Go to My service view.')
    self.__goToMyService()
    time.sleep(1)
    # print('[HiraBot] Selecting research number')
    self.__select_research_number()
    # print('[HiraBot] Selecting research center')
    self.__select_research_center()
    # print('[HiraBot] Selecting visiter(s)')
    self.__select_visitor()
  

  def selectReservationDate(self):
    # print('[HiraBot] Selecting reservation date')
    return self.__select_reservation_date()
  

  # 신청
  def apply(self):
    time.sleep(1)
    # Switch to default frame from cmsView
    print('[HiraBot] Submitting...')
    self.driver.switch_to.frame("cmsView")
    self.driver.find_element_by_xpath('//*[@id="ods_WSF_1_insert_BTN_APPLY"]').click()

  def refresh(self):
    self.driver.refresh()
  
  def quit(self, time_s=5):
    time.sleep(time_s)
    self.driver.quit()

  # 연구과제관리번호 선택
  def __select_research_number(self):
    
    self.driver.find_element_by_id("WSF_1_insert_APLY_MGMT_NO_label").click()
    self.driver.find_element_by_xpath(self.research_number_xpath).click()
    self.driver.find_element_by_xpath('//*[@id="a"]/table/tbody')

  # MY서비스 - 분석센터이용 페이지로 이동
  def __goToMyService(self):
    self.driver.get('https://nhiss.nhis.or.kr/bd/af/bdafa002lv.do')
    time.sleep(1)
    self.driver.switch_to.frame("cmsView")

  # 센터구분
  def __select_research_center(self):
    self.driver.find_element_by_id("WSF_1_insert_ZN_CEN_CD_label").click()
    self.driver.find_element_by_xpath(self.research_center_xpath).click() # 광주

  # 예약일자 선택
  def __select_reservation_date(self):
    self.driver.switch_to.frame("cmsView")
    self.driver.find_element_by_id("ods_WSF_1_insert_BTN_DT").click()
    time.sleep(1)
    # Switch to default frame from cmsView
    self.driver.switch_to.default_content()


    # Get target day which is two weeks later than today.
    #TODO: comment out line below. 
    # target_day = (datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%d")
    #TODO: delete hard-coded target day below.
    target_day = "2021-09-21"
    target_index = get_target_index_js(self.driver, target_day)
    # print(f"[HiraBot] target_index for {target_day}: {target_index}")
    if target_index != -1:
      select_target_day_with_index_js(self.driver, target_index)
      return True
    else:
      return False


  def __select_visitor(self):
    # Select visitor(s)

    self.driver.find_element_by_id("ods_WSF_1_insert_BTN_VISTM").click()
    time.sleep(1)
    self.driver.switch_to.default_content()

    # print("[HiraBot] Researchers:")
    for visiter in self.visiters:
      select_visitor_js(self.driver, visiter)
      # print(f"    {visiter}")
    self.driver.execute_script("window[2].BTN_SELECT_Click()")

def run_until_success():
  start = time.time()
  # Nhiss Bot 설정.
  nhiss_bot = NhissBot(os=OS)
  nhiss_bot.setResearchNumberXpath(RESEARCH_NUMBER_XPATH)
  nhiss_bot.setResearchCenterXpath(RESEARCH_CENTER_XPATH)
  nhiss_bot.setCredential(
    id= CREDENTIAL_ID,
    pwd= CREDENTIAL_PWD,
    name=CREDENTIAL_NAME
  )
  nhiss_bot.setResearchVisiters(RESEARCH_VISITER_LIST)
  
  today = datetime.now()
  #TODO: Set date and time to login.
  # NHISS 로그인.
  nhiss_bot.login()
  # NHISS 예약 신청 작업 실행.
  nhiss_bot.selectReservationOptions()  
  reservation_result = nhiss_bot.selectReservationDate()
  current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  if reservation_result:
    # nhiss_bot.apply() # 예약 신청 버튼 클릭.
    # nhiss_bot.quit()  # 브라우저를 종료.
    end = time.time()
    elapsed = end - start
    print("------------------------- 성공 !! -------------------------")
    print(f"[HiraBot] Reservation Success! Time elapsed: {int(elapsed)} Current Time: {current_time}")
    msg = f"[HiraBot] 예약 성공하였습니다!"
    send_message(msg)
    return True
  else:
    nhiss_bot.quit()  # 브라우저를 종료.    
    end = time.time()
    elapsed = end - start
    print("------------------------- 실패 !! -------------------------")
    print(f"[HiraBot] Reservation Failed! Time elapsed: {int(elapsed)} Current Time: {current_time}")
    # count_down(int(abs( - elapsed)))
    return False

def run_on_time():
  start = time.time()
  # Nhiss Bot 설정.
  nhiss_bot = NhissBot(os=OS)
  nhiss_bot.setResearchNumberXpath(RESEARCH_NUMBER_XPATH)
  nhiss_bot.setResearchCenterXpath(RESEARCH_CENTER_XPATH)
  nhiss_bot.setCredential(
    id= CREDENTIAL_ID,
    pwd= CREDENTIAL_PWD,
    name=CREDENTIAL_NAME
  )
  nhiss_bot.setResearchVisiters(RESEARCH_VISITER_LIST)
  
  today = datetime.now()
  #TODO: Set date and time to login.
  nhiss_bot.wait_until_kst(today.year, today.month, today.day, 23, 55, 0)
  # NHISS 로그인.
  nhiss_bot.login()
  # NHISS 예약 신청 작업 실행.
  nhiss_bot.selectReservationOptions()

  #TODO: NHISS Bot을 실행시킬 시간(예약 실행 시간)을 설정.
  
  nhiss_bot.wait_until_kst(today.year, today.month, today.day + 1, 0, 0, 0)
  reservation_result = nhiss_bot.selectReservationDate()
  print("예약 신청 버튼 클릭!")
  #TODO: 실제 예약 진행시 아래의 코드를 Comment-out하여 실행해주세요.

  nhiss_bot.apply() # 예약 신청 버튼 클릭.
  # nhiss_bot.quit()  # 브라우저를 종료.
  end = time.time()
  elapsed = end - start
  print(f"[HiraBot] Elapsed: {elapsed}")
  msg = f"[HiraBot] 예약 성공하였습니다!"
  send_message(msg)

def handle_exception():
  while True:
    try:
      result = run_until_success()
      if result:
        break
    except WebDriverException:
      print("------------------------- WebDriverException 발생 -------------------------")
      # count_down(60)


if __name__ == "__main__":
  # run_on_time()
  send_message("[HiraBot] 공단 예약 신청을 시작합니다.")
  handle_exception()
