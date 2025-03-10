import os
import time
import requests

import cv2

from urllib.parse import quote
from bs4 import BeautifulSoup
from ultralytics import YOLO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


# ChromeOptions 객체 생성
chrome_options = Options()

# headless 모드 설정
chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
chrome_options.add_argument('--disable-gpu')


# 넷플릭스 영화/시리즈 가져오는 함수
def get_netflix_list(url, naver_list):
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(1)

        for j in range(1,9):
            name = driver.find_element(By.XPATH, f'//*[@id="mflick"]/div/div/ul[{1}]/li[{j}]/strong/a').text
            naver_list.append(name)

        driver.find_element(By.XPATH, '//*[@id="main_pack"]/section[1]/div[2]/div/div/div[3]/div/a[2]').click()
        time.sleep(1)  # 페이지 로딩 대기

        for j in range(1,2):
            name = driver.find_element(By.XPATH, f'//*[@id="mflick"]/div/div/ul[{2}]/li[{j}]/strong/a').text
            naver_list.append(name)

        return naver_list
    
    except Exception as e:
        print(f"오류 발생: {e}")
        return None
    
    finally:
        # 드라이버 종료
        driver.quit()


# 이미지에서 사람 감지 함수
def detect_person(image_path):
    # YOLOv8 모델 로드
    model = YOLO("yolov8n.pt")
    image = cv2.imread(image_path)
    if image is None:
        return False  # 이미지 로드 실패 시 감지 안 됨 처리
    
    results = model(image)  # YOLOv8 실행
    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) == 0:  # YOLOv8에서 "0"은 'person' 클래스
                return True  # 사람이 감지됨
    return False  # 사람이 없음


# 네이버 포스터 & 스틸컷 저장 함수
def save_stillcut_image(movie_name):
    movie_name_encoded = quote(movie_name)
    url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=영화+{movie_name_encoded}+포토"

    response = requests.get(url)
    if response.status_code != 200:
        print("페이지를 불러오지 못했습니다.")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # 스틸컷 이미지 가져오기
        stillcut_tags = []
        stillcut_img = soup.find("div", class_="area_card _image_base_stillcut")
        if stillcut_img:
            stillcut_tags = stillcut_img.find_next("div", class_="movie_photo_list _list").find_all('img', class_='_img')

        if not stillcut_tags:
            print("스틸컷 이미지를 찾을 수 없습니다.")
            return None

        cnt = 0
        # 사람이 있는 스틸컷 저장 (사람 나올 때까지 반복)
        for idx, img_tag in enumerate(stillcut_tags):
            stillcut_url = img_tag['data-img-src']
            stillcut_response = requests.get(stillcut_url, stream=True)

            if stillcut_response.status_code == 200:
                add_date = time.strftime('%Y%m%d')
                image_name = movie_name.replace(':','').replace('?', '').replace('/', '').replace('<', '').replace('>', '')
                stillcut_path = f"image/original_{add_date}/img_{image_name}_{idx+1}.jpg"


                with open(stillcut_path, "wb") as f:
                    f.write(stillcut_response.content)

                if True:
                # if detect_person(stillcut_path):  # 사람이 감지되면 저장
                    print(f"사람이 있는 스틸컷 저장 완료: {stillcut_path}")
                    cnt += 1
                    if cnt == 3:
                        return
                else:
                    os.remove(stillcut_path)  # 사람이 없으면 삭제 후 다음 이미지 탐색

        print("사람이 포함된 스틸컷을 찾지 못했습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

