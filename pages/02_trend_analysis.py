import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta
import streamlit as st
from lib.finance_library import calculate_volatility,calculate_disparity  # finance_library 모듈에서 변동성, 이격도 함수를 불러옵니다.

# 페이지 설정
st.set_page_config(layout="wide")

# Streamlit 설정
st.markdown(
    """
    <h1 style='font-size: 24px;'>Stock Analysis Dashboard</h1>
    """, 
    unsafe_allow_html=True
)
st.sidebar.header("Input Options")

# 전역 변수로 티커 설명 설정
ticker_descriptions = {
    "TSLA": "Tesla, Inc.",
    "^GSPC": "S&P 500 Index",
    "PLUG": "Plug Power Inc.",
    "005930.KS": "Samsung Electronics Co., Ltd.",
    "^SOX": "PHLX Semiconductor Sector Index"
}

# 사용자 입력 설정
def setup_inputs():
    today = date.today()
    one_year_ago = today.replace(year=today.year - 1)
    start_date = st.sidebar.date_input("Start Date", value=one_year_ago)
    end_date = st.sidebar.date_input("End Date", value=today)
    ticker = st.sidebar.text_input("Enter Ticker", value="^GSPC")  # ^GSPC는 S&P500

    # ticker 값이 비어있으면 사용자가 유효한 값을 입력할 때까지 다음 단계로 진행하지 않음
    if ticker == "":
        st.sidebar.error("Please enter a valid ticker symbol.")
    return start_date, end_date, ticker

# Ticker 리스트 설정
def display_ticker_list():
    st.sidebar.markdown('<div class="ticker-list"><strong>- Ticker List -</strong></div>', unsafe_allow_html=True)
    for ticker, description in ticker_descriptions.items():
        st.sidebar.markdown(f'<div class="ticker-list" title="{description}">{ticker}</div>', unsafe_allow_html=True)

# 데이터 불러오기 및 처리
def fetch_and_process_data(ticker, start_date, end_date):
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    data = stock_data[['Open', 'High', 'Low', 'Adj Close']].copy()
    data.columns = ['Open', 'High', 'Low', 'Adj Close']
    data = data / data.iloc[0] * 100
    return data.astype(float)  # mplfinance에서 float type 사용

def plot_data_plotly(ticker_description, data, disparity_5d, disparity_20d, volatility):
    x_start_date, x_end_date = data.index.min(), data.index.max()
    monthly_dates = pd.date_range(start=x_start_date, end=x_end_date, freq='MS')

    # 5일 및 20일 이동평균 계산
    data['MA_5'] = data['Adj Close'].rolling(window=5).mean()
    data['MA_20'] = data['Adj Close'].rolling(window=20).mean()

    # Plotly subplots 설정
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                        subplot_titles=(
                            f"{ticker_description} Candlestick Chart with 5-Day and 20-Day Moving Averages",
                            f"{ticker_description} 5-Day and 20-Day Disparity",
                            f"{ticker_description} Rolling 20-Day Annualized Volatility"
                        ),
                        row_heights=[0.5, 0.25, 0.25])

    # 캔들스틱 차트 추가
    fig.add_trace(
        go.Candlestick(x=data.index,
                       open=data['Open'], high=data['High'],
                       low=data['Low'], close=data['Adj Close'],
                       increasing_line_color='red', decreasing_line_color='blue'),
        row=1, col=1
    )

    # 5일 이평선 추가
    fig.add_trace(
        go.Scatter(x=data.index, y=data['MA_5'], mode='lines', line=dict(color='orange'), name='5-Day MA'),
        row=1, col=1
    )

    # 20일 이평선 추가
    fig.add_trace(
        go.Scatter(x=data.index, y=data['MA_20'], mode='lines', line=dict(color='purple'), name='20-Day MA'),
        row=1, col=1
    )

    # 5일 및 20일 그래프 추가
    fig.add_trace(
        go.Bar(x=disparity_5d.index, y=disparity_5d - 100, marker_color='red', name='5-Day Disparity'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=disparity_20d.index, y=disparity_20d - 100, mode='lines', line=dict(color='black'), name='20-Day Disparity'),
        row=2, col=1
    )

    # 변동성 그래프 추가
    fig.add_trace(
        go.Scatter(x=volatility.index, y=volatility, mode='lines', line=dict(color='green'), name='Volatility'),
        row=3, col=1
    )

    # 각 서브플롯에 대해 매월 수직선 추가, paper 기반으로 설정
    for date in monthly_dates:
        fig.add_vline(x=date, line_dash="dash", line_color="gray", line_width=1, yref="paper", y0=0.70, y1=1.0, row=1, col=1)
        fig.add_vline(x=date, line_dash="dash", line_color="gray", line_width=1, yref="paper", y0=0.37, y1=0.68, row=2, col=1)
        fig.add_vline(x=date, line_dash="dash", line_color="gray", line_width=1, yref="paper", y0=0, y1=0.35, row=3, col=1)

    # 레이아웃 조정
    fig.update_layout(height=800, width=700, title_text=f"Data Visualization for {ticker_description}", showlegend=False)
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Disparity Index", row=2, col=1)
    fig.update_yaxes(title_text="Volatility", row=3, col=1)

    # Streamlit에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

# 메인 실행 로직을 main() 함수로 정의
def main():
    #사용자 입력
    start_date, end_date, ticker = setup_inputs()
    display_ticker_list()  # 티커 리스트 출력

    # Yahoo Finance에서 데이터 가져오기
    data = fetch_and_process_data(ticker, start_date, end_date)
    if data.empty:
        st.error("No data found for the selected ticker and date range. Please check your inputs.")
        return  # 데이터가 없을 경우 함수 종료
    
    # 이격도, 변동성 계산하기
    disparity_5d = calculate_disparity(data['Adj Close'], 5)
    disparity_20d = calculate_disparity(data['Adj Close'], 20)
    volatility = calculate_volatility(data['Adj Close'])

    # 티커 설명 가져오기
    ticker_description = ticker_descriptions.get(ticker, ticker)

    # 일봉, 이격도, 변동성 출력하기
    plot_data_plotly(ticker_description, data, disparity_5d, disparity_20d, volatility)

# 프로그램의 진입점에서 main() 함수 호출
if __name__ == "__main__":
    main()