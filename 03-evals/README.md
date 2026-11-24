# 평가 체계 (Evals)

우선순위: 1순위

검색 평가와 생성 평가를 분리하고, 골든셋·LLM judge·회귀 테스트까지 평가 체계를 갖춘다.

## Topics

| Topic | 내용 | 상태 |
| --- | --- | --- |
| [01-retrieval-metrics](./01-retrieval-metrics/README.md) | 검색 평가 지표: Recall@k, MRR, NDCG | 초안 |
| [02-generation-metrics](./02-generation-metrics/README.md) | 생성 평가 지표: 정확성, 답변 관련성 | 초안 |
| [03-golden-set](./03-golden-set/README.md) | 골든셋 50~200개 구축 (정답 + 근거 문서). 해석례·상황 시나리오로 시작, 실제 사용자 로그로 확대 | 진행 중 |
| [04-llm-judge](./04-llm-judge/README.md) | LLM-as-judge 채점 기준(rubric) 설계, 사람 판단과의 일치도 검증 | 초안 |
| [05-regression-ci](./05-regression-ci/README.md) | 배포 전 평가셋 자동 실행, CI 회귀 테스트 연결 | 초안 |

## 지표 분류: 두 축

평가 지표는 서로 독립인 두 축으로 나눈다. 폴더(`01`, `02`)는 첫 번째 축, 각 폴더 안의 파일(`01-reference-based`, `02-reference-free`)은 두 번째 축이다.

| 축 | 나누는 기준 | 답하는 질문 |
| --- | --- | --- |
| 단계 (폴더) | 무엇을 채점하는가: 검색 결과(문서 목록) / 답변 | **어디서** 잘못됐나 → 고칠 위치 |
| 기준 (파일) | 무엇과 비교하는가: 미리 만든 정답 / 정답 없이 judge 판단 | **얼마나 믿을 수 있나, 어디까지 잴 수 있나** → 신뢰도와 적용 범위 |

| | **정답 기반** (정답과 비교) | **정답 없음** (judge가 그 자리에서 판단) |
| --- | --- | --- |
| **검색** (문서 목록 채점) | [Recall@k, MRR, nDCG](./01-retrieval-metrics/01-reference-based.md)<br>정답 문서를 가져왔나 | [Context Relevance, Sufficiency](./01-retrieval-metrics/02-reference-free.md)<br>가져온 문서가 질문과 관련 있어 보이나 |
| **생성** (답변 채점) | [Answer Correctness, EM, Citation Recall](./02-generation-metrics/01-reference-based.md)<br>정답과 같은 답인가 | [Faithfulness, Answer Relevance](./02-generation-metrics/02-reference-free.md)<br>가져온 문서에 충실한가, 질문에 맞게 답했나 |

- 네 칸은 서로 대신하지 않는다. 한 축의 지표만으로는 다른 축의 질문에 답할 수 없다.
- 헷갈리는 지표는 **채점되는 대상**으로 구분한다. Faithfulness, Citation은 검색 결과나 근거 문서를 보지만 점수가 매겨지는 것은 답변이므로 생성 지표다.
- 정답 없는 생성 지표는 검색 결과를 임시 기준으로 쓴다. 그래서 검색이 틀리면 충실한 오답이 만점을 받는다.

### 시스템 유형별로 쓰는 지표

단계 축은 시스템 유형이 아니라 **평가하는 결과물 유형**으로 나눈다. 검색 지표는 "찾기"를, 생성 지표는 "쓰기"를 평가한다. 하나의 시스템에 두 결과물이 모두 있을 수 있다.

| 시스템 | 결과물 | 쓰는 지표 |
| --- | --- | --- |
| 검색 서비스 (문서 목록만 보여 줌) | 문서 목록 | **검색만** |
| RAG (찾아서 답변 생성) | 문서 목록 + 답변 | **검색 + 생성 둘 다** |
| LLM 단독 (검색 없이 답변) | 답변 | **생성만** (Faithfulness처럼 컨텍스트가 필요한 지표는 제외) |

- RAG는 생성형이지만 생성 지표만 쓰지 않는다. 검색 지표를 함께 봐야 답변이 틀렸을 때 원인이 검색인지 생성인지 나눌 수 있다.
- 중간에 LLM(쿼리 재작성, 리랭킹)을 써도 최종 결과물이 문서 목록이면 검색 서비스로 본다. 결과를 사람이 읽는지 LLM이 읽는지에 따라 기준 지표가 달라진다 ([01-reference-based](./01-retrieval-metrics/01-reference-based.md) 3.1 참고).

### 두 지표를 함께 읽는 법

| 함께 보는 두 지표 | 같은 축 | 다른 축 | 의미 | 확인할 곳 |
| --- | --- | --- | --- | --- |
| 검색 정답 기반 Precision 낮음 / 검색 정답 없음 Context Relevance 높음 | 단계 (검색) | 기준 | 골든셋 누락 또는 judge가 관대함 | 골든셋, judge |
| 생성 정답 없음 Faithfulness 높음 / 생성 정답 기반 Correctness 낮음 | 단계 (생성) | 기준 | 충실한 오답. 정답 없는 지표의 구조적 한계 | 검색 Recall로 원인 확인 |
| 검색 정답 기반 Recall 높음 / 생성 정답 기반 Correctness 낮음 | 기준 (정답 기반) | 단계 | 근거를 받고도 틀림 | 프롬프트, 생성 모델 |
| 검색 정답 기반 Recall 낮음 / 생성 정답 기반 Correctness 낮음 | 기준 (정답 기반) | 단계 | 근거를 못 가져옴 | 검색기, 필터, 청킹 |

- 기준 축이 엇갈리면 **평가 도구**(골든셋, judge)를 먼저 의심하고, 단계 축이 엇갈리면 **시스템**(검색기, 생성기)을 의심한다.
- 질의별 원인 나누기 표는 [02-generation-metrics](./02-generation-metrics/README.md)의 "검색 평가와 분리하기" 참고

노트 작성 방식은 루트 [README](../README.md)의 작성 규칙 참고.
