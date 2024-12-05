import streamlit as st
import os

# 현재 작업 디렉토리 구하기
current_dir = os.getcwd()

# 파일 경로 생성
file_path = os.path.join(current_dir, 'docs', 'SSAM(Turtle_Trading)_manual.md')

# 파일 존재 여부 확인
if not os.path.exists(file_path):
    st.error(f"파일이 존재하지 않습니다: {file_path}")
else:
    # Markdown 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # Streamlit 페이지에 Markdown 내용 렌더링
    st.markdown(markdown_content, unsafe_allow_html=True)
