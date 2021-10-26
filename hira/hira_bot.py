import time
import requests
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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


  def init_driver(self):
    driver = webdriver.Chrome(f"./files/driver/{OS}/chromedriver_94")
    return driver


  def get_time_delta(self):
    check_time = requests.get('https://opendata.hira.or.kr/home.do').headers['Date']
    
    debug_print(check_time)
    check_time_object = datetime.strptime(check_time, format) + timedelta(hours=9)
    debug_print(check_time_object)
    debug_print(f"봇 실행 예약 시간: {TARGET_DATE}")
    delta = datetime.strptime(TARGET_DATE, "%Y-%m-%d %H:%M:%S") - check_time_object
    debug_print(delta)
    return delta


  def go_login_page(self, driver):
    driver.get('https://opendata.hira.or.kr/op/oph/selectCnfcUseAplPrsnt.do')


  def login(self, driver, wait):
    a_result = wait.until(EC.presence_of_element_located((By.ID, "login")))
    driver.find_element_by_id('loginId').send_keys(LOGIN_ID)
    driver.find_element_by_id('loginPwd').send_keys(LOGIN_PASSWORD + Keys.RETURN)


  def close_popups(self, driver):
    main = driver.window_handles
    for handle in main[1:]:
      driver.switch_to.window(handle)
      driver.close()
    driver.switch_to.window(driver.window_handles[0])

  def click_alert(self, driver):
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    driver.switch_to.alert.accept()

  def go_apply_page(self, driver, wait):
    wait.until(EC.element_to_be_clickable((By.ID, "applyBtn")))
    driver.find_element_by_id('applyBtn').click()
    self.click_alert(driver)


  def click_center(self, driver, wait, each_branch):
    wait.until(EC.element_to_be_clickable(
      (By.XPATH, f'//*[@id="cnfcPrSeatUseAplVO"]/fieldset/table[1]/thead/tr/th[{each_branch[0]}]/button')))
    driver.find_element_by_xpath(
      f'//*[@id="cnfcPrSeatUseAplVO"]/fieldset/table[1]/thead/tr/th[{each_branch[0]}]/button').click()


  def get_items(self, driver):
    items = driver.find_elements_by_xpath("//table/tbody/tr/td/span/span[not(@class='bdc_ico_add')]")
    # "//table/tbody/tr/td/span/span[not(@class='bdc_ico_ing') and not(@class='bdc_ico_done')]")
    return items


  def run_on_time(self):
  
    delta = self.get_time_delta()

    # count_down(int(delta.total_seconds()))
    # time.sleep(int(delta.total_seconds()))

    driver = self.init_driver()

    # 크롬 창 최대화
    driver.maximize_window()

    # 로그인 페이지 접속
    wait = WebDriverWait(driver, timeout=10)
    self.go_login_page(driver)

    # 로그인
    self.login(driver, wait)

    # 로그인 후 팝업 닫기
    time.sleep(1.5)
    self.close_popups(driver)
    # 신청 페이지 이동
    self.go_apply_page(driver, wait)

    # 지점 선택
    # TODO: 순서에 따라 지점을 선택해가도록 변경
    success = False
    btn_list = []
    for each_branch in branch_list:
      print(each_branch)
      # 센터명 버튼 클릭
      self.click_center(driver, wait, each_branch)
      driver.implicitly_wait(2)
      # 센터 이름이 나올때 까지 대기
      self.click_alert(driver)
      wait.until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="bdc_title"]'), each_branch[2]))
      items = self.get_items(driver)

      if not items:
        # debug_print(f"No item found for {each_branch[2]}")
        continue
      # else:
        # debug_print(f"{len(items)} item(s) found for {each_branch[2]}")

      item_list = [item.get_attribute("id") for item in items]
      debug_print(item_list)

      for each_priority in priority_list:
        debug_print(f"each_priority: {each_priority}")
        for idx in range(each_branch[4]+1, 0, -1):
          expected_btn_list = [
            f"btn_{each_branch[3]}{idx:02d}_{each_priority[0]}",
            f"btn_{each_branch[3]}{idx:02d}_{each_priority[1]}"
          ]
          if expected_btn_list[0] in item_list and expected_btn_list[1] in item_list:
            btn_list = [driver.find_element_by_id(btn) for btn in expected_btn_list]
            # btn_list = [driver.find_element_by_id(f"btn_{each_branch[3]}{idx:02d}_{each_priority[0]}"),
            #             driver.find_element_by_id(f"btn_{each_branch[3]}{idx:02d}_{each_priority[1]}")]
          else:
            continue
          debug_print(f"가능한 곳 발견! {each_branch}: {expected_btn_list}")
          driver.find_element_by_id(f"{each_branch[3]}{idx:02d}").click()
          wait.until(EC.element_to_be_clickable((By.ID, f"{each_branch[3]}{idx:02d}")))
          for btn in btn_list: btn.click()
          driver.find_element_by_id("btnNext").click()
          success = True
          time.sleep(600)
          break
        if success:
          break
      if success:
        break

    # 새로고침
    # driver.refresh()

    # 3초 후
    # time.sleep(3)

    # 드라이버 종료(크롬창 닫힘)
    # driver.quit()
    return success

  def run_until_success(self):
    # TODO: OS 에 따른 드라이버 path 를 config 파일로 이동
    driver = self.init_driver()

    # 로그인 페이지 접속
    wait = WebDriverWait(driver, timeout=10)
    self.go_login_page(driver)

    # 로그인
    self.login(driver, wait)

    # 로그인 후 팝업 닫기
    time.sleep(1.5)
    self.close_popups(driver)

    # 신청 페이지 이동
    self.go_apply_page(driver, wait)

    # 지점 선택
    # TODO: 순서에 따라 지점을 선택해가도록 변경
    success = False
    btn_list = []

    for each_branch in branch_list:
      # 센터명 버튼 클릭
      self.click_center(driver, wait, each_branch)
      # driver.implicitly_wait(2)
      # 센터 이름이 나올때 까지 대기
      wait.until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="bdc_title"]'), each_branch[2]))
      items = self.get_items(driver)

      if not items:
        # debug_print(f"No item found for {each_branch[2]}")
        continue
      # else:
        # debug_print(f"{len(items)} item(s) found for {each_branch[2]}")

      item_list = [item.get_attribute("id") for item in items]
      debug_print(item_list)

      for each_priority in priority_list:
        debug_print(f"each_priority: {each_priority}")
        for idx in range(each_branch[4]+1, 0, -1):
          debug_print(idx)
          if f"btn_{each_branch[3]}{idx:02d}_{each_priority[0]}" in item_list and f"btn_{each_branch[3]}{idx:02d}_{each_priority[1]}" in item_list:
            btn_list = [driver.find_element_by_id(f"btn_{each_branch[3]}{idx:02d}_{each_priority[0]}"),
                        driver.find_element_by_id(f"btn_{each_branch[3]}{idx:02d}_{each_priority[1]}")]
          else:
            continue
          debug_print(btn_list)
          driver.find_element_by_id(f"{each_branch[3]}{idx:02d}").click()
          wait.until(EC.element_to_be_clickable((By.ID, f"{each_branch[3]}{idx:02d}")))
          for btn in btn_list: btn.click()
          driver.find_element_by_id("btnNext").click()
          success = True
          break
        if success:
          break
      if success:
        break

    # 크롬 창 최대화
    driver.maximize_window()

    # 새로고침
    # driver.refresh()

    # 3초 후
    # time.sleep(3)

    # 드라이버 종료(크롬창 닫힘)
    driver.quit()
    return success
