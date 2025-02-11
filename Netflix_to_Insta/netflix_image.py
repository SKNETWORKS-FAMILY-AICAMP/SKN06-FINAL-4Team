import os
import time
from datetime import datetime

import requests
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter

# 키노라이즈에서 포스터 이미지 가져오는 함수
def get_netflix_image(movie_name):
    try:
        # ChromeOptions 객체 생성
        chrome_options = Options()

        # headless 모드 설정
        chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
        chrome_options.add_argument('--disable-gpu')
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

        add_date = time.strftime('%Y%m%d')
        os.makedirs(f'image/poster_{add_date}', exist_ok=True)

        # 이미지 저장
        for index, img in enumerate(image_elements):
            img_url = img.get_attribute("src")  # 이미지의 URL 가져오기
            if img_url:  # 유효한 URL인지 확인
                response = requests.get(img_url)
                if response.status_code == 200:
                    # 파일 저장 경로 설정
                    image_name = movie_name.replace(':','')
                    file_name = f"image/poster_{add_date}/img_{image_name}.jpg"
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


# 인스타 이미지 생성 함수
def insta_netflix(title, tagline, ori='n'):
    # 포스터 열기
    image_name = title.replace(':','')

    add_date = time.strftime('%Y%m%d')
    poster = Image.open(f"image/poster_{add_date}/img_{image_name}.jpg")
    
    # 이미지를 정사각형으로 만들기 (가로 길이에 맞춤)
    width, height = poster.size
    new_height = width
    
    # 이미지의 상단을 기준으로 크롭
    poster = poster.crop((0, 0, width, new_height))
    
    # 이미지에 테두리 추가
    border_width = int(width * 0.02)  # 이미지 너비의 2%를 테두리 너비로 설정
    poster = ImageOps.expand(poster, border=border_width, fill='white')
    
    # 테두리 안쪽으로 이미지 크롭
    poster = poster.crop((border_width, border_width, width + border_width, new_height + border_width))
    
    # Netflix 로고 추가
    if ori != 'n':
        netflix_logo = Image.open("logo/Netflix-N.png").convert('RGBA')
        logo_size = int(width * 0.1)  # 포스터의 10% 크기
        netflix_logo = netflix_logo.resize((logo_size, logo_size))
        logo_position = (width - logo_size - border_width, border_width)
        poster.paste(netflix_logo, logo_position, netflix_logo)
    
    # # ni_movie_mu.jpg 추가
    # ni_movie_mu = Image.open("logo/5-cutout.png")
    # ni_movie_mu_size = int(width * 0.1)  # 포스터의 10% 크기
    # ni_movie_mu = ni_movie_mu.resize((ni_movie_mu_size, ni_movie_mu_size))
    # ni_movie_mu_position = (border_width, border_width)
    # poster.paste(ni_movie_mu, ni_movie_mu_position)

    # 그리기 컨텍스트 생성
    draw = ImageDraw.Draw(poster)
    
    # 폰트 선택 및 크기 설정
    font_path = "/font/Katuri.otf"
    title_font_size = int(width * 0.080)
    tagline_font_size = int(width * 0.040)
    title_font = ImageFont.truetype(font_path, title_font_size)
    tagline_font = ImageFont.truetype(font_path, tagline_font_size)
    
    # 텍스트 크기 계산
    title_bbox = draw.textbbox((0, 0), f'#{title}', font=title_font)
    tagline_bbox = draw.textbbox((0, 0), f'"{tagline}"', font=tagline_font)
    
    # 텍스트 위치 지정 (가운데 정렬, title은 tagline 바로 위에)
    tagline_y = new_height * 0.93  # 하단에서 10% 위치
    title_y = tagline_y - (title_bbox[3] - title_bbox[1]) - 15  # tagline 위 10픽셀
    
    title_x = (width - (title_bbox[2] - title_bbox[0])) / 2
    tagline_x = (width - (tagline_bbox[2] - tagline_bbox[0])) / 2
    
    # 텍스트 추가 함수 (테두리 포함, title은 더 두꺼운 테두리)
    def draw_text_with_outline(draw, x, y, text, font, text_color, outline_color, outline_width=2):
        # 테두리 그리기
        for i in range(-outline_width, outline_width+1):
            for j in range(-outline_width, outline_width+1):
                draw.text((x+i, y+j), text, font=font, fill=outline_color)
        # 텍스트 그리기
        draw.text((x, y), text, font=font, fill=text_color)
    
    #흰색 배경 추가 (제목 크기의 2/3 지점부터 하단까지)
    start_y = title_y + (title_bbox[3] - title_bbox[1]) * (2/3)
    background_box = [
        0,                      # 왼쪽 끝
        start_y,                # 시작 지점 (제목의 2/3 지점)
        width,                  # 오른쪽 끝
        new_height + border_width  # 이미지 하단까지
    ]
    draw.rectangle(background_box, fill="white")
    
    # 텍스트 추가 (흰색 글씨, 검정 테두리)
    draw_text_with_outline(draw, title_x, title_y, f'# {title}', title_font, (255, 255, 255), (0, 0, 0))
    draw_text_with_outline(draw, tagline_x, tagline_y, f'"{tagline}"', tagline_font, (255, 255, 255), (0, 0, 0))

    add_date = time.strftime('%Y%m%d')
    os.makedirs(f'image/insta_{add_date}', exist_ok=True)

    # 수정된 포스터 저장
    now = time.strftime('%Y%m%d%H%M')
    output_path = f"image/insta_{add_date}/{now}_insta_{image_name}.jpg"
    poster.save(output_path)


