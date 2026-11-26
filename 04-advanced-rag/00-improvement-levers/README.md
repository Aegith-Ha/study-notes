# 지표 개선 레버 (Improvement Levers)

검색·생성 지표를 올리기 위해 바꿀 수 있는 것(레버)을 한곳에 모은 전체 개요다. 형태소 분석, 임베딩 모델, 청킹, 리랭커, 프롬프트처럼 흩어져 있는 레버를 파이프라인 단계로 묶고, 무엇부터 시도할지 정한다. 이 README에는 전체 그림과 메인 결정을 두고, 레버별 표와 실험 규칙은 하위 노트에 둔다.

- 틀린 질문에서 출발해 원인을 찾는 방향은 [02-retrieval-basics/04-naive-rag/02-failure-modes](../../02-retrieval-basics/04-naive-rag/02-failure-modes.md) 참고
- 각 기법의 자세한 내용은 [04-advanced-rag](../README.md)의 주제별 폴더 참고

## 하위 노트

- [01-lever-map](./01-lever-map.md): 레버를 당기기 전 평가 점검, 파이프라인 위의 레버 위치(L1~L12), 검색 쪽 레버 표, 생성 쪽 레버 표 (움직이는 지표, 재색인 여부, 비용, 자세한 노트 링크)
- [02-order-and-rules](./02-order-and-rules.md): 싼 것부터 시도하는 순서와 예외, 레버를 비교할 때 지킬 실험 규칙

## 전체 그림

```text
[색인할 때 — 바꾸면 다시 색인]
문서 ──▶ 파싱 ──▶ 청킹 ──▶ 토큰화 / 임베딩 ──▶ 색인
         L1       L2         L3 · L4               L5

[질문할 때 — 색인 그대로 바꿈]
질문 ──▶ 질의 처리 ──▶ 1차 검색 ──▶ 결과 합치기 ──▶ 리랭킹 ──▶ 컨텍스트 조립 ──▶ 생성
         L6            L7            L8              L9          L10              L11 · L12
```

| 묶음 | 레버 | 주로 움직이는 지표 | 다루는 곳 |
| --- | --- | --- | --- |
| 문서 준비 | 파싱, 청킹 | Recall, Set Recall, Context Sufficiency | [05-document-parsing](../05-document-parsing/README.md), [04-chunking](../04-chunking/README.md) |
| 색인 | 토큰화·사용자 사전, BM25 설정, 임베딩 모델·입력·파인튜닝, 벡터 인덱스 | BM25 / dense Recall | [02-retrieval-basics](../../02-retrieval-basics/README.md), [07-ml/02-embedding-finetuning](../../07-ml/02-embedding-finetuning/README.md) |
| 검색 | 질의 변환, 필터·라우팅, 후보 수, 결과 합치기, 리랭커 | Recall@k, MRR, nDCG | [01-hybrid-search](../01-hybrid-search/README.md), [02-reranking](../02-reranking/README.md), [03-query-transform](../03-query-transform/README.md) |
| 구조 활용 | 참조 링크 확장, 그래프, 요약 트리 | 다중 근거 질문의 Set Recall | [07-graph-hierarchical](../07-graph-hierarchical/README.md) |
| 생성 | 컨텍스트 조립, 프롬프트, 생성 모델, 파인튜닝, 여러 번 검색 | Answer Correctness, Faithfulness, 거절 | [02-retrieval-basics/04-naive-rag](../../02-retrieval-basics/04-naive-rag/README.md), [07-ml/03-lora-qlora](../../07-ml/03-lora-qlora/README.md), [05-agents](../../05-agents/README.md) |

- 레버마다 무엇을 바꾸는지, 비용은 얼마인지는 [01-lever-map](./01-lever-map.md) 3장, 4장의 표를 본다.

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 시작점 | 레버를 고르기 전에 평가 점검(판정 안 된 문서, pool 편향, judge 검증, 노이즈)과 실패 유형 분류부터 | 평가 문제를 시스템 문제로 착각하지 않고, 가장 많은 실패에 맞는 레버를 고르기 위해 |
| 시도 순서 | 프롬프트·조립 → 결과 합치기·후보 수 → 리랭커 → 질의 변환 → 토큰화·입력 구성 → 청킹·파싱 → 임베딩 교체 → 파인튜닝·그래프 | 싸고, 재색인이 필요 없고, 되돌리기 쉬운 것부터 |
| 순서의 예외 | Recall@50부터 낮으면 리랭커를 건너뛰고 색인 쪽 레버로 / Recall@50은 높은데 Recall@5만 낮으면 리랭커 먼저 | 리랭커는 1차 검색이 가져온 후보 안에서만 효과가 있음 |
| 비교 방법 | 한 번에 레버 하나, dev 세트, 같은 토큰 예산, 생성은 여러 번 실행, 유형별·질의별 변화, 비용·지연 함께 | 효과의 원인을 하나로 좁히고 노이즈와 구분 |
| 채택 후 | 해당 주제 README 메인 결정에 반영, 회귀 테스트 기준선 재계산 | 다음 비교의 출발점을 맞춤 |

- 시도 순서와 실험 규칙의 자세한 이유는 [02-order-and-rules](./02-order-and-rules.md) 참고

## 관련 코드

- 레버별 구현은 각 주제 README의 관련 코드에서 lawlens([99-projects/01-lawlens](../../99-projects/01-lawlens.md)) 파일로 연결한다
- 레버별 비교 실행: lawlens 평가 CLI [`eval.py`](https://github.com/Aegith-Ha/LawLens/blob/main/scripts/eval.py)
- 실행 방법은 연결된 프로젝트 README 참고
