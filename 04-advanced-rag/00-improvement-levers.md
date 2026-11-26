# 지표 개선 레버 (Improvement Levers)

검색·생성 지표를 올리기 위해 **바꿀 수 있는 것**(레버)을 파이프라인 단계별로 모으고, 각 레버가 어떤 지표를 움직이는지, 비용이 얼마나 드는지, 어떤 순서로 시도할지 정리한다. 레버마다 자세한 내용은 해당 노트로 연결한다.

- 틀린 질문에서 출발해 원인을 찾는 방향은 [02-retrieval-basics/04-naive-rag/02-failure-modes](../02-retrieval-basics/04-naive-rag/02-failure-modes.md) 참고. 이 노트는 반대로 레버에서 출발한다
- 지표 정의는 [03-evals/01-retrieval-metrics](../03-evals/01-retrieval-metrics/README.md), [03-evals/02-generation-metrics](../03-evals/02-generation-metrics/README.md) 참고

## 1. 레버를 당기기 전에: 평가가 맞는가

점수가 낮거나 개선이 안 보일 때, 시스템보다 **평가 쪽 문제**인 경우가 있다. 레버를 바꾸기 전에 먼저 확인한다.

| 확인 | 의심되는 상황 | 자세히 |
| --- | --- | --- |
| 판정 안 된 문서 | 새 검색기 점수가 낮은데 Judged@k도 낮음 | [03-golden-set/02-pooling](../03-evals/03-golden-set/02-pooling.md) 5장, 6장 |
| pool 편향 | pool에 참여한 검색기와 비슷한 방식만 점수가 높음 | 같은 노트 6장 "Pool 편향 점검" |
| judge 미검증 | 정답 없는 지표만 오르고 정답 기반 지표는 그대로 | [03-evals/04-llm-judge](../03-evals/04-llm-judge/README.md) |
| 표본 노이즈 | 차이가 질문 1~2건 수준, 다시 돌리면 결과가 바뀜 | [03-evals/02-generation-metrics/01-reference-based](../03-evals/02-generation-metrics/01-reference-based.md) 3.6, [05-regression-ci](../03-evals/05-regression-ci/01-gate-design.md) 5장 |
| 비교 조건 | 청크 크기가 다른데 같은 k로 비교함 | [03-evals/01-retrieval-metrics/01-reference-based](../03-evals/01-retrieval-metrics/01-reference-based.md) 3.7 |

- 두 계열 지표가 엇갈릴 때 무엇을 의심할지는 [03-evals README](../03-evals/README.md) "두 지표를 함께 읽는 법" 참고

## 2. 레버가 있는 위치

```text
[색인할 때]
문서 ──▶ 파싱 ──▶ 청킹 ──▶ 토큰화 / 임베딩 ──▶ 색인 (BM25, 벡터, 그래프)
         L1       L2         L3 · L4               L5

[질문할 때]
질문 ──▶ 질의 처리 ──▶ 1차 검색 ──▶ 결과 합치기 ──▶ 리랭킹 ──▶ 컨텍스트 조립 ──▶ 생성
         L6            L7            L8              L9          L10              L11 · L12
```

- 색인할 때의 레버(L1~L5)는 바꾸면 **문서 전체를 다시 색인**해야 한다. 질문할 때의 레버(L6~L12)는 색인을 그대로 두고 바꿀 수 있다. 이 차이가 시도 순서를 정한다(5장).

## 3. 검색 쪽 레버

