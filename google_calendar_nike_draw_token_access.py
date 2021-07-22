import requests
from bs4 import BeautifulSoup
import re

import datetime
########### 구글 인증 및 토큰 가져오기 #############
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# 구글 캘린더 API 서비스 객체 생성
from googleapiclient.discovery import build


url = "https://www.nike.com/kr/launch/?type=upcoming&activeDate=date-filter:AFTER_DATE"
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Accept-Language":"ko-KR,ko"
    }

res = requests.get(url, headers=headers)
res.raise_for_status()
soup = BeautifulSoup(res.text, "lxml")

item_addr = "launch-list-item item-imgwrap pb2-sm va-sm-t ncss-col-sm-12 ncss-col-md-6 ncss-col-lg-4 pb4-md prl0-sm prl2-md ncss-col-sm-6 ncss-col-lg-3 pb4-md prl2-md pl0-md pr1-md d-sm-h d-md-ib upcomingItem"
nike_items = soup.find_all("li", attrs={"class":item_addr})

# 구글 클라우드 콘솔에서 다운받은 OAuth 2.0 클라이언트 파일경로
creds_filename = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# 파일에 담긴 인증 정보로 구글 서버에 인증하기
# 새 창이 열리면서 구글 로그인 및 정보 제공 동의 후 최종 인증이 완료됩니다.
creds = None
if os.path.exists('token.json'):    # 암호 토큰의 인증정보를 가져온다.
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:    # 인증정보의 유효성 체크
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        flow = InstalledAppFlow.from_client_secrets_file(creds_filename, SCOPES)
    else:   # 인증정보 유효하지 않다면 웹에 연결하여 인증 받는다.
        flow = InstalledAppFlow.from_client_secrets_file(creds_filename, SCOPES)
        creds = flow.run_local_server(port=0)
    # creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:  # 받은 인증정보를 토큰으로 저장한다.
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)

Nike_calendarId = "trel0u8qfj1l7oa0r3qrqbj7d0@group.calendar.google.com"    # 나이키 캘린더 ID

# 구글캘린더에 이벤트 추가
def google_calendar_insert_event(draw_name, event_start, event_end):
    event = {
        'summary': 'Nike Draw', # 일정 제목
        'description': draw_name, # 일정 설명
        'start': { # 시작 날짜
            'dateTime': event_start, 
            'timeZone': 'Asia/Seoul',
        },
        'end': { # 종료 날짜
            'dateTime': event_end, 
            'timeZone': 'Asia/Seoul',
        },
        'reminders': { # 알림 설정
            'useDefault': False,
            'overrides': [
                # {'method': 'email', 'minutes': 24 * 60}, # 24 * 60분 = 하루 전 알림
                {'method': 'popup', 'minutes': 0}, # 10분 전 알림
            ],
        }
    }
    # # calendarId : 캘린더 ID. primary이 기본 값입니다.
    event = service.events().insert(calendarId=Nike_calendarId, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

# 구글 캘린더의 같은 일자 같은 이름의 이벤트 있는지 확인
def google_calendar_select(time_min, time_max, draw_name):
    time_min = time_min + '+09:00'
    time_max = time_max + '+09:00'
    
    events_result = service.events().list(calendarId = Nike_calendarId,
                                      timeMin = time_min,
                                      timeMax = time_max,
                                      maxResults = 5,
                                      singleEvents = True,
                                      orderBy = 'startTime'
                                     ).execute()
    # print(events_result['items'])
    print("===================")
    # print("====={}=====".format(draw_name))
    for item in events_result['items']:
        # print(item['summary'])
        # print(item['description'])
        # print(item['start']['dateTime'])
        if item['description'].strip() == draw_name.strip():
            print("False")
            print("===================")
            return False
    print("===================")
    print(draw_name)
    print("True")
    return True

my_year = datetime.date.today().year    # 올해
my_month = datetime.date.today().month  # 이달

# 나이키 드로우 페이지의 정보를 긁어온다.
for nike_item in nike_items:
    month = nike_item.find("p", attrs={"class":"headline-4"}).get_text()    # 이벤트 월
    day = nike_item.find("p", attrs={"class":"headline-1"}).get_text()      # 이벤트 일
    draw = nike_item.find("div", attrs={"class":"ncss-row caption"})
    if draw.find("h3",attrs={"class":"headline-5"}):
        draw_time = draw.find("h3",attrs={"class":"headline-5"}).get_text() # 이벤트 시간
    
        p = re.compile("응모 시작$")
        m = p.search(draw_time)
        
        draw_name = draw.find("h6",attrs={"class":"headline-3"}).get_text() # 이벤트 이름

        if m:   # 응모 시작이라는 글이 있으면 캘린더 추가 시작
            if int(month.split('월')[0]) < int(my_month):   # 이벤트 월이 현재 월 보다 작으면 년도를 1 더함
                my_year += 1
            event_start = "{}-{}-{}T{}:00".format(my_year,month.split('월')[0].zfill(2),day,draw_time.split(' ')[1])

            draw_end_time = datetime.datetime.strptime(draw_time.split(' ')[1],"%H:%M")
            draw_end_time += datetime.timedelta(minutes=30)
            draw_end_time = draw_end_time.strftime("%H:%M")
            event_end = "{}-{}-{}T{}:00".format(my_year,month.split('월')[0].zfill(2),day,draw_end_time)
            
            if google_calendar_select(event_start, event_end, draw_name):   # 같은 이름의 드로우가 없는 경우 참
                google_calendar_insert_event(draw_name, event_start, event_end) # 이벤트를 추가한다.