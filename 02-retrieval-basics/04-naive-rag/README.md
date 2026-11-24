# 기본 RAG (Naive RAG)

검색 결과를 그대로 프롬프트에 넣어 답하는 가장 단순한 RAG를 정리한다. 이 파이프라인이 생성 평가의 기준선이고, 여기서 드러난 실패 유형이 [04-advanced-rag](../../04-advanced-rag/README.md)에서 무엇부터 할지 정한다. 이 README에는 기준선 설정을 두고, 구조와 실패 유형 설명은 하위 노트에 둔다.

- 검색기는 [01-sparse-retrieval](../01-sparse-retrieval/README.md), [02-dense-retrieval](../02-dense-retrieval/README.md) 참고
- 생성 지표는 [03-evals/02-generation-metrics](../../03-evals/02-generation-metrics/README.md) 참고

## 하위 노트

- [01-pipeline](./01-pipeline.md): 색인·질의 단계 구조, 단계별 결정, 프롬프트 구성, 생성 평가와의 연결(oracle / BM25 / dense)
- [02-failure-modes](./02-failure-modes.md): 실패 유형 10가지, 드러나는 지표, 고치는 고급 기법, 분류 방법

## 메인 결정 (초안): 기준선 설정

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 청크 | 조문 단위 | 골든셋 판정 단위와 같아 매핑 불필요 |
| 검색기 | BM25, dense(선택한 모델) 각각 | 두 기준선 비교, 하이브리드의 출발점 |
| top-k | 5 | 검색 메인 지표 Recall@5와 일치 |
| 컨텍스트 조립 | 검색 순위 순, `[doc_id] 법령명 조문 제목` + 본문, 같은 문서 중복 제거 | 인용 채점과 중복 제거 규칙 일치 |
| 프롬프트 | 자료만 사용 / 답할 수 없으면 고정 문구로 거절 / 문장마다 [doc_id] 인용 | Faithfulness, 거절, 인용을 지표로 잴 수 있게 |
| 생성 | 모델 버전 고정, temperature 0 | 재현성, 회귀 테스트 |
| 실행 | oracle / BM25 top-5 / dense top-5 세 가지, 프롬프트·생성 설정 동일 | 검색과 생성 문제 분리 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 검색 서비스 [`service.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/retrieval/service.py)
  - 답변 생성 [`answer.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/generation/answer.py), 프롬프트 [`answer.md`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/generation/prompts/answer.md)는 아직 구현 전 (Phase 2 TODO)
- 실행 방법은 연결된 프로젝트 README 참고
