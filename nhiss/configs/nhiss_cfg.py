OS = '' # Nhiss Bot이 실행되는 OS
RESEARCH_NUMBER_XPATH = '/html/body/div[5]/div/table/tbody/tr[2]/td[2]' #TODO: 연구과제관리번호 xpath 등록. 기본값: 첫번째 연구과제

# RESEARCH_CENTER_XPATH = '/html/body/div[6]/div/table/tbody/tr[2]/td[2]' #빅데이터 분석센터 (서울) 서울은 full xpath 사용
RESEARCH_CENTER_XPATH = '/html/body/div[6]/div/table/tbody/tr[4]/td[2]' #경인지역본부 분석센터 xpath
# RESEARCH_CENTER_XPATH = '/html/body/div[6]/div/table/tbody/tr[6]/td[2]' #광주지역본부 분석센터 xpath
CREDENTIAL_ID = ''                                   #TODO: NHISS 접속 유저 정보 등록.
CREDENTIAL_PWD = '!'
CREDENTIAL_NAME = ''
RESEARCH_VISITER_LIST = ['']                #TODO: 방문자 이름 등록.
NOTIFICATION_FLAG = True
REGISTER_AM = True                              # 서울 지역 신청 시 오전, 오후 시간대에 등록 (일반은 영향 x)
