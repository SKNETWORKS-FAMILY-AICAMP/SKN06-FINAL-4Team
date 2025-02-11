import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# 넷플릭스 영화/시리즈 가져오는 함수
def get_netflix_list(url, naver_list):
    try:
        # ChromeOptions 객체 생성
        chrome_options = Options()

        # headless 모드 설정
        chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(1)

        for j in range(1,9):
            name = driver.find_element(By.XPATH, f'//*[@id="mflick"]/div/div/ul[{1}]/li[{j}]/strong/a').text
            naver_list.append(name)

        driver.find_element(By.XPATH, '//*[@id="main_pack"]/section[1]/div[2]/div/div/div[3]/div/a[2]').click()
        time.sleep(1)  # 페이지 로딩 대기

        for j in range(1,2):
            name = driver.find_element(By.XPATH, f'//*[@id="mflick"]/div/div/ul[{2}]/li[{j}]/strong/a').text
            naver_list.append(name)

        return naver_list
    
    except Exception as e:
        print(f"오류 발생: {e}")
        return None
    
    finally:
        # 드라이버 종료
        driver.quit()


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


# 키노라이즈에서 영화 정보 가져오는 함수 
# seasonInfo 작품정보 / 소개내용, 장르, 제작연도, 제작국가 
def get_netflix_info(movie_name):
    try:
        # ChromeOptions 객체 생성
        chrome_options = Options()

        # headless 모드 설정
        chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://m.kinolights.com/search')
        time.sleep(1)

        search_box = driver.find_element(By.CLASS_NAME, "search-form__input")  # 검색창의 name 속성 값이 searchQuery라고 가정
        search_box.send_keys(movie_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="searchContentList"]/div/a/div[2]').click()
        time.sleep(1)

        pub_year = driver.find_element(By.XPATH, '//*[@id="contents"]/div[4]/section[1]/ul/li[8]/span[2]').text
        genre = driver.find_element(By.XPATH, '//*[@id="contents"]/div[4]/section[1]/ul/li[1]/span[2]').text
        pub_country = driver.find_element(By.XPATH, '//*[@id="contents"]/div[4]/section[1]/ul/li[7]/span[2]').text
        comment = driver.find_element(By.XPATH, '//*[@id="contents"]/div[4]/section[1]/div/div/div/span').text

        pub_year = {'제작연도':pub_year}
        genre = {'장르':genre}
        pub_country = {'제작국가':pub_country}
        # comment = {'한줄소개': short_gen(comment)}
        comment = {'한줄소개': comment}

        # 채널 추가
        # 방영일 추가
        # 연령등급 추가
        # -> 방영일, 장르, 채널, 연령등급은 그냥 표기
        # -> 한줄소개를 수정하여 사용

        info = [genre]
        print(f'{movie_name}의 정보를 저장했습니다.')
        return info

    except Exception as e:
        print(f'{movie_name}의 정보를 찾을수 없습니다.')
        return None
    
    finally:
        # 드라이버 종료
        driver.quit()


# 키노라이즈에서 리뷰 가져오는 함수
def get_netflix_review(movie_name):
    try:
        # ChromeOptions 객체 생성
        chrome_options = Options()

        # headless 모드 설정
        chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://m.kinolights.com/search')
        time.sleep(1)

        search_box = driver.find_element(By.CLASS_NAME, "search-form__input")  # 검색창의 name 속성 값이 searchQuery라고 가정
        search_box.send_keys(movie_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="searchContentList"]/div/a/div[2]').click()
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="review"]').click()
        time.sleep(1)        

        for _ in range(0,5):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(1)

        # scroll_location = driver.execute_script("return document.body.scrollHeight")

        # while True:
        #     #현재 스크롤의 가장 아래로 내림
        #     driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        #     #전체 스크롤이 늘어날 때까지 대기
        #     time.sleep(1)

        #     #늘어난 스크롤 높이
        #     scroll_height = driver.execute_script("return document.body.scrollHeight")
        #     #늘어난 스크롤 위치와 이동 전 위치 같으면(더 이상 스크롤이 늘어나지 않으면) 종료
        #     if scroll_location == scroll_height:
        #         break
        #     #같지 않으면 스크롤 위치 값을 수정하여 같아질 때까지 반복
        #     else:
        #         #스크롤 위치값을 수정
        #         scroll_location = driver.execute_script("return document.body.scrollHeight")

        reviews = ''
        try:
            for i in range(1, 100):
                review = driver.find_element(By.XPATH, f'//*[@id="contents"]/div[5]/section[2]/div/article[{i}]/div[3]/a/h5').text
                reviews = reviews + review
        except:
            pass
        print(f'{movie_name}의 리뷰를 저장했습니다.')
        return reviews

    except Exception as e:
        print(f'{movie_name}의 리뷰를 찾을수 없습니다.')
        return None

    finally:
        # 드라이버 종료
        driver.quit()


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
        print(result)

        return result


def write_text(title, infos):
    title = title.replace(' ', '')
    info_text = '#' + title + '\n'

    for i in infos:
        key = list(i.keys())[0]
        info_text = info_text + key + ': '
        info_text = info_text + i[key] + '\n'

    # print(info_text)
        
    info_text = info_text + '\n#영화추천 #시리즈추천 #ott\n'
    return info_text

def get_netflix_comment(title):
    try:
        # ChromeOptions 객체 생성
        chrome_options = Options()

        # headless 모드 설정
        chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://m.kinolights.com/search')
        time.sleep(1)

        search_box = driver.find_element(By.CLASS_NAME, "search-form__input")  # 검색창의 name 속성 값이 searchQuery라고 가정
        search_box.send_keys(title)
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="searchContentList"]/div/a/div[2]').click()
        time.sleep(1)

        comment = driver.find_element(By.XPATH, '//*[@id="contents"]/div[4]/section[1]/div/div/div/span').text

        return comment


    except Exception as e:
        print(f'{title}의 정보를 찾을수 없습니다.')
        return None
    
    finally:
        # 드라이버 종료
        driver.quit()
