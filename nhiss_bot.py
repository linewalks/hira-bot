import time
import requests
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# # 지점 선택
# # TODO: 순서에 따라 지점을 선택해가도록 변경
# success = False
# for each_branch in branch_list:
#   wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="cnfcPrSeatUseAplVO"]/fieldset/table[1]/thead/tr/th[{each_branch[0]}]/button')))
  
#   driver.find_element_by_xpath(f'//*[@id="cnfcPrSeatUseAplVO"]/fieldset/table[1]/thead/tr/th[{each_branch[0]}]/button').click()
#   driver.implicitly_wait(2)
  
#   wait.until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="bdc_title"]'), each_branch[2]))
#   #wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/section/section[3]/div[1]/form/fieldset/table[2]")))

#   items = driver.find_elements_by_xpath("//table/tbody/tr/td/span/span[not(@class='bdc_ico_ing') and not(@class='bdc_ico_done')]")
#   if not items:
#     continue
  
#   btn_list = []
#   temp_key = None

#   for each in items:
#     each_key = each.get_attribute("id").split("_")[1]
#     if temp_key != each_key:
#       temp_key = each_key
#       btn_list = [each]
#     else:
#       btn_list.append(each)
#       driver.find_element_by_id(each_key).click()
#       wait.until(EC.element_to_be_clickable((By.ID, each.get_attribute("id"))))
#       for btn in btn_list: btn.click()
#       driver.find_element_by_id("btnNext").click()
#       success = True
#       break
  
#   if success:
#     break


class NhissBot:
  
  def __init__(self, 
      os: str, 
      research_center_xpath: str,
      research_number_xpath: str):
    self.os = os
    # self.driver = webdriver.Chrome(f'./files/driver/{self.os}/chromedriver')
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
    print(f'[HiraBot] Target Time (KST) {target_datetime}')
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
    time.sleep(time_to_wait_sec)
    print('[HiraBot] Time to activate HiraBot!')
    self.driver = webdriver.Chrome(f'./files/driver/{self.os}/chromedriver')

  def setCredential(self, id, pwd, name):
    self.user_id = id
    self.user_pwd = pwd
    self.user_name = name
  
  def login(self):
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
    self.__goToMyService()
    time.sleep(1)

    self.__select_research_number()
    self.__select_research_center()
    self.__select_reservation_date()
    self.__select_visitor()
  

  def apply(self):
    time.sleep(1)
    # Switch to default frame from cmsView
    self.driver.switch_to.frame("cmsView")
    self.driver.find_element_by_xpath('//*[@id="ods_WSF_1_insert_BTN_APPLY"]').click()

  def refresh(self):
    self.driver.refresh()
  

  def quit(self, time_s=5):
    time.sleep(time_s)
    self.driver.quit()


  def __select_research_number(self):
    # 연구과제관리번호 선택
    # tr[순서 + 1]
    self.driver.find_element_by_id("WSF_1_insert_APLY_MGMT_NO_label").click()
    self.driver.find_element_by_xpath(self.research_number_xpath).click()
    

  # MY서비스 - 분석센터이용 페이지로 이동
  def __goToMyService(self):
    self.driver.get('https://nhiss.nhis.or.kr/bd/af/bdafa002lv.do')
    time.sleep(1)
    self.driver.switch_to.frame("cmsView")

  # 센터구분
  def __select_research_center(self):
    self.driver.find_element_by_id("WSF_1_insert_ZN_CEN_CD_label").click()

    # driver.find_element_by_xpath('/html/body/div[6]/div/table/tbody/tr[2]/td[2]').click() # 서울
    self.driver.find_element_by_xpath(self.research_center_xpath).click() # 광주
    # element = driver.find_element_by_xpath('//*[@id="a"]/table/tbody/tr[2]/td[2]') # 서울
    # driver.execute_script(("arguments[0].click();", element))
    # driver.find_element_by_xpath('//*[@id="a"]/table/tbody/tr[4]/td[2]').click() # 수원
    
  
  def __select_reservation_date(self):
    # 예약일자 선택
    # time.sleep(1)
    self.driver.find_element_by_id("ods_WSF_1_insert_BTN_DT").click()
    time.sleep(1)
    # Switch to default frame from cmsView
    self.driver.switch_to.default_content()

    # Get target day which is two weeks later than today.
    target_day = (datetime.now() + timedelta(weeks=2)).strftime("%Y-%m-%d")
    print(target_day)


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
      window[2].BTN_SELECT_Click()
    """, self.user_name)


if __name__ == "__main__":
  nhiss_bot = NhissBot(
  os='linux',
  research_center_xpath= '//*[@id="a"]/table/tbody/tr[6]/td[2]',
  research_number_xpath= '//*[@id="a"]/table/tbody/tr[3]/td[2]'
  )
  nhiss_bot.wait_until_kst(2021, 7, 7, 16, 45, 55)
  nhiss_bot.setCredential(
    id= 'kokoko1230',
    pwd= 'password2@',
    name='박근우'
  )

  nhiss_bot.login()

  nhiss_bot.selectReservationOptions()
  # nhiss_bot.apply()
  # nhiss_bot.quit()
