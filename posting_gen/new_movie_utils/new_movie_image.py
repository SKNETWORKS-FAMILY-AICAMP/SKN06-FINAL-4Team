import os
import time

from PIL import Image


base_dir = os.getcwd()
add_date = time.strftime('%Y%m%d')
input_path = os.path.join(base_dir, 'image', f'original_{add_date}')
output_path = os.path.join(base_dir, 'image', f'insta_{add_date}')
os.makedirs(output_path, exist_ok=True)


# 포스터 전체를 넣고 빈공간은 검정색으로 두는 함수
def make_sq_poster(image_name):
    # 포스터 열기    
    image_path = os.path.join(input_path, f'{image_name}')
    poster = Image.open(image_path)

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
    output_name = image_name.replace('0.jpg', '3.jpg')
    save_as = os.path.join(output_path, f"insta_{output_name}")

    # 수정된 포스터 저장
    new_image.save(save_as)
    print(f"인스타그램용 이미지 저장 완료: {save_as}")
