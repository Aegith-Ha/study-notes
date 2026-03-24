import json
import random
import argparse
from pathlib import Path


TOPICS = {
    "search": {
        "keywords": [
            "bm25", "tf-idf", "랭킹", "문서", "검색", "질의", "색인", "역색인",
            "토크나이저", "형태소", "스코어", "검색엔진"
        ],
        "phrases": [
            "BM25는 정보 검색에서 자주 사용하는 랭킹 함수이다.",
            "검색 엔진은 질의와 문서의 관련도를 계산해 결과를 정렬한다.",
            "문서 길이 정규화는 BM25 점수 계산에서 중요한 요소다.",
            "역색인은 검색 시스템의 핵심 자료구조 중 하나이다.",
            "토크나이저와 형태소 분석기는 검색 품질에 직접적인 영향을 준다."
        ],
        "query_templates": [
            "bm25 검색 랭킹",
            "문서 검색 점수 계산",
            "형태소 분석기 검색 품질",
            "역색인 기반 검색 엔진",
            "bm25 문서 길이 정규화"
        ],
        "title_templates": [
            "{k1} 기본 개념",
            "{k1}와 {k2} 비교",
            "{k1} 기반 {k2} 정리",
            "{k1}와 {k2}를 이용한 {k3}",
            "{k1} {k2} {k3} 개요"
        ],
    },
    "llm": {
        "keywords": [
            "rag", "llm", "프롬프트", "임베딩", "리트리버", "리랭커",
            "생성", "컨텍스트", "청크", "벡터", "파인튜닝", "응답"
        ],
        "phrases": [
            "RAG는 검색과 생성 모델을 결합하는 구조이다.",
            "LLM은 입력된 컨텍스트를 바탕으로 응답을 생성한다.",
            "임베딩 기반 검색은 관련 문서를 빠르게 찾는 데 사용된다.",
            "청크 분할 방식은 RAG 품질에 큰 영향을 준다.",
            "리트리버와 리랭커는 검색 증강 시스템의 핵심 구성요소다."
        ],
        "query_templates": [
            "rag 문서 검색 생성",
            "llm 컨텍스트 기반 응답",
            "임베딩 검색 리트리버",
            "청크 분할 rag 품질",
            "리랭커 포함 rag 구조"
        ],
        "title_templates": [
            "{k1} 기본 구조",
            "{k1}와 {k2} 개요",
            "{k1} 기반 {k2} 설계",
            "{k1}를 이용한 {k2} 생성",
            "{k1} {k2} {k3} 정리"
        ],
    },
    "python": {
        "keywords": [
            "파이썬", "리스트", "딕셔너리", "셋", "튜플", "반복문",
            "함수", "클래스", "예외", "제너레이터", "타입힌트", "모듈"
        ],
        "phrases": [
            "파이썬의 리스트는 순서가 있는 가변 자료형이다.",
            "딕셔너리는 키와 값으로 데이터를 저장한다.",
            "제너레이터는 큰 데이터를 효율적으로 순회하는 데 유용하다.",
            "타입힌트는 코드 가독성과 정적 분석에 도움을 준다.",
            "예외 처리는 프로그램의 안정성을 높이는 중요한 요소다."
        ],
        "query_templates": [
            "파이썬 리스트 딕셔너리 차이",
            "제너레이터 사용 이유",
            "파이썬 타입힌트 예제",
            "예외 처리 기본",
            "파이썬 함수와 클래스"
        ],
        "title_templates": [
            "{k1} 기본 정리",
            "{k1}와 {k2} 차이",
            "{k1} 사용 예제",
            "{k1} 기반 {k2} 설명",
            "{k1} {k2} {k3} 정리"
        ],
    },
    "database": {
        "keywords": [
            "데이터베이스", "sql", "인덱스", "조인", "트랜잭션", "정규화",
            "테이블", "쿼리", "락", "commit", "rollback", "실행계획"
        ],
        "phrases": [
            "SQL은 관계형 데이터베이스를 다루는 표준 언어다.",
            "인덱스는 조회 성능을 높이지만 쓰기 비용을 증가시킬 수 있다.",
            "트랜잭션은 데이터 일관성을 보장하기 위한 단위이다.",
            "조인 연산은 여러 테이블의 데이터를 결합하는 방법이다.",
            "실행계획 분석은 쿼리 성능 최적화에 매우 중요하다."
        ],
        "query_templates": [
            "sql 인덱스 성능",
            "트랜잭션 commit rollback",
            "테이블 조인 실행계획",
            "데이터베이스 정규화",
            "쿼리 최적화 인덱스"
        ],
        "title_templates": [
            "{k1} 기본 원리",
            "{k1}와 {k2} 정리",
            "{k1} 기반 {k2} 최적화",
            "{k1} {k2} {k3} 개요",
            "{k1} 사용 시 {k2}"
        ],
    },
    "linux": {
        "keywords": [
            "리눅스", "프로세스", "쉘", "파일", "권한", "서비스",
            "네트워크", "포트", "로그", "systemd", "grep", "awk"
        ],
        "phrases": [
            "리눅스는 서버 환경에서 널리 사용되는 운영체제다.",
            "프로세스 확인에는 ps와 top 같은 명령어를 자주 사용한다.",
            "파일 권한은 읽기 쓰기 실행 비트로 구성된다.",
            "로그 분석은 장애 원인을 찾는 데 매우 중요하다.",
            "systemd는 서비스 관리와 부팅 제어를 담당한다."
        ],
        "query_templates": [
            "리눅스 프로세스 확인",
            "파일 권한 변경",
            "systemd 서비스 로그",
            "grep awk 로그 분석",
            "리눅스 포트 확인"
        ],
        "title_templates": [
            "{k1} 기본 사용법",
            "{k1}와 {k2} 명령어",
            "{k1} 기반 {k2} 확인",
            "{k1} {k2} {k3} 정리",
            "{k1} 로그 분석 방법"
        ],
    },
    "korean_nlp": {
        "keywords": [
            "한국어", "형태소", "분석기", "복합명사", "조사", "어절",
            "토큰화", "띄어쓰기", "불용어", "품사", "사전", "정규화"
        ],
        "phrases": [
            "한국어 검색에서는 형태소 분석기의 선택이 매우 중요하다.",
            "조사 처리 방식은 검색 정확도에 영향을 줄 수 있다.",
            "복합명사 분해 여부에 따라 토큰화 결과가 달라진다.",
            "띄어쓰기 오류는 한국어 정보 검색에서 흔한 문제다.",
            "품사 기반 필터링은 불필요한 토큰을 줄이는 데 도움이 된다."
        ],
        "query_templates": [
            "한국어 형태소 분석기",
            "복합명사 분해 검색",
            "조사 처리 토큰화",
            "띄어쓰기 오류 검색",
            "품사 기반 불용어 제거"
        ],
        "title_templates": [
            "{k1} 검색 처리",
            "{k1}와 {k2} 분석",
            "{k1} 기반 {k2} 정리",
            "{k1} {k2} {k3} 비교",
            "{k1} 처리 시 {k2}"
        ],
    },
}

