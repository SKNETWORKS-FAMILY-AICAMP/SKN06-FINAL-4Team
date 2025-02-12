import json
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import os
import random


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


def insta_post_1(movie_name, tagline):
    """
    카드뉴스 이미지 생성 함수입니다. Temp_No_1
    - 배경 이미지: 스틸컷
    - 텍스트: 영화 제목 (#영화제목), 한줄 리뷰 (tagline)
    - 텍스트가 이미지 크기를 넘어서면 자동으로 줄바꿈 + 중앙 정렬
    """
    background_image_path = f"images/{movie_name}_stillcut.jpg"
    output_path = f"insta_post/{movie_name}_card_news.jpg"

    # 배경 이미지 열기
    try:
        background = Image.open(background_image_path)
        background = background.resize((800, 800))
    except IOError:
        print(f"❌ 배경 이미지를 불러올 수 없습니다: {background_image_path}")
        return

    # 그리기 컨텍스트 생성
    draw = ImageDraw.Draw(background)

    # 이미지 크기
    width, height = background.size
    border_width = 10  # 하단 배경 여백
    new_height = height + border_width  # 최종 이미지 크기

    # 폰트 설정
    font_path = "C:/USERS/PLAYDATA/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/Katuri.ttf"
    try:
        title_font = ImageFont.truetype(font_path, int(width * 0.080))  # 제목 폰트 크기
        tagline_font = ImageFont.truetype(font_path, int(width * 0.040))  # 서브 텍스트 크기
    except IOError:
        print("❌ 폰트를 찾을 수 없습니다. 기본 폰트 사용")
        title_font = tagline_font = ImageFont.load_default()

    # 📌 텍스트 크기 조절 & 줄바꿈 적용
    max_text_width = int(width * 0.75)  # 텍스트 최대 너비 (75% 이미지 너비)
    wrapped_title_lines = wrap_text_centered(f"# {movie_name}", title_font, max_text_width)  # 영화 제목 줄바꿈
    wrapped_tagline_lines = wrap_text_centered(f'"{tagline}"', tagline_font, max_text_width)  # 태그라인 줄바꿈

    # 텍스트 위치 설정
    title_total_height = sum(title_font.getbbox(line)[3] for line in wrapped_title_lines)
    tagline_total_height = sum(tagline_font.getbbox(line)[3] for line in wrapped_tagline_lines)

    total_text_height = title_total_height + tagline_total_height   # 제목 + 태그라인 + 여백
    start_y = (height - total_text_height) * 0.9  # 전체 텍스트를 중앙 정렬

    # 📌 텍스트 테두리 포함 출력 함수
    def draw_text_with_outline(draw, x, y, text, font, text_color, outline_color, outline_width=2):
        """
        - 테두리가 있는 텍스트 출력
        - x, y 위치에 검은색 테두리를 먼저 그린 후 흰색 본문 출력
        """
        for i in range(-outline_width, outline_width+1):
            for j in range(-outline_width, outline_width+1):
                draw.text((x+i, y+j), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=text_color)

    # 📌 하얀 상자 크기 조정 (기존 로직 유지)
    background_box_y = start_y + (title_total_height * (2/3))  # 제목 크기의 2/3 지점부터
    background_box = [
        0,                    # 왼쪽 끝
        background_box_y,      # 시작 지점 (제목의 2/3 지점)
        width,                # 오른쪽 끝
        new_height            # 이미지 하단까지
    ]
    draw.rectangle(background_box, fill="white")

    # 📌 제목 텍스트 출력 (중앙 정렬)
    current_y = start_y
    for line in wrapped_title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        x = (width - (bbox[2] - bbox[0])) / 2  # 중앙 정렬
        draw_text_with_outline(draw, x, current_y, line, title_font, (255, 255, 255), (0, 0, 0))
        current_y += bbox[3] - bbox[1] + 5  # 줄 간격 추가

    # 📌 태그라인 텍스트 출력 (중앙 정렬)
    current_y += 20  # 제목과 태그라인 사이 여백 추가
    for line in wrapped_tagline_lines:
        bbox = draw.textbbox((0, 0), line, font=tagline_font)
        x = (width - (bbox[2] - bbox[0])) / 2  # 중앙 정렬
        draw_text_with_outline(draw, x, current_y, line, tagline_font, (255, 255, 255), (0, 0, 0))
        current_y += bbox[3] - bbox[1] + 5  # 줄 간격 추가

    # ✅ 최종 이미지 저장 (예외 처리 추가)
    try:
        background.save(output_path)
        print(f"✅ 카드뉴스 이미지 저장 완료: {output_path}")
    except Exception as e:
        print(f"❌ 이미지 저장 실패: {e}")


def split_text(text):
    """ '첫 번째 문장 : 나머지 문장'을 처리하여 3줄로 나눔 """
    if ":" not in text:
        print("🚨 입력 형식이 올바르지 않습니다. '문장 : 문장' 형식으로 입력하세요.")
        return None, None, None

    first_part, remaining_text = text.split(":", 1)
    words = remaining_text.strip().split()
    
    total_words = len(words)
    split1 = total_words // 2  # 두 번째 줄과 세 번째 줄은 비슷한 글자 수로 나눔
    
    line1 = first_part.strip()
    line2 = " ".join(words[:split1])
    line3 = " ".join(words[split1:])
    
    return line1, line2, line3


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


