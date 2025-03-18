import streamlit as st
from PIL import Image
import json

from netflix_utils.netflix_insta import *
from new_movie_utils.new_movie_insta import *
from boxoffice_utils.boxoffice_insta import *
from ni_movie_mu_utils.upload_posting import *

def run():
    # 🎯 1. 게시물 유형 선택
    st.subheader("어떤 게시글을 생성할까요?")
    posting_type = st.radio("게시글 유형을 선택하세요.", 
                            ["넷플릭스 지금 많이 보는", "넷플릭스 주간순위", "넷플릭스 신작", 
                            "박스오피스 주간 순위", "새 영화 뉴스 요약"])

    caption = ""

    # 🎬 2. 게시글 생성 버튼
    if st.button("📢 게시글 생성"):
        with st.spinner("AI가 게시글을 생성하는 중..."):
            if posting_type == "넷플릭스 지금 많이 보는":
                caption = make_netflix_posting_most_watched()
            elif posting_type == "넷플릭스 주간순위":
                caption = make_netflix_posting_weekly()
            elif posting_type == "넷플릭스 신작":
                caption = make_netflix_posting_new()
            elif posting_type == "박스오피스 주간 순위":
                caption = make_boxoffice_posting()
            elif posting_type == "새 영화 뉴스 요약":
                caption = make_new_news_posting()

        # 🎯 3. 생성된 게시글 미리보기 (수정 가능)
        st.subheader("📢 생성된 인스타그램 게시글")
        caption = st.text_area("📝 AI 생성 게시글을 수정하세요.", caption, height=200)

        # caption 저장하기
        with open('caption.json', 'w', encoding='utf-8') as f:
            json.dump({"caption": caption}, f, ensure_ascii=False)

        add_date = time.strftime('%Y%m%d')
        base_dir = os.getcwd()
        image_folder = os.path.join(base_dir, 'image', f'insta_{add_date}')

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
            upload_images(caption)  # 실제 업로드 함수 실행
        st.success("✅ 게시글이 업로드되었습니다!")

        st.balloons()