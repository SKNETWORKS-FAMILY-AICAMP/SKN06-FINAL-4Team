import streamlit as st
from model.pipeline import *

# 스트림릿 UI 설정
st.title("영화 추천 시스템")
st.write("영화에 대해 궁금한 점을 물어보세요!")

# 사용자 질문 입력 받기
question = st.text_input("질문을 입력하세요:")
score = st.slider("무무스코어를 설정하세요 \n(선택된 숫자 이상의 영화를 추천합니다)", 0, 10, 8)

if question:
    user_question = question
    mumupoint = score
    delete_all_files_in_folder("background_images")
    delete_all_files_in_folder("insta_post")

    recommend_movies = recommend_pipeline(user_question, mumupoint)

    if not recommend_movies :
        st.write("[INFO] 🆖영화 정보가 없습니다. 질문을 변경하거나 무무스코어 설정을 낮춰주세요.🥲")
    else :
        st.write("[INFO] 🆗영화 추천 게시물이 정상적으로 생성되었습니다.")


