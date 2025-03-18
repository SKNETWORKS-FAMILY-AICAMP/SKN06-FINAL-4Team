import os
import time

from PIL import Image, ImageDraw, ImageFont


base_dir = os.getcwd()
add_date = time.strftime('%Y%m%d')
input_path = os.path.join(base_dir, 'image', f'original_{add_date}')
output_path = os.path.join(base_dir, 'image', f'insta_{add_date}')
os.makedirs(output_path, exist_ok=True)

font_path = 'C:/Users/Playdata/AppData/Local/Microsoft/Windows/Fonts/DX헤드01Light.ttf'

# 스틸컷과 기사 요약을 넣어 게시물을 만드는 함수 
def insta_new_movies_dx(image_name, title, news):
    # 설정: 배경 크기 및 이미지 폴더 경로
    background_width = 1080  # Instagram 권장 너비
    background_height = background_width 
    background_color = "black"

    # 검정 배경 생성
    background = Image.new("RGB", (background_width, background_height), background_color)

    # 폴더에서 이미지 파일 가져오기
    image_path = os.path.join(input_path, image_name)
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
    font_title = ImageFont.truetype(font_path, 60)  # 제목 폰트 크기
    font_news = ImageFont.truetype(font_path, 35)  # 뉴스 폰트 크기

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
    save_as = os.path.join(output_path, f"insta_{image_name}")
    background.save(save_as)
    print(f"결과 저장: {save_as}")


# 대문 페이지 만드는 함수 
def make_first_page_dx(titles):
    # 0.jpg로 끝나는 이미지 파일 목록 가져오기
    image_files = [f for f in os.listdir(input_path) if f.endswith('0.jpg')]
    image_count = len(image_files)

    # 인스타그램 정사각형 이미지 크기 (예: 1080x1080)
    canvas_size = (1080, 1080)

    # 새 캔버스 생성 (흰색 배경)
    canvas = Image.new('RGB', canvas_size, 'white')

    # 각 이미지의 너비 계산
    image_width = canvas_size[0] // image_count

    for i, image_file in enumerate(image_files):
        # 이미지 열기
        img_path = os.path.join(input_path, image_file)
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

    # 저장 경로 설정
    save_as = os.path.join(output_path, "00_first_page.jpg")
    canvas.save(save_as)
