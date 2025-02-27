import os
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from PIL import Image, ImageDraw, ImageFont
import cv2

from urllib.parse import quote
from bs4 import BeautifulSoup
from ultralytics import YOLO


# 키노라이즈에서 포스터 이미지 가져오는 함수
def get_poster_image(movie_name):
    try:
        # ChromeOptions 객체 생성
        chrome_options = Options()

        add_date = time.strftime('%Y%m%d')
        os.makedirs(f'image/poster_{add_date}', exist_ok=True)

        # # headless 모드 설정
        # chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
        # chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://m.kinolights.com/search')
        time.sleep(1)

        search_box = driver.find_element(By.CLASS_NAME, "search-form__input")  # 검색창의 name 속성 값이 searchQuery라고 가정
        search_box.send_keys(movie_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="searchContentList"]/div/a/div[2]').click()
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div[2]/div[1]/div[2]/div/div[1]/img').click()
        time.sleep(1)
        image_elements = driver.find_elements(By.XPATH, '//*[@id="root"]/div[2]/div[2]/div/div/div[2]/div/div/div[1]/img') 

        # 이미지 저장
        for index, img in enumerate(image_elements):
            img_url = img.get_attribute("src")  # 이미지의 URL 가져오기
            if img_url:  # 유효한 URL인지 확인
                response = requests.get(img_url)
                if response.status_code == 200:
                    # 파일 저장 경로 설정
                    image_name = movie_name.replace(':','').replace('?', '').replace('/', '').replace('<', '').replace('>', '')
                    file_name = f"image/poster_{add_date}/{image_name}_0.jpg"
                    with open(file_name, "wb") as f:
                        f.write(response.content)
                    print(f"이미지 저장 완료: {file_name}")
                else:
                    print(f"이미지 다운로드 실패: {img_url}")
        return

    except Exception as e:
        print(f'{movie_name}의 이미지를 찾을수 없습니다.')
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
def save_movie_image(movie_name):
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
                stillcut_path = f"image/poster_{add_date}/{image_name}_{idx+1}.jpg"


                with open(stillcut_path, "wb") as f:
                    f.write(stillcut_response.content)

                if detect_person(stillcut_path):  # 사람이 감지되면 저장
                    print(f"사람이 있는 스틸컷 저장 완료: {stillcut_path}")
                    cnt += 1
                    if cnt == 3:
                        return
                else:
                    os.remove(stillcut_path)  # 사람이 없으면 삭제 후 다음 이미지 탐색

        print("사람이 포함된 스틸컷을 찾지 못했습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")


# 스틸컷과 기사 요약을 넣어 게시물을 만드는 함수수
def make_news_post(image_name, title, news):
    # 설정: 배경 크기 및 이미지 폴더 경로
    background_width = 1080  # Instagram 권장 너비
    background_height = background_width 
    background_color = "black"
    add_date = time.strftime('%Y%m%d')
    base_dir = os.getcwd()
    image_folder = os.path.join(base_dir, 'image', f"poster_{add_date}")
    os.makedirs(f'image/insta_{add_date}', exist_ok=True)
    output_folder = os.path.join(base_dir, 'image', f'insta_{add_date}')

    # 검정 배경 생성
    background = Image.new("RGB", (background_width, background_height), background_color)

    # 폴더에서 이미지 파일 가져오기
    image_path = os.path.join(image_folder, image_name)
    with Image.open(image_path) as img:
        # 이미지 크기 조정 (너비 맞춤)
        img_ratio = img.width / img.height
        target_height = int(background_width / img_ratio)

        if target_height > background_height:
            # 세로가 너무 길면 잘라내기
            img_resized = img.resize((background_width, target_height))
            crop_top = (target_height - background_height) // 2
            img_cropped = img_resized.crop((0, 0, background_width, background_height))
        else:
            # 세로가 배경에 맞으면 그대로 사용
            img_cropped = img.resize((background_width, target_height))

        # 이미지 배경에 붙이기 (위쪽 정렬)
        background.paste(img_cropped, (0, 0))

    # 텍스트 추가
    draw = ImageDraw.Draw(background)
    base_dir = os.getcwd()
    head_font = 'DX헤드01Light.ttf'
    body_font = head_font
    head_path = os.path.join(base_dir,'font', head_font)
    body_path = os.path.join(base_dir,'font', body_font)
    font_title = ImageFont.truetype(head_path, 60)  # 제목 폰트 크기
    font_news = ImageFont.truetype(body_path, 35)  # 뉴스 폰트 크기

    # 텍스트 위치 계산
    text_margin = 30
    text_start_y = background_height - 400  # 이미지 아래쪽에 텍스트 배치

    # 제목 추가
    title = "#"+title
    title_bbox = draw.textbbox((text_margin, text_start_y), title, font=font_title)
    draw.text((text_margin, text_start_y), title, fill="white", font=font_title)

    # 빨간 줄 추가
    line_thickness = 10  # 선의 두께
    line_y = title_bbox[3] -20  # 제목 아래 5픽셀 위치에 선 그리기
    line_start_x = title_bbox[2] + 20  # 제목 끝에서 10픽셀 떨어진 지점부터 시작
    line_end_x = background_width  # 오른쪽 여백까지
    draw.line([(line_start_x, line_y), (line_end_x, line_y)], fill="red", width=line_thickness)

    # 뉴스 내용 추가 (여러 줄로 나누어 표시)
    news_lines = []
    news = '- ' + news
    words = news.split()
    current_line = ""
    for word in words:
        line_width = draw.textlength(current_line + " " + word, font=font_news)
        if line_width <= background_width - 2 * (text_margin+50):
            current_line += " " + word if current_line else word
        else:
            news_lines.append(current_line)
            current_line = word
    if current_line:
        news_lines.append(current_line)

    for i, line in enumerate(news_lines):
        draw.text((text_margin+50, text_start_y + 80 + i * 47), line.strip(), fill="white", font=font_news)

    # 결과 저장 및 확인
    output_path = os.path.join(output_folder, f"insta_{image_name}")
    background.save(output_path)
    print(f"결과 저장: {output_path}")


