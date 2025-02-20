from instagrapi import Client
from PIL import Image
import os
import json

# 1. 인스타그램 로그인
cl = Client()
cl.login("ni_movie_mu", "nimoviemu520")  # 계정 정보 입력

# 2. JSON에서 게시글과 해시태그 불러오기
json_path = "instagram_post_result.json"

with open(json_path, "r", encoding="utf-8") as f:
    insta_data = json.load(f)

# 3. 게시글 내용 가져오기
post_text = insta_data.get("게시글", "🎬 이번 주말, 꼭 봐야 할 영화 추천!")
hashtags = insta_data.get("해시태그", "")

# 4. 최종 인스타그램 캡션 조합
caption = f"{post_text}\n\n{hashtags}"
print(f"📌 인스타그램 캡션:\n{caption}")  # 디버깅용 출력

# 5. 이미지 변환 함수 (JPEG로 변환)
# def convert_to_jpeg(image_path):
#     img = Image.open(image_path)
#     rgb_img = img.convert("RGB")  # PNG 같은 경우 RGB로 변환해야 함
#     new_path = image_path.rsplit(".", 1)[0] + ".jpg"  # 확장자를 JPG로 변경
#     rgb_img.save(new_path, "JPEG")
#     return new_path

# 6. 업로드할 이미지 파일 목록 불러오기
image_dir = "insta_post"  # 이미지가 저장된 디렉토리
valid_extensions = (".jpg", ".jpeg", ".png")  # 허용되는 이미지 확장자

# 📌 디렉토리에서 이미지 파일 가져오기 (파일명 기준 정렬)
image_paths = sorted([
    os.path.join(image_dir, img) for img in os.listdir(image_dir)
    if img.lower().endswith(valid_extensions)
])

# 7. 이미지 변환 적용 (JPEG 아닌 경우 변환) + 순서 유지
# converted_image_paths = [convert_to_jpeg(img) if not img.lower().endswith(".jpg") else img for img in image_paths]


# paths = []
# for img in image_paths:
#     if not img.lower().endswith(".jpg"):
#         print(img)
#         paths.append(convert_to_jpeg(img))

#     else:
#         print(img)
#         paths.append(img)

# 8. 카루셀 업로드 (순서 유지)
try:
    cl.album_upload(image_paths, caption)
    print("✅ 원하는 순서대로 여러 이미지가 한 개의 게시물로 업로드되었습니다!")
except Exception as e:
    print(f"❌ 업로드 실패: {e}")
