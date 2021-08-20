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