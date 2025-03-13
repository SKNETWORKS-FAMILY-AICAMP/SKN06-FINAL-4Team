import os
import time

from ni_movie_mu_utils.crawling_kino import *
from ni_movie_mu_utils.crawling_naver import * 

from boxoffice_utils.boxoffice_image import * 
from boxoffice_utils.boxoffice_image_katuri import *
from boxoffice_utils.boxoffice_image_dx import *

from boxoffice_utils.boxoffice_text import *


base_dir = os.getcwd()
add_date = time.strftime('%Y%m%d')
input_path = os.path.join(base_dir, 'image', f'original_{add_date}')
output_path = os.path.join(base_dir, 'image', f'insta_{add_date}')
os.makedirs(output_path, exist_ok=True)


def make_boxoffice_posting():
    weekly_boxoffice = get_weekly_boxoffice()
    movie_list = list(weekly_boxoffice.keys())

    cnt = 1
    for i in movie_list:
        get_kino_image(i)
        watches = weekly_boxoffice[i][1]
        tot_watches = weekly_boxoffice[i][2]
        # insta_boxoffice_katuri(i, watches, tot_watches, cnt)
        insta_boxoffice_dx(i, watches, tot_watches, cnt)
        cnt += 1

    # make_list_page_katuri(movie_list[0:5], 'z0')
    # make_list_page_katuri(movie_list[5:10], 'z1')

    make_list_page_dx(movie_list[0:5], 'z0')
    make_list_page_dx(movie_list[5:10], 'z1')

    image_paths = [os.path.join(output_path, f) for f in os.listdir(output_path) if f.endswith(('.png', '.jpg', '.jpeg'))][0:4]
    save_as = os.path.join(base_dir, 'image', f'insta_{add_date}', '00_instagram_grid.jpg')
    create_instagram_grid(image_paths, save_as)

    image_paths = [os.path.join(output_path, f) for f in os.listdir(output_path) if f.endswith(('.png', '.jpg', '.jpeg'))][5:9]
    save_as = os.path.join(base_dir, 'image', f'insta_{add_date}', '01_instagram_grid.jpg')
    create_instagram_grid(image_paths, save_as)

    image_paths = [os.path.join(output_path, f) for f in os.listdir(output_path) if f.endswith(('.png', '.jpg', '.jpeg'))][2:10]
    for filename in image_paths:
        try:
            os.unlink(filename)
        except Exception as e:
            print(f"파일 {filename} 삭제 중 오류 발생: {e}")

    # make_first_page_katuri()
    make_first_page_dx()

    # 포스트 캡션
    caption = boxoffice_caption(weekly_boxoffice)

    # 로그 저장
    save_boxoffice_csv(weekly_boxoffice)

    return caption
