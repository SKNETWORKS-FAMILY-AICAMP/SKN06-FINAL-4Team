import os
import time
from datetime import datetime
import pandas as pd 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv


base_dir = os.getcwd()
csv_path = os.path.join(base_dir, 'csv')
os.makedirs(csv_path, exist_ok=True)

# .env 파일 로드
load_dotenv()

# ChromeOptions 객체 생성
chrome_options = Options()

# headless 모드 설정
chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
chrome_options.add_argument('--disable-gpu')


# 새영화 소개 뉴스 크롤링
def get_new_movie():
    # 연합뉴스 영화 url

    try:
        for k in range(1, 10):
            news_url = f'https://www.yna.co.kr/entertainment/movies/{k}'
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(news_url)
            time.sleep(1)

            for i in range(26):
                try:
                    # 제목에 '새영화'가 포함되어 있는지 확인 
                    title = driver.find_element(By.XPATH, f'//*[@id="container"]/div[2]/div[2]/div[1]/section/div/ul/li[{i+1}]/div/div/strong/a/span').text
                    if '[새영화]' in title:
                        driver.find_element(By.XPATH, f'//*[@id="container"]/div[2]/div[2]/div[1]/section/div/ul/li[{i+1}]/div/div/strong/a/span').click()
                        time.sleep(1)

                        # 텍스트 저장 
                        context = ''
                        j = 1
                        while True:
                            try:
                                txt = driver.find_element(By.XPATH, f'//*[@id="articleWrap"]/div[1]/p[{j}]').text
                                j += 1
                                context = context + txt
                            except:
                                return context
                        break
                
                except:
                    continue

    except Exception as e:
        print(f"오류 발생: {e}")
        return None

    finally:
        # 드라이버 종료
        driver.quit()


# 뉴스 생성 함수
def news_gen(title, news):
        messages = [
                ("system", """
                당신은 영화 전문가입니다. 
                아래 [[Context]]에는 영화에 대한 소개 뉴스가 있습니다.
                [[Context]]의 내용을 바탕으로 영화 소개 내용을 요약해서 작성해 주세요.
                2개 문단으로 작성해주세요. 한 문단은 100자가 넘지 않게 작성해 주세요.
                이모티콘은 절대 사용하지 말아주세요.  
                [[Context]]에 있는 내용으로만 작성하세요.
                말투는 공손하게 존댓말로 작성을 하고, 약간 위트 있는 느낌으로 작성해주세요. 

                [[Context]]
                {context}"""),
        ]

        prompt_template = ChatPromptTemplate(messages)
        model = ChatOpenAI(model="gpt-4o-mini")
        parser = StrOutputParser()

        # Chain 구성 retriever(관련문서 조회) -> prompt_template(prompt생성) -> model(정답) -> output parser
        chain = prompt_template | model | parser

        news = f'영화제목은 {title}입니다. 이 영화의 정보는 다음과 같습니다.' + news
        result = chain.invoke(news)

        return result


# 게시물에 들어갈 캡션 생성 함수 
def new_movie_caption(new_movie):
    info_text = '#새로개봉하는영화 를 소개할게요!!\n\n'

    for i in new_movie:
        name = i.replace(' ', '')
        info_text = info_text + '#' + name + ' : '
        info_text = info_text + new_movie[i][0] + new_movie[i][1] + '\n\n'
        
    info_text = info_text + '#ni_movie_mu #새영화 #극장가소식 \n'
    return info_text


# 로그 저장하는 함수 
def save_new_movie_csv(info):
    file_name = 'new_movie.csv'
    file_path = os.path.join(csv_path, file_name)

    # 데이터 준비
    data = {
        'title': list(info.keys()),
        'news': list(info.values()),
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
