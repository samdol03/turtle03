import pandas as pd
import numpy as np

#Max Drow Down
def MDD(data, window=252):
    # 주어진 데이터에 대해 최대 손실 감소를 계산하는 함수
    RollMax = data.rolling(window, min_periods=1).max()
    DailyDrawdown = data / RollMax - 1
    MaxDailyDrawdown = DailyDrawdown.rolling(window, min_periods=1).min()
    return MaxDailyDrawdown * 100  # 결과를 퍼센트로 반환

# 이격도
def calculate_volatility(data, period=20, annual_factor=252):
    log_returns = np.log(data / data.shift(1))
    volatility = log_returns.rolling(window=period).std() * np.sqrt(annual_factor) * 100
    return volatility

# 변동성
def calculate_disparity(data, moving_average_period):
    moving_average = data.rolling(window=moving_average_period).mean()
    disparity = (data / moving_average) * 100
    return disparity  