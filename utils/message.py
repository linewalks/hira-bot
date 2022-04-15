def convert_target_day(target_day, is_register_am):
  return target_day + '(오전)' if is_register_am else '(오후)'

def success_msg(user_name, region, target_day, research_name):
  return f"[Bot] {user_name}님 {region}지역 공단봇 예약 성공하였습니다! target day: {target_day}\n• 연구명: {research_name}"

def failure_msg(user_name, region, target_day):
  return f"[Bot] {user_name}님 {region}지역 공단봇 예약 실패하였습니다! target day: {target_day}"