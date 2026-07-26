# Sparse Retrieval

문서와 query에 등장하는 단어를 기반으로 관련 문서를 찾는 전통적인 정보 검색 방법을 학습한다.

Sparse retrieval은 문서에 존재하는 전체 단어 중 일부에만 가중치를 부여해 문서를 표현한다. 검색할 때는 query와 문서가 공유하는 단어와 각 단어의 중요도를 이용해 관련성 점수를 계산한다.

## 학습 순서

1. [Inverted Index](./01-inverted-index/README.md)
   - 단어가 어떤 문서와 위치에 등장하는지 저장하는 자료 구조
   - term dictionary, posting list, positional index
   - AND/OR 조건을 이용한 기본 검색
2. [TF-IDF](./02-tf-idf/README.md)
   - 문서 안에서 자주 등장하지만 전체 문서에서는 드문 단어에 높은 가중치를 부여하는 방법
   - TF, IDF, TF-IDF vector
   - cosine similarity를 이용한 문서 순위 계산
3. [BM25](./03-bm25/README.md)
   - TF-IDF를 발전시켜 단어 빈도 포화와 문서 길이를 보정하는 검색 모델
   - BM25, BM25+, BM25L, BM25F 비교
   - [실험 데이터](./03-bm25/data/README.md) 생성과 검색 모델 평가 준비

## 각 단계의 관계

| 단계 | 핵심 역할 | 다음 단계에서 추가되는 내용 |
| --- | --- | --- |
| Inverted Index | query 단어가 포함된 문서를 빠르게 찾는다. | 단어와 문서의 중요도를 점수로 표현한다. |
| TF-IDF | 단어 빈도와 희소성을 이용해 문서 관련도를 계산한다. | 단어 빈도 포화와 문서 길이 차이를 보정한다. |
| BM25 | TF-IDF의 한계를 보정해 검색 순위를 계산한다. | 검색 결과를 qrels 및 평가 지표와 비교한다. |

Inverted index는 검색 대상 문서를 찾는 자료 구조이고, TF-IDF와 BM25는 찾은 문서의 관련성 점수를 계산하는 방법이다. BM25 검색 결과는 [`evaluation`](../evaluation/README.md)의 qrels, metrics, benchmark를 이용해 평가할 수 있다.

## 예제 실행

저장소 루트에서 `study-py312` 환경을 활성화한 뒤 학습 순서대로 실행한다.

```bash
conda activate study-py312

python 02-search-ir/sparse-retrieval/01-inverted-index/inverted_index.py
python 02-search-ir/sparse-retrieval/02-tf-idf/tf_idf.py
python 02-search-ir/sparse-retrieval/03-bm25/bm25.py
```

각 예제의 입력 형식과 추가 옵션은 해당 폴더의 README에서 확인한다.
