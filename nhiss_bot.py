import time
from typing import List
import requests
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NhissBot:
  
  def __init__(self, 
      os: str, 
      research_center_xpath: str,
      research_number_xpath: str,
      debug=False):
    
    self.debug = debug
    self.os = os
    if self.debug:
      self.driver = webdriver.Chrome(f'./files/driver/{self.os}/chromedriver')
    else:
      self.driver = None
    # 센터구분 xpath
    self.research_center_xpath = research_center_xpath
    # 연구과제관리번호 선택
    self.research_number_xpath = research_number_xpath

  
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
    cur_gmt_time = requests.get('https://opendata.hira.or.kr/home.do').headers['Date']
    cur_gmt_time = datetime.strptime(cur_gmt_time, format)
    print(f'[HiraBot] Current Time (GMT): {cur_gmt_time}')
    cur_kst_time = cur_gmt_time + time_diff
    print(f'[HiraBot] Current Time (KST): {cur_kst_time}')
    delta = target_datetime - cur_kst_time
    time_to_wait_sec = float(delta.total_seconds())
    print(f'[HiraBot] Waiting for: {time_to_wait_sec}s')
    try:
      time.sleep(time_to_wait_sec)
    except ValueError:
      print('[HiraBot][TargetTimeError] Target Time must be in the future')
      exit(1)
    print('[HiraBot] Time to activate HiraBot!')
    self.driver = webdriver.Chrome(f'./files/driver/{self.os}/chromedriver')

  def setCredential(self, id, pwd, name):
    self.user_id = id
    self.user_pwd = pwd
    self.user_name = name
  
  def setResearchers(self, researchers: List[str]):
    self.researchers = researchers

  def login(self):
    print(f'[HiraBot] Log-in as \
    \n    Id:{self.user_id}\n    Name:{self.user_name}')
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
    print('[HiraBot] Go to My service view.')
    self.__goToMyService()
    time.sleep(1)
    print('[HiraBot] Selecting research number')
    self.__select_research_number()
    print('[HiraBot] Selecting research center')
    self.__select_research_center()
    print('[HiraBot] Selecting reservation date')
    self.__select_reservation_date()
    print('[HiraBot] Selecting visiter(s)')
    self.__select_visitor()
  

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
    self.driver.find_element_by_id("ods_WSF_1_insert_BTN_DT").click()
    time.sleep(1)
    # Switch to default frame from cmsView
    self.driver.switch_to.default_content()

    # Get target day which is two weeks later than today.
    target_day = (datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%d")
    self.driver.execute_script("""
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
      if (target_index != -1){
        window[2].WShtAC_1.SetGridCellText("CHK", target_index, 1)
      }
      window[2].BTN_SELECT_Click()
    """, target_day)
  

  def __select_visitor(self):
    # Select visitor(s)
    time.sleep(1)
    self.driver.switch_to.frame("cmsView")
    self.driver.find_element_by_id("ods_WSF_1_insert_BTN_VISTM").click()
    time.sleep(1)
    self.driver.switch_to.default_content()

    def select_visitor_js(researcher_name):
      self.driver.execute_script("""
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
      """, researcher_name)
    print("[HiraBot] Researchers:")
    for researcher_name in self.researchers:
      select_visitor_js(researcher_name)
      print(f"    {researcher_name}")
    self.driver.execute_script("window[2].BTN_SELECT_Click()")


if __name__ == "__main__":
  import sys
  sys.stdout.flush()
  nhiss_bot = NhissBot(
  os='linux',
  #TODO: Put research center xpath below.
  research_center_xpath= '//*[@id="a"]/table/tbody/tr[6]/td[2]',
  #TODO: Put research number xpath below.
  research_number_xpath= '//*[@id="a"]/table/tbody/tr[3]/td[2]',
  debug=False
  )

  #TODO: Set the date time to be the target time below.
  nhiss_bot.wait_until_kst(2021, 7, 8, 10, 0, 0)

  #TODO: Enter your credentail below.
  nhiss_bot.setCredential(
    id= 'kokoko1230',
    pwd= 'password2@',
    name='박근우'
  )

  #TODO: Enter researcher name(s) below.
  researchers = [
    '성기훈',
    '문여래',
    '박근우'
  ]

  nhiss_bot.setResearchers(researchers)
  nhiss_bot.login()
  nhiss_bot.selectReservationOptions()
  #TODO: Comment out when executed for real reservation.
  # nhiss_bot.apply()
  nhiss_bot.quit()
