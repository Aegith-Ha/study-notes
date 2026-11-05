# Error Analysis

검색 모델이 정답을 찾지 못하거나 관련 없는 문서를 상위에 배치한 사례를 분석한다.

## 왜 metric만으로는 부족한가?

nDCG가 `0.55`에서 `0.69`로 올랐다면 전체 랭킹이 나아졌다는 것은 알 수 있다. 하지만 tokenizer가 개선된 것인지, title 가중치가 효과를 낸 것인지, 특정 query만 좋아진 것인지는 평균 점수만으로 알 수 없다.

Error analysis는 query별 검색 결과를 직접 보고 실패의 반복 패턴을 찾는 과정이다. 발견한 패턴을 토대로 개선 가설을 만들고, 코드를 수정한 뒤 benchmark를 다시 실행해 가설을 검증한다.

## False positive와 false negative

query의 `top-k` 검색 문서 집합을 $R_k$, qrels에서 relevance가 `0`보다 큰 정답 집합을 $G$라고 하면 다음과 같다.

$$
False\ Positive = R_k - G
$$

$$
False\ Negative = G - R_k
$$

- **False positive(오검색)**: 상위에 노출됐지만 qrels에서 정답이 아닌 문서다. Precision을 낮춘다.
- **False negative(미검색)**: qrels에서 정답이지만 `top-k`에 들지 못한 문서다. Recall을 낮춘다.

예를 들어 정답이 `{A, B, C}`이고 top-3 결과가 `{A, D, E}`라면 false positive은 `{D, E}`, false negative는 `{B, C}`다.

## 분석 항목

- query와 예상 정답
- 실제 검색 결과와 순위
- 오검색(false positive) 및 미검색(false negative) 구분
- 원인 분류: tokenizer, query 불명확성, 용어 불일치, 인덱스, 스코어링 등
- 개선 가설과 재평가 결과

개별 사례에는 사용한 query ID, document ID, 모델 버전을 함께 기록해 재현 가능하게 관리한다.

## 예제 소스

- [`analyze_bm25_errors.py`](./analyze_bm25_errors.py): query별 상위 검색 결과에서 false positive와 false negative를 찾아 JSON으로 정리한다.

### 분석 원리

`analyze_bm25_errors.py`는 선택한 BM25 모델로 query를 검색한 뒤 다음 정보를 저장한다.

- `query_id`, `query`, `intent`, `concept_id`: 어떤 검색어에서 실패했는지 식별한다.
- `false_positive_doc_ids`: 검색됐지만 qrels상 정답이 아닌 문서다.
- `false_negative_doc_ids`: 정답이지만 상위 `k`개에서 누락된 문서다.
- `results`: 순위, document ID, BM25 score, relevance, `doc_type`, `concepts`를 함께 보여 준다. `00-data`의 title은 무작위 키워드 조합이라 정답 판단에 도움이 되지 않으므로, 문서가 실제로 다루는 `concepts`를 출력한다.

score는 모델 내부의 상대적인 순위 값이다. BM25 score `10`이 relevance `2`라는 뜻은 아니다. 모델이 만든 score와 사람이 정한 relevance를 비교하면 모델의 판단이 어디서 엇나갔는지 파악할 수 있다.

## 원인을 분류하는 예

| 유형 | 확인할 내용 | 개선 가설 |
| --- | --- | --- |
| Tokenization | 한국어 조사나 복합어가 잘못 분리됐는가? | 형태소 분석기, synonym 적용 |
| Vocabulary mismatch | query와 문서가 같은 뜻을 다른 단어로 표현했는가? | query expansion, dense retrieval |
| Field weighting | title과 body의 중요도가 잘못 설정됐는가? | BM25F 필드 가중치 조정 |
| Document length | 긴 문서가 과도한 보정을 받거나 패널티를 받는가? | `b`, `k1`, BM25+/BM25L 비교 |
| Ambiguous query | query가 짧거나 의도가 여러 가지인가? | query 분류, clarification |
| Qrels issue | 실제 관련 문서가 미판정인가? | qrels 재검수 및 추가 라벨링 |

