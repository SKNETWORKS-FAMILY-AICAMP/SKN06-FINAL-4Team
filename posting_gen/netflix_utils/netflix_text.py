import os
import time
from datetime import datetime
import pandas as pd 
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv


base_dir = os.getcwd()
csv_path = os.path.join(base_dir, 'csv')
os.makedirs(csv_path, exist_ok=True)

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# 한줄소개 요약하는 함수 
def short_gen(comment):
    messages = [
        ("system", """
        당신은 영화 전문가입니다. 
        아래 [[Context]]에는 영화에 대한 한줄소개가 있습니다.
        한줄소개를 30자 이내로 요약해주세요. 
        말투는 영화 전문가 다운 사용하는 말투를 사용해주세요.
        이모티콘을 1~2개 사용해주세요.
        context에 내용이 없으면, 검색하여 작성해주세요.
        
        [[Context]]
        {context}"""),
    ]

    prompt_template = ChatPromptTemplate(messages)
    model = ChatOpenAI(model="gpt-4o-mini")
    parser = StrOutputParser()

    # Chain 구성 retriever(관련문서 조회) -> prompt_template(prompt생성) -> model(정답) -> output parser
    chain = prompt_template | model | parser

    result = chain.invoke(comment)
    
    return result


# 한줄 리뷰 생성 함수
def review_gen(review):
    messages = [
        ("system", """
        당신은 영화 전문가입니다. 
        아래 [[Context]]에는 영화에 대한 소개와 리뷰들이 있습니다.
        [[Context]]의 내용을 바탕으로 영화 소개 내용을 작성해 주세요.
        반드시 한줄로 작성해주세요.
        반드시 20자 이내로 요약해주세요. 
        이모티콘은 절대 사용하지 말아주세요.
        따옴표도 사용하지 말아주세요. 
        가능하면 긍정적인 내용으로 작성해 주세요. 
        [[Context]]에 내용이 없으면, 검색하여 작성해주세요.
        말투는 10대 20대가 인스타그램에서 사용하는 말투를 사용해주세요.

        [[Context]]
        {context}"""),
    ]

    prompt_template = ChatPromptTemplate(messages)
    model = ChatOpenAI(model="gpt-4o-mini")
    parser = StrOutputParser()

    # Chain 구성 retriever(관련문서 조회) -> prompt_template(prompt생성) -> model(정답) -> output parser
    chain = prompt_template | model | parser

    result = chain.invoke(review)

    return result


# 게시물 하단 캡션 생성하는 함수 
def netflix_caption(title, infos):
    title = title.replace(' ', '')
    info_text = '#' + title + '\n'

    for i in infos:
        key = list(i.keys())[0]
        info_text = info_text + key + ': '
        info_text = info_text + i[key] + '\n'

    # print(info_text)
            
    info_text = info_text + '\n#영화추천 #시리즈추천 #ott\n'
    return info_text


# 로그 저장하는 함수 
def save_netflix_csv(info):
    file_name = 'netflix.csv'
    file_path = os.path.join(csv_path, file_name)
    
    # 데이터 준비
    data = {
        'title': list(info.keys()),
        'review': list(info.values()),
        'posting_date': datetime.now().date()
    }

    # 기존 파일이 있는지 확인 후 처리
    if os.path.exists(file_path):
        # 기존 파일 읽기
        df_existing = pd.read_csv(file_path, parse_dates=['posting_date'])
        
        # 새 데이터 DataFrame 생성 후 기존 데이터와 병합
        df_new = pd.DataFrame(data)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        # 파일이 없으면 새로 DataFrame 생성
        df_combined = pd.DataFrame(data)

    # CSV로 저장 (덮어쓰기)
    df_combined.to_csv(file_path, index=False, date_format='%Y-%m-%d')

    print(df_combined)
