## NHISS Bot Manual (국민건강보험 분석센터이용 신청 봇)

### Setup

1. 파이썬 가상환경을 생성합니다. (Python Version 3.8.x)
2. 소스코드를 가져옵니다.
```
git clone https://yona.linewalks.com/TaskForce/hira-bot
```
3. 생성된 가상환경에서 아래의 명령어로 파이썬 패키지들을 설치합니다.
```
pip3 install -r requirements.txt
```
4. chromedriver 를 설치합니다.
    - https://chromedriver.chromium.org/downloads
    - 실행하게될 컴퓨터의 OS와 설치된 Chrome brower 버젼과 호환되는 chromedriver를 설치해야합니다.
    - 다운받은 `files/driver/{OS}/`에 저장해줍니다.
        - ex) files/driver/linux/chromedriver.exe

### Configuration 설정
- `/files/configs/nhiss_cfg.py`로 접근한다.
- 해당 `nhiss_cfg.py`에서 아래의 설정값들을 입력해준다.
    - `OS`: Nhiss Bot을 실행시키는 컴퓨터의 운영체제 (linux, macos, window중 택 1)
        - 사용하고자 하는 OS, Chrome Webdriver Version, 그리고 실제 사용되는 Chrome Version가 일치해야합니다. 이 부분 문제시 알려주세요.
    - `RESEARCH_NUMBER_XPATH`: [아래 Xpath 가져오기](https://yona.linewalks.com/TaskForce/hira-bot/issue/5#yb-header-xpath-%EA%B0%80%EC%A0%B8%EC%98%A4%EA%B8%B0)를 참고하여 원하는 연구과제관리번호 Xpath를 입력.
    - `RESEARCH_CENTER_XPATH`: [아래 Xpath 가져오기](https://yona.linewalks.com/TaskForce/hira-bot/issue/5#yb-header-xpath-%EA%B0%80%EC%A0%B8%EC%98%A4%EA%B8%B0)를 참고하여 원하는 분석센터 Xpath를 입력.
    - `CREDENTIAL_ID`: NHISS 접속 ID.
    - `CREDENTIAL_PWD`: NHISS 접속 비밀번호.
    - `CREDENTIAL_NAME`: NHISS 접속 계정 이름.
    - `RESEARCH_VISITER_LIST`: 방문자 이름 리스트.
- `/nhiss_bot.py`에서 `if __name__ == "__main__":`(아래 참고) 아래에 있는 코드에서 Nhiss bot 실행 시간을 설정
```python
nhiss_bot.wait_until_kst(2021, 7, 8, 11, 27, 40) #year #month #day #hour #minute #second
```
> 실행 시간을 과거의 시간으로 설정해두면 아래와 같은 에러메시지와 함께 실행되지 않습니다.
```
[HiraBot] Running on pid 43576
[HiraBot] Target  Time (KST): 2021-07-08 11:27:40             
[HiraBot] Current Time (GMT): 2021-07-08 19:23:10
[HiraBot] Current Time (KST): 2021-07-09 04:23:10
[HiraBot] Waiting for: -60930.0s                      
[HiraBot][TargetTimeError] Target Time must be in the future
```
### 실행
- 아래의 명렁어를 실행합니다.
```shell
sh bin/run.sh
```


### 로그 보기
- Nhiss-bot 실행 중 발생하는 로그는 nohup.out에서 확인가능.

### Xpath 가져오기
> 아래는 연구과제관리번호 선택란에서 NHIS-2020-1-211의 Xpath를 가져오는 화면입니다.
![스크린샷 2021-07-08 오후 1.53.20.png](/files/8316) 
