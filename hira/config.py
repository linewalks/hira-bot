# (
#   테이블에서 센터 index(본원기준 2부터 시작), 
#   브랜치 넘버, 
#   센터 지역 이름, 
#   hira+브랜치 넘버,
#   센터 예약 자리 수
# )
branch_list = [
  (3, '01', '서울', 'hira01', 13),
  (8, '06', '수원', 'hira06', 2),
  (11, '10', '인천', 'hira10', 2),
  (7, '05', '대전', 'hira05', 2),
  (6, '04', '광주', 'hira04', 2)
]

# YYYYMMDD
priority_list = [
  ('20220211', '20220212'),
]

OS = "windows" # macos, linux, windows
TARGET_DATE = "2022-02-10 14:29:00" # Example Data Format: 2021-12-29 19:01:00
### 로그인 정보
LOGIN_ID = "jindex2411"
LOGIN_PASSWORD = "q1w2e3r4t5!"
