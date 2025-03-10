from ni_movie_mu_utils.crawling_kino import *
from ni_movie_mu_utils.crawling_naver import * 

from netflix_utils.netflix_text import *
from netflix_utils.netflix_image_katuri import *
from netflix_utils.netflix_image_dx import *


# 지금 많이 찾는
rec_url = 'https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&mra=bkdJ&qvt=0&query=%EB%84%B7%ED%94%8C%EB%A6%AD%EC%8A%A4%20%EC%B6%94%EC%B2%9C'
#주간 순위
rank_url = 'https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&mra=bkdJ&qvt=0&query=%EB%84%B7%ED%94%8C%EB%A6%AD%EC%8A%A4%20%EC%A3%BC%EA%B0%84%20%EC%88%9C%EC%9C%84'
# 신작
new_url = 'https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&mra=bkdJ&qvt=0&query=%EB%84%B7%ED%94%8C%EB%A6%AD%EC%8A%A4%20%EC%8B%A0%EC%9E%91'
# 오리지널
ori_url = 'https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&mra=bkdJ&qvt=0&query=%EB%84%B7%ED%94%8C%EB%A6%AD%EC%8A%A4%20%EC%98%A4%EB%A6%AC%EC%A7%80%EB%84%90'

rec_list = []
rank_list = []
new_list = []
ori_list = []

movie_infos = dict()
movie_reviews = dict()
short_reviews = dict()


def make_netflix_posting():
    # 입력 후 함수 실행 
    list_input = input('''
                    넷플릭스 검색 리스트: 
                    1. 지금 많이보는 
                    2. 주간 순위 
                    3. 신작 영화/시리즈 
                    q. 취소 
                    ''')
    
    while True:
        if list_input == '1':
            search_list = get_netflix_list(rec_url, rec_list)
            print('넷플릭스 지금 많이보는 영화/시리즈가 선택되었습니다.')
            info_texts = '#넷플릭스 에서 #지금많이보는 영화/시리즈를 소개할게요!! \n\n'
            break

        elif list_input == '2':
            search_list = get_netflix_list(rank_url, rank_list)
            print('넷플릭스 주간 순위가 선택되었습니다.')
            info_texts = '#넷플릭스 #주간순위 가 높은 영화/시리즈를 소개할게요!! \n\n'
            break

        elif list_input == '3':
            search_list = get_netflix_list(new_url, new_list)
            print('넷플릭스 신작 영화/시리즈가 선택되었습니다.')
            info_texts = '#넷플릭스 #신작 영화/시리즈를 소개할게요!! \n\n'
            break

        elif list_input == 'q':
            search_list = []
            print('실행을 종료하였습니다.')
            return None

        else:
            # search_list = get_netflix_list(ori_url, ori_list)
            print('1~3번 사이에서 선택해주세요.')
            list_input = input('''
                        넷플릭스 검색 리스트: 
                        1. 지금 많이보는 
                        2. 주간 순위
                        3. 신작 영화/시리즈 
                    ''')
            
    for i in search_list:
        try:
            info = get_movie_info(i)
            movie_infos[i] = info
            info_text = netflix_caption(i, info)
            info_texts = info_texts + info_text
            
            review = get_movie_review(i)
            comment = get_movie_comment(i)
            movie_reviews[i] = review + comment
            get_kino_image(i)
            short_review = review_gen(movie_reviews[i])

            # insta_netflix_katuri(i, short_review)
            insta_netflix_dx(i, short_review)
            
        except:
            continue

    try:
        # first_page_netflix_katuri(list_input)
        first_page_netflix_dx(list_input)

        print('\n게시물 올라갈 캡션 내용입니다.\n')
        print(info_texts)
        print("저장된 게시물과 텍스트를 확인 후 업로드를 진행해 주세요.")
        return info_texts

    except:
        print('종료 되었습니다.')
        return None
