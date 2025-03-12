from netflix_utils.netflix_insta import *
from new_movie_utils.new_movie_insta import *
from boxoffice_utils.boxoffice_insta import * 
from ni_movie_mu_utils.upload_posting import *


# caption = ''

# # 생성 원하는 게시물 입력
# posting_type = input('''
#                     원하는 게시물 타입을 선택하세요.
#                     1. 주제에 맞는 추천 영화
#                     2. 넷플릭스 영화/시리즈
#                     3. 박스오피스 주간 순위
#                     4. 새영화 뉴스 요약 
#                     q. 취소
#                     ''')
# while True:
#     if posting_type == '1':
#         break

#     elif posting_type == '2':
#         caption = make_netflix_posting()
#         break

#     elif posting_type == '3':
#         caption = make_boxoffice_posting()
#         break

#     elif posting_type == '4':
#         caption = make_new_news_posting()
#         break
    
#     elif posting_type == 'q':
#         print('종료되었습니다.')
#         break

#     else:
#         print('1~4번 사이에서 선택해 주세요.')
#         posting_type = input('''
#                     원하는 게시물 타입을 선택하세요.
#                     1. 주제에 맞는 추천 영화
#                     2. 넷플릭스 영화/시리즈
#                     3. 박스오피스 주간 순위
#                     4. 새영화 뉴스 요약 
#                     q. 취소
#                     ''')

# print(caption)

caption = '''
#새로개봉하는영화 를 소개할게요!!

#침범 : 영화 '침범'은 20년의 격차를 두고 세 명의 여성의 이야기를 다룬 미스터리 스릴러입니다. 1장에서 반려견을 죽이는 어린 소현과 그녀의 엄마 영은의 갈등이 전개되며, 소현의 반사회적 성향이 드러납니다. 이런 문제 상황 속에서 영은이 내리는 결단이 관객을 긴장으로 몰아넣습니다.2장에서 는 20년 후, 과거의 기억을 잃은 민이 등장하여 신입 사원 해영과의 갈등을 통해 이야기가 확장됩니다. 각각의 장이 고유한 매력을 발산하며, 관객은 실제로 미스터리적인 요소에 빠져들게 됩니다. 이 영화는 동명의 웹툰을 원작으로 하여 재치 있는 스토리 구성이 인상적입니다. 12일 개봉 예정이며, 관람 등급은 15세 이상입니다.

#숨 : 영화 "숨"은 죽음을 준비하는 사람들의 삶을 통해 우리의 존재에 대해 성찰하게 만드는 작품입니다. 윤재호 감독은 이번 신작에서 고인의 장례 를 챙기는 유재철 장례지도사, 고독사와 범죄 현장을 정리하는 유품정리사 김새별, 그리고 죽음을 준비하는 폐지 줍는 노인 문인산 씨의 이야기를 담 아냈습니다. 관객은 드라마틱한 인생의 단면들을 만나며, 죽음을 둘러싼 다양한 시각을 경험하게 됩니다. 죽음에 대한 터부를 넘어서려는 시도가 인상적인 이 영화는 제24회 전주국제영화제에서도 주목받았고, 오는 12일 개봉할 예정입니다. 72분 동안 죽음과 삶의 진정한 의미를 탐구하는 시간이 될  것입니다.

#ni_movie_mu #새영화 #극장가소식
'''

upload = input('게시물을 업로드 할지 선택하세요. (Y/N)')

if upload.lower() == 'y':
    upload_images(caption)

