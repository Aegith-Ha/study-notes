# Study Notes

개인 학습 및 실습 기록 저장소입니다.

## Structure
- [`00-infra/`](./00-infra/) : 실습 공통 인프라 (Milvus)
- [`01-python/`](./01-python/) : Python 기초 및 실습
- [`02-search-ir/`](./02-search-ir/) : 검색(IR), sparse·dense·hybrid retrieval, reranking, evaluation
- [`03-rag/`](./03-rag/) : RAG 구조, chunking, retrieval integration, evaluation
- [`04-llmops/`](./04-llmops/) : LLM 기초 개념, LLMOps
- [`98-etc/`](./98-etc/) : 단순 설명 모음
- [`99-projects/`](./99-projects/) : 프로젝트 실습

## Learning Path

```
00-infra (Milvus 구축)
  → 02-search-ir : 문서를 잘 찾는 법 (평가: Recall@k, nDCG)
  → 03-rag       : 찾은 문서로 답을 잘 만드는 법 (평가: 답변 품질)
```

## Document Index

각 주제의 세부 목차는 폴더별 README에서 관리한다.

| Section | 내용 | 상태 |
| --- | --- | --- |
| [Milvus](./00-infra/milvus/) | Milvus 설치, 실행, 접속 확인 (Milvus Lite부터 시작) | 예정 |
| [Search / IR](./02-search-ir/README.md) | Data, Sparse, Dense, Hybrid, Reranking, Evaluation | 진행 중 |
| [RAG](./03-rag/README.md) | Data, Basics, Chunking, Retrieval Integration, Evaluation, Advanced | 예정 |
| [LLMOps](./04-llmops/README.md) | LLM 기초 개념, LLMOps | 예정 |

### Search / IR

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| 공통 데이터 (corpus, queries, qrels) | [README](./02-search-ir/00-data/README.md) | - | [generate_corpus.py](./02-search-ir/00-data/generate_corpus.py) |
| Inverted Index | [README](./02-search-ir/01-sparse-retrieval/01-inverted-index/README.md) | - | [inverted_index.py](./02-search-ir/01-sparse-retrieval/01-inverted-index/inverted_index.py) |
| TF-IDF | [README](./02-search-ir/01-sparse-retrieval/02-tf-idf/README.md) | - | [tf_idf.py](./02-search-ir/01-sparse-retrieval/02-tf-idf/tf_idf.py) |
| BM25, BM25+, BM25L, BM25F | [README](./02-search-ir/01-sparse-retrieval/03-bm25/README.md) | - | [bm25.py](./02-search-ir/01-sparse-retrieval/03-bm25/bm25.py) |
| Qrels | [README](./02-search-ir/05-evaluation/01-qrels/README.md) | - | [validate_qrels.py](./02-search-ir/05-evaluation/01-qrels/validate_qrels.py) |
| Metrics (P@k, R@k, MRR, nDCG) | [README](./02-search-ir/05-evaluation/02-metrics/README.md) | - | [evaluate_metrics_bm25.py](./02-search-ir/05-evaluation/02-metrics/evaluate_metrics_bm25.py) |
| Benchmarks, Report | [README](./02-search-ir/05-evaluation/03-benchmarks/README.md) | - | [run_benchmark.py](./02-search-ir/05-evaluation/03-benchmarks/run_benchmark.py), [render_report.py](./02-search-ir/05-evaluation/03-benchmarks/render_report.py) |
| Error Analysis | [README](./02-search-ir/05-evaluation/04-error-analysis/README.md) | - | [analyze_bm25_errors.py](./02-search-ir/05-evaluation/04-error-analysis/analyze_bm25_errors.py) |
| Slice Analysis | [README](./02-search-ir/05-evaluation/05-slice-analysis/README.md) | - | [analyze_query_slices.py](./02-search-ir/05-evaluation/05-slice-analysis/analyze_query_slices.py) |
| Significance | [README](./02-search-ir/05-evaluation/06-significance/README.md) | - | [compare_models.py](./02-search-ir/05-evaluation/06-significance/compare_models.py) |

### Python

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| argparse | [README](./01-python/argparse/README.md) | - | [example.py](./01-python/argparse/example.py) |
| pydantic | [README](./01-python/pydantic/README.md) | - | [example.py](./01-python/pydantic/example.py) |

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
- 폴더마다 하나씩 두고, 하위 주제 목차는 해당 폴더 README에서 관리
- GitHub용
- 실행 방법, 주요 파일, 명령어, 출력 예시, 관련 Velog 링크

### README_VELOG.md
- Velog 게시용 원문
- 개념 설명, 코드 설명, 예시, 정리
- GitHub 상대 링크는 최소화
- 작성 후 Document Index의 `Velog 원문` 칸에 링크 추가

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

## 실행 환경
- [`environment.yml`](./environment.yml)

```bash
conda env create -f environment.yml
conda activate study-py312
```
