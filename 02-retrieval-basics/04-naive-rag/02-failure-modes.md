# 기본 RAG의 실패 유형 (Failure Modes)

naive RAG에서 자주 생기는 실패를 유형별로 나누고, 어떤 지표로 드러나는지, 어떤 고급 기법으로 고치는지 연결한다. 기준선 결과를 분석할 때 이 표로 실패를 분류하면 [04-advanced-rag](../../04-advanced-rag/README.md)에서 무엇부터 할지 정할 수 있다.

- 폴더 요약과 기본 선택은 [README](./README.md) 참고
- 파이프라인 구조는 [01-pipeline](./01-pipeline.md) 참고
- 반대로 바꿀 수 있는 것(레버)에서 출발해 정리한 목록은 [04-advanced-rag/00-improvement-levers](../../04-advanced-rag/00-improvement-levers/README.md) 참고

## 1. 실패 유형

| # | 유형 | 예 | 드러나는 지표 | 고치는 곳 |
| --- | --- | --- | --- | --- |
| F1 | 표현 불일치 | "결제했는데 돈이 안 돌아와요"로 "환불 처리 기준" 섹션을 못 찾음 | BM25 Recall@5 낮음, dense는 성공 | 하이브리드 ([04-advanced-rag/01-hybrid-search](../../04-advanced-rag/01-hybrid-search/README.md)) |
| F2 | 정확 일치 실패 | "E-4012"를 물었는데 dense가 비슷한 다른 코드의 문서를 가져옴 | dense Recall@5 낮음, BM25는 성공 | 하이브리드 ([04-advanced-rag/01-hybrid-search](../../04-advanced-rag/01-hybrid-search/README.md)) |
| F3 | 순위 문제 | 정답이 top-20 안에는 있는데 top-5 밖 | Recall@20 높고 Recall@5 낮음, MRR 낮음 | 리랭커 ([04-advanced-rag/02-reranking](../../04-advanced-rag/02-reranking/README.md)) |
| F4 | 모호하거나 짧은 질문 | "환불?" | 여러 검색기 모두 Recall 낮음 | 쿼리 재작성, HyDE ([04-advanced-rag/03-query-transform](../../04-advanced-rag/03-query-transform/README.md)) |
| F5 | 조건 누락 | "2024년 개정 후 기준"인데 구버전 문서를 가져옴 | 구버전 문서 반환율 높음 | 메타데이터 필터 ([04-advanced-rag/03-query-transform](../../04-advanced-rag/03-query-transform/README.md)) |
| F6 | 청크 경계 문제 | 본문과 예외 문장("단, …")이 다른 청크로 나뉨 | Claim Recall 낮음(조건 누락), Context Sufficiency 낮음 | 청킹 ([04-advanced-rag/04-chunking](../../04-advanced-rag/04-chunking/README.md)) |
| F7 | 파싱 손실 | 표 안의 금액·기한이 텍스트로 깨져 검색 안 됨 | 특정 문서 유형에서만 Recall 낮음 | 문서 파싱 ([04-advanced-rag/05-document-parsing](../../04-advanced-rag/05-document-parsing/README.md)) |
| F8 | 근거를 받고도 틀림 | 정답 문서를 받았는데 예외 조건을 빠뜨림 | Recall@5 성공 + Correctness 실패 | 프롬프트, 생성 모델 |
| F9 | 근거 밖 내용 생성 | 자료에 없는 절차를 덧붙임 | Faithfulness 낮음 | 프롬프트, 생성 모델 |
| F10 | 거절 실패 | 자료에 근거가 없는데 사전 지식으로 답함 | 답 없음 질의 거절 정확도 낮음 | 프롬프트 |
| F11 | 다중 근거 부족 | "환불 기한과 배송비 부담 주체는?"에 두 섹션이 필요한데 top-5에 하나만 옴 | 문서 단위 Recall@5는 보통, 조합 충족률(Set Recall) 낮음 ([01-reference-based](../../03-evals/01-retrieval-metrics/01-reference-based.md) 3.6) | 쿼리 분해 ([04-advanced-rag/03-query-transform](../../04-advanced-rag/03-query-transform/README.md)), 다양성 고려 재정렬 ([04-advanced-rag/02-reranking/02-candidate-depth](../../04-advanced-rag/02-reranking/02-candidate-depth.md) 5장 MMR), top-k 늘리기 |
| F12 | 문서 간 충돌 | 구버전과 신버전, 일반 규정과 예외 규정이 함께 들어와 섞인 답을 냄 | Recall@5 성공 + Correctness 실패, 답변에 서로 다른 기준이 섞임 | 메타데이터 필터(최신만), 컨텍스트에 시행일·버전 표시, 충돌 시 처리 규칙을 프롬프트에 |
| F13 | 대화 맥락 누락 | 앞 질문 뒤에 "그럼 예외는?"을 그대로 검색 | 대화형 질의에서만 Recall 낮음 | 대화 맥락으로 질문 재작성 ([04-advanced-rag/03-query-transform/01-query-rewrite-hyde](../../04-advanced-rag/03-query-transform/01-query-rewrite-hyde.md)) |

