# 참고 자료 : https://seokii.tistory.com/119
# 네이버 페이 : https://finance.naver.com/

import tkinter as tk
from tkinter import ttk
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt

# JSON 데이터 저장 함수
def save_to_json(dataframe, filename):
    dataframe.to_json(filename, orient="records", force_ascii=False, indent=4)

# 데이터 수집 및 JSON 저장 (사용자의 원래 코드를 기반으로 처리)
def fetch_stock_data():
    import requests
    from bs4 import BeautifulSoup
    from io import StringIO
    import time

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

        # JSON 저장
        save_to_json(df, "stock_data.json")
        print("데이터가 'stock_data.json' 파일에 저장되었습니다.")

    except Exception as e:
        print(f"실행 에러: {e}")

# UI 생성 함수 - 그래프 표시
def create_ui_from_json(filename):
    import matplotlib.font_manager as fm

    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

    # JSON 데이터 읽기
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON 파일을 찾을 수 없습니다. 데이터를 먼저 수집해주세요.")
        return

    # DataFrame으로 변환
    dataframe = pd.DataFrame(data)

    # 날짜와 종가 데이터만 추출
    dataframe['날짜'] = pd.to_datetime(dataframe['날짜'])
    dataframe.sort_values(by='날짜', inplace=True)
    dates = dataframe['날짜']
    closing_prices = dataframe['종가'].astype(float) * 10  # 단위를 원으로 변경

    # 그래프 그리기
    plt.figure(figsize=(10, 5))
    plt.plot(dates, closing_prices, marker='o', linestyle='-', color='b', label='종가 (원)')
    plt.title("주식 종가 추이", fontsize=16)
    plt.xlabel("날짜", fontsize=12)
    plt.ylabel("종가 (원)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

# 데이터 수집 및 UI 실행
if __name__ == "__main__":
    fetch_or_display = input("데이터를 수집하려면 'fetch', 그래프를 보려면 'display'를 입력하세요: ").strip().lower()
    if fetch_or_display == "fetch":
        fetch_stock_data()
    elif fetch_or_display == "display":
        create_ui_from_json("stock_data.json")
    else:
        print("올바른 입력값이 아닙니다. 'fetch' 또는 'display'를 입력해주세요.")