| # | 레버 | 바꾸는 것 (예) | 주로 움직이는 지표 | 재색인 | 비용 | 자세히 |
| --- | --- | --- | --- | --- | --- | --- |
| L1 | 문서 파싱 | 표·PDF 레이아웃 처리, 이미지 설명 | 특정 문서 유형의 Recall | 필요 | 중 | [05-document-parsing](./05-document-parsing/README.md) |
| L2 | 청킹 | 크기, 겹침, 구조 단위, 부모-자식, 청크 앞 맥락 추가 | Recall@k, Set Recall, Context Sufficiency, Claim Recall | 필요 | 중 | [04-chunking](./04-chunking/README.md) |
| L3 | 토큰화 (sparse) | 형태소 분석기, 사용자 사전, n-gram | BM25 Recall, 코드·고유명사 질문 | 필요 | 낮음 | [01-inverted-index-tfidf](../02-retrieval-basics/01-sparse-retrieval/01-inverted-index-tfidf.md) 4장 |
| L3 | BM25 설정 | k1·b, BM25F(필드별 가중치), 학습된 sparse로 교체 | BM25 Recall | 일부 필요 | 낮음 | [02-bm25](../02-retrieval-basics/01-sparse-retrieval/02-bm25.md) 3~5장 |
| L4 | 임베딩 모델 | 모델 교체, 다국어·한국어 특화, 멀티 벡터 | dense Recall, 일상어 질문(user 말투) | 필요 | 중 | [02-model-selection](../02-retrieval-basics/02-dense-retrieval/02-model-selection.md), [01-embedding-basics](../02-retrieval-basics/02-dense-retrieval/01-embedding-basics.md) 4장 |
| L4 | 임베딩 입력 구성 | 제목·섹션 제목 붙이기, 질의·문서 접두어 | dense Recall | 필요 | 낮음 | [01-embedding-basics](../02-retrieval-basics/02-dense-retrieval/01-embedding-basics.md) 3장 |
| L4 | 임베딩 파인튜닝 | 도메인 데이터로 추가 학습 | dense Recall | 필요 | 높음 | [07-ml/02-embedding-finetuning](../07-ml/02-embedding-finetuning/README.md) |
| L5 | 벡터 인덱스 | HNSW `ef`·`M`, IVF `nprobe` | ANN Recall (정확 검색 대비 손실) | 일부 필요 | 낮음 | [01-ann-algorithms](../02-retrieval-basics/03-vector-index/01-ann-algorithms.md) 3장 |
| L6 | 질의 변환 | 재작성, 다중 질의, HyDE, 분해 | 짧고 모호한 질문의 Recall | 불필요 | 중 (LLM 호출) | [01-query-rewrite-hyde](./03-query-transform/01-query-rewrite-hyde.md) |
| L6 | 필터와 라우팅 | 메타데이터 필터, 식별자 정확 조회 | 구버전 반환율, 식별자 질문 MRR | 불필요 | 낮음 | [02-metadata-filter](./03-query-transform/02-metadata-filter.md) |
| L7 | 1차 검색 후보 수 | 검색기별 top-N | 리랭킹 전 Recall@N (리랭커의 상한) | 불필요 | 낮음 | [02-candidate-depth](./02-reranking/02-candidate-depth.md) |
| L8 | 결과 합치기 | RRF k, 가중치, 참여 검색기 | Recall@k, MRR | 불필요 | 낮음 | [01-hybrid-search](./01-hybrid-search/README.md) |
| L9 | 리랭커 | 모델 교체, 입력 구성, 파인튜닝 | MRR, nDCG, Recall@5 | 불필요 | 중 (지연 증가) | [02-reranking](./02-reranking/README.md) |
| - | 구조 활용 | 참조 링크 확장, 그래프, 요약 트리 | 다중 근거 질문의 Set Recall | 필요 | 높음 | [07-graph-hierarchical](./07-graph-hierarchical/README.md) |

## 4. 생성 쪽 레버

| # | 레버 | 바꾸는 것 (예) | 주로 움직이는 지표 | 비용 | 자세히 |
| --- | --- | --- | --- | --- | --- |
| L10 | 컨텍스트 조립 | 넣는 청크 수(k), 순서, 중복 제거, 청크 앞 출처 표시 | Answer Correctness, Faithfulness, 인용 | 낮음 | [01-pipeline](../02-retrieval-basics/04-naive-rag/01-pipeline.md) 2장 |
| L11 | 프롬프트 | 자료만 쓰라는 지시, 거절 문구, 인용 형식, 예시 | Faithfulness, 거절 정확도, 인용 지표 | 낮음 | [01-pipeline](../02-retrieval-basics/04-naive-rag/01-pipeline.md) 3장 |
| L12 | 생성 모델 | 모델 교체, 긴 컨텍스트 모델 | Answer Correctness, Faithfulness | 중 (단가) | [06-long-context-vs-rag](./06-long-context-vs-rag/README.md) |
| L12 | 생성 모델 파인튜닝 | 답변 형식·거절·인용 방식 학습 | 형식 준수, 거절 정확도 | 높음 | [07-ml/03-lora-qlora](../07-ml/03-lora-qlora/README.md) |
| - | 여러 번 검색 | 검색 여부·횟수를 LLM이 결정 | 어려운 질문의 Recall, Correctness | 높음 (지연) | [05-agents/01-agentic-rag](../05-agents/01-agentic-rag/README.md) |

