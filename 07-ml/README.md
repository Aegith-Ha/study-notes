# ML 심화 (Machine Learning)

우선순위: 5순위

평가 체계를 갖춘 뒤 모델 자체를 다룬다.

## Topics

| Topic | 내용 | 상태 |
| --- | --- | --- |
| [01-pytorch-hf](./01-pytorch-hf/README.md) | PyTorch, Hugging Face 실습 | 초안 |
| [02-embedding-finetuning](./02-embedding-finetuning/README.md) | 임베딩 모델 / 리랭커 도메인 파인튜닝 (sentence-transformers) | 초안 |
| [03-lora-qlora](./03-lora-qlora/README.md) | LoRA / QLoRA | 초안 |
| [04-vllm-serving](./04-vllm-serving/README.md) | vLLM으로 오픈소스 LLM 서빙 | 초안 |

## 무엇을 바꾸나

| 주제 | 바꾸는 것 | 효과를 재는 곳 | 먼저 확인할 것 |
| --- | --- | --- | --- |
| [02-embedding-finetuning](./02-embedding-finetuning/README.md) | 검색 모델 (임베딩, 리랭커) | [03-evals/01-retrieval-metrics](../03-evals/01-retrieval-metrics/README.md) | 기성 모델 + 하이브리드 + 리랭커로 부족한가 |
| [03-lora-qlora](./03-lora-qlora/README.md) | 생성 모델의 행동 (형식, 거절, 문체) | [03-evals/02-generation-metrics](../03-evals/02-generation-metrics/README.md) | 프롬프트 개선으로 부족한가 |
| [04-vllm-serving](./04-vllm-serving/README.md) | 모델을 돌리는 방식 (자체 서빙) | 지연·처리량·비용 + 회귀 테스트 | 데이터 반출 제약, 요청량 |

- 모델을 바꾸는 작업은 앞 섹션의 방법(프롬프트, 검색 개선)보다 비싸고 되돌리기 어렵다. 평가 체계([03-evals](../03-evals/README.md))로 남은 문제가 무엇인지 확인한 뒤 시작한다.
- 학습 데이터와 골든셋은 반드시 분리한다. 섞이면 점수만 오르고 실제 성능은 그대로다.

노트 작성 방식은 루트 [README](../README.md)의 작성 규칙 참고.
