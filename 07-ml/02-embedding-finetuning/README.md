# 임베딩·리랭커 파인튜닝 (Embedding Fine-tuning)

기성 임베딩 모델과 리랭커가 특정 도메인에서 부족할 때 도메인 데이터로 파인튜닝하는 방법을 정리한다. 학습 데이터 만들기와 손실·평가를 하위 노트에 두고, 이 README에는 기본 선택과 이유를 둔다.

- 기성 모델 비교는 [02-retrieval-basics/02-dense-retrieval/03-model-selection](../../02-retrieval-basics/02-dense-retrieval/03-model-selection.md), 리랭커는 [04-advanced-rag/02-reranking](../../04-advanced-rag/02-reranking/README.md) 참고

## 하위 노트

- [01-training-data](./01-training-data.md): (질의, 관련 문서) 쌍 만들기, 하드 네거티브 채굴, 거짓 네거티브, 골든셋과의 분리
- [02-loss-and-evaluation](./02-loss-and-evaluation.md): 대조 손실과 배치 내 네거티브 손계산 예시, 리랭커 학습, 평가와 일반 성능 저하 확인

## 기본 선택과 이유

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 시작 조건 | 기성 모델 + 하이브리드 + 리랭커 후에도 검색 실패가 용어·표현 차이에서 남을 때 | 파인튜닝은 데이터·유지 비용이 큼 |
| 학습 데이터 | 문서에서 LLM으로 만든 합성 질문 + 사람 검토 표본 | 대량 확보, 품질 확인 |
| 골든셋 분리 | 골든셋 질문·유사 질문은 학습에서 제외, 문서 단위로도 분리 확인 | 평가 오염 방지 |
| 네거티브 | 배치 내 네거티브 + BM25·기성 모델로 채굴한 하드 네거티브 (상위 일부 제외) | 효과 크고, 거짓 네거티브 줄임 |
| 손실 | MultipleNegativesRankingLoss 계열 | 쌍 데이터만으로 학습 |
| 평가 | 골든셋 dev로 선택, test로 최종 1회 + 일반 한국어 검색 세트로 저하 확인 | 과적합·망각 확인 |
| 교체 비용 | 모델이 바뀌면 전체 문서 재색인 | 재색인 시간도 교체 비용으로 봄 |

## 관련 코드

- 학습 데이터 생성, 학습, 평가 스크립트: - (프로젝트 등록 후 [99-projects](../../99-projects/README.md)를 거쳐 링크)
- 실행 방법은 연결된 프로젝트 README 참고
- 참고 라이브러리: `sentence-transformers`, `FlagEmbedding`
