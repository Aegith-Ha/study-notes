# 기본 RAG의 실패 유형 (Failure Modes)

naive RAG에서 자주 생기는 실패를 유형별로 나누고, 어떤 지표로 드러나는지, 어떤 고급 기법으로 고치는지 연결한다. 기준선 결과를 분석할 때 이 표로 실패를 분류하면 [04-advanced-rag](../../04-advanced-rag/README.md)에서 무엇부터 할지 정할 수 있다.

- 폴더 요약, 메인 결정, 결과는 [README](./README.md) 참고
- 파이프라인 구조는 [01-pipeline](./01-pipeline.md) 참고

## 1. 실패 유형

| # | 유형 | 예 | 드러나는 지표 | 고치는 곳 |
| --- | --- | --- | --- | --- |
| F1 | 표현 불일치 | "집주인이 보증금을 안 줘요"로 "임대차보증금 반환" 조문을 못 찾음 | BM25 Recall@5 낮음, dense는 성공 | 하이브리드 ([04-advanced-rag/01-hybrid-search](../../04-advanced-rag/01-hybrid-search/README.md)) |
| F2 | 정확 일치 실패 | "제3조의2"를 물었는데 dense가 비슷한 다른 조문을 가져옴 | dense Recall@5 낮음, BM25는 성공 | 하이브리드 ([04-advanced-rag/01-hybrid-search](../../04-advanced-rag/01-hybrid-search/README.md)) |
| F3 | 순위 문제 | 정답이 top-20 안에는 있는데 top-5 밖 | Recall@20 높고 Recall@5 낮음, MRR 낮음 | 리랭커 ([04-advanced-rag/02-reranking](../../04-advanced-rag/02-reranking/README.md)) |
| F4 | 모호하거나 짧은 질문 | "퇴직금?" | 여러 검색기 모두 Recall 낮음 | 쿼리 재작성, HyDE ([04-advanced-rag/03-query-transform](../../04-advanced-rag/03-query-transform/README.md)) |
| F5 | 조건 누락 | "2024년 개정 후 기준"인데 구버전 조문을 가져옴 | 구버전 문서 반환율 높음 | 메타데이터 필터 ([04-advanced-rag/03-query-transform](../../04-advanced-rag/03-query-transform/README.md)) |
| F6 | 청크 경계 문제 | 조문 본문과 단서 조항이 다른 청크로 나뉨 | Claim Recall 낮음(조건 누락), Context Sufficiency 낮음 | 청킹 ([04-advanced-rag/04-chunking](../../04-advanced-rag/04-chunking/README.md)) |
| F7 | 파싱 손실 | 표 안의 금액·기한이 텍스트로 깨져 검색 안 됨 | 특정 문서 유형에서만 Recall 낮음 | 문서 파싱 ([04-advanced-rag/05-document-parsing](../../04-advanced-rag/05-document-parsing/README.md)) |
| F8 | 근거를 받고도 틀림 | 정답 조문을 받았는데 예외 조항을 빠뜨림 | Recall@5 성공 + Correctness 실패 | 프롬프트, 생성 모델 |
| F9 | 근거 밖 내용 생성 | 자료에 없는 절차를 덧붙임 | Faithfulness 낮음 | 프롬프트, 생성 모델 |
| F10 | 거절 실패 | 자료에 근거가 없는데 사전 지식으로 답함 | 답 없음 질의 거절 정확도 낮음 | 프롬프트 |

## 2. 분류하는 방법

```text
기준선 결과 (BM25 / dense / oracle)에서 틀린 질의를 모은다
   │
   ├─ oracle에서도 틀림              → F8, F9, F10 (생성 문제)
   │
   └─ oracle에서는 맞음 (검색 문제)
        ├─ 한 검색기만 성공           → F1, F2
        ├─ top-20 안에는 있음         → F3
        ├─ 구버전·조건 위반 문서      → F5
        ├─ 정답 문서는 왔는데 일부만  → F6, F7
        └─ 어느 검색기도 못 찾음      → F4, F7
```

- 이 분류는 [02-generation-metrics](../../03-evals/02-generation-metrics/README.md)의 질의별 원인 나누기(검색 성공·실패 × 답변 맞음·틀림)를 한 단계 더 쪼갠 것이다.
- 유형별 질의 수를 [README](./README.md) 결과 표에 기록한다. 가장 많은 유형이 [04-advanced-rag](../../04-advanced-rag/README.md)에서 먼저 할 기법이다.

## 3. 확인할 점

- 한 질의가 여러 유형에 걸칠 수 있다. 처음에는 가장 앞단(검색 쪽)의 원인 하나만 붙인다. 앞단을 고치면 뒷단 증상이 사라지는 경우가 많다.
- 분류는 사람이 질의를 보며 하는 작업이다. dev 세트에서만 하고 test 세트는 열어 보지 않는다([05-regression-ci](../../03-evals/05-regression-ci/01-gate-design.md) 3장).
