# Study Notes

개인 학습 및 실습 기록 저장소입니다.

## Structure
- [`01-python/`](./01-python/) : Python 기초 및 실습
- [`02-search-ir/`](./02-search-ir/) : 검색(IR), BM25, analyzer, retrieval
- [`03-rag/`](./03-rag/) : RAG 구조, chunking, retriever, evaluation
- [`98-etc/`](./98-etc/) : 단순 설명 모음
- [`99-projects/`](./99-projects/) : 프로젝트 실습

## Document Index

### Python

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| argparse | [README](./01-python/argparse/README.md) | [README_VELOG](./01-python/argparse/README_VELOG.md) | [example.py](./01-python/argparse/example.py) |
| pydantic | [README](./01-python/pydantic/README.md) | [README_VELOG](./01-python/pydantic/README_VELOG.md) | [example.py](./01-python/pydantic/example.py) |

### Search / IR

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| Search / IR 개요 | [README](./02-search-ir/README.md) | - | - |
| BM25 검색 | [README](./02-search-ir/bm25/README.md) | [README_VELOG](./02-search-ir/bm25/README_VELOG.md) | [bm25.py](./02-search-ir/bm25/bm25.py) |
| BM25 더미 데이터 | [README](./02-search-ir/bm25/data/README.md) | - | [generate_dummy_corpus.py](./02-search-ir/bm25/data/generate_dummy_corpus.py) |
| 검색 평가 지표 | [README](./02-search-ir/evaluation/metrics/README.md) | [README_VELOG](./02-search-ir/evaluation/metrics/README_VELOG.md) | [evaluate_metrics_bm25.py](./02-search-ir/evaluation/metrics/evaluate_metrics_bm25.py) |

### RAG

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| RAG 개요 | [README](./03-rag/README.md) | - | - |

### ETC

| Topic | GitHub README | Velog 원문 | Code |
| --- | --- | --- | --- |
| Codex 프로젝트 세팅 | [README](./98-etc/codex/README.md) | - | - |

# README.md
 - GitHub용
 - 실행 방법, 주요 파일, 명령어, 출력 예시, 관련 Velog 링크

# README_VELOG.md
 - Velog 게시용 원문
 - 개념 설명, 코드 설명, 예시, 정리
 - GitHub 상대 링크는 최소화


## 실행환경
 - environmnet.yml
 - conda activate study-py312

# git comment 
- 타입	의미	예시
- feat	새로운 기능	feat: 회원가입 API 추가
- fix	버그 수정	fix: 로그인 시 세션 만료 오류 수정
- docs	문서 수정	docs: README 업데이트
- style	코드 스타일 변경(기능 변화 없음)	style: 들여쓰기 정리
- refactor	리팩토링	refactor: 검색 서비스 구조 개선
- perf	성능 개선	perf: 벡터 검색 속도 개선
- test	테스트 추가/수정	test: 검색 API 단위 테스트 추가
- build	빌드 관련	build: Maven 의존성 업데이트
- ci	CI/CD	ci: GitHub Actions 수정
- chore	기타 작업	chore: .gitignore 수정 
