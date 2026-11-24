# Hugging Face 생태계 (Hugging Face)

모델을 불러오고, 데이터를 다루고, 결과를 재현하는 데 쓰는 Hugging Face 도구(transformers, tokenizers, datasets, Hub)를 정리한다.

- 폴더 요약과 메인 결정은 [README](./README.md) 참고
- PyTorch 기초는 [01-pytorch-basics](./01-pytorch-basics.md) 참고

## 1. 구성 요소

| 라이브러리 | 하는 일 | 이 저장소에서 쓰는 곳 |
| --- | --- | --- |
| transformers | 모델 구조와 가중치 로드, 생성, Trainer | LoRA 학습, 리랭커 |
| tokenizers | 문장을 토큰 ID로 변환 | 모든 모델 |
| datasets | 데이터 로드·변환·분할, 캐시 | 학습 데이터 준비 |
| sentence-transformers | 임베딩·크로스 인코더 학습과 추론 | [02-embedding-finetuning](../02-embedding-finetuning/README.md) |
| peft | LoRA 등 효율적 파인튜닝 | [03-lora-qlora](../03-lora-qlora/README.md) |
| Hub | 모델·데이터 저장소, 모델 카드 | 모델 선택 |

## 2. 모델 불러오기

| 클래스 | 용도 |
| --- | --- |
| AutoTokenizer | 모델에 맞는 토크나이저 |
| AutoModel | 본체만 (임베딩 추출) |
| AutoModelForCausalLM | 다음 토큰 생성 (LLM) |
| AutoModelForSequenceClassification | 분류, 크로스 인코더 리랭커 |

- 모델과 토크나이저는 **같은 이름·버전**으로 불러온다. 다른 토크나이저를 쓰면 오류 없이 결과만 나빠진다.
- 최대 길이를 넘는 입력은 잘린다. 긴 조문이 잘리는지 토큰 수를 확인한다([02-retrieval-basics/02-dense-retrieval/02-model-selection](../../02-retrieval-basics/02-dense-retrieval/02-model-selection.md)).
- 생성 모델은 대화 템플릿(chat template)을 모델 것으로 적용한다. 틀린 템플릿은 품질을 크게 떨어뜨린다.

## 3. 한국어 토큰화

| 확인 | 이유 |
| --- | --- |
| 같은 문장의 토큰 수 | 한국어를 잘게 쪼개는 모델은 같은 길이 제한에 더 적은 내용이 들어감, 비용 증가 |
| 법령 용어 분해 | "근로기준법" 같은 단어가 어떻게 나뉘는지 |

- sparse 검색의 형태소 분석과는 다른 문제다. 여기는 모델 입력 단위다([02-retrieval-basics/01-sparse-retrieval](../../02-retrieval-basics/01-sparse-retrieval/README.md)와 비교).

## 4. Hub와 모델 카드

| 확인할 것 | 이유 |
| --- | --- |
| 라이선스 | 상업적 사용, 파생 모델 배포 조건 |
| 학습 데이터 | 평가 데이터가 학습에 들어갔을 가능성 |
| 최대 길이, 권장 사용법 | 질의 접두어("query: ") 같은 사용 규칙 |
| 리비전(커밋 해시) | 같은 이름 모델이 갱신될 수 있음 |

- 결과를 기록할 때 모델 이름과 함께 리비전을 남긴다.

## 5. 재현성

| 기록 | 예 |
| --- | --- |
| 라이브러리 버전 | torch, transformers, datasets |
| 모델 리비전 | Hub 커밋 해시 |
| 데이터 버전 | 학습 데이터 파일 해시, 골든셋 버전 |
| 시드, 하이퍼파라미터 | 학습률, 배치, 에폭 |

## 6. 확인할 점

- datasets 캐시는 원본이 바뀌어도 남아 있을 수 있다. 데이터를 바꿨는데 결과가 같으면 캐시를 의심한다.
- 모델을 처음 받을 때 용량이 크다. 저장 위치와 디스크 여유를 확인한다.
