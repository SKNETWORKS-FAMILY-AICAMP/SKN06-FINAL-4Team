import os
import time
import requests
from filestack import Client
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv('INSTA_API_KEY')
INSTAGRAM_ACCOUNT_ID = '17841472014925595'
FILESTACK_API_KEY = os.getenv('FILESTACK_API_KEY')

client = Client(FILESTACK_API_KEY)


# 이미지 업로드 및 URL 획득 함수
def upload_to_filestack(filepath):
    new_filelink = client.upload(filepath=filepath)
    return new_filelink.url


# Instagram API로 미디어 컨테이너 생성 (캐러셀 아이템)
def create_carousel_item(image_url):
    url = f"https://graph.instagram.com/v20.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        "image_url": image_url,
        "is_carousel_item": True,
        "access_token": ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json().get('id')


# 캐러셀 컨테이너 생성
def create_carousel_container(children_ids, caption):
    url = f"https://graph.instagram.com/v20.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        "media_type": "CAROUSEL",
        "children": ','.join(children_ids),
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json().get('id')


# 캐러셀 컨테이너 게시
def publish_container(container_id):
    url = f"https://graph.instagram.com/v20.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    payload = {
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json().get('id')


# 실제 실행 함수 (메인)
def upload_images(caption):
    add_date = time.strftime('%Y%m%d')
    base_dir = os.getcwd()
    image_folder = os.path.join(base_dir, 'image', f'insta_{add_date}')

    image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]
    
    if not image_files:
        print("업로드할 이미지가 없습니다.")
        return

    carousel_item_ids = []
    
    # 각 이미지를 filestack에 업로드 후 캐러셀 아이템 생성
    for image_file in image_files:
        local_path = os.path.join(image_folder, image_file)
        image_url = upload_to_filestack(local_path)
        print(f"Filestack 업로드 완료: {image_url}")

        item_id = create_carousel_item(image_url)
        print(f"캐러셀 아이템 생성 완료: {item_id}")
        
        carousel_item_ids.append(item_id)
        
        time.sleep(2)  # API 제한을 피하기 위한 짧은 대기

    # 캐러셀 컨테이너 생성 및 게시
    try:
        carousel_container_id = create_carousel_container(carousel_item_ids, caption)
        print(f"캐러셀 컨테이너 생성 완료: {carousel_container_id}")

        time.sleep(5)  # Instagram 내부 처리 시간 대기
        
        published_post_id = publish_container(carousel_container_id)
        print(f"게시 성공! 게시물 ID: {published_post_id}")
        
    except requests.exceptions.HTTPError as e:
        print(f"게시 실패: {e.response.json()}")

