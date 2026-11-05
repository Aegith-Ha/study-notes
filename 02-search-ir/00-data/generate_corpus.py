"""02-search-ir 공통 실험 데이터(corpus, queries, qrels) 생성기.

- 문서는 concept(의미 단위)를 하나 이상 포함한다.
- query는 concept마다 keyword / paraphrase 두 종류를 만든다.
  - keyword   : 문서에 실제로 나오는 단어로 구성 (sparse가 유리)
  - paraphrase: 같은 의미를 다른 단어로 표현 (dense가 유리)
- qrels는 토큰 겹침이 아니라 concept 일치로 라벨링한다.
  그래서 paraphrase query도 keyword query와 같은 정답 문서를 가진다.
"""

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "generated"

TOKEN_PATTERN = re.compile(r"[0-9a-zA-Z가-힣]+(?:-[0-9a-zA-Z가-힣]+)?")


# 주제별 concept 정의.
# - phrase    : 문서 본문에 들어가는 문장 (concept의 실제 내용)
# - keyword   : phrase의 단어를 그대로 쓴 query
# - paraphrase: 같은 의미를 phrase와 겹치지 않는 단어로 쓴 query
TOPICS = {
    "search": {
        "keywords": [
            "bm25", "tf-idf", "랭킹", "문서", "검색", "질의", "색인", "역색인",
            "토크나이저", "형태소", "스코어", "검색엔진",
        ],
        "concepts": [
            {
                "id": "search_bm25",
                "phrase": "BM25는 정보 검색에서 자주 사용하는 랭킹 함수이다.",
                "keyword": "bm25 랭킹 정보 검색",
                "paraphrase": "단어 빈도로 순서를 매기는 확률 기반 공식",
            },
            {
                "id": "search_relevance",
                "phrase": "검색 엔진은 질의와 문서의 관련도를 계산해 결과를 정렬한다.",
                "keyword": "검색 엔진 관련도 계산",
                "paraphrase": "찾기 시스템이 질문에 맞는 글을 어떤 순서로 보여주나",
            },
            {
                "id": "search_length_norm",
                "phrase": "문서 길이 정규화는 BM25 점수 계산에서 중요한 요소다.",
                "keyword": "문서 길이 정규화 bm25",
                "paraphrase": "긴 글이 유리해지지 않게 보정하는 이유",
            },
            {
                "id": "search_inverted_index",
                "phrase": "역색인은 검색 시스템의 핵심 자료구조 중 하나이다.",
                "keyword": "역색인 검색 시스템 자료구조",
                "paraphrase": "단어마다 등장한 글 목록을 저장해 두는 방법",
            },
            {
                "id": "search_tokenizer",
                "phrase": "토크나이저와 형태소 분석기는 검색 품질에 직접적인 영향을 준다.",
                "keyword": "토크나이저 형태소 분석기 검색 품질",
                "paraphrase": "글을 작은 단위로 쪼개는 도구가 찾기 정확도에 미치는 효과",
            },
        ],
        "title_templates": [
            "{k1} 기본 개념",
            "{k1}와 {k2} 비교",
            "{k1} 기반 {k2} 정리",
            "{k1}와 {k2}를 이용한 {k3}",
            "{k1} {k2} {k3} 개요",
        ],
    },
    "llm": {
        "keywords": [
            "rag", "llm", "프롬프트", "임베딩", "리트리버", "리랭커",
            "생성", "컨텍스트", "청크", "벡터", "파인튜닝", "응답",
        ],
        "concepts": [
            {
                "id": "llm_rag",
                "phrase": "RAG는 검색과 생성 모델을 결합하는 구조이다.",
                "keyword": "rag 생성 모델 결합",
                "paraphrase": "외부 지식을 찾아와서 답을 써 주는 언어모델 기법",
            },
            {
                "id": "llm_context",
                "phrase": "LLM은 입력된 컨텍스트를 바탕으로 응답을 생성한다.",
                "keyword": "llm 입력된 컨텍스트 응답",
                "paraphrase": "거대 언어모델이 주어진 배경 정보로 답을 만드는 과정",
            },
            {
                "id": "llm_embedding_search",
                "phrase": "임베딩 기반 검색은 관련 문서를 빠르게 찾는 데 사용된다.",
                "keyword": "임베딩 기반 검색 관련 문서",
                "paraphrase": "숫자 표현의 유사도로 비슷한 글을 신속하게 찾아내기",
            },
            {
                "id": "llm_chunking",
                "phrase": "청크 분할 방식은 RAG 품질에 큰 영향을 준다.",
                "keyword": "청크 분할 rag 품질",
                "paraphrase": "긴 글을 어떤 크기로 자르느냐에 따라 달라지는 대답 정확도",
            },
            {
                "id": "llm_retriever_reranker",
                "phrase": "리트리버와 리랭커는 검색 증강 시스템의 핵심 구성요소다.",
                "keyword": "리트리버 리랭커 검색 증강",
                "paraphrase": "후보를 가져오는 모듈과 순서를 다시 매기는 모듈의 역할",
            },
        ],
        "title_templates": [
            "{k1} 기본 구조",
            "{k1}와 {k2} 개요",
            "{k1} 기반 {k2} 설계",
            "{k1}를 이용한 {k2} 생성",
            "{k1} {k2} {k3} 정리",
        ],
    },
    "python": {
        "keywords": [
            "파이썬", "리스트", "딕셔너리", "셋", "튜플", "반복문",
            "함수", "클래스", "예외", "제너레이터", "타입힌트", "모듈",
        ],
        "concepts": [
            {
                "id": "python_list",
                "phrase": "파이썬의 리스트는 순서가 있는 가변 자료형이다.",
                "keyword": "파이썬 리스트 가변 자료형",
                "paraphrase": "값을 바꿀 수 있고 차례가 유지되는 배열 형태",
            },
            {
                "id": "python_dict",
                "phrase": "딕셔너리는 키와 값으로 데이터를 저장한다.",
                "keyword": "딕셔너리 키와 값 저장",
                "paraphrase": "이름표로 항목을 찾아오는 해시 맵 형태의 컨테이너",
            },
            {
                "id": "python_generator",
                "phrase": "제너레이터는 큰 데이터를 효율적으로 순회하는 데 유용하다.",
                "keyword": "제너레이터 큰 데이터 순회",
                "paraphrase": "yield로 하나씩 꺼내며 메모리를 아끼는 이터레이터",
            },
            {
                "id": "python_type_hint",
                "phrase": "타입힌트는 코드 가독성과 정적 분석에 도움을 준다.",
                "keyword": "타입힌트 코드 정적 분석",
                "paraphrase": "변수와 매개변수에 형식을 표기해 읽기 쉽게 하고 오류를 미리 잡기",
            },
            {
                "id": "python_exception",
                "phrase": "예외 처리는 프로그램의 안정성을 높이는 중요한 요소다.",
                "keyword": "예외 처리 프로그램의 안정성",
                "paraphrase": "try except로 오류가 나도 멈추지 않게 만드는 법",
            },
        ],
        "title_templates": [
            "{k1} 기본 정리",
            "{k1}와 {k2} 차이",
            "{k1} 사용 예제",
            "{k1} 기반 {k2} 설명",
            "{k1} {k2} {k3} 정리",
        ],
    },
    "database": {
        "keywords": [
            "데이터베이스", "sql", "인덱스", "조인", "트랜잭션", "정규화",
            "테이블", "쿼리", "락", "commit", "rollback", "실행계획",
        ],
        "concepts": [
            {
                "id": "db_sql",
                "phrase": "SQL은 관계형 데이터베이스를 다루는 표준 언어다.",
                "keyword": "sql 관계형 데이터베이스 표준",
                "paraphrase": "표 형태 저장소에 명령을 보내는 공통 문법",
            },
            {
                "id": "db_index",
                "phrase": "인덱스는 조회 성능을 높이지만 쓰기 비용을 증가시킬 수 있다.",
                "keyword": "인덱스 조회 성능 쓰기 비용",
                "paraphrase": "찾기는 빨라지지만 insert update가 느려지는 이유",
            },
            {
                "id": "db_transaction",
                "phrase": "트랜잭션은 데이터 일관성을 보장하기 위한 단위이다.",
                "keyword": "트랜잭션 데이터 일관성",
                "paraphrase": "여러 작업을 전부 반영하거나 전부 취소해 정합성을 지키는 묶음",
            },
            {
                "id": "db_join",
                "phrase": "조인 연산은 여러 테이블의 데이터를 결합하는 방법이다.",
                "keyword": "조인 연산 테이블 결합",
                "paraphrase": "두 표의 행을 공통 열로 이어 붙이기",
            },
            {
                "id": "db_query_plan",
                "phrase": "실행계획 분석은 쿼리 성능 최적화에 매우 중요하다.",
                "keyword": "실행계획 분석 쿼리 성능 최적화",
                "paraphrase": "explain으로 느린 조회문의 병목 찾기",
            },
        ],
        "title_templates": [
            "{k1} 기본 원리",
            "{k1}와 {k2} 정리",
            "{k1} 기반 {k2} 최적화",
            "{k1} {k2} {k3} 개요",
            "{k1} 사용 시 {k2}",
        ],
    },
    "linux": {
        "keywords": [
            "리눅스", "프로세스", "쉘", "파일", "권한", "서비스",
            "네트워크", "포트", "로그", "systemd", "grep", "awk",
        ],
        "concepts": [
            {
                "id": "linux_os",
                "phrase": "리눅스는 서버 환경에서 널리 사용되는 운영체제다.",
                "keyword": "리눅스 서버 환경 운영체제",
                "paraphrase": "오픈소스 os를 백엔드 머신에 많이 쓰는 이유",
            },
            {
                "id": "linux_process",
                "phrase": "프로세스 확인에는 ps와 top 같은 명령어를 자주 사용한다.",
                "keyword": "프로세스 확인 ps top 명령어",
                "paraphrase": "돌아가는 프로그램 목록과 cpu 점유를 보는 방법",
            },
            {
                "id": "linux_permission",
                "phrase": "파일 권한은 읽기 쓰기 실행 비트로 구성된다.",
                "keyword": "파일 권한 읽기 쓰기 실행 비트",
                "paraphrase": "chmod 755 숫자가 뜻하는 접근 허용 범위",
            },
            {
                "id": "linux_log",
                "phrase": "로그 분석은 장애 원인을 찾는 데 매우 중요하다.",
                "keyword": "로그 분석 장애 원인",
                "paraphrase": "서버가 죽었을 때 기록을 뒤져 문제를 추적하기",
            },
            {
                "id": "linux_systemd",
                "phrase": "systemd는 서비스 관리와 부팅 제어를 담당한다.",
                "keyword": "systemd 서비스 관리 부팅 제어",
                "paraphrase": "데몬을 켜고 끄고 재시작 시 자동으로 올라오게 등록하기",
            },
        ],
        "title_templates": [
            "{k1} 기본 사용법",
            "{k1}와 {k2} 명령어",
            "{k1} 기반 {k2} 확인",
            "{k1} {k2} {k3} 정리",
            "{k1} 로그 분석 방법",
        ],
    },
    "korean_nlp": {
        "keywords": [
            "한국어", "형태소", "분석기", "복합명사", "조사", "어절",
            "토큰화", "띄어쓰기", "불용어", "품사", "사전", "정규화",
        ],
        "concepts": [
            {
                "id": "ko_analyzer",
                "phrase": "한국어 검색에서는 형태소 분석기의 선택이 매우 중요하다.",
                "keyword": "한국어 검색에서는 형태소 분석기의 선택",
                "paraphrase": "우리말 문장을 처리할 때 mecab okt 중 무엇을 고를지",
            },
            {
                "id": "ko_josa",
                "phrase": "조사 처리 방식은 검색 정확도에 영향을 줄 수 있다.",
                "keyword": "조사 처리 검색 정확도",
                "paraphrase": "은 는 이 가 같은 토씨를 떼어낼지 말지",
            },
            {
                "id": "ko_compound_noun",
                "phrase": "복합명사 분해 여부에 따라 토큰화 결과가 달라진다.",
                "keyword": "복합명사 분해 토큰화",
                "paraphrase": "합성어를 낱말 단위로 쪼갤지에 따른 차이",
            },
            {
                "id": "ko_spacing",
                "phrase": "띄어쓰기 오류는 한국어 정보 검색에서 흔한 문제다.",
                "keyword": "띄어쓰기 오류 한국어 정보 검색",
                "paraphrase": "붙여 쓴 글자 때문에 원하는 글을 못 찾는 상황",
            },
            {
                "id": "ko_pos_filter",
                "phrase": "품사 기반 필터링은 불필요한 토큰을 줄이는 데 도움이 된다.",
                "keyword": "품사 기반 필터링 불필요한 토큰",
                "paraphrase": "명사 동사만 남기고 쓸모없는 낱말을 걸러내기",
            },
        ],
        "title_templates": [
            "{k1} 검색 처리",
            "{k1}와 {k2} 분석",
            "{k1} 기반 {k2} 정리",
            "{k1} {k2} {k3} 비교",
            "{k1} 처리 시 {k2}",
        ],
    },
}

