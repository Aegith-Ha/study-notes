# Pydantic이란?

> Python 타입 힌트를 기준으로 데이터를 검증하고 변환해주는 라이브러리

API 요청 데이터, 설정값, JSON 응답, DB에서 읽어온 데이터처럼 외부에서 들어오는 값은 항상 믿을 수 없다.
Pydantic을 사용하면 이런 데이터를 Python 객체로 다루기 전에 타입, 필수값, 범위, 형식 등을 먼저 검증할 수 있다.

이 예제는 Pydantic v2 문법을 기준으로 작성했다.


---

## 예제 코드

```python
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationError, computed_field, field_validator, model_validator


class Address(BaseModel):
    """사용자의 주소 정보를 표현하는 중첩 모델입니다."""

    # Field(...)에서 ...은 "필수값"이라는 뜻입니다.
    # 즉, city 값이 없으면 Pydantic이 ValidationError를 발생시킵니다.
    city: str = Field(..., min_length=2, description="도시 이름")

    # 문자열 길이를 제한하면 너무 짧거나 긴 값이 들어오는 것을 막을 수 있습니다.
    # 예: "12345"는 통과하지만, "1"은 min_length 조건 때문에 실패합니다.
    zip_code: str = Field(..., min_length=5, max_length=10, description="우편번호")


class User(BaseModel):
    """회원 가입 요청 데이터를 검증하기 위한 Pydantic 모델입니다."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    user_id: int = Field(..., alias="id", ge=1, description="사용자 고유 ID")
    name: str = Field(..., min_length=2, max_length=30)
    email: EmailStr
    age: int = Field(default=20, ge=0, le=120)
    role: Literal["user", "admin"] = "user"
    is_active: bool = True
    address: Address
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name은 공백만 입력할 수 없습니다.")
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

    @model_validator(mode="after")
    def admin_must_be_adult(self) -> "User":
        if self.role == "admin" and self.age < 18:
            raise ValueError("admin role은 18세 이상만 사용할 수 있습니다.")
        return self

    @computed_field
    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.role})"
```

전체 코드는 [`example.py`](./example.py)에 있다.

---

## 핵심 개념

## 1) `BaseModel`

Pydantic 모델은 보통 `BaseModel`을 상속해서 만든다.

```python
class Address(BaseModel):
    city: str
    zip_code: str
```

이렇게 작성하면 `city`, `zip_code`를 가진 데이터 구조가 만들어지고, 값을 넣을 때 타입 검증이 수행된다.

---

## 2) 타입 힌트 기반 검증

```python
age: int
is_active: bool
```

Pydantic은 타입 힌트를 보고 값을 검증한다.
가능한 경우에는 타입 변환도 수행한다.

예를 들어 `"29"`는 `int`로 변환 가능하므로 `29`가 되고, `"true"`는 `bool` 값인 `True`로 변환될 수 있다.

`is_active`처럼 `bool` 타입으로 선언한 필드는 문자열로 `"true"` 또는 `"false"`가 들어와도 가능한 경우 bool 값으로 변환된다.

```python
User.model_validate({
    "id": 1,
    "name": "Kim",
    "email": "kim@example.com",
    "is_active": "true",
    "address": {
        "city": "Seoul",
        "zip_code": "04524",
    },
})
```

위처럼 `"true"`가 들어오면 `is_active`는 `True`가 된다.  
즉, 활성 상태인 사용자로 해석된다.

반대로 `"false"`가 들어오면 `False`로 변환된다.

```python
User.model_validate({
    "id": 1,
    "name": "Kim",
    "email": "kim@example.com",
    "is_active": "false",
    "address": {
        "city": "Seoul",
        "zip_code": "04524",
    },
})
```

이 경우 `is_active`는 `False`가 된다.  
즉, 비활성 상태인 사용자로 해석된다.

중요한 점은 `"true"`와 `"false"` 모두 문자열이지만, `bool` 타입으로 변환 가능한 값이기 때문에 검증 실패가 아니라 정상 데이터로 처리된다는 것이다.

---

## 3) `Field`

`Field`는 필드에 세부 검증 조건이나 메타데이터를 추가할 때 사용한다.

```python
age: int = Field(default=20, ge=0, le=120)
```

위 코드는 다음 의미를 가진다.

- 값이 없으면 기본값 `20`을 사용한다.
- `ge=0`이므로 0 이상이어야 한다.
- `le=120`이므로 120 이하여야 한다.

문자열에는 `min_length`, `max_length` 같은 조건을 자주 사용한다.

```python
name: str = Field(..., min_length=2, max_length=30)
```

---

## 4) 필수값과 기본값

```python
city: str = Field(...)
age: int = Field(default=20)
```

`Field(...)`처럼 `...`을 넣으면 필수값이라는 뜻이다.
반대로 `default=20`처럼 기본값을 주면 입력 데이터에 해당 필드가 없어도 모델을 만들 수 있다.