def create_post_door(text, image_folder):
    """
    인스타 게시물 대문을 만드는 템플릿 함수입니다.
    - 게시물 제목 3줄 변경
    - : 기준 첫번째 줄은 작은 글씨 적용
    - 랜덤한 배경 이미지 위에 3D 효과 및 빛 반사 효과 적용 (중앙 정렬 포함) 
    """
    output_path = f"insta_post/movie_post_Door.jpg"

    # ✅ 랜덤 배경 이미지 선택
    background_image_path = get_random_background_image(image_folder)
    if background_image_path is None:
        return

    # 배경 이미지 열기
    try:
        background = Image.open(background_image_path).convert("RGBA")
        background = background.resize((800, 800))
        background = background.filter(ImageFilter.GaussianBlur(2))  # 블러 적용 (조금 더 부드럽게)
    except IOError:
        print("🚨 배경 이미지를 불러올 수 없습니다.")
        return

    draw = ImageDraw.Draw(background)

    # ✅ **배경 어둡게 하기 (반투명한 검은색 레이어 추가)**
    darken_intensity = 120  # ✅ 배경 어두운 정도 (값이 클수록 더 어두움)
    dark_overlay = Image.new("RGBA", background.size, (0, 0, 0, darken_intensity))
    background = Image.alpha_composite(background, dark_overlay)

    # 📌 **폰트 크기 설정**
    font_size = 100  # 테스트용 폰트 크기
    first_line_font_size = int(font_size * 0.5)  # 첫 번째 줄 폰트 크기 축소
    font_path = "C:/USERS/PLAYDATA/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/KATURI.ttf"
    font_large = ImageFont.truetype(font_path, font_size)
    font_small = ImageFont.truetype(font_path, first_line_font_size)

    # 문장 줄바꿈 처리 (총 3줄)
    line1, line2, line3 = split_text(text)
    if line1 is None:
        return

    # ✅ **각 줄의 가로 중앙 정렬을 위해 텍스트 크기 계산**
    def get_text_x(line, font):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        return (background.size[0] - text_width) // 2

    # ✅ **문장 전체를 이미지 중앙에 배치**
    total_text_height = first_line_font_size + (font_size * 2) + 30  # 첫 줄 + 나머지 2줄 + 간격
    start_y = (background.size[1] - total_text_height) // 2  # 전체 높이 기준 중앙 정렬

    text_x1 = get_text_x(line1, font_small)
    text_x2 = get_text_x(line2, font_large)
    text_x3 = get_text_x(line3, font_large)

    text_y1 = start_y
    text_y2 = start_y + first_line_font_size + 15  # 첫 줄과 두 번째 줄 사이 간격
    text_y3 = text_y2 + font_size + 10  # 두 번째 줄과 세 번째 줄 사이 간격

    # --- (1) 그림자 추가 (첫 줄 포함) ---
    shadow_img = Image.new("RGBA", background.size, (255, 255, 255, 0))
    shadow_color = (145, 117, 94, 200)  # 그림자 색상
    shadow_offset = 5  # 그림자 거리 조정
    shadow_draw = ImageDraw.Draw(shadow_img)

    def draw_shadow(draw_obj, x, y, text, font):
        draw_obj.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)

    draw_shadow(shadow_draw, text_x1, text_y1, line1, font_small)  # 첫 줄 그림자
    draw_shadow(shadow_draw, text_x2, text_y2, line2, font_large)
    draw_shadow(shadow_draw, text_x3, text_y3, line3, font_large)

    # --- (2) 윤곽선 추가 (첫 번째 줄 제외) ---
    outline_img = Image.new("RGBA", background.size, (255, 255, 255, 0))
    outline_draw = ImageDraw.Draw(outline_img)
    outline_color = (255, 255, 255, 255)
    outline_width = 9  # 윤곽선 두께

    def draw_outline(draw_obj, x, y, text, font):
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw_obj.text((x + dx, y + dy), text, font=font, fill=outline_color)

    draw_outline(outline_draw, text_x2, text_y2, line2, font_large)
    draw_outline(outline_draw, text_x3, text_y3, line3, font_large)

    # --- (3) 첫 번째 줄 (연한 노란색 적용, 윤곽선 없음) ---
    text_img = Image.new("RGBA", background.size, (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_img)
    pale_yellow = (255, 255, 237)
    text_draw.text((text_x1, text_y1), line1, font=font_small, fill=pale_yellow)

    # --- (4) 두 번째 및 세 번째 줄  ---
    base_color = (255, 48, 120)  # 찐분홍
    line3_color = (255, 99, 154)  # 덜 찐분홍
    text_draw.text((text_x2, text_y2), line2, font=font_large, fill=base_color)
    text_draw.text((text_x3, text_y3), line3, font=font_large, fill=line3_color)

    # --- (5) 최종 합성 ---
    result = Image.alpha_composite(background, outline_img)
    result = Image.alpha_composite(result, shadow_img)
    result = Image.alpha_composite(result, text_img)

    # ✅ 최종 이미지 저장 (예외 처리 추가)
    try:
        result = result.convert("RGB")  # ✅ RGBA → RGB 변환
        result.save(output_path, format="JPEG")  # ✅ JPEG 형식으로 저장
    except Exception as e:
        print(f"❌ 이미지 저장 실패: {e}")