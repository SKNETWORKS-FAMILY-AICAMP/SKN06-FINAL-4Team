import pandas as pd
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import openai
import os

load_dotenv()
hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
openai_client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

# 임베딩 모델 로드
model = SentenceTransformer("all-MiniLM-L6-v2", use_auth_token=hf_api_key)

# 엑셀 DB 로드
EXCEL_FILE_PATH = "../data/MOVIE_DB/MOVIE_DB_7005.xlsx"
df = pd.read_excel(EXCEL_FILE_PATH).fillna("")
review_db_path = "../data/MOVIE_DB/Reviews.xlsx"
review_df = pd.read_excel(review_db_path)

# FAISS 인덱스 저장 파일 경로
FAISS_INDEX_FILE = "../search_model/faiss_index.bin"
MOVIE_INDICES_FILE = "../search_model/movie_indices.npy"

#####################################################################
# 다중 벡터화
#####################################################################

def build_faiss_index():
    print("[INFO] 다중 벡터 기반 FAISS 인덱스 구축 중...")

    all_embeddings = []
    movie_mapping = []

    for idx, row in df.iterrows():
        embeddings_list = []

        # 🔹 "장르" 벡터화 (각 장르 개별 벡터 생성)
        if pd.notna(row['장르']):
            genres = row['장르'].split(", ")  # "액션, 범죄" → ["액션", "범죄"]
            genre_embeddings = model.encode(genres, convert_to_numpy=True)
            embeddings_list.append(genre_embeddings)

        # 🔹 "키워드" 벡터화 (각 키워드 개별 벡터 생성)
        if pd.notna(row['키워드(한글)']):
            keywords = row['키워드(한글)'].split(", ")  # "탈출, 나치, 역사" → ["탈출", "나치", "역사"]
            keyword_embeddings = model.encode(keywords, convert_to_numpy=True)
            embeddings_list.append(keyword_embeddings)

        # 🔹 "영화 소개" 벡터화 (문장 단위 벡터 생성)
        if pd.notna(row['소개']):
            intro_embedding = model.encode([row['소개']], convert_to_numpy=True)
            embeddings_list.append(intro_embedding)

        # 🔹 모든 벡터를 하나로 합치기
        if embeddings_list:
            movie_embeddings = np.vstack(embeddings_list)
            all_embeddings.append(movie_embeddings)

            # 🔹 해당 영화의 ID를 여러 개 추가 (벡터 개수만큼)
            for _ in range(len(movie_embeddings)):
                movie_mapping.append(idx)

    # 🔹 벡터 배열로 변환 및 정규화
    all_embeddings = np.vstack(all_embeddings)
    faiss.normalize_L2(all_embeddings)

    # 🔹 FAISS 인덱스 생성
    d = all_embeddings.shape[1]  # 벡터 차원 수
    index = faiss.IndexFlatIP(d)
    index.add(all_embeddings)

    # 🔹 인덱스 저장
    faiss.write_index(index, FAISS_INDEX_FILE)
    np.save(MOVIE_INDICES_FILE, np.array(movie_mapping))

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
    예시: {{"장르": ["로맨스", "코미디", "드라마"], "분위기": ["감성적인", "따뜻한"], "키워드": ["크리스마스", "겨울", "눈", "연말"], "감독": "봉준호", "주연": "송강호", "제외할 키워드": ["폭력", "강간", "잔인한"], "핵심 키워드" : ["크리스마스"]}}
    
    분석 결과에 대한 장르, 분위기, 키워드, 제외할 키워드는 3개씩 반환합니다.
    
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


## 제외할 키워드를 가지고 있는 영화 필터링하는 함수
def filter_movies_by_exclusion(df, exclusion_keywords):
    if not exclusion_keywords:
        return df  # 제외할 키워드가 없으면 그대로 반환
    mask = df.apply(lambda row: not any(excl in row["키워드(한글)"] for excl in exclusion_keywords), axis=1)
    return df[mask]


