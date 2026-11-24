# PyTorch와 Hugging Face 기초 (PyTorch, Hugging Face)

이후 주제(임베딩 파인튜닝, LoRA, 서빙)에 필요한 PyTorch 학습 루프와 Hugging Face 생태계(transformers, datasets, Hub)의 기본을 정리한다. 이 README에는 메인 결정과 실습 기록을 두고, 개념은 하위 노트에 둔다.

- 임베딩 모델을 쓰는 쪽의 기초는 [02-retrieval-basics/02-dense-retrieval](../../02-retrieval-basics/02-dense-retrieval/README.md) 참고

## 하위 노트

- [01-pytorch-basics](./01-pytorch-basics.md): 텐서, 자동 미분, 학습 루프, device와 dtype, GPU 메모리 계산 손계산 예시
- [02-huggingface](./02-huggingface.md): transformers(Auto 클래스, 토크나이저), datasets, Hub와 모델 카드·라이선스, 재현성

## 메인 결정 (초안)

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 학습 방식 | 직접 짠 학습 루프 1회 실습 후 라이브러리 Trainer 사용 | 원리를 알고 나서 편의 도구 |
| 기본 dtype | 학습은 bf16 혼합 정밀도, 지원 안 되는 GPU는 fp16 | 메모리 절반, fp16보다 수치 안정 |
| 모델 출처 | Hub 모델은 버전(커밋 해시) 고정, 모델 카드의 라이선스 확인 | 재현성, 상업적 사용 조건 |
| 재현성 | 시드, 라이브러리 버전, 데이터 버전 기록 | 결과 비교 가능 |
| 메모리 계획 | 학습 전 파라미터 수로 필요 메모리를 계산 | 실행 후 OOM 반복 방지 |

## 실험 조건

| 항목 | 값 |
| --- | --- |
| 프로젝트 / 커밋 | - |
| GPU / 메모리, CUDA 버전 | - |
| torch, transformers, datasets 버전 | - |

## 결과

### 실습 기록

| 실습 | 모델 / 데이터 | 결과 | 메모 |
| --- | --- | --- | --- |
| 직접 짠 학습 루프 (분류) | - | - | - |
| Trainer로 같은 작업 | - | - | - |
| 임베딩 추출과 코사인 유사도 | - | - | - |

### 메모리 계산 vs 실측

| 모델 / 설정 | 계산값 | 실측 최대 메모리 | 차이 원인 |
| --- | --- | --- | --- |
| - | - | - | - |

## 관련 코드

- 실습 코드: - (프로젝트 등록 후 [99-projects](../../99-projects/README.md)를 거쳐 링크)
- 실행 방법은 연결된 프로젝트 README 참고