IRRELEVANT_TOPICS = [
    {
        "topic": "cooking",
        "keywords": ["요리", "레시피", "된장찌개", "오븐", "채소"],
        "phrases": [
            "요리는 재료와 조리법의 조합으로 맛을 만든다.",
            "된장찌개에는 두부와 애호박을 자주 넣는다.",
            "오븐 조리는 풍미를 높이는 데 효과적이다."
        ],
        "title_templates": [
            "{k1} 기본 레시피",
            "{k1}와 {k2} 조리법",
            "{k1} 맛있게 만드는 법"
        ],
    },
    {
        "topic": "fitness",
        "keywords": ["운동", "근력", "유산소", "회복", "스트레칭"],
        "phrases": [
            "운동은 꾸준함이 중요하며 회복도 훈련의 일부다.",
            "근력 운동과 유산소 운동은 목적이 다를 수 있다.",
            "스트레칭은 몸의 긴장을 줄이는 데 도움을 준다."
        ],
        "title_templates": [
            "{k1} 기본 가이드",
            "{k1}와 {k2} 차이",
            "{k1} 회복 방법"
        ],
    },
    {
        "topic": "travel",
        "keywords": ["여행", "호텔", "항공권", "관광", "일정"],
        "phrases": [
            "여행 일정은 이동 시간과 숙소 위치를 함께 고려해야 한다.",
            "항공권 가격은 시즌과 예약 시점에 따라 달라진다.",
            "관광지는 이동 동선을 기준으로 묶는 것이 편하다."
        ],
        "title_templates": [
            "{k1} 준비 방법",
            "{k1}와 {k2} 계획",
            "{k1} 일정 정리"
        ],
    },
]