# 대문페이지 생성 함수 
def make_first_page(list_input):

    def get_month_and_week():
        today = datetime.now()
        
        # 몇 번째 달인지 구하기
        month = today.month
        
        # 몇 번째 주인지 구하기
        week_of_year = today.isocalendar()[1]
        
        # 해당 월의 첫 주 구하기
        first_day_of_month = datetime(today.year, today.month, 1)
        first_week_of_month = first_day_of_month.isocalendar()[1]
        
        # 월의 몇 번째 주인지 계산
        week_of_month = week_of_year - first_week_of_month + 1
        
        return f'{month}월 {week_of_month}주차'


    def split_text(text):
        line1, line2 = text.split(', ')
        line3 = get_month_and_week()
        return line1, line2, line3


    def get_random_background_image(image_folder):
        """ 폴더 내에서 랜덤한 배경 이미지 선택 """
        images = [f for f in os.listdir(image_folder) if f.lower().endswith((".jpg"))]
        print('이미지를 선택하였습니다.')
        return os.path.join(image_folder, random.choice(images))


    def create_3d_text_with_light_effect(text, font_path, image_folder, output_folder, shadow_color, shadow_offset, outline_width, font_size, darken_intensity=120):
        """ 랜덤한 배경 이미지 위에 3D 효과 및 빛 반사 효과 적용 (중앙 정렬 포함) """
        # 랜덤 배경 이미지 선택
        background_image_path = get_random_background_image(image_folder)
        output_path = os.path.join(output_folder, "000_insta.jpg")

        # 배경 이미지 열기
        try:
            background = Image.open(background_image_path).convert("RGBA")
            background = background.resize((800, 800))
            background = background.filter(ImageFilter.GaussianBlur(2))  # 블러 적용 (조금 더 부드럽게)
        except IOError:
            print("배경 이미지를 불러올 수 없습니다.")
            return

        draw = ImageDraw.Draw(background)

        # 배경 어둡게 하기 (반투명한 검은색 레이어 추가)
        dark_overlay = Image.new("RGBA", background.size, (0, 0, 0, darken_intensity))
        background = Image.alpha_composite(background, dark_overlay)

        # 폰트 크기 적용
        font = ImageFont.truetype(font_path, font_size)

        # 문장 줄바꿈 처리 (무조건 3줄)
        line1, line2, line3 = split_text(text)

        # 각 줄의 가로 중앙 정렬을 위해 텍스트 크기 계산
        def get_text_x(line):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            return (background.size[0] - text_width) // 2

        # 문장 전체를 이미지 중앙에 배치
        total_text_height = font_size * 3 + 30  # 줄 3개 + 간격
        start_y = (background.size[1] - total_text_height) // 2  # 전체 높이 기준 중앙 정렬

        text_x1, text_x2 = get_text_x(line1), get_text_x(line2)
        text_x3 = get_text_x(line3)

        text_y1, text_y2, text_y3 = start_y, start_y + font_size + 15, start_y + 2 * (font_size + 15)

        # --- (1) 윤곽선(하얀색) 추가 ---
        outline_img = Image.new("RGBA", background.size, (255, 255, 255, 0))
        outline_draw = ImageDraw.Draw(outline_img)
        outline_color = (255, 255, 255, 255)

        def draw_outline(draw_obj, x, y, text):
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw_obj.text((x + dx, y + dy), text, font=font, fill=outline_color)

        draw_outline(outline_draw, text_x1, text_y1, line1)
        draw_outline(outline_draw, text_x2, text_y2, line2)
        draw_outline(outline_draw, text_x3, text_y3, line3)

        # --- (2) 그림자 추가 ---
        shadow_img = Image.new("RGBA", background.size, (255, 255, 255, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)

        def draw_shadow(draw_obj, x, y, text):
            draw_obj.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)

        draw_shadow(shadow_draw, text_x1, text_y1, line1)
        draw_shadow(shadow_draw, text_x2, text_y2, line2)
        draw_shadow(shadow_draw, text_x3, text_y3, line3)

        text_img = Image.new("RGBA", background.size, (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_img)

        # --- (4) 첫번째 및 두번째 줄  ---
        base_color = (229, 9, 20)  # 넷플릭스 레드
        line3_color = (178,7,16)  # 넷플릭스 다크 레드
        pale_yellow = (255, 255, 150) 
        text_draw.text((text_x1, text_y1), line1, font=font, fill=base_color)
        text_draw.text((text_x2, text_y2), line2, font=font, fill=line3_color)
        text_draw.text((text_x3, text_y3), line3, font=font, fill=pale_yellow)

        # --- (5) 최종 합성 ---
        result = Image.alpha_composite(background, outline_img)
        result = Image.alpha_composite(result, shadow_img)
        result = Image.alpha_composite(result, text_img)

        # 이미지 저장
        result = result.convert('RGB')
        result.save(output_path, 'JPEG', quality=95)
        print(f"이미지가 저장되었습니다: {output_path}")

    # 함수 시작
    font_path = "/font/Katuri.otf"
    add_date = time.strftime('%Y%m%d')
    base_dir = os.getcwd()
    image_folder = os.path.join(base_dir,'image', f'poster_{add_date}')  # 랜덤 배경 이미지가 저장된 폴더
    output_folder = os.path.join(base_dir, 'image', f'insta_{add_date}')  # 이미지 저장 폴더
    print(image_folder)

    shadow_color = (145, 117, 94, 200)  # 그림자 색상
    shadow_offset = 5  # 그림자 거리 조정
    outline_width = 9  # 윤곽선 두께
    darken_intensity = 120  # 배경 어두운 정도 (값이 클수록 더 어두움)

    if list_input == '1':
        text_input = '넷플릭스, "지금 많이보는"'
    elif list_input == '2':
        text_input = '넷플릭스, "주간 순위"'
    elif list_input == '3':
        text_input = '넷플릭스, "신작 영화/시리즈"'

    optimal_font_size = 105  # 테스트용 폰트 크기

    create_3d_text_with_light_effect(
        text_input, font_path, image_folder, output_folder,
        shadow_color=shadow_color,
        shadow_offset=shadow_offset,
        outline_width=outline_width,
        font_size=optimal_font_size,
        darken_intensity=darken_intensity
    )
