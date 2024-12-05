import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta
import streamlit as st
from lib.finance_library import MDD, calculate_volatility  # finance_library 모듈에서 MDD,calculate_volatility 함수를 불러옵니다.

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
    "448330.KS": "Samsung Kodex Wise Samsung Electronics Balanced Etf",
    "447770.KS": "Mirae Asset Tiger Tesla Balanced Etf",
    "448540.KS": "Kim Ace Nvidia 30 Blend Fund",
    "447660.KS": "Hanwha ARIRANG Apple Balanced ETF"
}

# 사용자 입력 설정
def setup_inputs():
    today = date.today()
    one_year_ago = today.replace(year=today.year - 1)
    start_date = st.sidebar.date_input("Start Date", value=one_year_ago)
    end_date = st.sidebar.date_input("End Date", value=today)
    tickers = {}
    ticker_weights = {}
    num_tickers = len(ticker_descriptions)

    initial_weight = 1.0 / num_tickers if num_tickers > 0 else 0  # 티커 수로 나누어 초기 가중치 설정

    # 사용자로부터 number_input을 통해 가중치 입력받기
    for ticker, description in ticker_descriptions.items():
        weight = st.sidebar.number_input(f"Weight for {ticker} ({description})", min_value=0.0, max_value=1.0, value=initial_weight, step=0.01, format="%.2f")
        tickers[ticker] = ticker
        ticker_weights[ticker] = weight

    # 총합 검사 및 메시지 표시
    check_total(ticker_weights)

    # st.session_state에 ticker_weights 저장
    if 'ticker_weights' not in st.session_state:
        st.session_state.ticker_weights = {}
    st.session_state.ticker_weights = ticker_weights

    return start_date, end_date, tickers, ticker_weights

# 총합 검사 및 가중치 조정 함수
def check_total(ticker_weights):
    total_weight = sum(ticker_weights.values())
    if total_weight < 1:
        st.sidebar.error("경고: 가중치의 총합이 1보다 작습니다.")
    elif total_weight > 1.0:
        st.sidebar.warning("경고: 가중치의 총합이 1보다 큽니다.")
    else:
        st.sidebar.success("총합이 1입니다.")

# 데이터 불러오기 및 처리
@st.cache_data
def fetch_and_process_data(ticker, start_date, end_date):
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    data = stock_data[['Open', 'High', 'Low', 'Adj Close']].copy()
    data.columns = ['Open', 'High', 'Low', 'Adj Close']
    data = data / data.iloc[0] * 100
    return data.astype(float)  # mplfinance에서 float type 사용

# 일봉, MDD, 변동성 출력하기
# 일봉, MDD, 변동성 출력하기
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

def plot_data_plotly(data_dict, mdd_dict, volatility_dict):
    # Plotly subplots 설정
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                        subplot_titles=(
                            "Adjusted Close Prices for Multiple Tickers",
                            "Maximum Drawdowns (MDD) for Multiple Tickers",
                            "Rolling 20-Day Volatility for Multiple Tickers"
                        ),
                        row_heights=[0.5, 0.25, 0.25])

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # 색상 팔레트 설정
    ticker_list = list(data_dict.keys())  # 티커 리스트 생성

    # 각 티커별로 차트 데이터 추가
    for ticker, data in data_dict.items():
        color_index = ticker_list.index(ticker) % len(colors)  # 티커의 인덱스를 색상 인덱스로 사용
        # 지수화된 조정 종가
        data['Adj Close'] = data['Adj Close'] / data['Adj Close'].iloc[0]

        if ticker == 'portfolio':
            fig.add_trace(
                go.Scatter(x=data.index, y=data['Adj Close'], mode='lines+markers', name=f'{ticker} Adj Close', marker=dict(color='red', symbol='circle'), line=dict(color='red')),
                row=1, col=1
            )
        else:
            fig.add_trace(
                go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name=f'{ticker} Adj Close', legendgroup='price', line=dict(color=colors[color_index])),
                row=1, col=1
            )

    for ticker, data in mdd_dict.items():
        if ticker == 'portfolio':
            # 포트폴리오에 대해 특별한 마커 및 색상 설정
            fig.add_trace(
                go.Scatter(x=data.index, y=data, mode='lines+markers', name=f'{ticker} MDD', marker=dict(color='red', symbol='square'), line=dict(color='red')),
                row=2, col=1
            )
        else:
            color_index = ticker_list.index(ticker) % len(colors)
            # 다른 티커에 대한 MDD 바 차트 추가
            fig.add_trace(
                go.Scatter(x=data.index, y=data, mode='lines', name=f'{ticker} MDD', legendgroup='mdd', line=dict(color=colors[color_index])),
                row=2, col=1
            )

    for ticker, data in volatility_dict.items():
        if ticker == 'portfolio':
            # 포트폴리오에 대해 특별한 마커 및 색상 설정
            fig.add_trace(
                go.Scatter(x=data.index, y=data, mode='lines+markers', name=f'{ticker} Volatility', marker=dict(color='red', symbol='diamond'), line=dict(color='red')),
                row=3, col=1
            )
        else:
            color_index = ticker_list.index(ticker) % len(colors)
            # 다른 티커에 대한 변동성 라인 차트 추가
            fig.add_trace(
                go.Scatter(x=data.index, y=data, mode='lines', name=f'{ticker} Volatility', legendgroup='volatility', line=dict(color=colors[color_index])),
                row=3, col=1
            )


    # 레이아웃 조정
    fig.update_layout(height=800, width=700, title_text="Data Visualization for Multiple Tickers", showlegend=False)
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="MDD", row=2, col=1)
    fig.update_yaxes(title_text="Volatility", row=3, col=1)

    # Streamlit에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

