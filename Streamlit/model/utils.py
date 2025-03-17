#### 이미지 크롤링 및 다운로드
#### 이미지 다운 받을 경로 설정 후에 사용할 것!

import os
import shutil


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


def poster_to_background_images(movies_titles, source_folder="data/posters_db"):
    """
    DB에 위치한 포스터 사진을 "background_images" 폴더로 복사하는 함수입니다.
    """

    destination_folder = "recommend_data/cache_file/background_images"

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    image_name = f"{movies_titles}_poster.jpg"
    source_path = os.path.join(source_folder, image_name)
    destination_path = os.path.join(destination_folder, image_name)

    # 파일 존재 여부 확인 후 복사
    if os.path.exists(source_path):
        shutil.copy2(source_path, destination_path)  # 원본 유지, 복사
        print(f"✅ 파일 복사 완료: {source_path} → {destination_path}")
    else:
        print(f"❌ 파일 없음: {source_path}")

    print("🎉 모든 파일 복사 완료!")