# 검색 주제와 무관한 문서. qrels 정답에 절대 포함되지 않는 negative sample이다.
IRRELEVANT_TOPICS = [
    {
        "topic": "cooking",
        "keywords": ["요리", "레시피", "된장찌개", "오븐", "채소"],
        "phrases": [
            "요리는 재료와 조리법의 조합으로 맛을 만든다.",
            "된장찌개에는 두부와 애호박을 자주 넣는다.",
            "오븐 조리는 풍미를 높이는 데 효과적이다.",
        ],
        "title_templates": ["{k1} 기본 레시피", "{k1}와 {k2} 조리법", "{k1} 맛있게 만드는 법"],
    },
    {
        "topic": "fitness",
        "keywords": ["운동", "근력", "유산소", "회복", "스트레칭"],
        "phrases": [
            "운동은 꾸준함이 중요하며 회복도 훈련의 일부다.",
            "근력 운동과 유산소 운동은 목적이 다를 수 있다.",
            "스트레칭은 몸의 긴장을 줄이는 데 도움을 준다.",
        ],
        "title_templates": ["{k1} 기본 가이드", "{k1}와 {k2} 차이", "{k1} 회복 방법"],
    },
    {
        "topic": "travel",
        "keywords": ["여행", "호텔", "항공권", "관광", "일정"],
        "phrases": [
            "여행 일정은 이동 시간과 숙소 위치를 함께 고려해야 한다.",
            "항공권 가격은 시즌과 예약 시점에 따라 달라진다.",
            "관광지는 이동 동선을 기준으로 묶는 것이 편하다.",
        ],
        "title_templates": ["{k1} 준비 방법", "{k1}와 {k2} 계획", "{k1} 일정 정리"],
    },
]

