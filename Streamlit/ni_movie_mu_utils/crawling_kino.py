import os
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


# ChromeOptions 객체 생성
chrome_options = Options()

# # headless 모드 설정
# chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
# chrome_options.add_argument('--disable-gpu')


# 키노라이즈에서 포스터 이미지 가져오는 함수
def get_kino_image(movie_name):
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://m.kinolights.com/search')
        time.sleep(1)

        search_box = driver.find_element(By.CLASS_NAME, "search-form__input")  # 검색창의 name 속성 값이 searchQuery라고 가정
        search_box.send_keys(movie_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="searchContentList"]/div/a/div[2]').click()
        time.sleep(1)

        driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div[2]/div[1]/div[2]/div/div[1]/img').click()
        time.sleep(1)
        image_elements = driver.find_elements(By.XPATH, '//*[@id="root"]/div[2]/div[2]/div/div/div[2]/div/div/div[1]/img') 

        add_date = time.strftime('%Y%m%d')
        os.makedirs(f'image/original_{add_date}', exist_ok=True)

        # 이미지 저장
        for index, img in enumerate(image_elements):
            img_url = img.get_attribute("src")  # 이미지의 URL 가져오기
            if img_url:  # 유효한 URL인지 확인
                response = requests.get(img_url)
                if response.status_code == 200:
                    # 파일 저장 경로 설정
                    image_name = movie_name.replace(':','').replace('?', '').replace('/', '').replace('<', '').replace('>', '')
                    file_name = f"image/original_{add_date}/img_{image_name}_0.jpg"
                    with open(file_name, "wb") as f:
                        f.write(response.content)
                    print(f"이미지 저장 완료: {file_name}")
                else:
                    print(f"이미지 다운로드 실패: {img_url}")
        return

    except Exception as e:
        print(f'{movie_name}의 이미지를 찾을수 없습니다.')
        return None

    finally:
        # 드라이버 종료
        driver.quit()


# 키노라이즈에서 영화 정보 가져오는 함수 
def get_movie_info(movie_name):
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://m.kinolights.com/search')
        time.sleep(1)

        search_box = driver.find_element(By.CLASS_NAME, "search-form__input")
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
def get_movie_review(movie_name):
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://m.kinolights.com/search')
        time.sleep(1)

        search_box = driver.find_element(By.CLASS_NAME, "search-form__input")
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


def get_movie_comment(title):
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://m.kinolights.com/search')
        time.sleep(1)

        search_box = driver.find_element(By.CLASS_NAME, "search-form__input")
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
