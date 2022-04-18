def success_msg(user_name, region, target_day, research_name):
  return f"[Bot] {user_name}님 {region}지역 공단봇 예약 성공하였습니다! target day: {target_day}\n• 연구명: {research_name}"

def failure_msg(user_name, region, target_day):
  return f"[Bot] {user_name}님 {region}지역 공단봇 예약 실패하였습니다! target day: {target_day}"
