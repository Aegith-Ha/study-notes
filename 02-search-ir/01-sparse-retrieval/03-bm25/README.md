# BM25, BM25+, BM25L, BM25F

synthetic corpus를 대상으로 BM25 계열 검색 모델을 학습하고 실행하는 예제다.

- `bm25.py`: BM25, BM25+, BM25L, BM25F 구현 및 CLI 검색 실행
- 데이터: 02-search-ir 공통 데이터인 [`00-data/generated`](../../00-data/README.md)를 사용한다.

네 모델은 모두 **query에 포함된 단어가 문서에 얼마나 잘 등장하는지**를 기준으로 관련도 점수를 계산한다. 문서 길이, 단어 반복, 필드 가중치를 처리하는 방식에 차이가 있다.

## 1. BM25

BM25는 정보 검색에서 널리 쓰이는 sparse retrieval 랭킹 함수다.

- query 단어가 문서에 있으면 점수가 올라간다.
- 흔한 단어보다 드문 단어에 더 높은 점수를 준다.
- 단어가 반복될수록 점수가 올라가지만 증가 폭은 점차 줄어든다.
- 긴 문서가 우연히 유리해지지 않도록 문서 길이를 정규화한다.

### TF

`TF(term frequency)`는 특정 단어가 문서에 등장한 횟수다. BM25에서는 TF가 커져도 점수가 무한정 증가하지 않고 어느 정도부터 증가 폭이 줄어든다. 이를 **TF saturation**이라고 한다.

### IDF

`IDF(inverse document frequency)`는 전체 문서에서 해당 단어가 얼마나 드문지를 나타낸다.

- 많은 문서에 등장하는 단어: 낮은 IDF
- 적은 문서에만 등장하는 단어: 높은 IDF

`문서`, `검색`처럼 흔한 단어보다 `BM25F`, `nDCG`처럼 드문 단어가 검색 의도를 더 구체적으로 나타낼 가능성이 있으므로 더 큰 점수를 받는다.

### 문서 길이 정규화

긴 문서는 단어가 많이 포함될 가능성이 높다. 단순 등장 횟수만 사용하면 긴 문서가 과하게 유리할 수 있으므로, BM25는 현재 문서 길이와 평균 문서 길이를 비교해 점수를 보정한다.

### 코드와 파라미터

`bm25.py`의 `bm25()` 함수가 기본 BM25를 계산한다.

```python
def bm25(
    query_tokens: list[str],
    index: FlatIndex,
    *,
    k1: float = 1.2,
    b: float = 0.75,
) -> dict[str, float]:
```

- `k1`: 단어 반복 횟수의 포화 정도를 조절한다.
- `b`: 문서 길이 정규화 강도를 조절한다. `0`이면 문서 길이를 거의 보지 않고, `1`에 가까울수록 강하게 반영한다.

## 2. BM25+

BM25+는 긴 문서가 기본 BM25의 길이 정규화 때문에 지나치게 낮은 점수를 받는 문제를 완화한 변형이다. TF component에 일정한 보정값을 더한다.

```python
tf_component + delta
```

`bm25.py`의 `bm25_plus()` 함수가 BM25+를 계산한다.

```python
def bm25_plus(
    query_tokens: list[str],
    index: FlatIndex,
    *,
    k1: float = 1.2,
    b: float = 0.75,
    delta: float = 1.0,
) -> dict[str, float]:
```

`delta`는 query 단어가 등장한 긴 문서가 과하게 불리해지는 현상을 줄이는 보정값이다.

BM25+는 다음 상황에 적합하다.

- 문서 간 길이 차이가 큰 corpus
- 긴 문서에 query 단어가 의미 있게 포함된 경우
- 기본 BM25가 긴 문서에 너무 강한 패널티를 주는 경우

## 3. BM25L

BM25L도 길이 정규화 문제를 완화하지만, BM25+와 보정 위치가 다르다. 먼저 문서 길이를 반영해 TF를 정규화한 뒤, 정규화된 TF에 `delta`를 더한다.

