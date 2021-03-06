import time
import requests
from typing import List
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoAlertPresentException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from nhiss.tasks.error import ForceQuit
from nhiss.helper_js import (
  get_popup_message,
  get_remark_status,
  get_target_index_js,
  is_available_click_check,
  select_target_day_with_index_js,
  select_target_day_with_index_js_in_seoul,
  select_visitor_js
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
    chrome_options = webdriver.ChromeOptions()

    if headless:
      chrome_options.add_argument("--headless")
      chrome_options.add_argument("--no-sandbox")
      
    chrome_options.add_experimental_option("excludeSwitches", ['enable-logging'])
    chrome_options.add_argument("--disable-gpu")
    self.driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        chrome_options=chrome_options
    )
    print("driver check 완료")

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
      second=second
    )

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
      while time_to_wait_sec > 0:
        print('left time seconds: ', time_to_wait_sec, flush=True)
        time.sleep(time_to_wait_sec if time_to_wait_sec < 10 else 10)
        time_to_wait_sec -= 10
    except ValueError:
      print('[HiraBot][TargetTimeError] Target Time must be in the future', flush=True)
      exit(1)
    print('[HiraBot] Time to activate HiraBot!', flush=True)

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
    try:
      self.driver.get('https://nhiss.nhis.or.kr/bd/ay/bdaya003iv.do')
      self.wait = WebDriverWait(self.driver, timeout=10)
    except:
      raise Exception('Chrome 드라이버 로딩 에러')

    # 로그인
    # TODO: 계정 정보 config 파일로 이동
    try:
      username_field = self.driver.find_element_by_id('j_username')
      password_field = self.driver.find_element_by_id('j_password')

      if username_field is None:
        raise Exception('페이지 로딩 에러')

      username_field.send_keys(self.user_id)
      password_field.send_keys(self.user_pwd)

      # Cannot construct KeyEvent from non-typeable key 문제 해결
      action = ActionChains(self.driver)
      action.key_down(Keys.RETURN).perform()

      self.driver.get('https://nhiss.nhis.or.kr/bd/ay/bdaya001iv.do')

    # 로그인 후 팝업 닫기
      main = self.driver.window_handles 
      for handle in main: 
        if handle != main[0]: 
          self.driver.switch_to.window(handle) 
          self.driver.close() 
      self.driver.switch_to.window(self.driver.window_handles[0])

    except WebDriverException as err:
      raise ForceQuit('아이디, 패스워드 자동 입력 에러')

  
  def selectReservationOptions(self, region):
    try:
      if region == 'seoul':
        self.__go_to_seoul_register()
        self.__select_research_number()
        self.__select_visitor()
      else:
        self.__go_to_general_register()
        self.__select_research_number()
        self.__select_research_center()
        self.__select_visitor()
    except ForceQuit as err:
      raise ForceQuit(err)

  def selectReservationDate(self, target_day, is_seoul):
    return self.__select_reservation_date(target_day, is_seoul)

  # 연구명 가져오기
  def getResearchName(self):
    try:
      research_name = self.driver.find_element_by_id("ods_WSF_1_insert_RSCH_NM").get_attribute("value")

      return research_name
    except Exception as err:
      print(err)
      raise Exception("연구명 Fetch Error")

  # 신청
  def clickApplyButtonAndCheckSuccess(self):
    try:
      self.driver.find_element_by_xpath('//*[@id="ods_WSF_1_insert_BTN_APPLY"]').click()
      WebDriverWait(self.driver, 3).until(EC.alert_is_present())  # alert 창이 뜰 때까지 기다려야 함(2022-03-27 성공 시에 뜸)
      alert_text = self.driver.switch_to.alert.text
      return True if "예약이 완료" in alert_text else False
    except Exception as e:
      popup_text= get_popup_message(self.driver)
      if popup_text:
          raise Exception(f'연구 신청 Error: *팝업 메시지* {popup_text}')
      raise Exception(f'연구 신청 Error: {e}')

  def refresh(self):
    self.driver.refresh()
  
  def quit(self):
    self.driver.quit()

  # 연구과제관리번호 선택
  def __select_research_number(self):
    try:
      WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, "WSF_1_insert_APLY_MGMT_NO_label"))).click()
      WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, self.research_number_xpath))).click()
    except:
      raise ForceQuit('해당 연구과제가 존재하지 않습니다.')

  # 예약신청(일반) 메뉴로 이동
  def __go_to_general_register(self):
    self.driver.get('https://nhiss.nhis.or.kr/bd/af/bdafa002lv.do')
    time.sleep(1)
    WebDriverWait(self.driver, 3).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "cmsView")))

  # 예약신청(서울) 메뉴로 이동
  def __go_to_seoul_register(self):
    self.driver.get('https://nhiss.nhis.or.kr/bd/af/bdafa002Slv.do')
    time.sleep(1)
    li_length_of_pc_tab = len(self.driver.find_elements_by_xpath("//ul[@id='PC_tab1']/li"))
    if li_length_of_pc_tab == 3:
      WebDriverWait(self.driver, 3).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "cmsView")))
    else:
      raise ForceQuit('서울이 선택지에 없습니다.')

  # 센터구분
  def __select_research_center(self):
    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, "WSF_1_insert_ZN_CEN_CD_label"))).click()
    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, self.research_center_xpath))).click()

  # 예약일자 선택
  def __select_reservation_date(self, target_day, is_seoul):
    # TODO: 에러 처리 구체화 (중복 신청 or 1주일에 3일만 신청 가능 조건)
    try:
      if target_day is None:
        raise Exception('예약 희망 날짜를 입력하지 않았습니다.')

      WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.ID, "ods_WSF_1_insert_BTN_DT"))).click()

      # 예약일자 선택창 대기
      time.sleep(1.5)
      self.driver.switch_to.default_content()


      time.sleep(0.3) # target_index 받아오는 시간 대기
      target_index = get_target_index_js(self.driver, target_day)
      
      if target_index == -1:
        raise Exception(f'해당 날짜({target_day})에 맞는 좌석을 선택할 수 없습니다.')
      else:
        text = get_remark_status(self.driver, target_index)
        if text == '예약불가' or text == '예약완료':
          raise Exception(f'해당 날짜({target_day})는 *{text}* 상태입니다')
        else:
          if is_available_click_check(self.driver, target_index):
            if is_seoul:
              select_target_day_with_index_js_in_seoul(self.driver, target_index) 
            else:
              select_target_day_with_index_js(self.driver, target_index)
            self.driver.switch_to.frame('cmsView')
          else:
            # 선택 일자 클릭 불가능 시 나오는 팝업의 text는 find_by_element로 찾을 수 없음.
            # script로 msg를 삽입하는 형태이기 때문일 것으로 추정.
            raise Exception('센터 예약은 1주 최대 3일 예약가능합니다.')
    except Exception as err:
      raise Exception(f'{err}')

  # 방문객 선택
  def __select_visitor(self):
    self.driver.find_element_by_id("ods_WSF_1_insert_BTN_VISTM").click() 

    # 방문자 선택창 대기
    time.sleep(2)
    self.driver.switch_to.default_content()
    
    for visiter in self.visiters:
      select_visitor_js(self.driver, visiter)

    time.sleep(0.5)
    self.driver.execute_script("window[2].BTN_SELECT_Click()")
    self.driver.switch_to.frame('cmsView')
