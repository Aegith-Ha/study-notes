# Inverted Index

역색인(inverted index)은 **단어에서 해당 단어가 등장한 문서를 찾는 자료구조**다. 문서 전체를 매번 순회하지 않고 query에 포함된 단어의 posting만 조회할 수 있어 sparse retrieval의 기반이 된다.

## 구조

문서를 그대로 저장하는 forward index는 문서에서 단어를 찾는 방향이다.

```text
doc-1 -> ["검색", "시스템"]
doc-2 -> ["검색", "평가"]
```

역색인은 이 관계를 반대로 저장한다.

```text
"검색"   -> {"doc-1": [0], "doc-2": [0]}
"시스템" -> {"doc-1": [1]}
"평가"   -> {"doc-2": [1]}
```

- term dictionary: 색인에 포함된 전체 단어
- posting list: 특정 단어가 등장한 문서 목록
- term frequency: 한 문서에서 단어가 등장한 횟수
- document frequency: 단어가 등장한 문서 수
- position: 문서 안에서 단어가 등장한 위치

`inverted_index.py`는 position까지 저장하는 positional inverted index를 만든다.

## 검색 과정

query가 `검색 평가`라면 두 단어의 posting을 가져온다.

```text
검색 -> {doc-1, doc-2}
평가 -> {doc-2}
```

- AND 검색: posting의 교집합인 `doc-2`
- OR 검색: posting의 합집합인 `doc-1`, `doc-2`

이 단계는 일치하는 문서를 찾는 **retrieval**이다. TF-IDF나 BM25는 찾아낸 문서 사이의 순서를 결정하는 **ranking**을 추가한다.

## 실행 방법

repository 루트에서 실행한다.

```bash
python 02-search-ir/sparse-retrieval/inverted-index/inverted_index.py
```

query와 연산자를 직접 지정할 수 있다.

```bash
python 02-search-ir/sparse-retrieval/inverted-index/inverted_index.py \
  --query "검색 평가" \
  --operator and
```

```bash
python 02-search-ir/sparse-retrieval/inverted-index/inverted_index.py \
  --query "검색 평가" \
  --operator or
```

## TF-IDF, BM25와의 관계

```text
문서
  -> tokenize
  -> inverted index
  -> query term의 posting 조회
  -> TF-IDF 또는 BM25 점수 계산
  -> 상위 문서 반환
```

역색인은 검색 대상을 빠르게 좁히는 구조이고, TF-IDF와 BM25는 posting에 저장된 통계를 이용해 관련도 점수를 계산한다.

