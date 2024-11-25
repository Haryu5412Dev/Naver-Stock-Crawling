# 참고 자료 : https://seokii.tistory.com/119
# 네이버 페이 : https://finance.naver.com/

import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time
from datetime import datetime

code = input('종목 코드를 입력하세요: ')

headers = {'User-agent': 'Mozilla/5.0'}
url = f'https://finance.naver.com/item/sise_day.naver?code={code}'
df = pd.DataFrame()

try:
    req = requests.get(url, headers=headers)
    req.raise_for_status()
    html = BeautifulSoup(req.text, "lxml")

    # 마지막 페이지 확인
    pgrr = html.find('td', class_='pgRR')
    if pgrr and pgrr.a:
        s = pgrr.a['href'].split('=')
        last_page = int(s[-1])
    else:
        last_page = 1

    # 최대 5페이지까지만 가져오기
    last_page = min(last_page, 5)

    # 데이터 수집
    for page in range(1, last_page + 1):
        print(f"{page} 페이지를 불러오는중 입니다...")
        try:
            req = requests.get(f'{url}&page={page}', headers=headers)
            req.raise_for_status()
            page_data = pd.read_html(StringIO(req.text), encoding='euc-kr')[0]
            df = pd.concat([df, page_data], ignore_index=True)
        except Exception as e:
            print(f"{page}번의 페이지를 불러오는데 에러가 발생했습니다")
        time.sleep(1)

    # 불필요한 행 제거
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # 날짜 필터링
    current_month = datetime.now().strftime('%Y.%m')  # 현재 연도와 월 (예: '2024.11')
    df['날짜'] = pd.to_datetime(df['날짜'], format='%Y.%m.%d')  # 날짜를 datetime 형식으로 변환
    df = df[df['날짜'].dt.strftime('%Y.%m') == current_month]  # 현재 월만 필터링

    # 결과 출력
    print(df)

except Exception as e:
    print(f"실행 에러: {e}")
