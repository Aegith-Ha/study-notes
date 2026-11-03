# Study Notes

개인 학습 및 실습 기록 저장소입니다.

## Structure
- [`01-python/`](./01-python/) : Python 기초 및 실습
- [`02-search-ir/`](./02-search-ir/) : 검색(IR), BM25, analyzer, retrieval, evaluation
- [`03-rag/`](./03-rag/) : RAG 구조, chunking, retriever, evaluation
- [`04-llmops/`](./04-llmops/) : LLM 기초 개념, LLMOps
- [`98-etc/`](./98-etc/) : 단순 설명 모음
- [`99-projects/`](./99-projects/) : 프로젝트 실습
- [`100-tmp/`](./100-tmp/) : 임시 실습 파일

## Document Index

### Python

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| argparse | [README](./01-python/argparse/README.md) | - | [example.py](./01-python/argparse/example.py) |
| pydantic | [README](./01-python/pydantic/README.md) | - | [example.py](./01-python/pydantic/example.py) |

### Search / IR

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| Search / IR 개요 | [README](./02-search-ir/README.md) | - | - |
| Sparse Retrieval 개요 | [README](./02-search-ir/sparse-retrieval/README.md) | - | - |
| Inverted Index | [README](./02-search-ir/sparse-retrieval/01-inverted-index/README.md) | - | [inverted_index.py](./02-search-ir/sparse-retrieval/01-inverted-index/inverted_index.py) |
| TF-IDF | [README](./02-search-ir/sparse-retrieval/02-tf-idf/README.md) | - | [tf_idf.py](./02-search-ir/sparse-retrieval/02-tf-idf/tf_idf.py) |
| BM25 검색 | [README](./02-search-ir/sparse-retrieval/03-bm25/README.md) | - | [bm25.py](./02-search-ir/sparse-retrieval/03-bm25/bm25.py) |
| BM25 더미 데이터 | [README](./02-search-ir/sparse-retrieval/03-bm25/data/README.md) | - | [generate_dummy_corpus.py](./02-search-ir/sparse-retrieval/03-bm25/data/generate_dummy_corpus.py) |
| 검색 평가 개요 | [README](./02-search-ir/evaluation/README.md) | - | - |
| Qrels | [README](./02-search-ir/evaluation/01-qrels/README.md) | - | [validate_qrels.py](./02-search-ir/evaluation/01-qrels/validate_qrels.py) |
| 검색 평가 지표 | [README](./02-search-ir/evaluation/02-metrics/README.md) | - | [evaluate_metrics_bm25.py](./02-search-ir/evaluation/02-metrics/evaluate_metrics_bm25.py) |
| Benchmarks | [README](./02-search-ir/evaluation/03-benchmarks/README.md) | - | [run_benchmark.py](./02-search-ir/evaluation/03-benchmarks/run_benchmark.py) |
| Reports | [README](./02-search-ir/evaluation/04-reports/README.md) | - | [render_report.py](./02-search-ir/evaluation/04-reports/render_report.py) |
| Error Analysis | [README](./02-search-ir/evaluation/05-error-analysis/README.md) | - | [analyze_bm25_errors.py](./02-search-ir/evaluation/05-error-analysis/analyze_bm25_errors.py) |
| Query Slice Analysis | [README](./02-search-ir/evaluation/06-slice-analysis/README.md) | - | [analyze_query_slices.py](./02-search-ir/evaluation/06-slice-analysis/analyze_query_slices.py) |
| Statistical Significance | [README](./02-search-ir/evaluation/07-significance/README.md) | - | [compare_models.py](./02-search-ir/evaluation/07-significance/compare_models.py) |

### RAG

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| RAG 개요 | [README](./03-rag/README.md) | - | - |

### LLMOps

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| LLMOps 개요 | [README](./04-llmops/README.md) | - | - |
| MLM vs AR | [노트](./04-llmops/01-basics/01-mlm-vs-ar.md) | - | - |
| Self-Supervised Learning vs Autoregressive | [노트](./04-llmops/01-basics/02-self-supervised-vs-autoregressive.md) | - | - |
| Foundation Model vs LLM vs LMM | [노트](./04-llmops/01-basics/03-foundation-model-vs-llm-vs-lmm.md) | - | - |

### ETC

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| Codex 프로젝트 세팅 | [README](./98-etc/codex/README.md) | - | - |
| VS Code 설정 | [README](./98-etc/vscode/README.md) | - | - |

## 작성 규칙

### 이름 규칙
- 폴더와 파일 이름은 `번호-kebab-case` 형식을 사용한다. (예: `01-inverted-index/`, `01-mlm-vs-ar.md`)
- 공백, 대문자, 마침표는 이름에 사용하지 않는다. (`README.md` 제외)

### README.md
- GitHub용
- 실행 방법, 주요 파일, 명령어, 출력 예시, 관련 Velog 링크

### README_VELOG.md
- Velog 게시용 원문
- 개념 설명, 코드 설명, 예시, 정리
- GitHub 상대 링크는 최소화
- 작성 후 Document Index의 `Velog 원문` 칸에 링크 추가

## 실행환경
- [`environment.yml`](./environment.yml)

```bash
conda env create -f environment.yml
conda activate study-py312
```

## Git 커밋 메시지

`타입: 설명` 형식을 사용한다. 필요하면 `타입(범위): 설명`으로 범위를 적는다.

| 타입 | 의미 | 예시 |
| --- | --- | --- |
| feat | 새로운 기능, 예제 코드 추가 | feat(search-ir): BM25F 예제 추가 |
| fix | 버그 수정 | fix: qrels 검증 시 빈 query 오류 수정 |
| docs | 문서, 학습 노트 추가/수정 | docs(llmops): MLM vs AR 노트 추가 |
| style | 코드 스타일 변경(기능 변화 없음) | style: 들여쓰기 정리 |
| refactor | 리팩토링 | refactor: 평가 지표 계산 함수 분리 |
| perf | 성능 개선 | perf: 벡터 검색 속도 개선 |
| test | 테스트 추가/수정 | test: metrics 단위 테스트 추가 |
| build | 빌드, 의존성 관련 | build: environment.yml 패키지 추가 |
| ci | CI/CD | ci: GitHub Actions 수정 |
| chore | 기타 작업 | chore: .gitignore 수정 |
