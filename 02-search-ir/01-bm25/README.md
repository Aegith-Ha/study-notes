# BM25, BM25+, BM25L, BM25F

synthetic corpus를 대상으로 BM25 계열 검색 모델을 학습하고 실행하는 예제다.

- `bm25.py`: BM25, BM25+, BM25L, BM25F 구현 및 CLI 검색 실행
- `data/`: 더미 문서, query, qrels 생성 스크립트와 생성 결과 저장 위치

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

## 실행 방법

모든 명령은 repository 루트(`/home/test0000/study-notes`)에서 실행한다.

### 기본 실행

```bash
python3 02-search-ir/01-bm25/bm25.py
```

기본 실행은 generated 데이터의 첫 번째 query와 `bm25` 모델을 사용한다.

### 모델 선택

```bash
python3 02-search-ir/01-bm25/bm25.py --model bm25f
```

`--model`에는 `bm25`, `bm25+`, `bm25l`, `bm25f`를 지정할 수 있다.

### 직접 query 검색

```bash
python3 02-search-ir/01-bm25/bm25.py \
  --query "bm25 검색 랭킹" \
  --model bm25f \
  --top-k 10
```

### generated query ID로 검색

```bash
python3 02-search-ir/01-bm25/bm25.py \
  --query-id q_90 \
  --model bm25 \
  --top-k 5
```

### 데이터 파일 직접 지정

```bash
python3 02-search-ir/01-bm25/bm25.py \
  --docs 02-search-ir/01-bm25/data/generated/corpus.jsonl \
  --queries 02-search-ir/01-bm25/data/generated/queries.json \
  --qrels 02-search-ir/01-bm25/data/generated/qrels.json
```

`corpus.jsonl`, `queries.json`, `qrels.json`이 없으면 기존 `bm25f_*` generated 파일을 fallback으로 사용한다.

## 정리

- 기본 키워드 검색에는 `BM25`를 사용한다.
- 긴 문서 패널티를 완화하려면 `BM25+` 또는 `BM25L`을 고려한다.
- 제목, 태그, 본문을 다르게 평가하려면 `BM25F`를 사용한다.

이 예제 데이터에는 `title`, `tags`, `text` 필드가 있으며, qrels도 title/tags 겹침을 중요하게 보도록 생성되어 있다. 따라서 현재 실험에서는 BM25F가 다른 모델보다 좋은 점수를 내기 쉽다.
