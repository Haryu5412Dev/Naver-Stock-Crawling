# 참고 자료 : https://seokii.tistory.com/119
# 네이버 페이 : https://finance.naver.com/

import tkinter as tk
from tkinter import ttk
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
from io import StringIO
import time
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic' 

# JSON 데이터 저장 함수
def save_to_json(dataframe, filename):
    dataframe.to_json(filename, orient="records", force_ascii=False, indent=4)

# 데이터 수집 및 JSON 저장 (일별 시세 중심)
def fetch_stock_data():

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

        # 불필요한 행 제거 및 날짜 처리
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        # 날짜, 종가, 저가, 고가만 추출
        df = df[['날짜', '종가', '저가', '고가']]

        # 날짜를 'YYYY-MM-DD' 형식으로 변환
        df['날짜'] = pd.to_datetime(df['날짜'], format='%Y.%m.%d', errors='coerce')
        df['날짜'] = df['날짜'].dt.strftime('%Y-%m-%d')

        # 날짜를 기준으로 정렬
        df = df.dropna(subset=['날짜']).sort_values(by='날짜', ascending=False)

        # 출력 확인 (테스트용)
        print(df[['날짜', '종가', '저가', '고가']])

        # JSON 저장
        save_to_json(df, "data/stock_data_daily.json")
        print("데이터가 'stock_data_daily.json' 파일에 저장되었습니다.")

    except Exception as e:
        print(f"실행 에러: {e}")

# UI 생성 함수 - 표로 표시 (일별 시세)
def create_ui_from_json(filename):
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
    dataframe['날짜'] = pd.to_datetime(dataframe['날짜'], errors='coerce')
    dataframe = dataframe.dropna(subset=['날짜'])  # 날짜 변환 실패한 데이터 제거
    dataframe.sort_values(by='날짜', inplace=True)

    # 지난 4일 동안의 데이터만 추출
    recent_days = dataframe.tail(4).copy()

    # 날짜 형식을 "YYYY-MM-DD"로 지정
    recent_days['날짜'] = recent_days['날짜'].dt.strftime('%Y-%m-%d')

    # UI 생성
    root = tk.Tk()
    root.title("주식 일별 시세 표")

    # 테이블 생성
    tree = ttk.Treeview(root, columns=('날짜', '종가', '저가', '고가'), show='headings')
    tree.heading('날짜', text='날짜')
    tree.heading('종가', text='종가')
    tree.heading('저가', text='저가')
    tree.heading('고가', text='고가')

    # 데이터 삽입
    for index, row in recent_days.iterrows():
        tree.insert('', 'end', values=(row['날짜'], row['종가'], row['저가'], row['고가']))

    tree.pack(expand=True, fill=tk.BOTH)

    # 그래프 표시
    plot_graph(recent_days)

    # 창 크기 조정
    root.geometry("800x600")
    root.mainloop()

# 주식 가격을 꺾은선 그래프로 표시
def plot_graph(dataframe):
    plt.figure(figsize=(10, 6))

    # 날짜와 종가, 저가, 고가를 꺾은선 그래프로 그리기
    plt.plot(dataframe['날짜'], dataframe['종가'], label='종가', marker='o', color='blue')
    plt.plot(dataframe['날짜'], dataframe['저가'], label='저가', marker='o', color='red')
    plt.plot(dataframe['날짜'], dataframe['고가'], label='고가', marker='o', color='green')

    # 제목과 레이블 추가
    plt.title("최근 4일 주식 가격")
    plt.xlabel("날짜")
    plt.ylabel("가격")

    # X축 날짜 포맷 설정
    plt.xticks(rotation=45)

    # 범례 추가
    plt.legend()

    # 그래프 출력
    plt.tight_layout()
    plt.show()

# 데이터 수집 및 UI 실행
if __name__ == "__main__":
    fetch_or_display = input("데이터를 수집하려면 'fetch', 표를 보려면 'display'를 입력하세요: ").strip().lower()
    if fetch_or_display == "fetch":
        fetch_stock_data()
    elif fetch_or_display == "display":
        create_ui_from_json("data/stock_data_daily.json")
    else:
        print("올바른 입력값이 아닙니다. 'fetch' 또는 'display'를 입력해주세요.")

