#### 이미지 크롤링 및 다운로드
#### 이미지 다운 받을 경로 설정 후에 사용할 것!

import pandas as pd
import os


# 엑셀 파일 읽어서 개봉일 추출하는 함수
def get_movie_date(file_path, movie_name):
    # 엑셀 파일 읽기
    df = pd.read_excel(file_path)

    # 영화 제목으로 데이터 필터링
    movie_data = df[df['영화 제목'] == movie_name]
    
    if movie_data.empty:
        print(f"'{movie_name}'에 해당하는 영화를 찾을 수 없습니다.")
        return None
    
    # 개봉일을 연도로 변환하여 반환
    try:
        year = pd.to_datetime(movie_data['개봉일'].iloc[0]).year
        return f"({year})"
    except Exception as e:
        print(f"개봉일을 처리하는 중 오류가 발생했습니다: {e}")
        return None


def delete_all_files_in_folder(folder_path):
    """
    지정된 폴더 안의 모든 파일을 삭제하는 함수.
    
    :param folder_path: 폴더 경로
    """
    if not os.path.exists(folder_path):
        print(f"Error: '{folder_path}' 폴더가 존재하지 않습니다.")
        return
    
    # 폴더 내 파일 삭제
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)  # 파일 삭제
                print(f"Deleted: {file_path}")
            else:
                print(f"Skipped (not a file): {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


