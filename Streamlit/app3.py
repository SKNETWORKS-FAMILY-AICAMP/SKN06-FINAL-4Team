import streamlit as st
from PIL import Image
import json

from netflix_utils.netflix_insta import *
from new_movie_utils.new_movie_insta import *
from boxoffice_utils.boxoffice_insta import *
from ni_movie_mu_utils.upload_posting import *

# 🎬 스트림릿 페이지 설정
st.set_page_config(page_title="영화 인스타 게시글 생성기", layout="wide")
st.title("🌟 AI 기반 영화 인스타 게시글 생성")

st.logo('nimoviemu.png', size="large", link=None, icon_image=None)

st.divider()

# Sidebar for navigation
st.sidebar.title("Ni_Movie_Mu")
selected_page = st.sidebar.radio("Options", ["주제에 맞는 영화 추천", "인기/신규 영화 추천"])

# Page logic
if selected_page == "주제에 맞는 영화 추천":
    import app3_0
    app3_0.run()

elif selected_page == "인기/신규 영화 추천":
    # Dynamically load app.3_1.py
    import app3_1  # Ensure app.3_1.py is in the same directory or accessible
    app3_1.run()  # Call a function from app.3_1.py to display its contents