def choose_topic():
    return random.choice(list(TOPICS.keys()))


def sample_keywords(topic_name, k_min=2, k_max=5):
    keywords = TOPICS[topic_name]["keywords"]
    k = random.randint(k_min, min(k_max, len(keywords)))
    return random.sample(keywords, k)


def random_noise_words(n=5):
    pool = [
        "테스트", "예시", "기본", "설명", "동작", "성능", "결과", "비교",
        "설계", "구현", "구조", "방식", "활용", "분석", "데이터"
    ]
    return random.sample(pool, min(n, len(pool)))


def build_title(topic_name, kws):
    templates = TOPICS[topic_name]["title_templates"]
    template = random.choice(templates)

    padded = kws[:]
    while len(padded) < 3:
        padded.append(random.choice(TOPICS[topic_name]["keywords"]))

    return template.format(k1=padded[0], k2=padded[1], k3=padded[2])


def build_irrelevant_title(topic_data, kws):
    template = random.choice(topic_data["title_templates"])
    padded = kws[:]
    while len(padded) < 2:
        padded.append(random.choice(topic_data["keywords"]))
    return template.format(k1=padded[0], k2=padded[1], k3=padded[0])


def build_tags(topic_name, kws, n_min=2, n_max=4):
    n = random.randint(n_min, min(n_max, len(kws)))
    return random.sample(kws, n)


def make_short_doc(doc_id, topic_name):
    kws = sample_keywords(topic_name, 2, 4)
    phrase = random.choice(TOPICS[topic_name]["phrases"])
    title = build_title(topic_name, kws)
    tags = build_tags(topic_name, kws)
    text = f"{phrase} 핵심 키워드는 {' '.join(kws)} 이다."

    return {
        "id": f"doc_{doc_id}",
        "topic": topic_name,
        "doc_type": "short",
        "title": title,
        "tags": tags,
        "text": text,
    }


def make_long_doc(doc_id, topic_name):
    phrases = random.sample(
        TOPICS[topic_name]["phrases"],
        k=min(4, len(TOPICS[topic_name]["phrases"]))
    )
    kws = sample_keywords(topic_name, 4, 7)
    extras = random_noise_words(5)
    repeated = random.choice(kws)
    title = build_title(topic_name, kws)
    tags = build_tags(topic_name, kws, 2, 5)

    parts = []
    parts.extend(phrases)
    parts.append(f"이 문서는 {topic_name} 주제를 길게 설명하기 위한 예시이다.")
    parts.append(f"주요 키워드는 {' '.join(kws)} 이며, 실험을 위해 일부 단어를 반복한다.")
    parts.append(f"{repeated} {repeated} {repeated} 관련 설명이 추가될 수 있다.")
    parts.append(f"추가 단어 {' '.join(extras)} 를 포함하여 문서 길이를 늘린다.")

    return {
        "id": f"doc_{doc_id}",
        "topic": topic_name,
        "doc_type": "long",
        "title": title,
        "tags": tags,
        "text": " ".join(parts),
    }


def make_keyword_repeated_doc(doc_id, topic_name):
    kws = sample_keywords(topic_name, 2, 3)
    target = random.choice(kws)
    phrase = random.choice(TOPICS[topic_name]["phrases"])
    title = build_title(topic_name, [target] + kws)
    tags = list(dict.fromkeys([target] + kws[:2]))
    repeated_block = " ".join([target] * random.randint(6, 12))
    text = f"{phrase} {repeated_block} 이 문서는 특정 키워드 반복이 많은 테스트용 문서이다."

    return {
        "id": f"doc_{doc_id}",
        "topic": topic_name,
        "doc_type": "keyword_repeated",
        "title": title,
        "tags": tags,
        "text": text,
    }


