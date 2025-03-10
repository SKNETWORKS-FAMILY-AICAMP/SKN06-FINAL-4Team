import os

from instagrapi import Client
import time

import requests
from flask import Flask, send_from_directory
from threading import Thread

id = ""
pw = ""


def upload_images(caption):
    # 1. 인스타그램 로그인
    cl = Client()
    cl.login(id, pw)  # 계정 정보 입력

    # 이미지가 있는 폴더 경로
    add_date = time.strftime('%Y%m%d')
    base_dir = os.getcwd()
    image_folder = os.path.join(base_dir, 'image', f'insta_{add_date}')

    # 폴더에서 이미지 파일 목록 가져오기
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg'))]
    image_paths = []

    for i in image_files:
        img = os.path.join(base_dir, 'image', f'insta_{add_date}',i)
        image_paths.append(img)

    # 업로드 (리스트 순서대로)
    try:
        cl.album_upload(image_paths, caption)
        print("게시물 업로드가 완료되었습니다!")
    except Exception as e:
        print(f"업로드 실패: {e}")



# app = Flask(__name__)

# # Instagram Graph API 설정
# ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
# INSTAGRAM_ACCOUNT_ID = "ni_movie_mu"

# # 이미지 호스팅을 위한 로컬 서버 설정
# @app.route('/images/<path:filename>')
# def serve_image(filename):
#     return send_from_directory('image', filename)

# def run_server():
#     app.run(port=8000)

# # Instagram API 함수
# def upload_image(image_url, caption):
#     url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
#     payload = {
#         "image_url": image_url,
#         "caption": caption,
#         "access_token": ACCESS_TOKEN
#     }
#     response = requests.post(url, data=payload)
#     return response.json()

# def publish_container(container_id):
#     url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
#     payload = {
#         "creation_id": container_id,
#         "access_token": ACCESS_TOKEN
#     }
#     response = requests.post(url, data=payload)
#     return response.json()

# # 메인 코드
# if __name__ == "__main__":
#     # 로컬 서버 시작
#     server_thread = Thread(target=run_server)
#     server_thread.start()
#     time.sleep(2)  # 서버가 시작될 때까지 잠시 대기

#     add_date = time.strftime('%Y%m%d')
#     base_dir = os.getcwd()
#     image_folder = os.path.join(base_dir, 'image', f'insta_{add_date}')

#     # 폴더에서 이미지 파일 목록 가져오기
#     image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]

#     # 포스트 캡션
#     caption = write_text(weekly_boxoffice)  # 이 함수는 이전 코드에서 가져온 것으로 가정합니다.

#     try:
#         for image_file in image_files:
#             # 로컬 서버를 통해 이미지 URL 생성
#             image_url = f"http://localhost:8000/images/{image_file}"
            
#             # 이미지 업로드
#             container = upload_image(image_url, caption)
            
#             if container and 'id' in container:
#                 result = publish_container(container['id'])
#                 if 'id' in result:
#                     print(f"게시물이 성공적으로 업로드되었습니다. 게시물 ID: {result['id']}")
#                 else:
#                     print(f"게시물 발행 실패: {result.get('error', {}).get('message', 'Unknown error')}")
#             else:
#                 print(f"컨테이너 생성 실패: {container.get('error', {}).get('message', 'Unknown error')}")
            
#             time.sleep(5)  # API 호출 사이에 약간의 지연 추가
#     except Exception as e:
#         print(f"업로드 실패: {e}")
#     finally:
#         # 서버 종료 (실제 구현에서는 더 안전한 방법으로 서버를 종료해야 합니다)
#         os._exit(0)

