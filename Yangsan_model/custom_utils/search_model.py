import pandas as pd
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import openai
import os

load_dotenv()
hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
openai_client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

# 임베딩 모델 로드
model = SentenceTransformer("all-MiniLM-L6-v2", use_auth_token=hf_api_key)

# 엑셀 DB 로드
EXCEL_FILE_PATH = "../../data/MOVIE_DB/MOVIE_DB_7005.xlsx"
df = pd.read_excel(EXCEL_FILE_PATH).fillna("")
review_db_path = "../../data/MOVIE_DB/Review_in_DB.xlsx"
review_df = pd.read_excel(review_db_path)

# FAISS 인덱스 저장 파일 경로
FAISS_INDEX_FILE = "faiss_index.bin"
MOVIE_INDICES_FILE = "movie_indices.npy"

######################################################################
# 평균 임베딩
    # 여러 개의 벡터를 평균 내어 하나의 벡터화 진행 -> 벡터의 개수가 다르더라도 항상 같은 차원의 벡터를 유지할 수 있도록
    # 벡터의 크기(norm)는 일정하지 않을 수 있음
# 정규화
    # 벡터 크기를 1로 맞춤 -> 벡터 간의 유사도 비교가 공정해질 수 있도록
    # FAISS는 일반적으로 내적을 통해 유사도 계산함. -> 정규화 하면 코사인 유사도와 동일한 효과를 가짐
#####################################################################

def build_faiss_index():
    """
    이 함수는 키워드 수에 따른 외곡을 방지하기 위해 아래와 같은 방법으로 임베딩 벡터화를 진행합니다.

    - 각 영화에 대해 **문장**을 생성하여 임베딩
    - 각 임베딩(장르, 소개, 키워드)을 평균 내어 단일 벡터로 생성
    - L2 정규화 (백터 크기 고정)
    - FAISS에 인덱스 추가
    """
    print("[INFO] 다중 벡터 기반 FAISS 인덱스 구축 중...")

    # 임베딩 차원 확인
    sample_text = "샘플 텍스트"
    d = model.encode([sample_text], convert_to_numpy=True).shape[1]

    # 🔹 저장할 임베딩 리스트 및 인덱스 매핑 리스트
    all_embeddings = []
    movie_mapping = []

    # 🔹 각 영화에 대한 임베딩 수행
    for idx, row in df.iterrows():
        embeddings_list = []

        # 🔹 장르 문장 변환 및 임베딩
        if pd.notna(row['장르']):
            genre_sentence = f"이 영화의 장르는 {row['장르']} 입니다."
            genre_embedding = model.encode([genre_sentence], convert_to_numpy=True)[0]
            embeddings_list.append(genre_embedding)
        else:
            embeddings_list.append(np.zeros(d))
            
        # 🔹 키워드 문장 변환 및 임베딩
        if pd.notna(row['키워드(한글)']):
            keyword_sentence = f"이 영화의 주요 키워드는 {row['키워드(한글)']} 입니다."
            keyword_embedding = model.encode([keyword_sentence], convert_to_numpy=True)[0]
            embeddings_list.append(keyword_embedding)
        else:
            embeddings_list.append(np.zeros(d))

        # 🔹 시놉시스 문장 변환 및 임베딩
        if pd.notna(row['소개']):
            synopsis_sentence = f"이 영화의 줄거리는 다음과 같습니다: {row['소개']}"
            synopsis_embedding = model.encode([synopsis_sentence], convert_to_numpy=True)[0]
            embeddings_list.append(synopsis_embedding)
        else:
            embeddings_list.append(np.zeros(d))

        # 🔹 평균 임베딩 + 정규화
        movie_embedding = np.mean(embeddings_list, axis=0)  # 평균 임베딩 계산
        movie_embedding /= np.linalg.norm(movie_embedding)  # L2 정규화 - 벡터 크기 1로 고정

        all_embeddings.append(movie_embedding)
        movie_mapping.append(idx)  # 해당 영화의 ID 저장

    # 🔹 벡터 배열 변환
    all_embeddings = np.vstack(all_embeddings)

    # 🔹 FAISS 인덱스 생성 및 저장
    index = faiss.IndexFlatIP(d)  # 내적 기반 유사도 검색
    index.add(all_embeddings)

    faiss.write_index(index, FAISS_INDEX_FILE)
    np.save("movie_indices.npy", np.array(movie_mapping))

    print("[INFO] FAISS 인덱스 저장 완료.")


