from ni_movie_mu_utils.crawling_kino import *
from ni_movie_mu_utils.crawling_naver import * 

from new_movie_utils.new_movie_image import *
from new_movie_utils.new_movie_image_dx import *

from new_movie_utils.new_movie_text import *


def make_new_news_posting():
    # 뉴스 구분 
    a = get_new_movie()
    new_movie = dict()
    summarized = dict()
    a = a. split('@yna.co.kr')
    texts = a[0].split('▲ ')

    for i in range(1, len(texts)):
        title, news = texts[i].split(' = ')
        new_movie[title] = news

    # 뉴스 요약 
    for i in new_movie:
        print(i)
        a = news_gen(i, new_movie[i]).split('\n\n')
        summarized[i] = a


    # 이미지 크롤링 
    for i in new_movie:
        get_kino_image(i)
        save_stillcut_image(i)


    # 게시물 생성
    for i in new_movie:
        for j in range(3):
            a = i.replace(':','').replace('?', '').replace('/', '').replace('<', '').replace('>', '')
            image = f'img_{a}_{j}.jpg'
            if j == 0:
                make_sq_poster(image)
            else:
                insta_new_movies_dx(image, i, summarized[i][j-1])

    # 대문 페이지 생성 
    titles = list(new_movie.keys())
    make_first_page_dx(titles)


    # 포스트 캡션
    caption = new_movie_caption(summarized)
    return caption