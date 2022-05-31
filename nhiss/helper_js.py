from time import sleep
from selenium.common.exceptions import JavascriptException, WebDriverException
from nhiss.tasks.error import ForceQuit

time_to_wait = 0.5

def get_target_index_js(driver, target_day):
  try:
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
  except:
    sleep(time_to_wait)
    return get_target_index_js(driver, target_day)

def is_available_click_check(driver, target_index):
  return driver.execute_script("""
    var target_index =  arguments[0]
    return window[2].CHK_Validation(target_index, 1)
  """, target_index)

def select_target_day_with_index_js(driver, target_index):
  driver.execute_script("""
    var target_index = arguments[0]

    window[2].WShtAC_1.SetGridCellText("CHK", target_index, 1)
    window[2].BTN_SELECT_Click()
  """, target_index)

def select_target_day_with_index_js_in_seoul(driver, target_index):
  driver.execute_script("""
    var target_index = arguments[0]
    var col_name = arguments[1]

    window[2].WShtAC_1.SetGridCellText('AM_CHK', target_index, 1)
    window[2].WShtAC_1.SetGridCellText('PM_CHK', target_index, 1)
    window[2].BTN_SELECT_Click()
  """, target_index)

def select_visitor_js(driver, visiter):
  try:
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
      } else {
        throw new Error()
      }
    """, visiter)
  except:
    raise ForceQuit('해당 방문자 없음')

def get_popup_message(driver):
    popup = driver.find_element_by_id('popup_message')
    return popup.text

def get_alert_text(driver):
  result = driver.switch_to_alert()
  return result.text

def get_remark_status(driver, target_index):
    return driver.execute_script("""
      var target_index =  arguments[0]
      var text = window[2].WShtAC_1.GetGridCellText("REMARK", target_index)
      return text
    """, target_index)