```python
normalized_tf = tf / length_norm
normalized_tf + delta
```

`bm25.py`의 `bm25l()` 함수가 BM25L을 계산한다.

```python
def bm25l(
    query_tokens: list[str],
    index: FlatIndex,
    *,
    k1: float = 1.2,
    b: float = 0.75,
    delta: float = 0.5,
) -> dict[str, float]:
```

BM25+의 기본 `delta`는 `1.0`, BM25L은 `0.5`다. 이는 절대적인 정답이 아니므로 실험을 통해 조정할 수 있다.

BM25L은 다음 상황에 적합하다.

- 긴 문서와 짧은 문서가 섞인 corpus
- 길이 정규화는 유지하면서 기본 BM25보다 완만하게 보정하려는 경우
- BM25+와 다른 방식으로 긴 문서 패널티를 조정하려는 경우

## 4. BM25F

BM25F는 문서를 하나의 본문으로 합치지 않고 여러 필드로 나누어 점수를 계산한다. 이 예제의 문서는 `title`, `tags`, `text` 필드로 구성된다.

같은 query 단어라도 제목에 등장한 경우가 본문에 한 번 등장한 경우보다 중요할 수 있다. BM25F는 이를 반영하기 위해 필드별 가중치와 길이 정규화 값을 사용한다.

`bm25.py`의 `bm25f()` 함수가 BM25F를 계산한다.

```python
def bm25f(
    query_tokens: list[str],
    index: FieldIndex,
    *,
    k1: float = 1.2,
    field_weights: dict[str, float] | None = None,
    field_b: dict[str, float] | None = None,
) -> dict[str, float]:
```

기본 필드 가중치는 다음과 같다.

```python
weights = {
    "title": 2.0,
    "tags": 2.0,
    "text": 0.5,
}
```

이 설정은 `title`과 `tags`에 등장한 query 단어를 `text`보다 중요하게 평가한다.

필드별 길이 정규화 값은 다음과 같다.

```python
b_values = {
    "title": 0.5,
    "tags": 0.0,
    "text": 0.75,
}
```

- `title`: 길이 정규화를 어느 정도 적용한다.
- `tags`: 길이 정규화를 거의 적용하지 않는다.
- `text`: 본문 길이 정규화를 강하게 적용한다.

BM25F는 다음 상황에 적합하다.

- 문서가 `title`, `body`, `tags`, `category`처럼 구조화된 경우
- 제목이나 태그의 단어를 더 중요하게 평가하려는 경우
- 검색 도메인에 맞춰 필드별 랭킹을 조정하려는 경우

## 모델 비교

| 모델 | 핵심 특징 | 적합한 상황 |
| --- | --- | --- |
| BM25 | 기본 sparse retrieval 랭킹 함수 | 일반적인 키워드 검색 |
| BM25+ | TF component에 `delta` 보정 추가 | 긴 문서가 과하게 불리한 경우 |
| BM25L | 정규화된 TF에 `delta` 보정 추가 | 길이 보정을 더 부드럽게 적용하려는 경우 |
| BM25F | 필드별 가중치와 길이 정규화 적용 | `title`, `tags`, `text`처럼 필드가 나뉜 문서 |

## 검색 처리 흐름

1. 문서와 query를 로드한다.
2. query와 문서를 토큰화한다.
3. 문서로 역색인을 만든다.
4. 선택한 BM25 모델로 문서별 점수를 계산한다.
5. 점수가 높은 문서를 상위 결과로 출력한다.

## 모델별 결과

`00-data`의 query 60개 전체에 대해 각 모델의 nDCG@10을 계산한 값이다. 파라미터는 코드의 기본값을 사용했다.

| 모델 | keyword | paraphrase |
| --- | --- | --- |
| BM25 | 0.683 | 0.000 |
| BM25+ | **0.701** | 0.000 |
| BM25L | 0.693 | 0.000 |
| BM25F | 0.565 | 0.001 |

