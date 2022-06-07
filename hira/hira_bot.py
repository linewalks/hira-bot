import chromedriver_autoinstaller
import os
import time
import requests
from datetime import timedelta, datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from hira.helper import debug_print
from utils.helper import count_down
from hira.config import (
  branch_list,
  priority_list,
  OS,
  TARGET_DATE,
  LOGIN_ID,
  LOGIN_PASSWORD
)

format = "%a, %d %b %Y %H:%M:%S %Z"

class HiraBot():
  def __init__(self):
    self.driver = None

  def init_driver(self):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ['enable-logging'])
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        chrome_options=chrome_options
    )
    self.driver = driver


  def get_time_delta(self):
    if TARGET_DATE == "now":
      return 0
    check_time = requests.get('https://opendata.hira.or.kr/home.do').headers['Date']
    
    debug_print(check_time)
    check_time_object = datetime.strptime(check_time, format) + timedelta(hours=9)
    debug_print(check_time_object)
    debug_print(f"봇 실행 예약 시간: {TARGET_DATE}")
    delta = datetime.strptime(TARGET_DATE, "%Y-%m-%d %H:%M:%S") - check_time_object
    debug_print(delta)
    return delta


  def go_login_page(self):
    self.driver.get('https://opendata.hira.or.kr/op/oph/selectCnfcUseAplPrsnt.do')


  def login(self, wait):
    a_result = wait.until(EC.presence_of_element_located((By.ID, "login")))
    self.driver.find_element_by_id('loginId').send_keys(LOGIN_ID)
    self.driver.find_element_by_id('loginPwd').send_keys(LOGIN_PASSWORD + Keys.RETURN)


  def close_popups(self):
    main = self.driver.window_handles
    for handle in main[1:]:
      self.driver.switch_to.window(handle)
      self.driver.close()
    self.driver.switch_to.window(self.driver.window_handles[0])

  def click_alert(self, ignore=False):
    try:
      WebDriverWait(self.driver, 3).until(EC.alert_is_present())
      self.driver.switch_to.alert.accept()
    except Exception as err:
      # alert이 신청 상황에 따라 발생 할수도 없을 수도 있기 때문에 raise 처리 X
      print("There is no alert")
      if not ignore:
        raise err


  def go_apply_page(self, wait):
    wait.until(EC.element_to_be_clickable((By.ID, "applyBtn")))
    self.driver.find_element_by_id('applyBtn').click()
    self.click_alert()


  def click_center(self, wait, each_branch):
    wait.until(EC.element_to_be_clickable(
      (By.XPATH, f'//*[@id="cnfcPrSeatUseAplVO"]/fieldset/table[1]/thead/tr/th[{each_branch[0]}]/button')))
    self.driver.find_element_by_xpath(
        f'//*[@id="cnfcPrSeatUseAplVO"]/fieldset/table[1]/thead/tr/th[{each_branch[0]}]/button'
    ).click()


  def get_items(self):
    items = self.driver.find_elements_by_xpath("//table/tbody/tr/td/span/span[not(@class='bdc_ico_add')]")
    return items


  def run_on_time(self):
  
    delta = self.get_time_delta()
    time.sleep(int(delta.total_seconds()))

    return self.run()

  def run(self):
    self.init_driver()

    # 크롬 창 최대화
    self.driver.maximize_window()

    # 로그인 페이지 접속
    wait = WebDriverWait(self.driver, timeout=10)
    self.go_login_page()

    # 로그인
    self.login(wait)

    # 로그인 후 팝업 닫기
    time.sleep(1.5)
    self.close_popups()
    # 신청 페이지 이동
    self.go_apply_page(wait)

    # 기존 이용 신청이 있는 경우에 "이용신청 클릭 시" 신청중으로 되돌아 갑니다. 얼럿이 추가로 발생
    self.click_alert(ignore=True)

    # 지점 선택
    # TODO: 순서에 따라 지점을 선택해가도록 변경
    success = False
    btn_list = []
    for each_branch in branch_list:
      debug_print(f"{each_branch[2]} 검색중..")
      # 센터명 버튼 클릭
      self.click_center(wait, each_branch)
      self.driver.implicitly_wait(2)
      # 센터 이름이 나올때 까지 대기
      self.click_alert()
      wait.until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="bdc_title"]'), each_branch[2]))
      items = self.get_items()

      if not items:
        continue

      item_list = [item.get_attribute("id") for item in items]
      pretty_items = [item[-8:-1] for item in item_list]
      debug_print(f"가능한 날짜: {pretty_items}")

      for each_priority in priority_list:
        for idx in range(each_branch[4]+1, 0, -1):
          expected_btn_list = [
            f"btn_{each_branch[3]}{idx:02d}_{each_priority[0]}",
            f"btn_{each_branch[3]}{idx:02d}_{each_priority[1]}"
          ]
          if expected_btn_list[0] in item_list and expected_btn_list[1] in item_list:
            btn_list = [self.driver.find_element_by_id(btn) for btn in expected_btn_list]
          else:
            continue
          debug_print(f"가능한 곳 발견! {each_branch}: {expected_btn_list}")
          self.driver.find_element_by_id(f"{each_branch[3]}{idx:02d}").click()
          wait.until(EC.element_to_be_clickable((By.ID, f"{each_branch[3]}{idx:02d}")))
          for btn in btn_list: btn.click()
          self.driver.find_element_by_id("btnNext").click()
          success = True
          break
        if success:
          break
      if success:
        break

    return success