# variant 문서에서 원래 단어 대신 쓰는 유사 표현
SYNONYM_MAP = {
    "검색": ["조회", "탐색", "retrieval"],
    "문서": ["텍스트", "자료", "콘텐츠"],
    "랭킹": ["순위", "정렬", "스코어링"],
    "형태소": ["토큰", "형태 단위"],
    "임베딩": ["벡터 표현", "dense vector"],
    "리트리버": ["retriever", "검색기"],
    "토큰화": ["tokenization", "분절"],
    "응답": ["답변", "response"],
    "분석기": ["파서", "분석 도구"],
}

# 긴 문서 길이를 늘리기 위한 일반 단어
NOISE_WORDS = [
    "테스트", "예시", "기본", "설명", "동작", "성능", "결과", "비교",
    "설계", "구현", "구조", "방식", "활용", "분석", "데이터",
]

CONCEPT_INDEX = {
    concept["id"]: (topic_name, concept)
    for topic_name, info in TOPICS.items()
    for concept in info["concepts"]
}


def choose_topic():
    return random.choice(list(TOPICS))


def choose_concept(topic_name):
    return random.choice(TOPICS[topic_name]["concepts"])


def sample_keywords(topic_name, k_min=2, k_max=5):
    keywords = TOPICS[topic_name]["keywords"]
    k = random.randint(k_min, min(k_max, len(keywords)))
    return random.sample(keywords, k)


