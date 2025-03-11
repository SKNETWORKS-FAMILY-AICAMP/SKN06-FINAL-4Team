import streamlit as st
from model.search_model import *

# 스트림릿 UI 설정
st.title("영화 추천 시스템")
st.write("영화에 대해 궁금한 점을 물어보세요!")

# 사용자 질문 입력 받기
question = st.text_input("질문을 입력하세요:")

if question:
    user_question = question
    st.write("[INFO] 질문 분석 중...")
    expanded_keyword = analyze_question_with_llm(user_question)

    key_word_index, key_word_indices = load_faiss_indices()

    st.write("[INFO] 어울리는 영화 고르는 중...")
    search_results = search_movies_with_faiss(expanded_keyword)

    recommended_movies = generate_recommendations(user_question, search_results)

    if not recommended_movies:
        st.write("\n❌ 추천할 영화를 찾을 수 없습니다.")
    else:
        st.write("\n🎬 최종 추천 영화 리스트: ", recommended_movies)


