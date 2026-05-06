"""재난별 대처법 안내 DTO를 정의한다."""

from pydantic import BaseModel

from app.domain.enums import ProtectedCategory


class ActionGuidePageResponse(BaseModel):
    """대처법 안내의 한 페이지를 반환한다."""

    page_no: int
    text: str
    image_url: str | None = None


class ActionGuideRuleResponse(BaseModel):
    """재난 종류와 보호대상자 분류에 맞는 대처법 안내를 반환한다."""

    guide_id: str
    disaster_type: str
    category: ProtectedCategory
    pages: list[ActionGuidePageResponse]
    enabled: bool
