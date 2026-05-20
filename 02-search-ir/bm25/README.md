# BM25 검색 실행

이 폴더는 synthetic corpus를 대상으로 BM25 계열 검색 모델을 실행하는 예제 코드가 있다.

## 주요 파일

- `bm25.py`: BM25, BM25+, BM25L, BM25F 구현과 CLI 검색 실행 스크립트
- `data/`: 검색에 사용할 더미 문서, query, qrels 생성 스크립트와 생성 결과 저장 위치

## 기본 실행

repo 루트(`/home/test0000/study-notes`)에서 실행한다.

```bash
python3 02-search-ir/bm25/bm25.py
```

기본 실행은 generated 데이터의 첫 번째 query를 사용하고, 기본 모델은 `bm25`다.

## 모델 선택

```bash
python3 02-search-ir/bm25/bm25.py --model bm25f
```

사용 가능한 모델:

- `bm25`
- `bm25+`
- `bm25l`
- `bm25f`

## 직접 query 검색

```bash
python3 02-search-ir/bm25/bm25.py \
  --query "bm25 검색 랭킹" \
  --model bm25f \
  --top-k 10
```

## generated query id로 검색

```bash
python3 02-search-ir/bm25/bm25.py \
  --query-id q_90 \
  --model bm25 \
  --top-k 5
```

## 데이터 파일 직접 지정

```bash
python3 02-search-ir/bm25/bm25.py \
  --docs 02-search-ir/bm25/data/generated/corpus.jsonl \
  --queries 02-search-ir/bm25/data/generated/queries.json \
  --qrels 02-search-ir/bm25/data/generated/qrels.json
```

`corpus.jsonl`, `queries.json`, `qrels.json`이 없으면 기존 `bm25f_*` generated 파일을 fallback으로 사용한다.
