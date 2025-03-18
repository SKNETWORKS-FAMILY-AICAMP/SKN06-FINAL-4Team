import streamlit as st
import json

from model.pipeline import *
from ni_movie_mu_utils.upload_posting import *

def run():
    # 스트림릿 UI 설정
    st.subheader("영화에 대해 궁금한 점을 물어보세요!")

    # 사용자 질문 입력 받기
    score = st.slider("무무스코어를 설정하세요 \n(선택된 스코어 이상의 영화를 추천합니다)", 0, 10, 8)
    question = st.text_input("질문을 입력하세요:")

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


        # 🎯 3. 생성된 게시글 미리보기 (수정 가능)
        st.subheader("📢 생성된 인스타그램 게시글")
        with open('recommend_data/cache_file/instagram_post_result.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            caption = data["게시글"] + '\n' + data['해시태그']
        caption = st.text_area("📝 AI 생성 게시글을 수정하세요.", caption, height=200)

        # caption 저장하기
        with open('caption.json', 'w', encoding='utf-8') as f:
            json.dump({"caption": caption}, f, ensure_ascii=False)

        base_dir = os.getcwd()
        image_folder = os.path.join(base_dir, 'insta_post')

        image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
        
        image_paths = []
        # 각 이미지를 filestack에 업로드 후 캐러셀 아이템 생성
        for image_file in image_files:
            local_path = os.path.join(image_folder, image_file)
            a = Image.open(local_path)
            image_paths.append(a)

        st.image(image_paths)

    st.divider()

    # ✅ 4. 게시글 업로드 버튼
    if st.button("🚀 인스타그램에 게시하기"):
        with st.spinner("게시 중..."):
            # caption 불러오기
            with open('caption.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                caption = data["caption"]
            upload_images(caption, 'y')  # 실제 업로드 함수 실행
        st.success("✅ 게시글이 업로드되었습니다!")

        st.balloons()
