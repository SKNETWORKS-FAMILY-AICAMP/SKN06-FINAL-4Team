
from model.search_model import *
from model.templates import *
from model.utils import delete_all_files_in_folder, poster_to_background_images
from model.instagram_post import *

def recommend_pipeline(user_question, mumupoint):

    print("\n[INFO] STEP 1: 사용자 질문 분석 중...")
    expanded_keywords = analyze_question_with_llm(user_question)
    
    print("\n[INFO] STEP 2: 영화 검색 진행 중...")
    search_results = search_movies_with_faiss(expanded_keywords, mumupoint)

    max_attemps = 3
    attempt = 0

    while len(search_results) <= 2 and attempt < max_attemps:
        print("\n[INFO] 영화 추천 개수가 부족합니다. 재검색 진행합니다.")

        expanded_keywords = analyze_question_with_llm(user_question)
        search_results = search_movies_with_faiss(expanded_keywords, mumupoint)

        attempt += 1  # 시도 횟수 증가

        if len(search_results) >= 3:
            print("\n[INFO] STEP 3: 추천 영화 선택 중...")
            break  # 충분한 개수를 찾았으면 종료

    if len(search_results) > 0 and len(search_results) <= 2:
        print(f"\n[INFO] 해당 점수대의 영화는 {len(search_results)}개 밖에 없습니다.")

    recommended_movies = generate_recommendations(user_question, search_results)

    if not recommended_movies:
        print("\n❌ 추천할 영화가 없습니다.")
        return recommended_movies
    
    else:
        print("\n🎬 최종 추천 영화 리스트:", recommended_movies)

        print("\n[INFO] STEP 4: 인스타그램 게시물 생성 중...")
        post_result = generate_instagram_post(user_question, recommended_movies)

        # 결과 저장
        with open("recommend_data/cache_file/instagram_post_result.json", "w", encoding="utf-8") as f:
            json.dump(post_result, f, ensure_ascii=False, indent=4)

        print("\n✅ 게시물 생성 완료! 결과가 instagram_post_result.json에 저장되었습니다.")

        print("\n📷 STEP 5: 인스타그램 게시물 이미지 찾는 중...")
        poster_to_background_images(recommended_movies)

        print("\n ✍️ STEP 6: 인스타그램 게시물 이미지 생성 중...")
        movie_post_list = find_review_data('recommend_data/cache_file/instagram_post_result.json')
        # 카드뉴스 이미지 생성
        for movie_name, tagline in movie_post_list:
            insta_post_1(movie_name, tagline)
            print(f"🎬 현재 생성 중인 영화: {movie_name}, 태그라인: {tagline}")
        # 게시물 대문 생성
        keywords = expanded_keywords.get("키워드")
        door_title = find_title_data('recommend_data/cache_file/instagram_post_result.json')
        create_post_door(door_title, keywords)
        
        print("\n✅ 게시물 생성 완료! 결과가 insta_post 폴더에 저장되었습니다.")

        return recommended_movies
