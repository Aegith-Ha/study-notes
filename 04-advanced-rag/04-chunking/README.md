# 청킹 (Chunking)

문서를 검색 단위로 나누는 방법과, 작게 찾고 크게 넘기는 부모-자식 청크, 청크에 맥락을 덧붙이는 contextual retrieval을 정리한다. 기본 RAG 실패 유형 중 F6(청크 경계 문제)을 고친다. 이 README에는 메인 결정을 두고, 방법 설명은 하위 노트에 둔다.

- 청크를 바꾸면 검색과 생성 지표가 모두 움직인다. [01-retrieval-metrics](../../03-evals/01-retrieval-metrics/README.md), [02-generation-metrics](../../03-evals/02-generation-metrics/README.md) 참고

## 하위 노트

- [01-chunking-strategies](./01-chunking-strategies.md): 크기의 영향, 고정 길이·문장·구조·의미 기준, 고정 길이 손계산, 법령 조·항 단위 청킹, 평가할 때 주의
- [02-parent-child-contextual](./02-parent-child-contextual.md): 부모-자식 청크, contextual retrieval(규칙 기반·LLM 생성), 평가

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 기준선 | 조 단위 (최대 길이 초과 조만 항 단위로 분할) | 단서·예외 보존, 골든셋 판정 단위와 같음 |
| 비교 설정 | 항 단위 / 고정 길이 300 + 겹침 50 / 부모(조)-자식(항) | 정밀도와 맥락의 균형 비교 |
| 맥락 추가 | 규칙 기반(법령명 + 조 번호 + 조 제목) 먼저, LLM 생성은 비교용 | 법령은 구조 정보가 풍부 |
| 맥락 적용 | sparse와 dense 양쪽 | BM25 정확 일치에도 도움 |
| 평가 | 문서 단위 매핑 Recall@5 + 근거 구간 포함률 + Claim Recall + 질의당 토큰 | 검색·생성·비용을 함께 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 조문 단위 청킹 + 계층 헤더 [`chunker.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/indexing/chunker.py), 색인 [`indexer.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/indexing/indexer.py)
- 실행 방법은 연결된 프로젝트 README 참고