def build_title(topic_name, kws):
    # 제목은 BM25F에서 별도 필드로 쓰이므로 키워드가 드러나게 만든다.
    template = random.choice(TOPICS[topic_name]["title_templates"])
    padded = kws[:]
    while len(padded) < 3:
        padded.append(random.choice(TOPICS[topic_name]["keywords"]))
    return template.format(k1=padded[0], k2=padded[1], k3=padded[2])


def build_tags(kws, n_min=2, n_max=4):
    n = random.randint(n_min, min(n_max, len(kws)))
    return random.sample(kws, n)


def make_doc(doc_id, topic_name, doc_type, title, tags, text, concepts):
    # concepts[0]은 문서의 주 concept, 나머지는 부 concept이다.
    return {
        "id": f"doc_{doc_id}",
        "topic": topic_name,
        "doc_type": doc_type,
        "concepts": concepts,
        "title": title,
        "tags": tags,
        "text": text,
    }


def make_short_doc(doc_id, topic_name):
    # 짧은 문서: 같은 키워드라도 짧은 문서에서 점수가 더 높게 나오는지 확인
    concept = choose_concept(topic_name)
    kws = sample_keywords(topic_name, 2, 4)
    text = f"{concept['phrase']} 핵심 키워드는 {' '.join(kws)} 이다."
    return make_doc(doc_id, topic_name, "short", build_title(topic_name, kws),
                    build_tags(kws), text, [concept["id"]])


