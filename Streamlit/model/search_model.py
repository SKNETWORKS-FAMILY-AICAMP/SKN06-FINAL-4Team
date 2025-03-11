import json
import numpy as np
import faiss
import openai
import os
import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
openai_client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
"영화 ID"
# 모델 로드
model = SentenceTransformer("BAAI/bge-m3", use_auth_token=hf_api_key)

# 엑셀 DB 로드
FAISS_KEY_WORD_INDEX_FILE = "data/key_word_faiss_index.idx"
KEY_WORD_INDICES_FILE = "data/key_word_indices.npy"
EXCEL_FILE_PATH = "data/Movie_DB_3262_2차.xlsx"
df = pd.read_excel(EXCEL_FILE_PATH).fillna("")

def load_faiss_indices():
    """
    FAISS 인덱스를 로드하고, 없을 경우 새로 생성
    """
    key_word_index = None
    key_word_indices = None

    if os.path.exists(FAISS_KEY_WORD_INDEX_FILE) and os.path.exists(KEY_WORD_INDICES_FILE):
        print("[INFO] 기존 FAISS 줄거리 인덱스 로드 중...")
        key_word_index = faiss.read_index(FAISS_KEY_WORD_INDEX_FILE)
        key_word_indices = np.load(KEY_WORD_INDICES_FILE)

    # 존재하지 않으면 새로 생성
    if key_word_index is None:
        print("❌ FAISS 인덱스를 찾을 수 없습니다. 새로 생성합니다...")
        build_faiss_indices()
        return load_faiss_indices()


    return key_word_index, key_word_indices

def build_faiss_indices():
    """
    FAISS 인덱스를 생성하고 저장
    """
    # 임베딩 저장용 리스트
    key_word_embeddings = []
    key_word_mapping = []

    # 1️⃣ 키워드 임베딩 생성 및 저장
    for idx, row in df.iterrows():
        if pd.notna(row['키워드']) and row['키워드'].strip():  # 빈 키워드 제외
            key_words = row['키워드'].split(',')    # 키워드 분할
            key_words = [kw.strip() for kw in key_words if kw.strip()]    # 공백 제거

            for key_word in key_words:
                embedding = model.encode(key_word, convert_to_numpy=True)
                key_word_embeddings.append(embedding)
                key_word_mapping.append(idx)    # 각각의 키워드와 영화 ID 매핑

    # 2️⃣ FAISS 인덱스 생성 및 저장
    if key_word_embeddings:
        key_word_embeddings_array = np.array(key_word_embeddings)

        # 코사인 유사도를 위해 L2 정규화
        faiss.normalize_L2(key_word_embeddings_array)

        # FAISS 인덱스 생성 (코사인 유사도 기반)
        key_word_index = faiss.IndexFlatIP(key_word_embeddings_array.shape[1])  # IndexFlatIP -> Inner Product(내적 진행) - (Cosine Similarity)
        key_word_index.add(key_word_embeddings_array)

        # 3️⃣ FAISS 인덱스 & 매핑된 영화 ID 저장
        faiss.write_index(key_word_index, FAISS_KEY_WORD_INDEX_FILE)
        np.save(KEY_WORD_INDICES_FILE, np.array(key_word_mapping))

    else:
        print("[ERROR] 저장할 키워드 임베딩이 없습니다.")



