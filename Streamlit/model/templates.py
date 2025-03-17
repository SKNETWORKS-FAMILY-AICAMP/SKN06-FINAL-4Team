import json
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import os
import random
import pandas as pd


def find_review_data(json_path):
    """
    json 파일에서 "리뷰 한 줄" KEY를 찾아 영화 제목과 한줄 리뷰를 추출하는 함수입니다.
    - 각 영화 제목과 리뷰를 리스트로 반환
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # "리뷰 한 줄" KEY에서 영화 제목과 리뷰 추출
    movie_post_reviews = data.get("리뷰 한 줄", {})

    # LIST로 반환
    movie_data = [(title, review) for title, review in movie_post_reviews.items()]
        
    return movie_data  # 영화 제목과 리뷰 리스트 반환


def find_title_data(json_path):
    """
    json 파일에서 "전체 게시글 제목" KEY를 찾아 값을 반환하는 함수입니다.
    - 게시물 대문 만드는 과정에서 사용
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # "전체 게시글 제목" KEY에서 값 반환
    movie_post_title = data.get("전체 게시글 제목", ())

    return movie_post_title


def wrap_text_centered(text, font, max_width):
    """
    텍스트 자동 줄바꿈(비슷한 길이 유지) 및 중앙 정렬하는 함수입니다.
    - text: 입력 텍스트
    - font: 사용할 폰트 객체
    - max_width: 허용되는 최대 너비
    - 줄바꿈 시 최대한 비슷한 길이 유지 + 중앙 정렬
    """
    words = text.split()
    wrapped_lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)  # 텍스트 크기 계산

        if bbox[2] > max_width:  # 허용 너비 초과 시 줄바꿈
            wrapped_lines.append(current_line.strip())
            current_line = word
        else:
            current_line = test_line

    wrapped_lines.append(current_line.strip())  # 마지막 줄 추가
    return wrapped_lines  # 줄바꿈된 텍스트 리스트 반환


def wrap_text_balanced(text, txt_font, txt_max_width):
    """
    텍스트 자동 줄바꿈 (비슷한 글자 수 유지).
    - text: 입력 텍스트 - 영화 제목
    - font: 사용할 폰트 객체 (사용은 안 하지만 일관성을 위해 유지)
    - max_chars_per_line: 한 줄에 들어갈 최대 글자 수
    """
    words = text.split()
    wrapped_lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = txt_font.getbbox(test_line)  # 텍스트 크기 계산

        if bbox[2] > txt_max_width:  # 허용 너비 초과 시 줄바꿈
            wrapped_lines.append(current_line.strip())
            current_line = word
        else:
            current_line = test_line

    wrapped_lines.append(current_line.strip())  # 마지막 줄 추가
    return wrapped_lines  # 줄바꿈된 텍스트 리스트 반환



def draw_bold_text(draw, position, text, font, fill, thickness=2):
    """
    글씨를 두껍게 보이도록 여러 번 그리는 함수
    - position: (x, y) 좌표
    - thickness: 얼마나 두껍게 할지 (값이 클수록 두꺼워짐)
    """
    x, y = position
    offsets = [-thickness, 0, thickness]  # 이동 범위
    for dx in offsets:
        for dy in offsets:
            draw.text((x + dx, y + dy), text, font=font, fill=fill)
    draw.text((x, y), text, font=font, fill=fill)  # 중앙 본문


# 엑셀 파일 읽어서 개봉일 추출하는 함수
def get_movie_date(movie_name):
    # 엑셀 파일 읽기
    EXCEL_FILE_PATH = "recommend_data/Movie_DB_Final_3387.xlsx"
    df = pd.read_excel(EXCEL_FILE_PATH).fillna("")

    # 영화 제목으로 데이터 필터링
    movie_data = df[df['영화 제목'] == movie_name]
    
    if movie_data.empty:
        print(f"'{movie_name}'에 해당하는 영화를 찾을 수 없습니다.")
        return None
    
    # 개봉일을 연도로 변환하여 반환
    try:
        year = pd.to_datetime(movie_data['개봉일'].iloc[0]).year
        return year
    except Exception as e:
        print(f"개봉일을 처리하는 중 오류가 발생했습니다: {e}")
        return None
    
