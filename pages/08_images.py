import streamlit as st
import os
from PIL import Image

# 현재 디렉토리 확인 및 이미지 폴더 절대 경로 설정
current_dir = os.getcwd()  # 현재 디렉토리 경로 확인
image_folder = os.path.join(current_dir, 'images')  # 이미지 폴더의 절대 경로 생성

# 이미지 폴더 경로 확인 및 처리
if not os.path.exists(image_folder):
    st.error(f"이미지 폴더가 존재하지 않습니다: {image_folder}")
else:
    # 이미지 파일 리스트 생성
    images = [os.path.join(image_folder, file) for file in os.listdir(image_folder)
              if file.lower().endswith(('png', 'jpg', 'jpeg')) and os.path.isfile(os.path.join(image_folder, file))]

    if not images:  # 이미지 파일이 없는 경우 처리
        st.warning("이미지 파일이 폴더에 없습니다.")
    else:
        # 전체 페이지를 넓게 사용
        st.set_page_config(layout="wide")
        
        # 이미지 파일을 2개씩 표시
        for i in range(0, len(images), 2):
            with st.container():
                cols = st.columns([1, 1])  # 두 개의 열 생성 (좌우 균등 비율)
                for col, image_path in zip(cols, images[i:i+2]):
                    try:
                        image = Image.open(image_path)
                        col.image(image, caption=os.path.basename(image_path), use_container_width=True)
                    except Exception as e:
                        col.error(f"이미지 파일을 로드하는 중 오류가 발생했습니다: {e}")
