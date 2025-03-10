import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


# ChromeOptions 객체 생성
chrome_options = Options()

# headless 모드 설정
chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
chrome_options.add_argument('--disable-gpu')

# 주간 박스오피스 순위를 가져오는 함수. 
def get_weekly_boxoffice():
    # 박스오피스 url
    box_office_url = 'https://www.kobis.or.kr/kobis/business/stat/boxs/findWeeklyBoxOfficeList.do'

    box_office = dict()

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(box_office_url)
        time.sleep(3)

        for i in range(1, 11):
            # 영화명, 매출, 주간 관객수, 누적 관객수 
            name = driver.find_element(By.XPATH, f'//*[@id="tbody_0"]/tr[{i}]/td[2]/span[1]/a').text
            sales = driver.find_element(By.XPATH, f'//*[@id="tbody_0"]/tr[{i}]/td[4]').text
            watches = driver.find_element(By.XPATH, f'//*[@id="tbody_0"]/tr[{i}]/td[8]').text
            tot_watches = driver.find_element(By.XPATH, f'//*[@id="tbody_0"]/tr[{i}]/td[10]').text

            info = [sales, watches, tot_watches]
            box_office[name] = info
        return box_office

    except Exception as e:
        print(f"오류 발생: {e}")
        return None

    finally:
        # 드라이버 종료
        driver.quit()


# 게시물 하단 캡션 생성하는 함수 
def boxoffice_caption(box_office):
    info_text = '이번주 #박스오피스 #주간순위 를 소개할게요!!\n\n'

    for i in box_office:
        name = i.replace(' ', '')
        info_text = info_text + '#' + name + ' : '
        info_text = info_text + box_office[i][1] + '명 / 누적 ' + box_office[i][2] + '명\n\n'
        
    info_text = info_text + '#ni_movie_mu #영화추천 \n출처: #영화관입장권통합전산망\n'
    return info_text


# 로그 저장하는 함수 
def save_boxoffice_csv():
    



    pass