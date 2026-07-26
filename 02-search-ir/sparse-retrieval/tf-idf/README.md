# TF-IDF

TF-IDF는 문서 안에서 자주 등장하면서 전체 corpus에서는 드문 단어에 높은 가중치를 주는 sparse retrieval 모델이다.

```text
TF-IDF(term, document) = TF(term, document) × IDF(term)
```

`tf_idf.py`는 문서와 query를 TF-IDF vector로 변환하고 cosine similarity로 문서 순위를 계산한다.

## TF: Term Frequency

TF는 특정 단어가 한 문서에 등장한 횟수다. 이 예제는 단어의 반복 효과를 완화하기 위해 sublinear TF를 사용한다.

```text
TF = 1 + log(term count)
```

같은 단어가 반복되면 중요도는 올라가지만 등장 횟수에 정비례해서 계속 커지지는 않는다.

## IDF: Inverse Document Frequency

IDF는 단어가 전체 corpus에서 얼마나 드문지를 나타낸다.

```text
IDF = log((N + 1) / (DF + 1)) + 1
```

- `N`: 전체 문서 수
- `DF`: 해당 단어가 등장한 문서 수
- `+1`: 처음 보는 단어나 0으로 나누는 경우를 처리하는 smoothing

여러 문서에 흔하게 등장하는 단어는 낮은 값을 받고, 소수 문서에만 등장하는 단어는 높은 값을 받는다.

## Vector와 cosine similarity

문서와 query를 vocabulary 크기의 sparse vector로 표현한다.

```text
document = {"검색": 0.42, "평가": 0.81}
query    = {"검색": 0.63, "평가": 0.78}
```

각 vector를 L2 정규화하면 두 vector의 내적이 cosine similarity가 된다.

```text
cosine_similarity(query, document) = query · document
```

점수는 `0`에 가까울수록 겹치는 중요 단어가 적고, `1`에 가까울수록 방향이 유사하다.

## 검색 처리 흐름

1. 문서를 tokenize한다.
2. document frequency와 IDF를 계산한다.
3. 문서를 TF-IDF vector로 변환하고 정규화한다.
4. query를 동일한 IDF 기준으로 vector화한다.
5. query와 각 문서의 cosine similarity를 계산한다.
6. 점수가 높은 문서부터 반환한다.

## 실행 방법

repository 루트에서 실행한다.

```bash
python 02-search-ir/sparse-retrieval/tf-idf/tf_idf.py
```

query와 결과 개수를 지정할 수 있다.

```bash
python 02-search-ir/sparse-retrieval/tf-idf/tf_idf.py \
  --query "검색 평가 지표" \
  --top-k 3
```

## BM25와의 차이

| 구분 | TF-IDF | BM25 |
| --- | --- | --- |
| TF 처리 | raw 또는 log-scaled TF | `k1`에 따른 TF saturation |
| 문서 길이 | 주로 vector 정규화 | 평균 문서 길이를 기준으로 명시적 보정 |
| 주요 파라미터 | TF·IDF 공식, normalization | `k1`, `b` |
| 용도 | vector space model과 검색 기초 학습 | 일반적인 키워드 검색의 강한 baseline |

TF-IDF를 먼저 이해하면 BM25의 TF saturation과 문서 길이 정규화가 왜 필요한지 비교하기 쉽다.

