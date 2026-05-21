from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationError,
    computed_field,
    field_validator,
    model_validator,
)


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

    # ConfigDict는 모델 전체 설정을 정의할 때 사용합니다.
    model_config = ConfigDict(
        # extra="forbid"는 모델에 선언하지 않은 필드가 들어오면 에러를 발생시킵니다.
        # API 요청에서 오타나 예상하지 못한 값이 조용히 무시되는 일을 줄일 수 있습니다.
        extra="forbid",
        # populate_by_name=True는 alias가 있는 필드도 Python 필드명으로 값을 넣을 수 있게 합니다.
        # 아래 user_id 필드는 alias가 "id"지만, user_id=1 형태도 허용됩니다.
        populate_by_name=True,
    )

    # alias="id"를 지정하면 외부 데이터에서는 "id"라는 키를 사용하고,
    # Python 코드 안에서는 user_id라는 더 명확한 이름으로 접근할 수 있습니다.
    user_id: int = Field(..., alias="id", ge=1, description="사용자 고유 ID")

    # min_length와 max_length로 문자열 길이를 검증합니다.
    # 공백만 있는 이름은 아래 field_validator에서 추가로 막습니다.
    name: str = Field(..., min_length=2, max_length=30)

    # EmailStr은 이메일 형식을 검증하는 Pydantic 타입입니다.
    # 이 타입을 사용하려면 email-validator 패키지가 함께 설치되어 있어야 합니다.
    email: EmailStr

    # age는 선택값이 아니라 기본값이 있는 필드입니다.
    # 입력 데이터에 age가 없어도 기본값 20이 사용됩니다.
    age: int = Field(default=20, ge=0, le=120)

    # Literal을 사용하면 정해진 문자열 중 하나만 허용할 수 있습니다.
    # 여기서는 일반 회원(user) 또는 관리자(admin)만 허용합니다.
    role: Literal["user", "admin"] = "user"

    # bool 타입은 문자열 "true", "false" 같은 값도 가능한 범위에서 자동 변환합니다.
    # 예: "true" -> True
    is_active: bool = True

    # 중첩 모델을 사용하면 address 내부 구조까지 함께 검증됩니다.
    address: Address

    # default_factory는 객체가 생성되는 시점에 기본값을 계산합니다.
    # datetime.now()를 직접 넣으면 파일을 import한 시점의 시간이 고정되므로,
    # 시간처럼 매번 새 값이 필요한 경우에는 default_factory를 사용합니다.
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        """이름이 공백 문자로만 이루어진 경우를 막습니다."""

        # Field(min_length=2)는 문자열 길이만 검사하므로 "  " 같은 값은 통과할 수 있습니다.
        # strip()으로 앞뒤 공백을 제거한 뒤 비어 있는지 확인합니다.
        if not value.strip():
            raise ValueError("name은 공백만 입력할 수 없습니다.")

        # 검증 후에는 앞뒤 공백이 제거된 값을 실제 모델에 저장합니다.
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """이메일을 소문자로 정규화합니다."""

        # 같은 이메일이라도 대소문자가 섞이면 비교나 검색이 불편해질 수 있습니다.
        # 저장 전에 lower()로 통일해두면 이후 처리가 단순해집니다.
        return value.lower()

    @model_validator(mode="after")
    def admin_must_be_adult(self) -> "User":
        """관리자는 18세 이상이어야 한다는 모델 단위 규칙을 적용합니다."""

        # field_validator는 한 필드만 검증할 때 적합하고,
        # model_validator는 여러 필드의 조합을 확인할 때 적합합니다.
        if self.role == "admin" and self.age < 18:
            raise ValueError("admin role은 18세 이상만 사용할 수 있습니다.")

        return self

    @computed_field
    @property
    def display_name(self) -> str:
        """출력용 이름을 계산해서 제공하는 필드입니다."""

        # computed_field는 DB나 요청 데이터에 직접 저장하지 않아도 되는 값을
        # 모델에서 계산해 함께 출력하고 싶을 때 유용합니다.
        return f"{self.name} ({self.role})"


def create_valid_user() -> User:
    """정상 데이터가 들어왔을 때 Pydantic이 어떻게 변환/검증하는지 보여줍니다."""

    raw_user = {
        # 모델 안에서는 user_id지만, 외부 입력은 alias인 id로 받을 수 있습니다.
        "id": 1,
        # 앞뒤 공백은 validator에서 제거됩니다.
        "name": "  Kim  ",
        # EmailStr로 형식을 검증한 뒤, validator에서 소문자로 변환됩니다.
        "email": "KIM@example.com",
        # 문자열로 들어온 숫자도 int로 변환 가능한 값이면 자동 변환됩니다.
        "age": "29",
        "role": "admin",
        # 문자열 "true"는 bool 값 True로 변환됩니다.
        "is_active": "true",
        # address 필드는 Address 모델로 다시 검증됩니다.
        "address": {
            "city": "Seoul",
            "zip_code": "04524",
        },
    }

    return User.model_validate(raw_user)


def show_valid_user() -> None:
    """정상 검증 결과를 출력합니다."""

    user = create_valid_user()

    print("=== 검증 성공 ===")
    print(f"user_id: {user.user_id}")
    print(f"name: {user.name}")
    print(f"email: {user.email}")
    print(f"age: {user.age}")
    print(f"role: {user.role}")
    print(f"is_active: {user.is_active}")
    print(f"city: {user.address.city}")
    print(f"display_name: {user.display_name}")

    print("\n=== dict로 변환 ===")
    # model_dump()는 Pydantic 모델을 dict로 변환합니다.
    # by_alias=True를 사용하면 user_id 대신 외부 입력 이름인 id로 출력됩니다.
    print(user.model_dump(by_alias=True))

    print("\n=== JSON 문자열로 변환 ===")
    # model_dump_json()은 JSON 문자열로 변환합니다.
    # indent=2를 주면 사람이 읽기 좋은 형태로 출력됩니다.
    print(user.model_dump_json(by_alias=True, indent=2))


def show_invalid_user() -> None:
    """잘못된 데이터가 들어왔을 때 어떤 에러가 나는지 보여줍니다."""

    invalid_user = {
        # ge=1 조건 때문에 0은 실패합니다.
        "id": 0,
        # 공백만 있는 이름은 custom validator에서 실패합니다.
        "name": "   ",
        # 이메일 형식이 아니므로 EmailStr 검증에서 실패합니다.
        "email": "not-email",
        # le=120 조건 때문에 150은 실패합니다.
        "age": 150,
        # Literal["user", "admin"]에 없는 값이므로 실패합니다.
        "role": "manager",
        # city는 min_length=2 조건 때문에 실패합니다.
        "address": {
            "city": "S",
            "zip_code": "1",
        },
        # extra="forbid" 설정 때문에 선언되지 않은 unknown 필드는 실패합니다.
        "unknown": "이 필드는 허용되지 않습니다.",
    }

    print("\n=== 검증 실패 ===")

    try:
        User.model_validate(invalid_user)
    except ValidationError as error:
        # ValidationError에는 어떤 필드에서 어떤 문제가 발생했는지 구조화된 정보가 들어 있습니다.
        # 실무에서는 이 정보를 API 응답으로 변환하거나 로그에 남길 수 있습니다.
        for index, detail in enumerate(error.errors(), start=1):
            print(f"{index}. 위치: {detail['loc']}")
            print(f"   메시지: {detail['msg']}")
            print(f"   에러 타입: {detail['type']}")


def main() -> None:
    show_valid_user()
    show_invalid_user()


if __name__ == "__main__":
    main()
