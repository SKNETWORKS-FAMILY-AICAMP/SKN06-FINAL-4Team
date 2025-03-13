import os
import time
from datetime import datetime
import random
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter


base_dir = os.getcwd()
add_date = time.strftime('%Y%m%d')
input_path = os.path.join(base_dir, 'image', f'original_{add_date}')
output_path = os.path.join(base_dir, 'image', f'insta_{add_date}')
os.makedirs(output_path, exist_ok=True)

font_path = 'C:/Users/Playdata/AppData/Local/Microsoft/Windows/Fonts/DX헤드01Light.ttf'


# 인스타 이미지 생성 함수
def insta_boxoffice_dx(title, watches, tot_watches, rank):
    try:
        # 포스터 열기
        image_name = title.replace(':','').replace('?', '').replace('/', '').replace('<', '').replace('>', '')
        image_path = os.path.join(input_path, f'img_{image_name}_0.jpg')
        poster = Image.open(image_path)

        tagline = f'{rank}위 {watches}명 / 누적 {tot_watches}명'
        print(tagline)

        # 이미지를 정사각형으로 만들기 (가로 길이에 맞춤)
        width, height = poster.size
        new_height = width
        
        # 이미지의 상단을 기준으로 크롭
        poster = poster.crop((0, 0, width, new_height))
        poster = poster.resize((1080, 1080))  # 인스타그램 정사각형 크기

        width, height = poster.size
        new_height = width
        
        # 그리기 컨텍스트 생성
        draw = ImageDraw.Draw(poster)
        
        # 폰트 선택 및 크기 설정
        title_font_size = int(width * 0.06)
        tagline_font_size = int(width * 0.045)
        title_font = ImageFont.truetype(font_path, title_font_size)
        tagline_font = ImageFont.truetype(font_path, tagline_font_size)
        
        # 텍스트 크기 계산
        title_bbox = draw.textbbox((0, 0), f'#{title}', font=title_font)
        tagline_bbox = draw.textbbox((0, 0), f'"{tagline}"', font=tagline_font)
        
        # 텍스트 위치 지정 (가운데 정렬, title은 tagline 바로 위에)
        tagline_y = new_height * 0.92  # 하단에서 10% 위치
        title_y = tagline_y - (title_bbox[3] - title_bbox[1]) - 25  # tagline 위 10픽셀
        
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
        start_y = title_y + (title_bbox[3] - title_bbox[1]) * (2/3) - 90
        background_box = [
            0,                      # 왼쪽 끝
            start_y,                # 시작 지점 (제목의 2/3 지점)
            width,                  # 오른쪽 끝
            new_height  # 이미지 하단까지
        ]
        
        draw.rectangle(background_box, fill=(0, 0, 0))
        
        # 텍스트 추가 (흰색 글씨, 검정 테두리)
        draw_text_with_outline(draw, title_x, title_y, f'#{title}', title_font, (255, 255, 255), (0, 0, 0))
        draw_text_with_outline(draw, tagline_x, tagline_y, tagline, tagline_font, (255, 255, 255), (0, 0, 0))

        # 수정된 포스터 저장
        save_as = os.path.join(output_path, f'No0{10-rank} insta_{image_name}.jpg')
        poster.save(save_as)

    except:
        print(f'{image_name}의 게시물 생성에 실패하였습니다.')