# 엑셀 파일 읽어서 별점 추출하는 함수
def get_mumuscore(movie_name):
    """
    주어진 영화 제목에 해당하는 별점을 엑셀에서 찾아 반환하는 함수.
    """
    EXCEL_FILE_PATH = "recommend_data/Movie_DB_Final_3387.xlsx"

    try:
        # 엑셀 파일 읽기
        df = pd.read_excel(EXCEL_FILE_PATH).fillna("")

        # 영화 제목으로 데이터 필터링
        movie_data = df[df['영화 제목'] == movie_name]

        if movie_data.empty:
            print(f"⚠ '{movie_name}'에 해당하는 영화를 찾을 수 없습니다.")
            return None

        # ✅ 별점 값을 가져오되, 첫 번째 값만 반환 (.iloc[0] 사용)
        score = movie_data['별점'].iloc[0]

        # ✅ 예외 처리: 데이터가 숫자가 아닐 경우 None 반환
        if isinstance(score, (int, float)):
            return score
        else:
            print(f"⚠ '{movie_name}'의 별점 데이터가 유효하지 않습니다: {score}")
            return None

    except Exception as e:
        print(f"❌ 무무스코어를 처리하는 중 오류가 발생했습니다: {e}")
        return None


def insta_post_1(movie_name, tagline):
    """
    카드뉴스 이미지 생성 함수입니다. Temp_No_1
    - 배경 이미지: 포스터
    - 텍스트: 영화 제목 (#영화제목), 한줄 리뷰 (tagline)
    - 텍스트가 이미지 크기를 넘어서면 자동으로 줄바꿈 + 중앙 정렬
    """
    img_width = 1080
    img_height = 1350
    btm_box_height = 1200
    top_box_height = 400

    sanitized_name = movie_name.replace(":", "").replace('?', '').replace('/', '').replace('<', '').replace('>', '')

    poster_path = f"recommend_data/posters_db/{sanitized_name}_poster.jpg"
    output_path = f"insta_post/{sanitized_name}_card_news.jpg"
    
    poster = Image.open(poster_path).convert("RGBA")
    poster = poster.resize((img_width, img_height))

    btm_gradient = Image.new("RGBA", (img_width, btm_box_height), (0, 0, 0, 0))
    for i in range(btm_box_height):
        alpha = int(300 * (i / btm_box_height))    # 전점 진해지는 효과
        ImageDraw.Draw(btm_gradient).rectangle([(0, i), (img_width, i + 1)], fill=(0, 0, 0, alpha))

    top_gradient = Image.new("RGBA", (img_width, top_box_height), (0, 0, 0, 0))
    for i in range(top_box_height):
        alpha = int(255 * (1-i / top_box_height))    # 전점 옅어지는 효과
        ImageDraw.Draw(top_gradient).rectangle([(0, i), (img_width, i + 1)], fill=(0, 0, 0, alpha))

    # 폰트 설정
    font_path = 'C:/WINDOWS/FONTS/MALGUNSL.TTF'
    title_font = ImageFont.truetype(font_path, 100)
    tagline_font = ImageFont.truetype(font_path, 35)
    date_font = ImageFont.truetype(font_path, 40)
    logo_font = ImageFont.truetype(font_path, 40)

    draw = ImageDraw.Draw(poster)

    title_text = wrap_text_balanced(f'# {movie_name}', title_font, img_width - 200)
    title_x = 50
    title_y = img_height - btm_box_height + 900

    date_text = f'개봉연도 : {get_movie_date(movie_name)} / 무무스코어 : {get_mumuscore(movie_name)} 점'
    date_x = 50
    date_y = img_height - btm_box_height + 835

    tagline_lines = wrap_text_centered(tagline, tagline_font, img_width - 100)
    tagline_x = 50
    tagline_y = img_height - btm_box_height + 710

    logo_text = "NI_MOVIE_MU"
    logo_x = 800
    logo_y = 50

    poster.paste(btm_gradient, (0, img_height - btm_box_height), btm_gradient)
    poster.paste(top_gradient, (0, 0), top_gradient)
    
    draw_bold_text(draw, (logo_x, logo_y), logo_text, logo_font, "silver", thickness=2)

    for title in title_text:
        draw_bold_text(draw, (title_x, title_y), title, title_font, fill="yellow", thickness=4)
        title_y += 120
        title_x += 80

    draw_bold_text(draw, (date_x, date_y), date_text, font=date_font, fill="yellow", thickness=2)

    for line in tagline_lines:
        draw_bold_text(draw, (tagline_x, tagline_y), line, font=tagline_font, fill="white", thickness=1)
        tagline_y += 60


    # ✅ 최종 이미지 저장 (예외 처리 추가)
    poster = poster.convert("RGB")
    try:
        poster.save(output_path, format="JPEG")
        print(f"✅ 카드뉴스 이미지 저장 완료: {output_path}")
    except Exception as e:
        print(f"❌ 이미지 저장 실패: {e}")



