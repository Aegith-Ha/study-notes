# BM25 더미 데이터 생성

이 폴더는 BM25 검색 실험용 synthetic corpus, query, qrels를 생성하는 스크립트를 담고 있다.

## 주요 파일

- `generate_dummy_corpus.py`: 더미 문서, query, qrels 생성 스크립트
- `generated/`: 생성된 데이터가 저장되는 기본 위치

## 기본 생성

repo 루트(`/home/test0000/study-notes`)에서 실행한다.

```bash
python3 02-search-ir/bm25/data/generate_dummy_corpus.py
```

기본값:

- 문서 수: `10000`
- query 수: `200`
- seed: `42`
- 출력 폴더: `02-search-ir/bm25/data/generated`

## 문서와 query 개수 지정

```bash
python3 02-search-ir/bm25/data/generate_dummy_corpus.py \
  --n_docs 10000 \
  --n_queries 200 \
  --seed 42
```

## 출력 경로 지정

```bash
python3 02-search-ir/bm25/data/generate_dummy_corpus.py \
  --n_docs 1000 \
  --n_queries 100 \
  --output_dir /tmp/bm25-generated
```

## 생성되는 파일

- `corpus.jsonl`: 검색 대상 문서
- `queries.json`: 평가 또는 검색에 사용할 query 목록
- `qrels.json`: query별 정답 문서와 relevance 라벨
- `summary.json`: 생성 결과 요약

## qrels relevance 의미

- `2`: highly relevant
- `1`: relevant

qrels는 사람이 라벨링한 정답이 아니라, topic 일치와 title/tags/text 토큰 겹침을 기준으로 자동 생성한 휴리스틱 라벨이다.