# 주간순위 리스트 페이지 만드는 함수 
def make_list_page_dx(movies, page):
    # 폴더 내 이미지 파일 목록 가져오기
    image_files = [f for f in os.listdir(input_path) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

    # 랜덤으로 이미지 선택
    random_image = random.choice(image_files)
    image_path = os.path.join(input_path, random_image)

    # 이미지 열기 및 크기 조정
    image = Image.open(image_path)
    image = image.resize((1080, 1080))  # 인스타그램 정사각형 크기

    # 이미지에 블러 효과 적용
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=5))

    # 그리기 객체 생성
    draw = ImageDraw.Draw(blurred_image)

    # 영화 제목 리스트 (예시)
    movie_titles = [movies[0], movies[1], movies[2], movies[3], movies[4]]

    # 폰트 설정 (폰트 파일 경로를 적절히 수정해주세요)
    font = ImageFont.truetype(font_path, 42)

    # 직사각형 및 텍스트 그리기
    for i, title in enumerate(movie_titles):
        # 직사각형 위치 및 크기 계산
        y_position = 200 + i * 150
        rectangle_shape = [(100, y_position), (980, y_position + 100)]
        
        # 반투명 흰색 직사각형 그리기
        draw.rectangle(rectangle_shape, fill=(0, 0, 0, 128))

        # 텍스트 그리기
        if page == 'z0':
            draw.text((120, y_position + 30), f' {i+1}위 {title}', font=font, fill=(255, 255, 255, 255))
        elif page == 'z1':
            draw.text((120, y_position + 30), f' {i+6}위 {title}', font=font, fill=(255, 255, 255, 255))

    # 이미지 저장
    save_as = os.path.join(output_path, f'{page}_insta.jpg')
    blurred_image.save(save_as)
    print('영화 순위 페이지를 생성하였습니다.')


# 대문페이지 생성 함수 
def make_first_page_dx():

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
        total_text_height = font_size * 2 + 30  # 줄 3개 + 간격
        start_y = (background.size[1] - total_text_height) // 2 + 270 # 전체 높이 기준 중앙 정렬

        # text_x1, text_x2 = get_text_x(line3), get_text_x(line2)
        text_x1 = text_x2 = 40
        # text_x3 = get_text_x(line3)

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

        draw_outline(outline_draw, text_x1, text_y1, line3)
        draw_outline(outline_draw, text_x2, text_y2, line2)
        # draw_outline(outline_draw, text_x3, text_y3, line3)

        # --- (2) 그림자 추가 ---
        shadow_img = Image.new("RGBA", background.size, (255, 255, 255, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)

        def draw_shadow(draw_obj, x, y, text):
            draw_obj.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)

        draw_shadow(shadow_draw, text_x1, text_y1, line3)
        draw_shadow(shadow_draw, text_x2, text_y2, line2)
        # draw_shadow(shadow_draw, text_x3, text_y3, line3)

        text_img = Image.new("RGBA", background.size, (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_img)

        # --- (4) 첫번째 및 두번째 줄  ---
        base_color = (80, 118, 219)  # kobis 파랑
        line3_color = (75, 93, 141)  # kobis 진한 파랑
        pale_yellow = (255, 255, 150)
        text_draw.text((text_x1, text_y1), line3, font=font, fill='black')
        text_draw.text((text_x2, text_y2), line2, font=font, fill='black')
        # text_draw.text((text_x3, text_y3), line3, font=font, fill=pale_yellow)

        # --- (5) 최종 합성 ---
        result = Image.alpha_composite(background, outline_img)
        result = Image.alpha_composite(result, shadow_img)
        result = Image.alpha_composite(result, text_img)

        # 이미지 저장
        result = result.convert('RGB')
        result.save(output_path, 'JPEG', quality=95)
        print(f"이미지가 저장되었습니다: {output_path}")

    # 함수 시작
    print(input_path)

    shadow_color = (145, 117, 94, 200)  # 그림자 색상
    shadow_offset = 3  # 그림자 거리 조정
    outline_width = 3  # 윤곽선 두께
    darken_intensity = 120  # 배경 어두운 정도 (값이 클수록 더 어두움)

    text_input = 'KOBIS, 박스오피스 순위'

    optimal_font_size = 60  # 테스트용 폰트 크기

    create_3d_text_with_light_effect(
        text_input, font_path, input_path, output_path,
        shadow_color=shadow_color,
        shadow_offset=shadow_offset,
        outline_width=outline_width,
        font_size=optimal_font_size,
        darken_intensity=darken_intensity
    )
