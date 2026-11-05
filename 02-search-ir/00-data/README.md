# 00. Data

02-search-ir의 sparse, dense, hybrid, reranking, evaluation 실험이 **공통으로 사용하는** corpus, queries, qrels.

모든 실험이 같은 데이터와 같은 정답지를 쓰므로, 모델 간 점수를 그대로 비교할 수 있다.

## 주요 파일

| 파일 | 내용 |
| --- | --- |
| `generate_corpus.py` | 데이터 생성 스크립트 (seed 고정) |
| `generated/corpus.jsonl` | 검색 대상 문서 500개 |
| `generated/queries.json` | query 60개 (concept 30개 × keyword/paraphrase) |
| `generated/qrels.json` | query별 정답 문서와 relevance |
| `generated/summary.json` | 분포 요약, query와 문서 간 토큰 겹침 통계 |

`generated/`는 git에 커밋해 **파일로 고정**한다. 생성 규칙을 바꾸면 이후 모든 실험 결과가 달라지므로, 재생성할 때는 그 영향을 함께 기록한다.

## 설계: concept 기반 라벨링

### 왜 concept인가

이전 버전(`100-tmp/sparse-retrieval/03-bm25/data`)은 query와 문서 사이의 **토큰 겹침 점수**로 qrels를 만들었다. 이 방식은 두 가지 문제가 있다.

- paraphrase query는 문서와 겹치는 단어가 없으므로 정답이 만들어지지 않는다.
- 정답 자체가 "단어가 겹치는 문서"라서 sparse 검색에 유리하게 편향된다.

그래서 각 문서에 **concept**(의미 단위)를 붙이고, query의 concept과 일치하는지로 정답을 매긴다.

### 구성

- 주제 6개 × concept 5개 = **concept 30개**
- concept 하나는 문서 문장(`phrase`) 1개, keyword query 1개, paraphrase query 1개로 이루어진다.

| concept | 문서 문장 (phrase) | keyword query | paraphrase query |
| --- | --- | --- | --- |
| `search_inverted_index` | 역색인은 검색 시스템의 핵심 자료구조 중 하나이다. | 역색인 검색 시스템 자료구조 | 단어마다 등장한 글 목록을 저장해 두는 방법 |
| `db_join` | 조인 연산은 여러 테이블의 데이터를 결합하는 방법이다. | 조인 연산 테이블 결합 | 두 표의 행을 공통 열로 이어 붙이기 |

- keyword query는 phrase에 나오는 단어를 그대로 쓰고, paraphrase query는 같은 뜻을 phrase와 겹치지 않는 단어로 쓴다.
- 이 조건은 `summary.json`의 `lexical_overlap`으로 확인할 수 있다. keyword는 평균 2.1개 토큰이 겹치고, paraphrase는 30개 모두 0개다.
- 같은 concept의 두 query는 `pair_id`가 같고 정답 문서도 같다. 그래서 **같은 정답에 대해 표현만 다를 때** sparse와 dense가 어떻게 달라지는지 1:1로 비교할 수 있다.

### qrels relevance

| relevance | 기준 |
| --- | --- |
| 2 | 문서의 주 concept(`concepts[0]`)이 query concept과 같음 |
| 1 | 문서의 부 concept(`concepts[1:]`)에 query concept이 포함됨 (long 문서만 해당) |

- query당 정답 수: 평균 22.1개 (최소 15, 최대 30)
- irrelevant 문서는 concept이 없으므로 어떤 query의 정답도 되지 않는다.
- 정답이 많기 때문에 Recall@10은 구조적으로 1이 될 수 없다. 순위 품질은 nDCG@10과 P@10으로 보고, Recall은 k를 키워서(@50, @100) 본다.

## 데이터 형식

### corpus.jsonl

```json
{"id": "doc_1", "topic": "search", "doc_type": "variant", "concepts": ["search_bm25"], "title": "...", "tags": ["..."], "text": "..."}
```

| 필드 | 설명 |
| --- | --- |
| `title`, `tags`, `text` | 검색 대상 필드 (BM25F에서 필드별 가중치를 줄 수 있음) |
| `topic` | search, llm, python, database, linux, korean_nlp, irrelevant |
| `doc_type` | 아래 표 참고 |
| `concepts` | 정답 판단용 메타데이터. **검색 입력으로 쓰면 안 된다** |

| doc_type | 비율 | 실험 목적 |
| --- | --- | --- |
| short | 25% | 짧은 문서에서 점수가 높게 나오는지 |
| long | 20% | concept 3개 + 노이즈 문장, 길이 정규화(b) 확인 |
| keyword_repeated | 15% | 같은 단어 6~12회 반복, TF 포화(k1) 확인 |
| variant | 15% | 동의어로 치환한 표현 (조회, retrieval 등) |
| mixed | 15% | 다른 주제 키워드가 섞인 노이즈 |
| irrelevant | 10% | 요리, 운동, 여행 같은 무관 문서 (negative) |

### queries.json

```json
{"queries": [{"query_id": "q_1", "topic": "search", "concept_id": "search_bm25", "pair_id": "search_bm25", "intent": "keyword", "query": "bm25 랭킹 정보 검색"}]}
```

`intent`는 `keyword` 또는 `paraphrase`다. slice analysis에서 이 필드를 기준으로 유형별 성능을 나눠 본다.

### qrels.json

```json
{"qrels": [{"query_id": "q_1", "doc_id": "doc_1", "relevance": 2}]}
```

## 확인 결과 (BM25 baseline)

`rank-bm25`의 BM25Okapi를 기본 파라미터로 쓰고, 정규식 토큰화로 title, tags, text를 하나로 합쳐 검색한 결과다.

| intent | P@10 (relevance=2 기준) |
| --- | --- |
| keyword | 0.597 |
| paraphrase | 0.020 |

paraphrase query는 문서와 겹치는 단어가 거의 없어 BM25로는 정답을 찾지 못한다. 이 차이를 dense retrieval이 얼마나 줄이는지가 [02. Dense Retrieval](../02-dense-retrieval/)의 비교 포인트다.

## 한계

- 사람이 만든 라벨이 아니라 규칙으로 생성한 synthetic 데이터다.
- 문장 템플릿이 적어서(concept당 phrase 1개) 같은 문장이 여러 문서에 반복된다.
- paraphrase query가 concept 문장과 겹치는 토큰은 0개지만, 코퍼스 전체와 비교하면 `방법`, `형태`, `만드는` 같은 일반 단어는 일부 겹친다.
- 공백 기반 토큰화에서는 `함수이다`와 `함수`처럼 조사나 어미가 붙은 형태가 다른 토큰이 된다. 한국어 형태소 분석의 필요성은 sparse 단계에서 따로 다룬다.

## 실행 방법

repo 루트에서 실행한다. 출력 경로 기본값은 스크립트 위치 기준 `generated/`이다.

```bash
conda activate study-py312
python 02-search-ir/00-data/generate_corpus.py
```

```bash
python 02-search-ir/00-data/generate_corpus.py --n_docs 500 --seed 42 --output_dir /tmp/search-data
```

출력 예시:

```
생성 완료: .../02-search-ir/00-data/generated
- docs: 500, queries: 60, qrels: 1326
- lexical overlap: {'keyword': {'avg_overlap_tokens': 2.1, 'zero_overlap_queries': 0, ...}, 'paraphrase': {'avg_overlap_tokens': 0.0, 'zero_overlap_queries': 30, ...}}
```
