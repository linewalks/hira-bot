import time
import requests
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

branch_list = [
  (3,'01','서울'),
  (8,'06','수원'),
  (11,'10','인천'),
  (7,'05','대전'),
  (6,'04','광주')
]

format = "%a, %d %b %Y %H:%M:%S %Z"

check_time = requests.get('https://opendata.hira.or.kr/home.do').headers['Date']
check_time_object = datetime.strptime(check_time, format) + timedelta(hours=9)
delta = datetime.strptime("2021-03-30 16:01:00", "%Y-%m-%d %H:%M:%S") - check_time_object
# time.sleep(float(delta.total_seconds()))
# date = requests.get('https://opendata.hira.or.kr/home.do').headers['Date']
# aa = datetime.strptime(date, format) + timedelta(hours=9)
# print (aa)

# TODO: OS 에 따른 드라이버 path 를 config 파일로 이동
driver = webdriver.Chrome('./files/driver/macos/chromedriver')

# 로그인 페이지 접속
wait = WebDriverWait(driver, timeout=1)
driver.get('https://opendata.hira.or.kr/op/oph/selectCnfcUseAplPrsnt.do')

# 로그인
# TODO: 계정 정보 config 파일로 이동  
a_result = wait.until(EC.presence_of_element_located((By.ID, "login")))
driver.find_element_by_id('loginId').send_keys('linewalks3')
driver.find_element_by_id('loginPwd').send_keys('linewalks1!' + Keys.RETURN)

# 로그인 후 팝업 닫기
time.sleep(1)
main = driver.window_handles 
for handle in main: 
  if handle != main[0]: 
    driver.switch_to.window(handle) 
    driver.close() 
driver.switch_to.window(driver.window_handles[0])

# 신청 페이지 이동
wait.until(EC.element_to_be_clickable((By.ID, "applyBtn")))
driver.find_element_by_id('applyBtn').click()

# 지점 선택
# TODO: 순서에 따라 지점을 선택해가도록 변경
success = False
for each_branch in branch_list:
  wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="cnfcPrSeatUseAplVO"]/fieldset/table[1]/thead/tr/th[{each_branch[0]}]/button')))
  
  driver.find_element_by_xpath(f'//*[@id="cnfcPrSeatUseAplVO"]/fieldset/table[1]/thead/tr/th[{each_branch[0]}]/button').click()
  driver.implicitly_wait(2)
  
  wait.until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="bdc_title"]'), each_branch[2]))
  #wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/section/section[3]/div[1]/form/fieldset/table[2]")))

  items = driver.find_elements_by_xpath("//table/tbody/tr/td/span/span[not(@class='bdc_ico_ing') and not(@class='bdc_ico_done')]")
  if not items:
    continue
  
  btn_list = []
  temp_key = None

  for each in items:
    each_key = each.get_attribute("id").split("_")[1]
    if temp_key != each_key:
      temp_key = each_key
      btn_list = [each]
    else:
      btn_list.append(each)
      driver.find_element_by_id(each_key).click()
      wait.until(EC.element_to_be_clickable((By.ID, each.get_attribute("id"))))
      for btn in btn_list: btn.click()
      driver.find_element_by_id("btnNext").click()
      success = True
      break
  
  if success:
    break

# 크롬 창 최대화
driver.maximize_window()

# 새로고침
# driver.refresh()

# 3초 후 
time.sleep(3)
print('Test Completed')

# 드라이버 종료(크롬창 닫힘)
# driver.quit()