def get_random_background_image(image_folder):
    """
    폴더 내에서 랜덤한 배경 이미지 선택하는 함수입니다.
    - 스틸컷 이미지를 대문에 사용하기 위해 사용     
    """
    if not os.path.exists(image_folder):
        print("🚨 이미지 폴더가 존재하지 않습니다.")
        return None

    images = [f for f in os.listdir(image_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    
    if not images:
        print("🚨 이미지 폴더에 사용할 이미지가 없습니다.")
        return None
    
    return os.path.join(image_folder, random.choice(images))



def create_post_door(text, keywords):
    """
    인스타 게시물 대문을 만드는 템플릿 함수입니다.
    - 게시물 제목 3줄로 구성된 문장 받음.
    - : 기준 첫번째 줄은 작은 글씨 적용
    - 랜덤한 배경 이미지 위에 3D 효과 적용 (중앙 정렬 포함) 
    """
    output_path = f"insta_post/movie_post_Door.jpg"

    # ✅ 랜덤 배경 이미지 선택
    img_width = 1080
    img_height = 1350
    box_height = 1200

    background_image_path = get_random_background_image("recommend_data/cache_file/background_images")
    background = Image.open(background_image_path).convert("RGBA")
    background = background.resize((img_width, img_height))

    gradient = Image.new("RGBA", (img_width, box_height), (0, 0, 0, 0))
    for i in range(box_height):
        alpha = int(280 * (i / box_height))    # 전점 진해지는 효과
        ImageDraw.Draw(gradient).rectangle([(0, i), (img_width, i + 1)], fill=(0, 0, 0, alpha))

    background = background.filter(ImageFilter.GaussianBlur(3))  # 블러 적용 (조금 더 부드럽게)

    # ✅ **배경 어둡게 하기 (반투명한 검은색 레이어 추가)**
    darken_intensity = 180  # ✅ 배경 어두운 정도 (값이 클수록 더 어두움)
    dark_overlay = Image.new("RGBA", background.size, (0, 0, 0, darken_intensity))
    background = Image.alpha_composite(background, dark_overlay)

    draw = ImageDraw.Draw(background)

    # 폰트 설정
    font_path = 'C:/WINDOWS/FONTS/MALGUNSL.TTF'
    text_font = ImageFont.truetype(font_path, 80)
    logo_font = ImageFont.truetype(font_path, 40)
    info_font = ImageFont.truetype(font_path, 25)

    post_text = wrap_text_centered(text, text_font, img_width - 100)

    # **각 줄의 가로 중앙 정렬을 위해 텍스트 크기 계산**
    def get_text_x(text, font):
        bbox = font.getmask(text).getbbox()
        text_width = bbox[2] - bbox[0]

        return (background.size[0] - text_width) // 2

    print("[DEBUG] post_text 확인 : ", post_text)
    text_y = img_height - box_height + 650

    logo_text = "NI_MOVIE_MU"
    logo_x = 800
    logo_y = 50

    info_text = f"영화 추천  |  오늘의 키워드 = {keywords}"
    info_y = 1280

    background.paste(gradient, (0, img_height - box_height), gradient)

    draw_bold_text(draw, (logo_x, logo_y), logo_text, logo_font, "silver", thickness=2)

    for post in post_text:
        draw_bold_text(draw, (get_text_x(post, text_font), text_y), post, text_font, fill="white", thickness=2)
        text_y += 120

    draw_bold_text(draw, (get_text_x(info_text, info_font), info_y), info_text, info_font, fill="white", thickness=1)


    # ✅ 최종 이미지 저장 (예외 처리 추가)
    background = background.convert("RGB")
    try:
        background.save(output_path, format="JPEG")
        print(f"✅ 카드뉴스 이미지 저장 완료: {output_path}")
    except Exception as e:
        print(f"❌ 이미지 저장 실패: {e}")


