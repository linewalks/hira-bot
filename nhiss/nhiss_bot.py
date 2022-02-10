import chromedriver_autoinstaller
import os
import time
import requests
from typing import List
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.helper import count_down, send_message
from nhiss.helper_js import (
  get_target_index_js,
  select_target_day_with_index_js,
  select_visitor_js
)
from nhiss.configs.nhiss_cfg import (
  OS,
  RESEARCH_NUMBER_XPATH,
  RESEARCH_CENTER_XPATH,
  CREDENTIAL_ID,
  CREDENTIAL_PWD,
  CREDENTIAL_NAME,
  RESEARCH_VISITER_LIST
)

RESEARCH_CENTER_XPATH_MAP = {
  '/html/body/div[6]/div/table/tbody/tr[1]/td[2]': '원주 본부',
  '/html/body/div[6]/div/table/tbody/tr[2]/td[2]': '명동',
  '/html/body/div[6]/div/table/tbody/tr[3]/td[2]': '명동(리서치)',
  '/html/body/div[6]/div/table/tbody/tr[4]/td[2]': '경인',
  '/html/body/div[6]/div/table/tbody/tr[5]/td[2]': '대전',
  '/html/body/div[6]/div/table/tbody/tr[6]/td[2]': '광주',
  '/html/body/div[6]/div/table/tbody/tr[7]/td[2]': '대구',
  '/html/body/div[6]/div/table/tbody/tr[8]/td[2]': '부산',
  '/html/body/div[6]/div/table/tbody/tr[9]/td[2]': '전주',
  '/html/body/div[6]/div/table/tbody/tr[10]/td[2]': '청주',
  '/html/body/div[6]/div/table/tbody/tr[11]/td[2]': '일산병원',
}

class NhissBot:
  
  def __init__(self, operating_system: str, headless: bool=False):
    self.operating_system = operating_system

    driver_path = os.path.join(os.getcwd(), "files", "driver", self.operating_system)
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split(".")[0]
    chromedriver_autoinstaller.install(path=driver_path)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    self.driver = webdriver.Chrome(
        executable_path=f'./files/driver/{self.operating_system}/{chrome_ver}/chromedriver',
        chrome_options=chrome_options
    )


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
    time_to_wait_sec = float(delta.total_seconds())
    try:
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
    # 로그인 페이지 접속
    self.wait = WebDriverWait(self.driver, timeout=1)
    self.driver.get('https://nhiss.nhis.or.kr/bd/ay/bdaya003iv.do')
    # 로그인
    # TODO: 계정 정보 config 파일로 이동
    self.driver.find_element_by_id('j_username').send_keys(self.user_id)
    self.driver.find_element_by_id('j_password').send_keys(self.user_pwd + Keys.RETURN)
    # 로그인 후 팝업 닫기
    main = self.driver.window_handles 
    for handle in main: 
      if handle != main[0]: 
        self.driver.switch_to.window(handle) 
        self.driver.close() 
    self.driver.switch_to.window(self.driver.window_handles[0])
  
  def selectReservationOptions(self):
    self.__go_to_my_service()
    self.__select_research_number()
    self.__select_research_center()
    self.__select_visitor()
  

  def selectReservationDate(self, target_day = None):
    return self.__select_reservation_date(target_day)
  

  # 신청
  def apply(self):
    WebDriverWait(self.driver, 3).until(EC.frame_to_be_available_and_switch_to_it("cmsView"))
    self.driver.find_element_by_xpath('//*[@id="ods_WSF_1_insert_BTN_APPLY"]').click()

  def refresh(self):
    self.driver.refresh()
  
  def quit(self):
    self.driver.quit()

  # 연구과제관리번호 선택
  def __select_research_number(self):
    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, "WSF_1_insert_APLY_MGMT_NO_label"))).click()
    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, self.research_number_xpath))).click()


  # MY서비스 - 분석센터이용 페이지로 이동
  def __go_to_my_service(self):
    self.driver.get('https://nhiss.nhis.or.kr/bd/af/bdafa002lv.do')
    time.sleep(1)
    WebDriverWait(self.driver, 3).until(EC.frame_to_be_available_and_switch_to_it("cmsView"))

  # 센터구분
  def __select_research_center(self):
    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, "WSF_1_insert_ZN_CEN_CD_label"))).click()
    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, self.research_center_xpath))).click()

  # 예약일자 선택
  def __select_reservation_date(self, target_day = None):
    WebDriverWait(self.driver, 3).until(EC.frame_to_be_available_and_switch_to_it("cmsView"))
    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, "ods_WSF_1_insert_BTN_DT"))).click()
    time.sleep(1)
    self.driver.switch_to.default_content()


    if target_day is None:
      # Get target day which is two weeks later than today.
      #TODO: comment out line below. 
      target_day = (datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%d")

    
    target_index = get_target_index_js(self.driver, target_day)
    if target_index != -1:
      select_target_day_with_index_js(self.driver, target_index)
      return True
    else:
      return False


  def __select_visitor(self):
    self.driver.find_element_by_id("ods_WSF_1_insert_BTN_VISTM").click()  
    time.sleep(1)
    self.driver.switch_to.default_content()
    for visiter in self.visiters:
      select_visitor_js(self.driver, visiter)
    self.driver.execute_script("window[2].BTN_SELECT_Click()")
