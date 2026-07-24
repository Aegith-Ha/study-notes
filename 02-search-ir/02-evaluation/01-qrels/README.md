# Qrels

Qrels(query relevance judgments)는 query별로 문서의 정답 여부나 관련도를 표현한 평가 기준 데이터다.

## 왜 필요한가?

검색 모델은 문서별 score를 만들 수는 있지만, 그 score가 정답을 의미하는지 스스로 판단할 수는 없다. Qrels는 모델의 예측과 비교할 **정답지** 역할을 한다.

하나의 qrels 항목은 `(query_id, doc_id, relevance)` 쌍으로 생각할 수 있다. 예를 들어 query `q_1`과 document `doc_10`이 매우 관련 있다면 relevance를 `3`으로 지정할 수 있다.

```json
{
  "qrels": [
    {"query_id": "q_1", "doc_id": "doc_10", "relevance": 3},
    {"query_id": "q_1", "doc_id": "doc_25", "relevance": 1}
  ]
}
```

## 이진 관련도와 다단계 관련도

- **이진 관련도**: `0`은 오답, `1`은 정답으로 분류한다. Precision과 Recall처럼 정답 개수를 세는 지표에 적합하다.
- **다단계 관련도**: `0`~`3`처럼 관련성의 강도를 구분한다. nDCG처럼 더 중요한 정답이 상위에 있는지 평가하는 지표에 유용하다.

라벨 기준은 중간에 바꾸면 기존 실험과 공정하게 비교할 수 없다. `3=질문에 직접 답함`, `2=핵심 정보를 포함`, `1=부분적으로 관련`, `0=관련 없음`처럼 명확한 기준을 먼저 정하는 것이 좋다.

## 관리 대상

- query ID와 document ID의 매핑
- 이진 관련도(`0`, `1`) 또는 다단계 관련도(`0`~`3` 등)
- 라벨링 기준, 작성 일자, 데이터 버전

BM25 예제에서 생성된 qrels는 [`01-bm25/data/generated/qrels.json`](../../01-bm25/data/generated/qrels.json)에 있다. 이 폴더에는 평가에 고정해 사용할 qrels와 라벨링 기준을 정리한다.

## 예제 소스

- [`validate_qrels.py`](./validate_qrels.py): qrels의 query/document 참조, relevance 값, 중복 라벨을 검증한다.

### 검증 원리

`validate_qrels.py`는 query ID 집합과 document ID 집합을 먼저 만든 뒤 각 qrels 항목을 한 번씩 순회한다.

1. `query_id`가 `queries.json`에 있는지 확인한다.
2. `doc_id`가 `corpus.jsonl`에 있는지 확인한다.
3. relevance가 `0` 이상의 정수인지 확인한다.
4. 같은 `(query_id, doc_id)` 쌍이 두 번 들어가지 않았는지 확인한다.

이 검증은 파일이 구조적으로 올바른지를 확인할 뿐, relevance 판단이 의미적으로 올바른지까지 판단하지는 않는다. 라벨의 품질은 사람의 검수와 일관된 라벨링 기준이 보장해야 한다.

## 사용법

기본값은 BM25 예제의 `corpus.jsonl`, `queries.json`, `qrels.json`이다.

```bash
python 02-search-ir/02-evaluation/01-qrels/validate_qrels.py
```

다른 데이터를 검증할 때는 세 파일을 함께 지정한다.

```bash
python 02-search-ir/02-evaluation/01-qrels/validate_qrels.py \
  --docs path/to/corpus.jsonl \
  --queries path/to/queries.json \
  --qrels path/to/qrels.json
```

모든 검증을 통과하면 `Qrels are valid.`를 출력한다. 잘못된 참조나 중복이 있으면 오류 목록을 출력하고 종료 코드 `1`을 반환한다.

## 학습 포인트

- qrels는 검색 모델이 만든 데이터가 아니라 모델을 평가하기 위한 외부 정답이다.
- 모든 query-document 쌍을 판정하기는 비싸므로 실무 qrels에는 미판정 문서가 많을 수 있다.
- 미판정은 반드시 오답이 아니다. 미판정 문서를 `0`으로 취급하면 점수가 낮아질 수 있다.
- 라벨 분포가 query별로 너무 다르면 평균 지표만으로 성능을 해석하기 어려울 수 있다.