# STEP3 : FAISS 검색 후 필터링 진행 (핵심 키워드 반영 + 감독, 주연 필터링 보강)
def search_movies_with_keywords(expanded_keywords, top_k=100):
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
    expanded_keywords.setdefault("핵심 키워드", [])
    expanded_keywords.setdefault("제외할 키워드", [])
    expanded_keywords.setdefault("감독", "")
    expanded_keywords.setdefault("주연", "")

    # 항상 존재하는 빈 데이터프레임 선언 (에러 방지)
    result_df = pd.DataFrame()

    # 🔹 1. 감독이 명확히 주어진 경우 → DB에서 직접 필터링
    if expanded_keywords["감독"]:
        result_df = df[df["감독"].str.contains(expanded_keywords["감독"], na=False)]
        result_df = filter_movies_by_exclusion(result_df, expanded_keywords["제외할 키워드"])
        return result_df

    # 🔹 2. 주연 배우가 명확히 주어진 경우 → DB에서 직접 필터링
    if expanded_keywords["주연"]:
        result_df = df[df["주연"].str.contains(expanded_keywords["주연"], na=False)]
        result_df = filter_movies_by_exclusion(result_df, expanded_keywords["제외할 키워드"])
        return result_df

    # 🔹 3. 핵심 키워드가 있다면, 해당 키워드를 최우선으로 검색
    keyword_filter_movies = pd.DataFrame()
    if expanded_keywords["핵심 키워드"]:
        keyword_filter_movies = df[df["키워드(한글)"].str.contains("|".join(expanded_keywords["핵심 키워드"]), na=False)]

    core_keyword_results = pd.DataFrame()
    if expanded_keywords["핵심 키워드"]:
        core_query_embedding = model.encode([", ".join(expanded_keywords["핵심 키워드"])], convert_to_numpy=True)
        faiss.normalize_L2(core_query_embedding)
        _, core_indices = index.search(core_query_embedding, top_k // 2)  # 핵심 키워드는 따로 검색
        core_keyword_results = df.iloc[movie_indices[core_indices[0]]].drop_duplicates(subset=["영화 제목"])

    # 🔹 4. FAISS 검색 수행 (장르 + 키워드 + 분위기 포함)
    query_text = expanded_keywords["장르"] + expanded_keywords["키워드"] + expanded_keywords["분위기"]
    weighted_query_text = query_text + (expanded_keywords["핵심 키워드"] * 2)  # 핵심 키워드 가중치 2배 적용
    query_embedding = model.encode([", ".join(weighted_query_text)], convert_to_numpy=True)

    faiss.normalize_L2(query_embedding)
    _, indices = index.search(query_embedding, top_k)

    faiss_results = df.iloc[movie_indices[indices[0]]].drop_duplicates(subset=["영화 제목"])
    faiss_results = filter_movies_by_exclusion(faiss_results, expanded_keywords["제외할 키워드"])

    print("[INFO] FAISS 검색 결과를 가져왔습니다.")

    # 🔹 5. 분위기 키워드 기반 FAISS 검색 추가 (기존의 DB 직접 검색 제거)
    mood_results = pd.DataFrame()
    if expanded_keywords["분위기"]:
        mood_query_embedding = model.encode([", ".join(expanded_keywords["분위기"])], convert_to_numpy=True)
        faiss.normalize_L2(mood_query_embedding)
        _, mood_indices = index.search(mood_query_embedding, top_k)
        mood_results = df.iloc[movie_indices[mood_indices[0]]].drop_duplicates(subset=["영화 제목"])


    # 6. 빈 데이터프레임 문제 해결 → 항상 존재하는 result_df와 병합
    result_df = pd.concat([result_df, keyword_filter_movies, mood_results, core_keyword_results, faiss_results]).drop_duplicates(subset=["영화 제목"])

    print(f"[INFO] 최종 검색된 영화 개수: {len(result_df)}")
    return result_df



# STEP4: LLM을 활용한 최종 추천 생성
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
        단, 질문과 관련이 없는 영화는 제외하고, 관련된 영화가 {max_results}개보다 적다면 적은 개수만 추천하세요.

        사람들에게 인지도가 높고 꾸준히 회자되는 영화를 우선적으로 추천하세요.
        다만, DB에 없는 영화는 포함하지 마세요.

        답변을 반환하기 전, 다시 한번 이 영화가 사용자의 질문에 어울리는 영화인지 판단하세요.

        JSON 형식으로 영화 리스트를 반환하세요. JSON 이외의 텍스트는 절대 포함하지 마세요.
        {json.dumps(batch, ensure_ascii=False)}

        예시:
        {{"추천 영화": ["영화1", "영화2", "영화3"]}}
        """

        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "당신은 영화 추천 전문가입니다."},
                    {"role": "user", "content": prompt}],
        )

        try:
            batch_recommendations = json.loads(response.choices[0].message.content).get("추천 영화", [])
            recommended_movies.extend(batch_recommendations)
        except json.JSONDecodeError:
            print("❌ LLM에서 잘못된 응답을 받았습니다.")

                # ✅ 최대 결과 개수만큼만 유지
        if len(recommended_movies) >= max_results:
            break

    return recommended_movies[:max_results]