# FAISS 인덱스 로드 (없으면 생성)
def load_faiss_index():
    if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(MOVIE_INDICES_FILE):
        print("[INFO] 기존 FAISS 인덱스 로드 중...")
        index = faiss.read_index(FAISS_INDEX_FILE)
        movie_indices = np.load(MOVIE_INDICES_FILE)
        return index, movie_indices
    else:
        print("❌ FAISS 인덱스를 찾을 수 없습니다. 새로 생성합니다...")
        build_faiss_index()  # FAISS 인덱스 생성
        index = faiss.read_index(FAISS_INDEX_FILE)
        movie_indices = np.load(MOVIE_INDICES_FILE)
        return index, movie_indices
    

# 제외할 키워드 필터링하는 함수
def filter_movies_by_exclusion(df, exclusion_keywords, threshold=0.8):
    if not exclusion_keywords:
        return df  # 제외할 키워드가 없으면 그대로 반환

    exclusion_embeddings = model.encode(exclusion_keywords, convert_to_numpy=True)  # 🔹 제외할 키워드 벡터화

    def is_relevant(row_keywords):
        if not row_keywords:
            return True  # 키워드가 없는 경우 필터링 대상 아님

        movie_keywords = row_keywords.split(", ")  # 🔹 영화 키워드 리스트화
        movie_embeddings = model.encode(movie_keywords, convert_to_numpy=True)  # 🔹 영화 키워드 벡터화

        # 🔹 제외할 키워드와 영화 키워드 간의 유사도 계산
        similarities = cosine_similarity(movie_embeddings, exclusion_embeddings)

        # 🔹 유사도가 threshold 이상인 키워드가 있으면 제외
        return not (similarities >= threshold).any()

    mask = df["키워드(한글)"].apply(is_relevant)  # 🔹 해당 조건을 만족하는 영화만 남김
    return df[mask]



