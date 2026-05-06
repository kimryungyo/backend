"""재난별 대처법 안내 도메인 모델을 정의한다."""

from dataclasses import dataclass

from app.domain.enums import ProtectedCategory


@dataclass
class ActionGuidePage:
    """재난별 대처법 안내의 한 페이지를 나타낸다."""

    page_no: int  # 안내 페이지 순서
    text: str  # 보호대상자에게 보여줄 쉬운 문장 안내
    image_url: str | None  # 안내 이미지 URL

    def has_image(self) -> bool:
        """안내 페이지에 이미지가 포함되어 있는지 확인한다."""
        return bool(self.image_url)


@dataclass
class ActionGuideRule:
    """재난 종류와 보호대상자 분류에 따라 제공되는 대처법 안내를 나타낸다."""

    guide_id: str  # 대처법 안내 ID
    disaster_type: str  # 이 안내가 적용되는 재난 종류 코드
    category: ProtectedCategory  # 이 안내가 적용되는 보호대상자 분류
    pages: list[ActionGuidePage]  # 상시 조회 가능한 페이지형 안내 목록
    enabled: bool  # 안내 사용 여부

    def applies_to(self, disaster_type: str, categories: list[ProtectedCategory]) -> bool:
        """재난 종류와 보호대상자 분류에 이 안내가 적용되는지 확인한다."""
        return self.enabled and self.disaster_type == disaster_type and self.category in categories

    def ordered_pages(self) -> list[ActionGuidePage]:
        """페이지 번호 순서대로 정렬된 대처법 안내 페이지를 반환한다."""
        return sorted(self.pages, key=lambda page: page.page_no)
