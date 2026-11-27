# 청킹 (Chunking)

문서를 검색 단위로 나누는 방법과, 작게 찾고 크게 넘기는 부모-자식 청크, 청크에 맥락을 덧붙이는 contextual retrieval을 정리한다. 기본 RAG 실패 유형 중 F6(청크 경계 문제)을 고친다. 이 README에는 기본 선택과 이유를 두고, 방법 설명은 하위 노트에 둔다.

- 청크를 바꾸면 검색과 생성 지표가 모두 움직인다. [01-retrieval-metrics](../../03-evals/01-retrieval-metrics/README.md), [02-generation-metrics](../../03-evals/02-generation-metrics/README.md) 참고

## 하위 노트

- [01-chunking-strategies](./01-chunking-strategies.md): 크기의 영향과 크기 고르는 절차, 고정 길이·문장·구조·의미 기준, 고정 길이·의미 기준 손계산, 토큰을 세는 기준, 구조 단위 청킹, 자르면 안 되는 블록(표·목록·코드), 반복 문구, 청크 ID·메타데이터와 다시 색인하기, 평가할 때 주의
- [02-parent-child-contextual](./02-parent-child-contextual.md): 부모-자식 청크, sentence-window, contextual retrieval(규칙 기반·LLM 생성)과 LLM 맥락 비용(프롬프트 캐시), 다른 방식(명제 단위, late chunking, 요약 트리), 평가

## 기본 선택과 이유

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 기준선 | 섹션 단위 (최대 길이 초과 섹션만 하위 항목 단위로 분할) | 예외 문장 보존, 골든셋 판정 단위와 같음 |
| 비교 설정 | 하위 항목 단위 / 고정 길이 300 + 겹침 50 / 부모(섹션)-자식(하위 항목) | 정밀도와 맥락의 균형 비교 |
| 크기 비교 | 구조가 없는 문서는 128~1,024토큰 후보를 같은 토큰 예산으로 비교 | 같은 k로 비교하면 큰 청크가 유리 |
| 토큰 기준 | 청크 크기는 임베딩 모델 토크나이저, 컨텍스트 예산은 생성 LLM 토크나이저 | 한국어는 토크나이저마다 토큰 수 차이가 큼 |
| 자르지 않는 단위 | 표·목록·코드 블록은 경계를 지키고, 반복 문구는 색인 전에 제거 | 블록이 잘리면 내용을 쓸 수 없음 |
| 청크 ID | 문서 ID + 버전 + 위치로 만들고, 바뀐 문서만 다시 색인 | qrels·캐시가 깨지지 않게 |
| 맥락 추가 | 규칙 기반(문서 제목 + 섹션 번호 + 섹션 제목) 먼저, LLM 생성은 비교용 | 구조 있는 문서는 구조 정보가 풍부 |
| 맥락 적용 | sparse와 dense 양쪽 | BM25 정확 일치에도 도움 |
| 평가 | 문서 단위 매핑 Recall@5 + 근거 구간 포함률 + Claim Recall + 질의당 토큰 | 검색·생성·비용을 함께 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 조문 단위 청킹 + 계층 헤더 [`chunker.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/indexing/chunker.py), 색인 [`indexer.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/indexing/indexer.py)
- 실행 방법은 연결된 프로젝트 README 참고