# STEP1 : 사용자 질문 LLM 분석 진행.
def analyze_question_with_llm(user_question):
    prompt = f"""
    사용자가 영화 추천을 요청했습니다.
    다음 질문을 기반으로 영화의 장르, 분위기, 키워드, 감독, 주연 등의 정보를 분석하세요.
    질문: "{user_question}"

    이 질문을 기반으로 가장 적절한 검색 키워드를 생성하세요.

    "핵심 키워드"는 질문에서 가장 중요한 요소이며, 특정한 배경, 테마, 계절, 감성 등을 나타낼 수 있습니다.
    "핵심 키워드"가 없는 경우에는 빈 값으로 설정하세요.

    - 예제:
        - "크리스마스 영화 추천해줘" → 핵심 키워드: ["크리스마스"]
        - "비 오는 날 볼 영화 추천해줘" → 핵심 키워드: ["비"]
        - "연인이랑 볼만한 영화 추천해줘" → 핵심 키워드: ["로맨스"]
        - "재미있는 영화 추천해줘" → 핵심 키워드: []
        - "가족과 볼 만한 영화 추천해줘" → 핵심 키워드: []
    
    "핵심 키워드"는 1개만 반환합니다.

    JSON 형식으로 반환하세요.
    예시: {{"장르": ["로맨스", "코미디", "드라마"], "분위기": ["감성적인", "따뜻한"], "키워드": ["크리스마스", "겨울", "눈", "연말"], "감독": "봉준호", "주연": "송강호", "제외할 키워드": ["폭력", "강간", "잔인한", "폭행", "우울", "살인"], "핵심 키워드" : ["크리스마스"]}}
    
    분석 결과에 대한 장르 3개, 분위기 3개, 키워드와 제외할 키워드는 각각 5개씩 반환합니다.
    
    질문을 분석한 뒤에 필요치 않는 KEY값은 반환하지 않습니다.
    예시: "봉준호 감독의 영화 추천해줘"와 같은 질문의 경우, "장르", "분위기", "키워드", "주연", "제외할 키워드" 등의 요소가 필요하지 않습니다. 반면에 "겨울에 볼만한 영화 추천해줘"와 같은 질문의 경우, "감독", "주연" 등의 요소가 필요하지 않습니다.
    특정 시리즈 영화 추천을 원할 경우, 시리즈마다 영화 감독과 배우가 변경되는 경우가 있기 때문에 이를 고려해야합니다.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "당신은 영화 추천 전문가입니다."},
                  {"role": "user", "content": prompt}],
    )
    # 🔹 응답 내용 가져오기
    raw_content = response.choices[0].message.content
    print("[INFO] GPT 응답:", raw_content)  # 디버깅용 출력

    # 빈 응답 체크
    if not raw_content:
        print("❌ GPT 응답이 비어 있습니다.")
        return {}

    # JSON 코드 블록 제거 (`json.loads()`를 적용하기 전 정리)
    if raw_content.startswith("```json"):
        raw_content = raw_content.strip("```json").strip("```").strip()

    try:
        parsed_json = json.loads(raw_content)  # 🔹 JSON 변환
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"❌ JSON 변환 실패: {e}")
        return {}


# STEP2: 1차 필터링
def search_movies_with_keywords(expanded_keywords, top_k=100):  # 처음 top_k = 100 
    """
    - 감독이나 주연 배우가 있는 경우: 전체 DB에서 직접 필터링 (FAISS 사용 X)
    - 핵심 키워드가 있는 경우: 해당 키워드를 최우선으로 검색 후 기존 검색 결과와 병합
    """
    index, movie_indices = load_faiss_index()

    if index is None or movie_indices is None:
        return pd.DataFrame()  # 인덱스가 없으면 빈 데이터프레임 반환

    expanded_keywords.setdefault("장르", [])
    expanded_keywords.setdefault("분위기", [])
    expanded_keywords.setdefault("키워드", [])
    expanded_keywords.setdefault("핵심 키워드", [])  # 🔹 리스트로 설정
    expanded_keywords.setdefault("제외할 키워드", [])
    expanded_keywords.setdefault("감독", [])
    expanded_keywords.setdefault("주연", [])

    result_df = pd.DataFrame()

    # 🔹 1. 감독/배우 리스트 기반 필터링
    if expanded_keywords["감독"] or expanded_keywords["주연"]:
        def has_common_element(db_list, query_list):
            if not db_list or not query_list:
                return False
            db_set = set(db_list.split(", "))
            query_set = set(query_list)
            return not db_set.isdisjoint(query_set)

        director_filter = df["감독"].apply(lambda x: has_common_element(x, expanded_keywords["감독"]))
        actor_filter = df["주연"].apply(lambda x: has_common_element(x, expanded_keywords["주연"]))

        result_df = df[director_filter | actor_filter]
        result_df = filter_movies_by_exclusion(result_df, expanded_keywords["제외할 키워드"])

        if not result_df.empty:
            return result_df

    # 🔹 2. 핵심 키워드 기반 검색 (문자열 기반 필터링)
    core_keyword_results = pd.DataFrame()

    if expanded_keywords["핵심 키워드"]:
        core_keyword = expanded_keywords["핵심 키워드"][0] if expanded_keywords["핵심 키워드"] else ""

        # 🔹 FAISS 검색 수행
        core_query_embedding = model.encode([core_keyword], convert_to_numpy=True)
        core_query_embedding /= (np.linalg.norm(core_query_embedding) + 1e-10)  # 정규화

        core_query_embedding = core_query_embedding.reshape(1, -1)  # FAISS는 2D 배열 필요
        _, core_indices = index.search(core_query_embedding, top_k // 2)  # 핵심 키워드 중심 검색

        # 🔹 검색된 영화 인덱스 변환 및 중복 제거
        core_movie_indices = [movie_indices[i] for i in core_indices[0]]
        core_keyword_results = df.iloc[core_movie_indices].drop_duplicates(subset=["영화 제목"])
        core_keyword_results = filter_movies_by_exclusion(core_keyword_results, expanded_keywords["제외할 키워드"])

    # 🔹 3. FAISS 검색 (키워드 + 분위기 & 장르 개별 임베딩)
    keyword_mood_text = ", ".join(expanded_keywords["키워드"] + expanded_keywords["분위기"])
    genre_text = ", ".join(expanded_keywords["장르"])
    
    if not keyword_mood_text:
        keyword_mood_text = "영화"
    if not genre_text:
        genre_text = "영화 장르"

    keyword_mood_embedding = model.encode([keyword_mood_text], convert_to_numpy=True)
    genre_embedding = model.encode([genre_text], convert_to_numpy=True)

    # 🔹 두 벡터를 평균 내어 최종 검색 벡터 생성
    query_embedding = (keyword_mood_embedding + genre_embedding) / 2
    query_embedding /= np.linalg.norm(query_embedding)  # 정규화

    query_embedding = query_embedding.reshape(1, -1)  # 2D 배열 변환
    faiss.normalize_L2(query_embedding)
    _, indices = index.search(query_embedding, top_k)

    faiss_movie_indices = [movie_indices[i] for i in indices[0]]
    faiss_results = df.iloc[faiss_movie_indices].drop_duplicates(subset=["영화 제목"])

    if not faiss_results.empty:
        faiss_results = filter_movies_by_exclusion(faiss_results, expanded_keywords["제외할 키워드"])

    # 🔹 4. 최종 결과 병합 및 중복 제거
    result_df = pd.concat([result_df, core_keyword_results, faiss_results]).drop_duplicates(subset=["영화 제목"])

    print(f"[INFO] 최종 검색된 영화 개수: {len(result_df)}")
    return result_df


# STEP3: LLM을 활용한 최종 추천 생성
def generate_recommendations(user_question, search_results, max_results=5, batch_size=10):
    if search_results.empty:
        return []

    movie_data = search_results[['영화 제목', '장르', '감독', '주연', '키워드(한글)']].to_dict(orient='records')
    total_movies = len(movie_data)


    # LLM 호출을 Batch 단위로 수행하여 RateLimit 방지
    recommended_movies = []
    for i in range(0, total_movies, batch_size):
        batch = movie_data[i:i+batch_size]

        prompt = f"""
        당신은 영화를 추천하는 영화 추천 전문가입니다.
        사용자가 영화 추천을 요청했습니다.
        질문: "{user_question}"
        사용자가 원하는 추천 개수: {max_results}개
        
        아래는 검색된 영화 목록입니다.
        이 중에서 사용자가 요청한 질문에 관련없는 영화는 제외하고, 가장 적절한 영화를 추천하세요.
        관련된 영화가 {max_results}개보다 적다면 적은 개수만 추천하세요.

        사람들에게 인지도가 높고 꾸준히 회자되는 영화를 우선적으로 추천하세요.
        질문이 특정 테마의 영화를 원하고 있다면 이를 바탕으로 추천하세요.
        다만, context에 없는 영화는 포함하지 마세요.

        **중요:** 답변은 **반드시** 다음 JSON 형식으로 영화제목 리스트를 반환하세요. 
        JSON 이외의 텍스트는 절대 포함하지 마세요.

        [[출력형식]] :
        {json.dumps(batch, ensure_ascii=False)}

        영화의 상세 정보를 포함하지 마세요.
        오직 "추천 영화"의 제목만 리스트에 포함해야 합니다. 

        예시:
        {{"추천 영화": ["영화1", "영화2", "영화3"]}}
        """

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "당신은 영화 추천 전문가입니다."},
                    {"role": "user", "content": prompt}],
        )

        # 삭제한 프롬프트 내용: 답변을 반환하기 전, 다시 한번 이 영화가 사용자의 질문에 어울리는 영화인지, context에 있는지 판단하세요.

        try:
            batch_recommendations = json.loads(response.choices[0].message.content).get("추천 영화", [])

            # ✅ dict 형태가 있는 경우, '영화 제목' 값만 추출하여 리스트에 추가
            batch_recommendations = [movie["영화 제목"] if isinstance(movie, dict) else movie for movie in batch_recommendations]

            # movie_list = []
            # for movie in batch_recommendations:
            #     if isinstance(movie, dict):
            #         movie_list.append(movie["영화 제목"])
            #         print(movie_list)
            #     else:
            #         movie_list.append(movie)
            #         print(movie_list)

            # recommended_movies = movie_list

            recommended_movies.extend(batch_recommendations)

        except json.JSONDecodeError:
            print("❌ LLM에서 잘못된 응답을 받았습니다.")
            print(f"응답내용: {response.choices[0].message.content}")

        # ✅ 최대 결과 개수만큼만 유지
        if len(recommended_movies) >= max_results:
            break

    return recommended_movies[:max_results]