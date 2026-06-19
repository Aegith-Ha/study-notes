# Pydantic 실행 예시

이 폴더는 Pydantic으로 입력 데이터를 검증하고 변환하는 예제 코드가 있다.

## 주요 파일

- `example.py`: `BaseModel`, `Field`, `EmailStr`, validator, 중첩 모델, `model_dump()` 예제
- `README_VELOG.md`: Velog 게시용 개념 정리 글

## conda 환경 준비

repo 루트(`/home/test0000/study-notes`)에서 실행한다.

```bash
conda env create -f environment.yml
conda activate study-py312
```

이미 환경이 만들어져 있으면 activate만 하면 된다.

```bash
conda activate study-py312
```

## 기본 실행

```bash
python 01-python/pydantic/example.py
```

이 예제는 정상 데이터 검증과 실패 데이터 검증을 한 번에 보여준다.

출력에서 아래 두 구간이 보이면 정상 실행된 것이다.

```text
=== 검증 성공 ===
user_id: 1
name: Kim
email: kim@example.com
age: 29
role: admin
is_active: True
city: Seoul
display_name: Kim (admin)
```

```text
=== 검증 실패 ===
1. 위치: ('id',)
   메시지: Input should be greater than or equal to 1
   에러 타입: greater_than_equal
```

`created_at` 값은 실행 시점마다 달라진다.

## 패키지만 직접 설치해서 실행

conda 환경을 쓰지 않고 현재 Python 환경에 직접 설치하려면 아래처럼 설치한다.

```bash
python3 -m pip install "pydantic[email]"
python3 01-python/pydantic/example.py
```

`EmailStr`을 사용하므로 `pydantic`만 설치하면 부족할 수 있다. 이메일 검증에 필요한 `email-validator`까지 함께 설치되는 `"pydantic[email]"` 형태를 사용한다.
