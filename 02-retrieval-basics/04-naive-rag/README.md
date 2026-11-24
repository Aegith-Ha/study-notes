# 기본 RAG (Naive RAG)

검색 결과를 그대로 프롬프트에 넣어 답하는 가장 단순한 RAG를 정리한다. 이 파이프라인이 생성 평가의 기준선이고, 여기서 드러난 실패 유형이 [04-advanced-rag](../../04-advanced-rag/README.md)에서 무엇부터 할지 정한다. 이 README에는 기준선 설정과 결과를 두고, 구조와 실패 유형 설명은 하위 노트에 둔다.

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

## 실험 조건

| 항목 | 값 |
| --- | --- |
| 프로젝트 / 커밋 | - |
| 문서 집합 버전, 골든셋 버전 | - |
| 검색기 설정 | - (BM25 토크나이저·파라미터, dense 모델·인덱스) |
| 프롬프트 버전 | - |
| 생성 모델 / 버전, temperature, 최대 토큰 | - |
| judge 모델 / 프롬프트 버전 | - |

## 결과: 기준선

[03-evals/02-generation-metrics](../../03-evals/02-generation-metrics/README.md)의 메인 지표로 잰다. 확정된 기준선은 그 README의 결과 표에도 옮긴다.

| 컨텍스트 | Recall@5 | Answer Correctness | Faithfulness | 거절 정확도 | 과잉 거절률 | Citation Support | 질의당 토큰 | p95 지연 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle | (1.0) | - | - | - | - | - | - | - |
| BM25 top-5 | - | - | - | - | - | - | - | - |
| dense top-5 | - | - | - | - | - | - | - | - |

- oracle과 BM25 / dense의 Answer Correctness 차이가 검색 때문에 잃는 몫이다.

### 실패 유형 분포 (dev 세트, 틀린 질의)

| 유형 | BM25 기준선 | dense 기준선 | 고치는 곳 |
| --- | --- | --- | --- |
| F1 표현 불일치 | - | - | 하이브리드 |
| F2 정확 일치 실패 | - | - | 하이브리드 |
| F3 순위 문제 | - | - | 리랭커 |
| F4 모호한 질문 | - | - | 쿼리 변환 |
| F5 조건 누락 | - | - | 메타데이터 필터 |
| F6 청크 경계 | - | - | 청킹 |
| F7 파싱 손실 | - | - | 문서 파싱 |
| F8~F10 생성 문제 | - | - | 프롬프트, 생성 모델 |

- 가장 많은 유형부터 [04-advanced-rag](../../04-advanced-rag/README.md)에서 다룬다.

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 검색 서비스 [`service.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/retrieval/service.py)
  - 답변 생성 [`answer.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/generation/answer.py), 프롬프트 [`answer.md`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/generation/prompts/answer.md)는 아직 구현 전 (Phase 2 TODO)
- 실행 방법은 연결된 프로젝트 README 참고