def make_long_doc(doc_id, topic_name):
    # 긴 문서: 주 concept 하나 + 부 concept 2개 + 반복/노이즈 문장으로 길이 정규화 실험
    concepts = random.sample(TOPICS[topic_name]["concepts"], k=3)
    kws = sample_keywords(topic_name, 4, 7)
    repeated = random.choice(kws)
    extras = random.sample(NOISE_WORDS, 5)

    parts = [c["phrase"] for c in concepts]
    parts.append(f"이 문서는 {topic_name} 주제를 길게 설명하기 위한 예시이다.")
    parts.append(f"주요 키워드는 {' '.join(kws)} 이며, 실험을 위해 일부 단어를 반복한다.")
    parts.append(f"{repeated} {repeated} {repeated} 관련 설명이 추가될 수 있다.")
    parts.append(f"추가 단어 {' '.join(extras)} 를 포함하여 문서 길이를 늘린다.")

    return make_doc(doc_id, topic_name, "long", build_title(topic_name, kws),
                    build_tags(kws, 2, 5), " ".join(parts), [c["id"] for c in concepts])


def make_keyword_repeated_doc(doc_id, topic_name):
    # 키워드 반복 문서: term frequency가 커질 때 점수 포화(saturation) 확인
    concept = choose_concept(topic_name)
    kws = sample_keywords(topic_name, 2, 3)
    target = random.choice(kws)
    repeated_block = " ".join([target] * random.randint(6, 12))
    text = f"{concept['phrase']} {repeated_block} 이 문서는 특정 키워드 반복이 많은 테스트용 문서이다."
    tags = list(dict.fromkeys([target] + kws[:2]))
    return make_doc(doc_id, topic_name, "keyword_repeated", build_title(topic_name, [target] + kws),
                    tags, text, [concept["id"]])


def make_variant_doc(doc_id, topic_name):
    # 유사 표현 문서: query와 정확히 같은 단어가 아닌 동의어가 섞이는 상황
    concept = choose_concept(topic_name)
    kws = sample_keywords(topic_name, 2, 4)
    variants = [random.choice(SYNONYM_MAP[kw]) if kw in SYNONYM_MAP else kw for kw in kws]
    text = f"{concept['phrase']} 유사 표현으로는 {' '.join(variants)} 같은 말이 사용될 수 있다."
    return make_doc(doc_id, topic_name, "variant", build_title(topic_name, kws),
                    build_tags(kws), text, [concept["id"]])


def make_mixed_doc(doc_id):
    # 혼합 문서: 주제는 맞지만 다른 주제의 키워드가 섞인 노이즈 문서
    topic_name = choose_topic()
    other_topic = random.choice([t for t in TOPICS if t != topic_name])
    concept = choose_concept(topic_name)
    kws_main = sample_keywords(topic_name, 2, 4)
    kws_other = sample_keywords(other_topic, 1, 2)
    text = (
        f"{concept['phrase']} "
        f"주요 키워드는 {' '.join(kws_main)} 이다. "
        f"비교를 위해 {' '.join(kws_other)} 관련 표현도 일부 포함한다."
    )
    return make_doc(doc_id, topic_name, "mixed", build_title(topic_name, kws_main),
                    build_tags(kws_main), text, [concept["id"]])


def make_irrelevant_doc(doc_id):
    # 무관 문서: 검색 주제와 상관없는 negative sample
    chosen = random.choice(IRRELEVANT_TOPICS)
    kws = random.sample(chosen["keywords"], k=random.randint(2, 4))
    padded = kws + [kws[0]]
    title = random.choice(chosen["title_templates"]).format(k1=padded[0], k2=padded[1])
    tags = random.sample(chosen["keywords"], k=3)
    text = " ".join(random.sample(chosen["phrases"], k=2)) + f" 관련 단어: {' '.join(kws)}"
    return make_doc(doc_id, "irrelevant", "irrelevant", title, tags, text, [])


def generate_document(doc_id):
    # 문서 타입 비율: short 25%, long 20%, keyword_repeated 15%, variant 15%, mixed 15%, irrelevant 10%
    r = random.random()
    if r < 0.25:
        return make_short_doc(doc_id, choose_topic())
    if r < 0.45:
        return make_long_doc(doc_id, choose_topic())
    if r < 0.60:
        return make_keyword_repeated_doc(doc_id, choose_topic())
    if r < 0.75:
        return make_variant_doc(doc_id, choose_topic())
    if r < 0.90:
        return make_mixed_doc(doc_id)
    return make_irrelevant_doc(doc_id)