def make_variant_doc(doc_id, topic_name):
    kws = sample_keywords(topic_name, 2, 4)
    phrase = random.choice(TOPICS[topic_name]["phrases"])
    title = build_title(topic_name, kws)
    tags = build_tags(topic_name, kws)

    synonym_map = {
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

    variants = []
    for kw in kws:
        if kw in synonym_map:
            variants.append(random.choice(synonym_map[kw]))
        else:
            variants.append(kw)

    text = f"{phrase} 유사 표현으로는 {' '.join(variants)} 같은 말이 사용될 수 있다."

    return {
        "id": f"doc_{doc_id}",
        "topic": topic_name,
        "doc_type": "variant",
        "title": title,
        "tags": tags,
        "text": text,
    }


def make_irrelevant_doc(doc_id):
    chosen = random.choice(IRRELEVANT_TOPICS)
    kws = random.sample(chosen["keywords"], k=random.randint(2, min(4, len(chosen["keywords"]))))
    title = build_irrelevant_title(chosen, kws)
    tags = random.sample(chosen["keywords"], k=min(3, len(chosen["keywords"])))
    text = " ".join(random.sample(chosen["phrases"], k=min(2, len(chosen["phrases"]))))
    text += f" 관련 단어: {' '.join(kws)}"

    return {
        "id": f"doc_{doc_id}",
        "topic": "irrelevant",
        "doc_type": "irrelevant",
        "title": title,
        "tags": tags,
        "text": text,
    }


def make_mixed_doc(doc_id):
    topic_name = choose_topic()
    kws_main = sample_keywords(topic_name, 2, 4)

    other_topic = choose_topic()
    while other_topic == topic_name:
        other_topic = choose_topic()

    kws_other = sample_keywords(other_topic, 1, 2)
    title = build_title(topic_name, kws_main)
    tags = build_tags(topic_name, kws_main)

    text = (
        f"{random.choice(TOPICS[topic_name]['phrases'])} "
        f"주요 키워드는 {' '.join(kws_main)} 이다. "
        f"비교를 위해 {' '.join(kws_other)} 관련 표현도 일부 포함한다."
    )

    return {
        "id": f"doc_{doc_id}",
        "topic": topic_name,
        "doc_type": "mixed",
        "title": title,
        "tags": tags,
        "text": text,
    }


def generate_document(doc_id):
    r = random.random()

    if r < 0.25:
        return make_short_doc(doc_id, choose_topic())
    elif r < 0.45:
        return make_long_doc(doc_id, choose_topic())
    elif r < 0.60:
        return make_keyword_repeated_doc(doc_id, choose_topic())
    elif r < 0.75:
        return make_variant_doc(doc_id, choose_topic())
    elif r < 0.90:
        return make_mixed_doc(doc_id)
    else:
        return make_irrelevant_doc(doc_id)


def generate_queries(n_queries=200):
    queries = []
    qid = 1

    for topic_name, info in TOPICS.items():
        for template in info["query_templates"]:
            queries.append({
                "query_id": f"q_{qid}",
                "topic": topic_name,
                "query": template,
                "intent": "topic_lookup",
            })
            qid += 1

        for _ in range(max(5, n_queries // len(TOPICS) // 2)):
            kws = random.sample(info["keywords"], k=random.randint(2, 4))
            queries.append({
                "query_id": f"q_{qid}",
                "topic": topic_name,
                "query": " ".join(kws),
                "intent": "keyword_match",
            })
            qid += 1

    random.shuffle(queries)
    return queries[:n_queries]


def simple_tokenize(text):
    return set(text.lower().split())


def compute_overlap_score(query, doc):
    q_tokens = simple_tokenize(query)

    title_tokens = simple_tokenize(doc["title"])
    tag_tokens = set(t.lower() for t in doc["tags"])
    text_tokens = simple_tokenize(doc["text"])

    score = 0.0
    score += len(q_tokens & title_tokens) * 3.0
    score += len(q_tokens & tag_tokens) * 4.0
    score += len(q_tokens & text_tokens) * 1.5

    if doc["doc_type"] == "short":
        score += 0.5
    elif doc["doc_type"] == "long":
        score += 0.3
    elif doc["doc_type"] == "keyword_repeated":
        score += 0.4
    elif doc["doc_type"] == "variant":
        score += 0.2
    elif doc["doc_type"] == "mixed":
        score -= 0.2
    elif doc["doc_type"] == "irrelevant":
        score -= 10.0

    return score


def generate_qrels(docs, queries, max_high=3, max_rel=5):
    """
    relevance:
      2 = highly relevant
      1 = relevant
    """
    qrels = []

    for q in queries:
        query_id = q["query_id"]
        query_text = q["query"]
        query_topic = q["topic"]

        candidates = []
        for doc in docs:
            if doc["topic"] != query_topic:
                continue
            if doc["doc_type"] == "irrelevant":
                continue

            score = compute_overlap_score(query_text, doc)
            if score > 0:
                candidates.append((doc["id"], score))

        candidates.sort(key=lambda x: x[1], reverse=True)

        high_docs = candidates[:max_high]
        rel_docs = candidates[max_high:max_high + max_rel]

        for doc_id, _ in high_docs:
            qrels.append({
                "query_id": query_id,
                "doc_id": doc_id,
                "relevance": 2
            })

        for doc_id, _ in rel_docs:
            qrels.append({
                "query_id": query_id,
                "doc_id": doc_id,
                "relevance": 1
            })

    return qrels


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def summarize_docs(docs):
    topic_counts = {}
    doc_type_counts = {}

    for doc in docs:
        topic_counts[doc["topic"]] = topic_counts.get(doc["topic"], 0) + 1
        doc_type_counts[doc["doc_type"]] = doc_type_counts.get(doc["doc_type"], 0) + 1

    return topic_counts, doc_type_counts


def summarize_qrels(qrels):
    per_query = {}
    rel_dist = {}

    for item in qrels:
        qid = item["query_id"]
        rel = item["relevance"]

        per_query[qid] = per_query.get(qid, 0) + 1
        rel_dist[str(rel)] = rel_dist.get(str(rel), 0) + 1

    if per_query:
        avg_qrels = sum(per_query.values()) / len(per_query)
    else:
        avg_qrels = 0.0

    return {
        "n_qrels": len(qrels),
        "avg_qrels_per_query": round(avg_qrels, 2),
        "relevance_distribution": rel_dist,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic BM25/BM25+/BM25L/BM25F test corpus with qrels"
    )
    parser.add_argument("--n_docs", type=int, default=10000, help="number of documents")
    parser.add_argument("--n_queries", type=int, default=200, help="number of queries")
    parser.add_argument("--output_dir", type=str, default="02-search-ir/bm25/data/generated", help="output directory")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument("--max_high", type=int, default=3, help="max relevance=2 docs per query")
    parser.add_argument("--max_rel", type=int, default=5, help="max relevance=1 docs per query")
    args = parser.parse_args()

    random.seed(args.seed)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    docs = [generate_document(i) for i in range(1, args.n_docs + 1)]
    queries = generate_queries(args.n_queries)
    qrels = generate_qrels(docs, queries, max_high=args.max_high, max_rel=args.max_rel)

    docs_path = output_dir / "bm25f_corpus.jsonl"
    queries_path = output_dir / "bm25f_queries.json"
    qrels_path = output_dir / "bm25f_qrels.json"
    summary_path = output_dir / "summary.json"

    write_jsonl(docs_path, docs)
    write_json(queries_path, {"queries": queries})
    write_json(qrels_path, {"qrels": qrels})

    topic_counts, doc_type_counts = summarize_docs(docs)
    qrels_summary = summarize_qrels(qrels)

    summary = {
        "n_docs": len(docs),
        "n_queries": len(queries),
        "seed": args.seed,
        "topics": topic_counts,
        "doc_types": doc_type_counts,
        "fields": ["title", "tags", "text"],
        "qrels": qrels_summary,
        "docs_path": str(docs_path),
        "queries_path": str(queries_path),
        "qrels_path": str(qrels_path),
        "note": (
            "Qrels are automatically generated heuristic relevance labels based on "
            "topic matching and token overlap across title, tags, and text fields."
        ),
    }

    write_json(summary_path, summary)

    print("생성 완료")
    print(f"- docs: {docs_path}")
    print(f"- queries: {queries_path}")
    print(f"- qrels: {qrels_path}")
    print(f"- summary: {summary_path}")


if __name__ == "__main__":
    main()