- **paraphrase는 모든 모델이 0에 가깝다.** BM25 계열은 단어가 겹쳐야 점수가 생기므로, 같은 뜻을 다른 단어로 물으면 정답을 찾지 못한다. sparse retrieval의 근본 한계이고, [Dense Retrieval](../../02-dense-retrieval/)이 필요한 이유다.
- **BM25F가 가장 낮다.** 이 데이터에서 정답을 결정하는 concept 문장은 `text`에만 있고, `title`과 `tags`는 주제 키워드를 무작위로 조합한 것이다. 그런데 BM25F의 기본 가중치는 `title`과 `tags`에 2.0, `text`에 0.5를 준다. 정답과 무관한 필드에 가중치를 몰아준 셈이다. 필드 가중치는 데이터에서 어느 필드가 정답을 담고 있는지에 맞춰야 한다.
- **BM25+와 BM25L이 BM25보다 약간 높다.** long 문서(concept 3개 + 노이즈 문장)는 길이 정규화 때문에 불리한데, delta 보정이 이 패널티를 줄여 준다.

## 정리

- 기본 키워드 검색에는 `BM25`를 사용한다.
- 긴 문서 패널티를 완화하려면 `BM25+` 또는 `BM25L`을 고려한다.
- 제목, 태그, 본문을 다르게 평가하려면 `BM25F`를 사용한다. 단, 필드 가중치는 정답 정보가 실제로 어느 필드에 있는지에 맞춰야 한다.
- 어떤 BM25 변형을 써도 표현이 다른 query(paraphrase)는 해결되지 않는다.

## 실행 방법

모든 명령은 repository 루트(`/home/test0000/study-notes`)에서 실행한다.

### 기본 실행

```bash
python 02-search-ir/01-sparse-retrieval/03-bm25/bm25.py
```

기본 실행은 generated 데이터의 첫 번째 query(`q_1`, keyword)와 `bm25` 모델을 사용한다.

출력 예시:

```
Loaded 500 docs
Model: bm25
Query: bm25 랭킹 정보 검색
Query id: q_1 (intent=keyword, concept=search_bm25)
Tokens: ['bm25', '랭킹', '정보', '검색']

[bm25]
 1. doc_259    score= 10.6826 rel=0 type=short            concepts=[search_tokenizer]
 2. doc_471    score= 10.5304 rel=1 type=long             concepts=[search_relevance, search_bm25, search_tokenizer]
 3. doc_186    score=  9.7115 rel=2 type=variant          concepts=[search_bm25]
```

- `rel`: qrels의 relevance (2: 주 concept 일치, 1: 부 concept 일치, 0: 정답 아님)
- `concepts`: 문서가 다루는 concept. query의 `concept`과 비교하면 왜 정답/오답인지 바로 보인다.

### 모델 선택

```bash
python 02-search-ir/01-sparse-retrieval/03-bm25/bm25.py --model bm25f
```

`--model`에는 `bm25`, `bm25+`, `bm25l`, `bm25f`를 지정할 수 있다.

### 직접 query 검색

```bash
python 02-search-ir/01-sparse-retrieval/03-bm25/bm25.py \
  --query "bm25 검색 랭킹" \
  --model bm25f \
  --top-k 10
```

### generated query ID로 검색

```bash
python 02-search-ir/01-sparse-retrieval/03-bm25/bm25.py \
  --query-id q_2 \
  --model bm25 \
  --top-k 5
```

`q_1`(keyword)과 `q_2`(paraphrase)는 같은 concept(`search_bm25`)의 query 쌍이다. 홀수 id가 keyword, 짝수 id가 paraphrase다. 두 query를 번갈아 실행하면, 정답은 같은데 표현만 바뀌었을 때 BM25 결과가 어떻게 무너지는지 볼 수 있다.

### 데이터 파일 직접 지정

```bash
python 02-search-ir/01-sparse-retrieval/03-bm25/bm25.py \
  --docs 02-search-ir/00-data/generated/corpus.jsonl \
  --queries 02-search-ir/00-data/generated/queries.json \
  --qrels 02-search-ir/00-data/generated/qrels.json
```

기본값이 위 경로이므로 다른 데이터를 쓸 때만 지정한다.
