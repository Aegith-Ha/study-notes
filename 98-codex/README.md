# Codex 프로젝트 세팅 #1

Codex를 프로젝트에 투입할 때 가장 중요한 건 **프로젝트 구조와 규칙을 AI에게 명확하게 알려주는 것**이다.

초기에 몇 개의 파일만 만들어두면 불필요한 코드 탐색이 줄어들고, 실수로 운영 환경을 건드리는 위험도 크게 줄어든다.

---

# 1. AGENTS.md 만들기

프로젝트 루트에 `AGENTS.md`를 생성한다.

```text
project/
├── AGENTS.md
├── app/
├── docs/
└── scripts/
```

Codex는 작업을 시작할 때 이 파일을 가장 먼저 참고한다.

즉,

- 프로젝트 구조 설명
- 개발 규칙
- 참조 문서 위치
- 금지사항

등을 미리 적어두면 이후 작업 품질이 좋아진다.

---

## 디렉토리별 AGENTS.md

프로젝트가 커지면 하위 디렉토리에도 별도로 둘 수 있다.

```text
project/
├── AGENTS.md
├── app/
│   ├── AGENTS.md
│   └── rag/
│       └── AGENTS.md
```

예를 들어:

- 루트 AGENTS.md → 전체 프로젝트 규칙
- app/AGENTS.md → FastAPI 규칙
- rag/AGENTS.md → 검색 로직 규칙

처럼 세분화 가능하다.

프로젝트가 커질수록 효과가 크다.

---

# Project Docs

프로젝트 문서 위치를 알려준다.

```md
# Project Docs

When modifying retrieval code:
- Read docs/rag_pipeline.md

When modifying Milvus backup code:
- Read docs/milvus_backup.md

When modifying Tibero integration:
- Read docs/tibero.md

Before modifying configuration-related code:
- Read .env.example
```

### 왜 필요한가?

보통 AI는 프로젝트 전체를 뒤져가며 구조를 파악하려고 한다.

하지만 문서 위치를 알려주면:

- 불필요한 파일 탐색 감소
- 토큰 절약
- 코드 수정 정확도 향상

효과가 있다.

특히 RAG 프로젝트는 구조가 복잡하기 때문에 거의 필수라고 생각한다.

---

# Dangerous Operations

AI가 하면 안 되는 작업을 명시한다.

```md
## Dangerous Operations

- Never run utility.drop_collection() unless explicitly requested.
- Never execute DROP TABLE statements.
- Never delete Milvus data directories.
- Never modify production Docker Compose files without confirmation.
- Never hardcode credentials.
```

### 왜 필요한가?

AI는 문제를 해결하려고 과감한 선택을 하는 경우가 있다.

예를 들면:

```python
utility.drop_collection("my_collection")
```

같은 코드를 아무 생각 없이 제안할 수도 있다.

미리 금지사항을 적어두면:

- 데이터 삭제 방지
- 운영 서버 사고 방지
- 보안 사고 방지

효과가 있다.

운영 환경이 있다면 반드시 작성하는 것을 추천한다.

---

# 2. 실행 스크립트 준비

```text
scripts/
├── run_api.sh
├── run_batch.sh
├── backup_milvus.sh
└── restore_milvus.sh
```

예시:

```bash
#!/bin/bash

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000
```

### 왜 필요한가?

AI는 프로젝트 실행 방법을 알아야 한다.

스크립트가 없으면:

```bash
python main.py
```

또는

```bash
uvicorn app.main:app
```

등을 추측하게 된다.

실행 스크립트를 제공하면:

- 실행 방법 통일
- 환경 차이 감소
- Codex 작업 정확도 향상

효과가 있다.

---

# 3. .env.example 만들기

```env
MILVUS_HOST=localhost
MILVUS_PORT=19530

TIBERO_HOST=localhost
TIBERO_PORT=8629
TIBERO_SID=tibero

TIBERO_JDBC_PATH=app/lib/tibero7-jdbc.jar
```

### 왜 필요한가?

AI가 설정값을 찾기 위해 프로젝트를 뒤지는 경우가 많다.

`.env.example` 하나만 있어도:

- 환경변수 이름 확인 가능
- 신규 개발자 온보딩 쉬움
- 배포 실수 감소

효과가 있다.

---

## 실제 .env는 커밋 금지

```gitignore
.env
```

실제 계정 정보는 넣지 말고

```env
TIBERO_USER=your_username
TIBERO_PASSWORD=your_password
```

형태로 예시만 제공하는 것이 좋다.

---

# 4. Architecture Diagram

간단한 구조도라도 만들어 둔다.

```text
User Query
  ↓
BM25 Search
  ↓
Dense Search
  ↓
Rerank
  ↓
LLM Verify
```

또는

```text
User
 ↓
FastAPI
 ↓
Retriever
 ├─ BM25
 └─ Milvus
 ↓
Reranker
 ↓
LLM
 ↓
Response
```

### 왜 필요한가?

AI는 구조를 이해해야 좋은 수정을 할 수 있다.

특히 RAG 프로젝트에서는:

- 검색 흐름
- 벡터 검색 위치
- 리랭킹 위치
- LLM 호출 위치

를 빠르게 파악할 수 있다.

---

# docs 문서 추천

```text
docs/
├── architecture.md
├── rag_pipeline.md
├── milvus_backup.md
└── tibero.md
```

## architecture.md

전체 시스템 구조

- API 흐름
- Batch 흐름
- Docker 구성

---

## rag_pipeline.md

검색 로직 설명

- Query Rewrite
- BM25
- Dense Search
- Hybrid Search
- Rerank
- Prompt 생성

---

## milvus_backup.md

운영 시 매우 중요

- 백업 생성
- 복구 방법
- cron 설정
- 장애 대응

---

## tibero.md

신규 개발자가 가장 어려워하는 부분

- JDBC 연결
- 계정 생성
- 테이블스페이스
- Import / Export

정도는 적어두는 것이 좋다.

---

# 최종 추천 구조

```text
project/
│
├── AGENTS.md
├── .env.example
│
├── docs/
│   ├── architecture.md
│   ├── rag_pipeline.md
│   ├── milvus_backup.md
│   └── tibero.md
│
├── scripts/
│   ├── run_api.sh
│   ├── run_batch.sh
│   ├── backup_milvus.sh
│   └── restore_milvus.sh
│
├── app/
│   ├── AGENTS.md
│   ├── routers/
│   ├── rag/
│   ├── core/
│   └── batch/
```

---

# 정리

Codex를 잘 쓰는 핵심은 좋은 프롬프트보다 **좋은 프로젝트 문서화**에 가깝다.

최소한 아래 4개만 준비해도 작업 품질이 크게 좋아진다.

1. AGENTS.md
2. 실행 스크립트
3. .env.example
4. docs 문서

특히 운영 환경(Milvus, Tibero, Docker)을 다루는 프로젝트라면 금지사항(Dangerous Operations)은 거의 필수라고 생각한다.