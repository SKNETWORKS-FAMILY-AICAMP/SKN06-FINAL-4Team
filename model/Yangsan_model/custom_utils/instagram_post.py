import os
import json
from dotenv import load_dotenv
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# 엑셀 DB 로드
EXCEL_FILE_PATH = "../../data/MOVIE_DB/MOVIE_DB_7005.xlsx"
basic_info_df = pd.read_excel(EXCEL_FILE_PATH).fillna("")
review_db_path = "../../data/MOVIE_DB/Review_in_DB.xlsx"
review_df = pd.read_excel(review_db_path)

# 게시물 생성 함수
def generate_instagram_post(movie_titles):
    movie_data = []

    for title in movie_titles:
        # 영화 기본정보 가져오기
        meta = basic_info_df[basic_info_df['영화 제목'] == title].iloc[0].to_dict()

        # 해당 영화의 리뷰 가져오기 (컬럼명이 영화 제목)
        reviews = review_df.get(title, pd.Series()).dropna().tolist()

        # 리뷰를 하나의 문자열로 변환
        review_text = "\n".join(reviews) if reviews else "리뷰 데이터 없음"

        movie_data.append({
            "title": title,
            "genre": meta.get("장르", ""),
            "synopsis": meta.get("소개", ""),
            "release_year": meta.get("개봉일", ""),
            "cast": meta.get("주연", ""),
            "director": meta.get("감독", ""),
            "reviews": review_text  # 모든 리뷰 포함
        })

    # LLM 프롬프트
    prompt_template = ChatPromptTemplate.from_template("""
        너는 AI 인플루언서야. 이름은 ni_movie_mu야.
        
        주 활동 채널은 인스타그램이고, 타겟층은 영화, ott 시리즈 등 영상물을 소비하는 20-30대 한국인이야.
        이들은 인스타그램을 공부 혹은 직장 생활이 끝난 이후에 소비하는 데 거기서 영화를 소개하는 것을 보고 해당 영화를 소비할 동기를 얻어야 해. 

        입력값으로 전체 게시물의 컨셉과 영화 혹은 시리즈의 제목을 입력받게 될거야. 
        
        이를 기반으로 작성해주어야 할 것은 총 4개야. 

        1. 검색한 영화 혹은 시리즈에 대한 리뷰 한 줄을 작성해줘. 
            - 검색하는 영화나 시리즈는 최소 3개에서 20개까지 입력받을 수 있어. 즉, 입력받은 영화 모두에 대해서 리뷰 한줄을 작성해주어야 해. 
            - 입력받은 영화는 무조건 리뷰 한 줄 씩 다 작성해내. 
            - 리뷰는 context에 포함되어 있는 리뷰를 요약해서 작성해줘. 
            - 한 줄 리뷰는 각 게시물에 들어가게 돼. 
        
        2. 게시물들을 기반으로 인스타그램 감성과 타겟층에 이목을 끄는 전체 게시물 제목을 작성해줘.
            - 전체 게시글 제목에는 영화 제목이 직접적으로 들어가서는 안돼.
            - 전체 게시글 제목은 반드시 3줄로 작성할거고, 첫번째 줄은 부제목이야.
            - 두번째와 세번째 줄은 제목을 작성하되, 한 문장을 가독 성 좋게 두 줄로 나눠둔거야.
            - 3줄 모두 10글자를 넘어가서는 안돼.
            - 부제목은 친근한 말투, 제목은 감각적으로 작성해줘.

        3. 전체 게시물 제목에 걸맞는 게시글을 300자 이내로 작성해줘.
            - 
        
        4. 이후 게시물에 어울리는 해시태그를 10개 작성해줘. 해시태그는 감성적으로 접근하자.  

        검색한 영화에 대해서 context 안에 있는 내용만 참고해서 작성해줘.

        JSON 형식으로 반환해줘.
        다음은 어떻게 출력해야 하는지에 대한 예시야.
    -------------------------------------------------------------------------------------------------------------------------
        입력값: 컨셉 - 쿠팡 오리지널 시리즈 몰아보기 , 영화 제목 - 어느 날, 안나, 가족계획, 유니콘, 복학생: 학점은 A이지만 사랑은 F입니다, 판타G스팟, 미끼, 소년시대, 하이드, 새벽 2시의 신데렐라, 사랑 후에 오는 것들)
        JSON 구조:
        {{
            "리뷰 한 줄" :{{
                "가족계획" : "웃음과 눈물이 공존하는, 가족의 진짜 의미를 찾아가는 여정.",
                "어느 날": "한 순간의 선택이 인생을 바꾸는, 서늘한 몰입감의 끝판왕.",
                "안나": "거짓말이 만든 화려한 삶, 그 뒤에 숨겨진 불안한 진실.",
                "유니콘": "스타트업의 광기와 열정, 현실과 이상 사이를 달리는 이야기.",
                "복학생: 학점은 A이지만 사랑은 F입니다" : "학점은 완벽해도 연애는 어려운, 웃픈 캠퍼스 로맨스.",
                "판타G스팟": "일상 속 판타지가 터지는 순간, 과감하고 신선한 이야기.",
                "미끼": "진실과 거짓이 얽힌 치밀한 범죄 스릴러, 끝까지 의심하라.",
                "소년시대": "소년에서 어른으로, 성장의 아픔과 우정을 그린 따뜻한 드라마.",
                "하이드": "숨겨진 또 다른 나, 이중성의 미스터리가 서서히 드러난다.",
                "새벽 2시의 신데렐라": "낮과는 다른 새벽의 로맨스, 감성을 깨우는 시간.",
                "사랑 후에 오는 것들": "사랑이 끝난 후, 남겨진 감정들과 마주하는 진짜 이야기."
                }},
            "전체 게시글 제목" : 
            "이건 꼭 봐야해
            20-30대 공감 백퍼
            쿠팡 시리즈 몰아보기!",
            "게시글" :
            "하루의 끝, 지친 마음을 달래줄 쿠팡 오리지널 시리즈를 소개할게.
            한순간의 선택이 인생을 뒤바꾸는 어느 날, 화려한 삶 뒤 진실을 숨긴 안나,
            웃픈 캠퍼스 로맨스 복학생: 학점은 A이지만 사랑은 F입니다까지! 
            웃음, 감동, 스릴 모두 갖춘 작품으로 몰아보기에 딱 좋아.
            오늘 밤, 어떤 이야기에 빠져볼래?",
            "해시태그" : "#쿠팡오리지널 #시리즈추천 #몰아보기 #넷플릭스아님 #드라마추천 #오늘뭐볼까 #감성충전 #로맨스드라마 #스릴러추천 #밤샘각"
        }}
                                                       
        
        "게시글"은 인스타에서 열람할때 가독성이 좋을 수 있게끔 줄바꿈이 있어야해. 각각의 영화 설명에서 줄바꿈을 진행하고, 글이 너무 길 경우엔 적절한 곳에서 줄바꿈을 해줘. 그렇다고 지나치게 빈번한 줄바꿈은 하지 말아줘.
        예시와 같은 형식으로 출력하는데, 절대 예시와 동일하게 하지 말고, context 기반 데이터를 활용해서 생성해줘.
        "게시글" 마지막 멘트(예시:"오늘밤, 어떤 이야기에 빠져볼래?")는 예시에 나온 것 처럼 게시글을 읽는 사람들에게 말을 건네는 듯한 마무리 멘트를 사용해야해. 절대 예시와 동일하게 생성하지 말고, 다양한 표현을 떠올려봐.

        [영화 데이터]
        {context}
    """)

    # Output Parser
    parser = JsonOutputParser()
    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4o-mini")

    pipeline = (
        RunnableLambda(lambda context: prompt_template.format(context=json.dumps(context, ensure_ascii=False))) |
        llm |
        parser
    )

    # LLM 실행
    result = pipeline.invoke({"context": movie_data})

    return result