- 생성 쪽 레버는 검색이 맞았는데 답이 틀린 질문(Recall 성공 + Correctness 실패)에서만 효과가 있다. oracle 컨텍스트 점수가 높으면 생성 쪽 여지가 작다([03-evals/02-generation-metrics](../03-evals/02-generation-metrics/README.md) "검색 평가와 분리하기").

## 5. 시도 순서

기본 원칙은 **싸고, 재색인이 필요 없고, 되돌리기 쉬운 것부터**다. 다만 실패 유형(F1~F10) 분포가 순서를 바꿀 수 있다.

| 순서 | 레버 | 이유 |
| --- | --- | --- |
| 1 | 실패 유형 분류 ([02-failure-modes](../02-retrieval-basics/04-naive-rag/02-failure-modes.md)) | 가장 많은 유형에 맞는 레버를 고르기 위해. 레버가 아니라 방향 잡기 |
| 2 | 프롬프트, 컨텍스트 조립 (L10, L11) | 생성 문제(F8~F10)가 많으면 가장 싸고 빠름 |
| 3 | 결과 합치기, 후보 수 (L7, L8) | 색인 그대로, 설정값만 바꿈 |
| 4 | 리랭커 (L9) | 색인 그대로. 지연이 늘어나는 것만 확인 |
| 5 | 필터·라우팅, 질의 변환 (L6) | 색인 그대로. LLM 호출 비용이 생김 |
| 6 | 토큰화, BM25 설정, 임베딩 입력 구성 (L3, L4) | 재색인 필요하지만 모델은 그대로 |
| 7 | 청킹, 파싱 (L1, L2) | 재색인 필요. 골든셋 판정 단위와의 매핑도 확인 |
| 8 | 임베딩 모델 교체 (L4) | 재색인 필요, 문서 전체 재인코딩 |
| 9 | 파인튜닝, 그래프·요약 트리 | 데이터 준비와 색인 비용이 큼. 앞 단계로 부족할 때만 |

- 1차 검색에서 정답을 못 가져오면(Recall@50도 낮음) 리랭커는 효과가 없다. 이때는 3·4번을 건너뛰고 6~8번으로 간다.
- 반대로 Recall@50은 높은데 Recall@5가 낮으면(F3) 리랭커가 가장 효과가 크다.

## 6. 실험 규칙

| 규칙 | 이유 |
| --- | --- |
| **레버는 한 번에 하나씩** 바꾼다 | 두 개를 같이 바꾸면 어느 쪽 효과인지 알 수 없다 |
| 비교는 **dev 세트**에서만 한다 | test 세트로 조정하면 기준선이 부풀려진다 ([03-golden-set/04-update-loop](../03-evals/03-golden-set/04-update-loop.md) 5장) |
| 청크 크기가 바뀌면 **같은 토큰 예산**으로 비교한다 | 큰 청크는 같은 k에서 내용이 많아 유리하다 |
| 생성 쪽은 **여러 번 실행**해 흔들림부터 잰다 | 차이가 흔들림보다 작으면 결론을 내지 않는다 |
| **유형별로 나눠** 본다 (말투, 답변 유형, 난이도) | 평균은 그대로인데 한 유형만 나빠지는 변경이 있다 |
| **질의별 변화**를 본다 (새로 맞은 질문, 새로 틀린 질문) | 평균에 가려진 회귀를 찾는다 |
| 품질과 함께 **비용·지연**을 기록한다 | Recall 1%p를 위해 지연이 2배가 되면 판단이 달라진다 |
| 설정 전체(모델 버전, 파라미터, 골든셋 버전)를 결과와 함께 남긴다 | 나중에 같은 결과를 재현하기 위해 |

## 7. 확인할 점

- 레버마다 효과가 있는 실패 유형이 다르다. 실패 유형 분포를 보지 않고 "좋다는 기법"부터 넣으면 비용만 늘고 지표는 그대로일 수 있다.
- 골든셋 점수만 오르고 실제 사용자 질문에서는 그대로일 수 있다(골든셋 과적합). 운영 지표와 함께 본다([06-llmops/04-feedback-loop](../06-llmops/04-feedback-loop/README.md)).
- 채택한 레버 설정은 해당 주제 README의 메인 결정에 반영하고, 회귀 테스트 기준선을 다시 잡는다([03-evals/05-regression-ci](../03-evals/05-regression-ci/README.md)).