def generate_queries():
    # concept마다 keyword / paraphrase query 한 쌍을 만든다.
    # pair_id가 같은 두 query는 정답 문서가 같으므로 sparse와 dense를 1:1로 비교할 수 있다.
    queries = []
    qid = 1
    for topic_name, info in TOPICS.items():
        for concept in info["concepts"]:
            for intent in ("keyword", "paraphrase"):
                queries.append({
                    "query_id": f"q_{qid}",
                    "topic": topic_name,
                    "concept_id": concept["id"],
                    "pair_id": concept["id"],
                    "intent": intent,
                    "query": concept[intent],
                })
                qid += 1
    return queries


def generate_qrels(docs, queries):
    """concept 일치 기준 relevance 라벨.

    2 = 문서의 주 concept(concepts[0])이 query concept과 같음
    1 = 문서의 부 concept(concepts[1:])에 query concept이 포함됨 (long 문서)
    """
    qrels = []
    for q in queries:
        for doc in docs:
            if not doc["concepts"]:
                continue
            if doc["concepts"][0] == q["concept_id"]:
                relevance = 2
            elif q["concept_id"] in doc["concepts"][1:]:
                relevance = 1
            else:
                continue
            qrels.append({"query_id": q["query_id"], "doc_id": doc["id"], "relevance": relevance})
    return qrels


def tokenize(text):
    return set(TOKEN_PATTERN.findall(text.lower()))


def lexical_overlap_report(queries):
    # query와 해당 concept phrase 사이의 토큰 겹침 수.
    # keyword는 겹침이 있어야 하고 paraphrase는 0이어야 의도대로 만들어진 것이다.
    report = {"keyword": [], "paraphrase": []}
    for q in queries:
        _, concept = CONCEPT_INDEX[q["concept_id"]]
        overlap = tokenize(q["query"]) & tokenize(concept["phrase"])
        report[q["intent"]].append(len(overlap))
    return {
        intent: {
            "avg_overlap_tokens": round(sum(v) / len(v), 2),
            "zero_overlap_queries": sum(1 for x in v if x == 0),
            "n_queries": len(v),
        }
        for intent, v in report.items()
    }


def summarize(docs, queries, qrels, seed):
    per_query = Counter(item["query_id"] for item in qrels)
    rel_dist = Counter(str(item["relevance"]) for item in qrels)
    counts = [per_query.get(q["query_id"], 0) for q in queries]
    return {
        "n_docs": len(docs),
        "n_queries": len(queries),
        "seed": seed,
        "topics": dict(Counter(d["topic"] for d in docs)),
        "doc_types": dict(Counter(d["doc_type"] for d in docs)),
        "intents": dict(Counter(q["intent"] for q in queries)),
        "n_concepts": len(CONCEPT_INDEX),
        "fields": ["title", "tags", "text"],
        "qrels": {
            "n_qrels": len(qrels),
            "avg_qrels_per_query": round(sum(counts) / len(counts), 2),
            "min_qrels_per_query": min(counts),
            "max_qrels_per_query": max(counts),
            "relevance_distribution": dict(rel_dist),
        },
        "lexical_overlap": lexical_overlap_report(queries),
        "note": (
            "Qrels are labeled by concept match, not token overlap. "
            "relevance=2: primary concept, relevance=1: secondary concept in long docs."
        ),
    }


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Generate shared corpus / queries / qrels for 02-search-ir")
    parser.add_argument("--n_docs", type=int, default=500, help="number of documents")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument("--output_dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="output directory")
    args = parser.parse_args()

    random.seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # seed가 같으면 항상 같은 corpus / queries / qrels가 만들어진다.
    docs = [generate_document(i) for i in range(1, args.n_docs + 1)]
    queries = generate_queries()
    qrels = generate_qrels(docs, queries)

    write_jsonl(args.output_dir / "corpus.jsonl", docs)
    write_json(args.output_dir / "queries.json", {"queries": queries})
    write_json(args.output_dir / "qrels.json", {"qrels": qrels})
    summary = summarize(docs, queries, qrels, args.seed)
    write_json(args.output_dir / "summary.json", summary)

    print(f"생성 완료: {args.output_dir}")
    print(f"- docs: {summary['n_docs']}, queries: {summary['n_queries']}, qrels: {summary['qrels']['n_qrels']}")
    print(f"- lexical overlap: {summary['lexical_overlap']}")


if __name__ == "__main__":
    main()
