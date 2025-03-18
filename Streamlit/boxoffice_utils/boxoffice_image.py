import os
import time

from PIL import Image


base_dir = os.getcwd()
add_date = time.strftime('%Y%m%d')
input_path = os.path.join(base_dir, 'image', f'original_{add_date}')
output_path = os.path.join(base_dir, 'image', f'insta_{add_date}')
os.makedirs(output_path, exist_ok=True)


# 4개 영화를 1장에 소개하는 이미지 만드는 함수 
def create_instagram_grid(image_paths, output_path):
    # 출력 이미지 크기 설정 (인스타그램 권장 크기: 1080x1080)
    grid_size = (1080, 1080)
    
    # 2x2 그리드 생성
    grid = Image.new('RGB', grid_size, color='white')
    
    # 각 이미지의 크기 계산
    img_size = (grid_size[0] // 2, grid_size[1] // 2)
    
    for i, path in enumerate(image_paths):
        if i >= 4:
            break
        
        img = Image.open(path)
        img = img.resize(img_size, Image.LANCZOS)
        
        # 이미지 위치 계산
        x = (i % 2) * img_size[0]
        y = (i // 2) * img_size[1]
        
        grid.paste(img, (x, y))
    
    grid.save(output_path)
    print('4 in 1 페이지가 생성되었습니다.')