---

## 5) 중첩 모델

```python
class User(BaseModel):
    address: Address
```

모델 안에 다른 모델을 필드로 넣을 수 있다.
이 경우 `address` 내부의 `city`, `zip_code`도 함께 검증된다.

```python
User.model_validate({
    "id": 1,
    "name": "Kim",
    "email": "kim@example.com",
    "address": {
        "city": "Seoul",
        "zip_code": "04524",
    },
})
```

---

## 6) `Literal`

`Literal`은 허용할 값을 고정할 때 사용한다.

```python
role: Literal["user", "admin"] = "user"
```

위 코드는 `role`에 `"user"` 또는 `"admin"`만 들어올 수 있다는 의미다.
`"manager"` 같은 값은 검증에 실패한다.

---

## 7) `field_validator`

`field_validator`는 특정 필드에 대한 사용자 정의 검증 로직을 작성할 때 사용한다.

```python
@field_validator("name")
@classmethod
def name_must_not_be_blank(cls, value: str) -> str:
    if not value.strip():
        raise ValueError("name은 공백만 입력할 수 없습니다.")
    return value.strip()
```

`Field(min_length=2)`는 문자열 길이를 검사하지만, `"  "`처럼 공백만 있는 값까지 막지는 못한다.
이런 경우 validator를 사용해서 직접 규칙을 추가할 수 있다.

---

## 8) `model_validator`

`model_validator`는 여러 필드를 함께 보고 검증해야 할 때 사용한다.

```python
@model_validator(mode="after")
def admin_must_be_adult(self) -> "User":
    if self.role == "admin" and self.age < 18:
        raise ValueError("admin role은 18세 이상만 사용할 수 있습니다.")
    return self
```

예제에서는 `role`이 `"admin"`이면 `age`가 18 이상이어야 한다는 규칙을 넣었다.
이런 규칙은 한 필드만 보고 판단할 수 없기 때문에 `model_validator`가 적합하다.

---

## 9) `computed_field`

`computed_field`는 저장된 값이 아니라 계산된 값을 출력 필드처럼 제공할 때 사용한다.

```python
@computed_field
@property
def display_name(self) -> str:
    return f"{self.name} ({self.role})"
```

`display_name`은 입력 데이터로 받지 않아도, 모델의 다른 필드를 이용해서 계산된다.

---

## 10) `model_validate`

`model_validate`는 dict 같은 외부 데이터를 Pydantic 모델로 검증하고 변환한다.

```python
user = User.model_validate(raw_user)
```

검증에 성공하면 `User` 객체가 반환된다.
검증에 실패하면 `ValidationError`가 발생한다.

---

## 11) `ValidationError`

검증 실패 시에는 `ValidationError`가 발생한다.
예제에서는 `error.errors()`를 사용해서 에러 정보를 하나씩 출력한다.

```python
try:
    User.model_validate(invalid_user)
except ValidationError as error:
    for detail in error.errors():
        print(detail["loc"], detail["msg"], detail["type"])
```

`errors()`의 각 항목에는 보통 다음 정보가 들어 있다.

- `loc`: 어떤 필드에서 문제가 생겼는지
- `msg`: 사람이 읽을 수 있는 에러 메시지
- `type`: Pydantic 내부 에러 타입

---

## 12) `model_dump`, `model_dump_json`

Pydantic 모델을 다시 dict나 JSON 문자열로 바꿀 수 있다.

```python
user.model_dump(by_alias=True)
user.model_dump_json(by_alias=True, indent=2)
```

`by_alias=True`를 사용하면 `user_id` 대신 alias인 `id`로 출력된다.
외부 API 응답 형식을 맞출 때 유용하다.

---

## 예상 출력

실행하면 먼저 정상 데이터의 변환 결과가 출력되고, 그 다음 잘못된 데이터의 검증 에러가 출력된다.

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

=== dict로 변환 ===
...

=== JSON 문자열로 변환 ===
...

=== 검증 실패 ===
1. 위치: ('id',)
   메시지: Input should be greater than or equal to 1
   에러 타입: greater_than_equal
...
```

---

## 정리

Pydantic은 외부 데이터를 안전하게 다루기 위한 검증 도구다.
특히 FastAPI 같은 웹 프레임워크에서 요청 body, 응답 schema, 설정값 검증에 자주 사용된다.

이 예제에서 다룬 내용은 다음과 같다.

- `BaseModel`로 데이터 모델 정의
- 타입 힌트 기반 검증과 자동 변환
- `Field`로 필수값, 기본값, 범위 지정
- 중첩 모델 검증
- `Literal`로 선택지 제한
- `field_validator`, `model_validator`로 사용자 정의 검증
- `computed_field`로 계산 필드 만들기
- `ValidationError` 처리
- `model_dump`, `model_dump_json`으로 dict/JSON 변환