## 2. 분류하는 방법

```text
기준선 결과 (BM25 / dense / oracle)에서 틀린 질의를 모은다
   │
   ├─ oracle에서도 틀림              → F8, F9, F10 (생성 문제)
   │                                    서로 다른 기준이 섞임 → F12
   │
   └─ oracle에서는 맞음 (검색 문제)
        ├─ 대화의 후속 질문           → F13
        ├─ 한 검색기만 성공           → F1, F2
        ├─ top-20 안에는 있음         → F3
        ├─ 구버전·조건 위반 문서      → F5 (생성까지 섞이면 F12)
        ├─ 필요한 근거 중 일부만 옴   → F11 (여러 문서) / F6, F7 (한 문서 안)
        └─ 어느 검색기도 못 찾음      → F4, F7
```

- 이 분류는 [02-generation-metrics](../../03-evals/02-generation-metrics/README.md)의 질의별 원인 나누기(검색 성공·실패 × 답변 맞음·틀림)를 한 단계 더 쪼갠 것이다.
- 유형별 질의 수를 센다. 가장 많은 유형이 [04-advanced-rag](../../04-advanced-rag/README.md)에서 먼저 할 기법이다.

### 분류 결과 예시

dev 세트 100질문, dense 기준선에서 틀린 34개를 분류한 결과 (숫자는 예시)

| 유형 | 질의 수 | 비율 | 다음 할 일 |
| --- | --- | --- | --- |
| F2 정확 일치 실패 | 9 | 26% | **하이브리드 (BM25 추가)** |
| F3 순위 문제 | 7 | 21% | 리랭커 |
| F11 다중 근거 부족 | 5 | 15% | 쿼리 분해, top-k 조정 |
| F6 청크 경계 | 4 | 12% | 청킹 |
| F8 근거를 받고도 틀림 | 4 | 12% | 프롬프트 |
| F4, F5, F7, F10 | 5 | 15% | 보류 |

읽는 법
- 가장 많은 F2부터 고친다. 하이브리드는 F1·F2를 함께 줄이고, 비용도 낮다.
- F3은 하이브리드 뒤에 다시 센다. 후보가 바뀌면 순위 문제의 수도 달라진다.
- 한 번에 하나만 바꾸고, 바꾼 뒤 같은 dev 세트로 다시 분류한다. 고친 유형이 줄었는지와 다른 유형이 늘지 않았는지를 같이 본다([04-advanced-rag/00-improvement-levers/02-order-and-rules](../../04-advanced-rag/00-improvement-levers/02-order-and-rules.md)).
- 유형별 질의가 몇 개뿐이면 비율 차이가 우연일 수 있다. 순서를 정하는 데만 쓰고 효과는 전체 지표로 확인한다.

## 3. 확인할 점

- 한 질의가 여러 유형에 걸칠 수 있다. 처음에는 가장 앞단(검색 쪽)의 원인 하나만 붙인다. 앞단을 고치면 뒷단 증상이 사라지는 경우가 많다.
- 분류는 사람이 질의를 보며 하는 작업이다. dev 세트에서만 하고 test 세트는 열어 보지 않는다([05-regression-ci](../../03-evals/05-regression-ci/01-gate-design.md) 3장).