# 포스터 전체를 넣고 빈공간은 검정색으로 두는 함수
def make_sq_poster(image_name):
    # 포스터 열기
    add_date = time.strftime('%Y%m%d')
    poster = Image.open(f"image/poster_{add_date}/{image_name}")
    
    # 원본 이미지 크기
    width, height = poster.size
    
    # 정사각형 크기 (세로 길이에 맞춤)
    square_size = height
    
    # 새 정사각형 이미지 생성 (검정 배경)
    new_image = Image.new('RGB', (square_size, square_size), (0, 0, 0))
    
    # 원본 이미지를 세로 길이에 맞게 리사이즈
    new_width = int(width * (square_size / height))
    resized_poster = poster.resize((new_width, square_size), Image.LANCZOS)
    
    # 리사이즈된 이미지를 새 이미지의 중앙에 붙이기
    paste_x = (square_size - new_width) // 2
    new_image.paste(resized_poster, (paste_x, 0))
    
    # 저장 경로 설정
    os.makedirs(f'image/insta_{add_date}', exist_ok=True)
    output_name = image_name.replace('0.jpg', '3.jpg')
    output_path = f"image/insta_{add_date}/insta_{output_name}"
    
    # 수정된 포스터 저장
    new_image.save(output_path)
    print(f"인스타그램용 이미지 저장 완료: {output_path}")


# 대문 페이지 만드는 함수 
def make_first_page(titles):
    # 폴더 경로 정의
    add_date = time.strftime('%Y%m%d')
    base_dir = os.getcwd()
    folder_path = os.path.join(base_dir, 'image', f"poster_{add_date}")

    # 0.jpg로 끝나는 이미지 파일 목록 가져오기
    image_files = [f for f in os.listdir(folder_path) if f.endswith('0.jpg')]
    image_count = len(image_files)

    # 인스타그램 정사각형 이미지 크기 (예: 1080x1080)
    canvas_size = (1080, 1080)

    # 새 캔버스 생성 (흰색 배경)
    canvas = Image.new('RGB', canvas_size, 'white')

    # 각 이미지의 너비 계산
    image_width = canvas_size[0] // image_count

    for i, image_file in enumerate(image_files):
        # 이미지 열기
        img_path = os.path.join(folder_path, image_file)
        img = Image.open(img_path)
        
        # 이미지 리사이즈 (캔버스 높이에 맞추고 너비는 비율 유지)
        aspect_ratio = img.width / img.height
        new_height = canvas_size[1]
        new_width = int(new_height * aspect_ratio)
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # 이미지를 캔버스에 붙이기
        x_offset = i * image_width
        # 이미지 좌측을 기준으로 크롭
        img_cropped = img.crop((0, 0, image_width, new_height))
        
        canvas.paste(img_cropped, (x_offset, 0))


    # 캔버스에 이미지를 붙인 후, 반투명 검은색 필터 추가
    overlay = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([(0, 0), canvas_size], fill=(0, 0, 0, 128))  # 128은 투명도 (0-255)
    canvas = Image.alpha_composite(canvas.convert('RGBA'), overlay)
    canvas = canvas.convert('RGB')  # JPEG 저장을 위해 RGB로 변환

    # 텍스트 추가
    draw = ImageDraw.Draw(canvas)

    # 폰트 설정
    base_dir = os.getcwd()
    font_name = 'DX헤드01Light.ttf'
    font_path = os.path.join(base_dir, 'font', font_name)

    # 폰트 크기를 2배로 설정
    font_size_large = 100 
    font_size_small = 60
    font_large = ImageFont.truetype(font_path, font_size_large)
    font_small = ImageFont.truetype(font_path, font_size_small)

    # 테두리가 있는 텍스트를 그리는 함수
    def draw_text_with_outline(draw, text, position, font, text_color, outline_color):
        x, y = position
        # 테두리 그리기
        draw.text((x-1, y-1), text, font=font, fill=outline_color)
        draw.text((x+1, y-1), text, font=font, fill=outline_color)
        draw.text((x-1, y+1), text, font=font, fill=outline_color)
        draw.text((x+1, y+1), text, font=font, fill=outline_color)
        # 텍스트 그리기
        draw.text((x, y), text, font=font, fill=text_color)

    # 텍스트 추가 (테두리 포함)
    draw_text_with_outline(draw, "최신 개봉 영화", (40, canvas_size[1] -160 -(80*len(titles))), font_large, (255, 255, 255), (0, 0, 0))
    for i in range(len(titles)):
        draw_text_with_outline(draw, f"#{titles[i]}", (60, canvas_size[1] - 120-(len(titles)-i-1)*80), font_small, (255, 255, 255), (0, 0, 0))

    # 결과 이미지 저장
    os.makedirs(f'image/insta_{add_date}', exist_ok=True)
    output_path = f"image/insta_{add_date}/00_first_page.jpg"
    canvas.save(output_path)
