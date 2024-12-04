import streamlit as st

# HTML 및 CSS 스타일 정의
html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Turtle Trading</title>
    <style>
        body {
            font-family: 'Nanum Gothic', sans-serif; /* 세련된 한글 폰트 */
            line-height: 1.8;
            margin: 20px;
        }
        h1 {
            color: #2c3e50;
            font-size: 1.5em;
        }
        p {
            color: #34495e;
            font-size: 1.2em;
        }
        a {
            color: #1e90ff;
            text-decoration: none;
            font-weight: bold;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>
        Turtle Trading
    </h1>
    <p>
        Turtle Trading은 1980년대 Richard Dennis와 William Eckhardt가 시작한 전설적인 추세 추종 시스템입니다. 
        이 시스템은 초보자도 성공적인 트레이더가 될 수 있는지 실험하기 위해 만들어졌습니다.
    </p>
    <h1><a href="https://example.com/trend-disparity-volatility" target="_blank">Trend Disparity Volatility</a></h1>
    <p>
        이 페이지는 추세, 이격도, 변동성을 확인할 수 있도록 구성되어 있습니다.
    </p>
</body>
</html>
"""

# Streamlit에서 HTML 렌더링
st.markdown(html_code, unsafe_allow_html=True)