# STEP1 : 사용자 질문 LLM 분석 진행.
def analyze_question_with_llm(user_question):
    prompt = f"""
    사용자가 영화 추천을 요청했습니다.
    다음 질문을 기반으로 영화의 장르, 분위기, 키워드, 감독, 주연 등의 정보를 분석하세요.
    질문: "{user_question}"

    이 질문을 기반으로 가장 적절한 검색 키워드를 생성하세요.

    ※주요 규칙※
    1. 키워드는 하나의 명사로만 작성해야합니다. (감독, 주연 이름 제외)
    - 예시 : "독립운동"(O), "한국 전쟁"(X)

    2. 반드시 json형식으로 반환하세요.

    3. 감독이나 주연배우에 대한 구체적인 요청이 있는 경우 감독/주연배우를 입력한 값으로 **무조건** 반환합니다. 이때, 키워드 값은 반환하지 않습니다.
    4. 분석 결과에 대한 키워드는 3개씩 반환합니다. 하지만 감독이나 주연배우를 찾는 질문에서는 키워드를 반환하지 않습니다.
    - 예시 : {{ "키워드": ["크리스마스", "겨울", "눈", "연말"]}}
    - 예시 : "ooo가 나오는", "ooo이 나오는", "ooo이 출연한" 등의 질문은 감독이나 주연배우를 찾는 질문이기 때문에 키워드 값을 반환하지 않습니다.

    5. 질문의 핵심적인 요소 하나를 키워드에 포함시킵니다.

    6. 질문에 필요하지 않는 값은 절대로 반환하지 않습니다.
    - 예시 : "봉준호 감독의 영화 추천해줘"와 같은 질문의 경우, "키워드", "주연" 요소가 필요하지 않습니다.
    - 예시 : "톰 크루즈가 나오는 영화 추천해줘"와 같은 질문의 경우, "키워드", "감독" 요소가 필요하지 않습니다.
    - 예시 : "겨울에 볼만한 영화 추천해줘"와 같은 질문의 경우, "감독", "주연"의 요소가 필요하지 않습니다.
    
    7. 시리즈 영화 추천을 요구받은 경우엔 주연이나 감독명을 사용해도 됩니다. 다만 시리즈마다 영화 감독과 배우가 변경되는 경우가 있기 때문에 이를 고려해야합니다.

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
    


def search_movies_with_faiss(expanded_keywords, top_k=300):
    """
    - 감독이나 주연 배우가 있는 경우: 전체 DB에서 직접 필터링 (FAISS 사용 X)
    - 핵심 키워드가 있는 경우: 해당 키워드를 최우선으로 검색 후 기존 검색 결과와 병합
    """
    key_word_index, key_word_indices = load_faiss_indices()

    print('[DEBUG] 키워드 확인 : ', expanded_keywords)
    # 영화 ID → 영화 이름 변환을 위한 딕셔너리 생성
    expanded_keywords.setdefault("키워드", [])
    expanded_keywords.setdefault("감독", [])
    expanded_keywords.setdefault("주연", [])

    # 감독, 주연이 문자열인 경우 리스트로 변환
    if isinstance(expanded_keywords["감독"], str):
        expanded_keywords["감독"] = [expanded_keywords["감독"]]
    if isinstance(expanded_keywords["주연"], str):
        expanded_keywords["주연"] = [expanded_keywords["주연"]]

    result_df = pd.DataFrame()

    # 🔹 1. 감독/배우 리스트 기반 필터링 -> 정답이 정해져 있기 때문에 DF에서 직접 반환
    
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
        print(result_df)

        if not result_df.empty:
            return result_df

    # 🔹 2. 검색용 키워드 임베딩 생성
    search_key_word_embeddings = []

    for keyword in expanded_keywords['키워드']:
        if isinstance(keyword, str) and keyword.strip():  # 빈 키워드 제외
            embedding = model.encode(keyword.strip(), convert_to_numpy=True)
            search_key_word_embeddings.append(embedding)

    # NumPy 배열로 변환
    if search_key_word_embeddings:
        search_key_word_embeddings_array = np.array(search_key_word_embeddings)
        faiss.normalize_L2(search_key_word_embeddings_array)
    else:
        return pd.DataFrame()  # 키워드가 없을 경우 빈 데이터프레임 반환

    # 🔹 3. 키워드 기반 필터링 : 1~5번 각 키워드 유사 영화 반환 -> 교집합 구하기
    _, search_indices_1 = key_word_index.search(search_key_word_embeddings_array[0].reshape(1, -1), top_k)
    search_results_1 = set(int(key_word_indices[n]) for n in search_indices_1[0])    # key_word_indices[n] -> np.int 교집합이 안구해짐 -> int로 변경

    _, search_indices_2 = key_word_index.search(search_key_word_embeddings_array[1].reshape(1, -1), top_k)
    search_results_2 = set(int(key_word_indices[n]) for n in search_indices_2[0])

    _, search_indices_3 = key_word_index.search(search_key_word_embeddings_array[2].reshape(1, -1), top_k)
    search_results_3 = set(int(key_word_indices[n]) for n in search_indices_3[0])
    
    # 🔹 4. 다섯 개의 결과에서 교집합을 구함
    final_recommended_movies = search_results_1 & search_results_2 & search_results_3

    # 3️⃣ 리스트 변환 후 결과 출력
    recommended_movie_ids = list(final_recommended_movies)

    print("🔍 추천 영화 ID 목록:", recommended_movie_ids)

    # 5️⃣ 영화 ID를 기반으로 DataFrame 필터링
    recommended_movies_df = df.loc[df.index.isin(recommended_movie_ids)]

    return recommended_movies_df  # ✅ 결과 반환


# STEP4: LLM을 활용한 최종 추천 생성
def generate_recommendations(user_question, search_results, max_results=8, batch_size=10):
    if search_results.empty:
        return []

    movie_data = search_results[['영화 제목', '개봉일', '장르', '감독', '주연', '줄거리', '키워드']].to_dict(orient='records')
    total_movies = len(movie_data)

    # LLM 호출을 Batch 단위로 수행하여 RateLimit 방지
    recommended_movies = []
    for i in range(0, total_movies, batch_size):
        batch = movie_data[i:i+batch_size]

        prompt = f"""
        당신은 영화를 추천하는 영화 추천 전문가입니다.
        사용자가 영화 추천을 요청했습니다.
        
        질문: "{user_question}"
        사용자가 원하는 추천 개수: 최대 {max_results}개
        제공된 영화 데이터: {json.dumps(batch, ensure_ascii=False)}
        
        질문을 정확하게 이해하고, 사용자에게 알맞는 영화를 추천해야합니다.
        질문을 반드시 숙지하세요.

        ※ 중요한 규칙 ※
        1. 제공된 '영화 데이터' 내에서만 추천하세요. (새로운 영화를 추가하지 마세요.)
        2. 질문과 관련이 없는 영화는 절대 추천하지 마세요.
        답변을 반환하기 전, 다시 한번 이 영화가 사용자의 질문에 어울리는 영화인지, DB에 있는지 판단하세요.

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
            # "추천 영화"가 dict 형태로 들어오지 않도록 필터링 (제목만 추출)
            batch_recommendations = [
                movie["영화 제목"] if isinstance(movie, dict) else movie
                for movie in batch_recommendations
            ]
            recommended_movies.extend(batch_recommendations)
        except json.JSONDecodeError:
            print("❌ LLM에서 잘못된 응답을 받았습니다.")

                # ✅ 최대 결과 개수만큼만 유지
        if len(recommended_movies) >= max_results:
            break

    return recommended_movies[:max_results]