# selected tickers로 새로운 dict 만들기
def filter_selected_tickers(select_ticker, data_dict, mdd_dict, volatility_dict):
    # Initialize dictionaries for filtered data
    filtered_data_dict = {}
    filtered_mdd_dict = {}
    filtered_volatility_dict = {}

    # Loop through selected tickers to populate new dictionaries
    for ticker in select_ticker["Ticker"].values:
        if ticker in data_dict:
            filtered_data_dict[ticker] = data_dict[ticker]
        if ticker in mdd_dict:
            filtered_mdd_dict[ticker] = mdd_dict[ticker]
        if ticker in volatility_dict:
            filtered_volatility_dict[ticker] = volatility_dict[ticker]
    return filtered_data_dict, filtered_mdd_dict, filtered_volatility_dict

# 포트폴리오 데이터 계산
def calculate_portfolio(data_dict):
    # st.session_state에서 ticker_weights를 직접 가져오기
    ticker_weights = st.session_state.ticker_weights
    # 각 주식 데이터에 가중치를 적용하여 포트폴리오의 가중 평균 계산
    portfolio_data = sum(data_dict[ticker] * weight for ticker, weight in ticker_weights.items() if ticker in data_dict)
    return portfolio_data


# 메인 실행 로직을 main() 함수로 정의
def main():
    # 사용자 입력
    start_date, end_date, tickers, ticker_weight = setup_inputs()

    # Yahoo Finance에서 데이터 가져오기
    data_dict = {}  # 딕셔너리로 ticker별 데이터 저장
    mdd_dict = {}   # ticker별 MDD 저장
    volatility_dict = {}  # 변동성 저장
    for ticker in tickers:
        data = fetch_and_process_data(ticker, start_date, end_date)
        if data.empty:
            st.error(f"No data found for {ticker}. Please check your inputs.")
        else:
            data_dict[ticker] = data
            mdd_dict[ticker] = MDD(data['Adj Close'], 30)  # def MDD(data, window=252):
            volatility_dict[ticker] = calculate_volatility(data['Adj Close'])  # def calculate_volatility(data, period=20, annual_factor=252):

    df = pd.DataFrame(list(ticker_descriptions.items()), columns=["Ticker", "Description"])
    # 멀티 선택할수있는 dataframe 만들기
    event = st.dataframe(
        data = df,
        use_container_width = True,
        hide_index = True,
        on_select = 'rerun',
        selection_mode = 'multi-row',
    )

    select_ticker = df.iloc[event.selection.rows]  # 선택된 row 전달
    data_dict, mdd_dict, volatility_dict = filter_selected_tickers(select_ticker, data_dict, mdd_dict, volatility_dict)  # selected tickers로 새로운 dict 만들기

    if not select_ticker.empty:
        data_dict['portfolio'] = calculate_portfolio(data_dict)
        mdd_dict['portfolio'] = MDD(data_dict['portfolio']['Adj Close'])
        volatility_dict['portfolio'] = calculate_volatility(data_dict['portfolio']['Adj Close'])

        # 일봉, MDD, 변동성 출력하기
        plot_data_plotly(data_dict, mdd_dict, volatility_dict)

# 프로그램의 진입점에서 main() 함수 호출
if __name__ == "__main__":
    main()