import os
import cv2
import requests
import numpy as np
from urllib.parse import quote
from bs4 import BeautifulSoup
from ultralytics import YOLO

# YOLOv8 모델 로드
model = YOLO("yolov8n.pt")

# 이미지에서 사람 감지 함수
def detect_person(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return False  # 이미지 로드 실패 시 감지 안 됨 처리
    
    results = model(image)  # YOLOv8 실행
    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) == 0:  # YOLOv8에서 "0"은 'person' 클래스
                return True  # 사람이 감지됨
    return False  # 사람이 없음

# 포스터 & 스틸컷 저장 함수
def save_movie_image(movie_name):
    movie_name_encoded = quote(movie_name)
    url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=영화+{movie_name_encoded}+포토"

    response = requests.get(url)
    if response.status_code != 200:
        print("❌ 페이지를 불러오지 못했습니다.")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # ✅ 포스터 이미지 가져오기
        poster_tags = []
        poster_img = soup.find("div", class_="area_card _image_base_poster")
        if poster_img:
            poster_tags = poster_img.find_next("div", class_="movie_photo_list _list").find_all('img', class_='_img')

        # ✅ 스틸컷 이미지 가져오기
        stillcut_tags = []
        stillcut_img = soup.find("div", class_="area_card _image_base_stillcut")
        if stillcut_img:
            stillcut_tags = stillcut_img.find_next("div", class_="movie_photo_list _list").find_all('img', class_='_img')

        if not poster_tags:
            print("❌ 포스터를 찾을 수 없습니다.")
            return None
        if not stillcut_tags:
            print("❌ 스틸컷 이미지를 찾을 수 없습니다.")
            return None

        # ✅ 포스터 저장 (글자 포함 여부 확인 생략)
        poster_url = poster_tags[1]['data-img-src']  # 두 번째 이미지
        poster_response = requests.get(poster_url, stream=True)
        if poster_response.status_code == 200:
            os.makedirs("images", exist_ok=True)
            poster_path = f"images/{movie_name}_poster.jpg"
            with open(poster_path, "wb") as f:
                f.write(poster_response.content)
            print(f"✅ 포스터 저장 완료: {poster_path}")
        else:
            print("❌ 포스터 다운로드 실패")

        # ✅ 사람이 있는 스틸컷 저장 (사람 나올 때까지 반복)
        for idx, img_tag in enumerate(stillcut_tags):
            stillcut_url = img_tag['data-img-src']
            stillcut_response = requests.get(stillcut_url, stream=True)

            if stillcut_response.status_code == 200:
                stillcut_path = f"images/{movie_name}_stillcut.jpg"
                with open(stillcut_path, "wb") as f:
                    f.write(stillcut_response.content)

                if detect_person(stillcut_path):  # 사람이 감지되면 저장
                    print(f"✅ 사람이 있는 스틸컷 저장 완료: {stillcut_path}")
                    return
                else:
                    os.remove(stillcut_path)  # 사람이 없으면 삭제 후 다음 이미지 탐색

        print("❌ 사람이 포함된 스틸컷을 찾지 못했습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def save_movie_images(movie_list):
    for movie in movie_list:
        save_movie_image(movie)  # 개별 영화 처리