# 문서 파싱 (Document Parsing)

PDF·스캔본·표·이미지에서 검색과 생성이 쓸 수 있는 텍스트를 정확히 뽑는 방법을 정리한다. 기본 RAG 실패 유형 중 F7(파싱 손실)을 고친다. 파싱에서 잃은 정보는 뒤의 어떤 기법으로도 되살릴 수 없다. 이 README에는 기본 선택과 이유를 두고, 방법 설명은 하위 노트에 둔다.

- 청킹은 [04-chunking](../04-chunking/README.md), 지표는 [03-evals](../../03-evals/README.md) 참고

## 하위 노트

- [01-pdf-layout](./01-pdf-layout.md): 자주 생기는 문제(읽기 순서, 머리말, 줄바꿈, 스캔), 도구 유형, 파싱 품질 재기
- [02-tables-images](./02-tables-images.md): 표가 어려운 이유, 표 변환 방법(마크다운, 행 단위 문장, 요약), 이미지 처리, 평가

## 기본 선택과 이유

| 항목 | 결정 | 이유 |
| --- | --- | --- |
| 원문 구조가 있는 문서 | 구조화된 원문(API, XML 등) 우선, PDF 파싱은 부록·서식·첨부에만 | 원문 구조가 있으면 파싱 오류가 없음 |
| PDF 파싱 | 텍스트 레이어 추출 기준선 vs 레이아웃 분석 비교 | 다단·표 문서에서 차이 확인 |
| 스캔본 | OCR, 글자 오류율 표본 측정 | 텍스트 0 방지 |
| 표 | 표 요약 + 행 단위 문장으로 검색, 원본 마크다운 표를 LLM에 전달 | 검색과 생성에 좋은 형태가 다름 |
| 이미지 | 도식만 멀티모달 LLM 설명, 표본 확인 | 비용 대비 효과 |
| 평가 | 근거 형식(본문 / 부록 / 첨부 / 스캔)별 Recall@5, 표 질문 EM | 파싱 문제는 평균에 묻힘 |

## 관련 코드

- lawlens ([99-projects/01-lawlens](../../99-projects/01-lawlens.md)): 법령 본문 파싱 [`statute.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/parsing/statute.py), 텍스트 정리 [`text.py`](https://github.com/Aegith-Ha/LawLens/blob/main/src/lawlens/parsing/text.py)
  - 입력이 API의 구조화된 응답이라 PDF·OCR·표 변환은 해당 없음
- 실행 방법은 연결된 프로젝트 README 참고