## BM25 분석 결과

### 사례: q_1 `bm25 랭킹 정보 검색` (concept: `search_bm25`, top-5)

| rank | doc | relevance | doc_type | concepts |
| ---: | --- | ---: | --- | --- |
| 1 | doc_259 | 0 | short | search_tokenizer |
| 2 | doc_471 | 1 | long | search_relevance, **search_bm25**, search_tokenizer |
| 3 | doc_186 | 2 | variant | **search_bm25** |
| 4 | doc_344 | 0 | variant | search_tokenizer |
| 5 | doc_494 | 0 | short | search_tokenizer |

1위 doc_259는 BM25 문서가 아니라 토크나이저 문서다. `검색`, `랭킹`은 `search` 주제 키워드라서 같은 주제 문서의 `핵심 키워드는 ...` 문장에 무작위로 들어간다. 그래서 query 단어가 겹치지만 다루는 내용(concept)은 다르다.

### 오검색 유형 집계 (BM25, top-10, query 60개)

전체 query의 top-10에서 정답이 아닌 문서(relevance 0)를 query 유형과 문서 주제 기준으로 세었다. 아래 표는 그중 일부다. 이 집계는 스크립트 출력(JSON)을 따로 가공한 것이다.

| query 유형 | 오검색 문서 | 건수 | 원인 |
| --- | --- | ---: | --- |
| keyword | 같은 주제, 다른 concept (short) | 24 | 주제 키워드 공유 |
| keyword | 같은 주제, 다른 concept (variant) | 16 | 주제 키워드 공유 |
| keyword | 같은 주제, 다른 concept (keyword_repeated) | 15 | 반복 키워드로 TF가 높음 |
| paraphrase | 다른 주제 (short) | 43 | `기반`, `방법` 같은 일반 단어만 겹침 |
| paraphrase | 다른 주제 (variant) | 32 | 위와 같음 |
| paraphrase | 무관 문서 (irrelevant) | 17 | 위와 같음 |

- **keyword:** 오검색이 모두 같은 주제 안에서 일어난다. 주제는 맞히지만 세부 concept을 구분하지 못한다. 앞 표의 *Ambiguous query* / *Field weighting* 유형에 가깝다.
- **paraphrase:** 오검색이 거의 다른 주제이거나 요리, 여행 같은 무관 문서다. 의미가 아니라 우연히 겹친 일반 단어로 순위가 정해진다. 앞 표의 *Vocabulary mismatch*에 해당하고, BM25 파라미터를 조정해서는 해결되지 않는다.

Error analysis의 목표는 개별 오류를 모두 없애는 것이 아니라, 반복되는 원인을 찾아 가장 효과가 큰 개선 실험으로 연결하는 것이다.

## 실행 방법

BM25의 상위 10개 결과를 분석하고 최대 10개 query 사례를 저장한다.

```bash
python 02-search-ir/05-evaluation/04-error-analysis/analyze_bm25_errors.py \
  --model bm25 \
  --top-k 10 \
  --max-cases 10 \
  --output 02-search-ir/05-evaluation/04-error-analysis/generated/bm25-errors.json
```

선택 가능한 모델은 `bm25`, `bm25+`, `bm25l`, `bm25f`다. `--output`을 생략하면 JSON을 표준 출력으로 보여 준다.

`--intent keyword` 또는 `--intent paraphrase`로 한 유형의 query만 분석할 수 있다. 두 유형은 실패 원인이 다르므로 나눠서 보는 것이 좋다.

```bash
python 02-search-ir/05-evaluation/04-error-analysis/analyze_bm25_errors.py \
  --model bm25 \
  --top-k 5 \
  --max-cases 1 \
  --intent keyword
```

이 예제는 qrels에 관련도가 없거나 `0`인 상위 문서를 false positive로 간주한다. 일부 문서만 판정한 qrels를 사용하면 미판정 문서도 false positive에 포함될 수 있다.
