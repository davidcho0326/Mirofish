"""
Campaign Seed Generator
캠페인 브리프를 MiroFish 코어가 이해하는 seed 텍스트로 변환.
LLM 호출 없이 순수 템플릿 조합.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional

from shared.fnf_brands import FNF_BRANDS, get_brand_context
from shared.korean_config import get_archetype_distribution

# Templates directory
_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../../templates')


@dataclass
class CampaignBrief:
    """캠페인 브리프 입력 데이터"""
    brand_key: str              # "MLB", "Discovery", etc.
    product_name: str           # "2026 SS 뉴욕 모노그램 백팩"
    product_description: str    # 제품 상세 설명
    target_audience: str        # "20대 여성, K-POP 관심, 대학생"
    campaign_message: str       # "Your City, Your Style"
    season: str                 # "SS" | "FW"
    campaign_type: str          # "launch" | "seasonal" | "collaboration" | "event"
    budget_level: str = "mid"   # "low" | "mid" | "high"
    additional_context: str = ""

    def validate(self):
        if self.brand_key not in FNF_BRANDS:
            available = ", ".join(FNF_BRANDS.keys())
            raise ValueError(f"Unknown brand: {self.brand_key}. Available: {available}")
        if self.season not in ("SS", "FW"):
            raise ValueError(f"Season must be 'SS' or 'FW', got: {self.season}")
        if self.campaign_type not in ("launch", "seasonal", "collaboration", "event"):
            raise ValueError(f"Invalid campaign_type: {self.campaign_type}")

    def to_dict(self):
        return asdict(self)


@dataclass
class CampaignSeed:
    """생성된 seed 데이터"""
    seed_text: str              # ~1000자 구조화된 문서
    brief: CampaignBrief
    brand_data: dict            # FNF_BRANDS[brand_key] 전체
    archetype_weights: dict     # 브랜드별 소비자 아키타입 분포

    def to_dict(self):
        return {
            "seed_text": self.seed_text,
            "brief": self.brief.to_dict(),
            "brand_data": self.brand_data,
            "archetype_weights": self.archetype_weights,
        }


class CampaignSeedGenerator:
    """캠페인 브리프 → seed 텍스트 변환기"""

    def __init__(self):
        self._brand_contexts = self._load_brand_contexts()

    def _load_brand_contexts(self) -> dict:
        path = os.path.join(_TEMPLATES_DIR, 'brand_contexts.json')
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        return data.get('contexts', {})

    def generate_seed(self, brief: CampaignBrief) -> CampaignSeed:
        """캠페인 브리프를 seed로 변환. LLM 호출 없음."""
        brief.validate()

        brand_data = FNF_BRANDS[brief.brand_key]
        archetype_weights = get_archetype_distribution(brief.brand_key)
        brand_context_text = get_brand_context(brief.brand_key)

        # 브랜드 컨텍스트 템플릿에서 시즌 키워드 추출
        brand_ctx = self._brand_contexts.get(brief.brand_key, {})
        seasonal_keywords = brand_ctx.get('seasonal_keywords', {}).get(brief.season, [])
        seed_intro = brand_ctx.get('seed_intro', '')

        # 캠페인 타입 한국어
        type_labels = {
            "launch": "신제품 론칭",
            "seasonal": "시즌 캠페인",
            "collaboration": "콜라보레이션",
            "event": "이벤트/프로모션",
        }
        campaign_type_ko = type_labels.get(brief.campaign_type, brief.campaign_type)

        # Seed 텍스트 조합
        sections = []

        # Section 1: 브랜드 개요
        sections.append(f"## 브랜드 개요\n{seed_intro}")
        sections.append(brand_context_text)

        # Section 2: 제품 정보
        sections.append(f"""## 제품 정보
- 제품명: {brief.product_name}
- 설명: {brief.product_description}
- 시즌: {brief.season} ({'봄/여름' if brief.season == 'SS' else '가을/겨울'})
- 시즌 키워드: {', '.join(seasonal_keywords) if seasonal_keywords else 'N/A'}""")

        # Section 3: 캠페인 브리프
        sections.append(f"""## 캠페인 브리프
- 캠페인 유형: {campaign_type_ko}
- 핵심 메시지: {brief.campaign_message}
- 타겟 오디언스: {brief.target_audience}
- 예산 규모: {brief.budget_level}""")

        # Section 4: 시장 컨텍스트
        competitors = brand_data.get('competitors', [])
        markets = brand_data.get('markets', [])
        sections.append(f"""## 시장 컨텍스트
- 주요 경쟁사: {', '.join(competitors)}
- 활동 시장: {', '.join(markets)}
- 가격대: {brand_data.get('price_range', 'N/A')}""")

        # Section 5: 추가 컨텍스트 (있는 경우)
        if brief.additional_context:
            sections.append(f"## 추가 컨텍스트\n{brief.additional_context}")

        seed_text = "\n\n".join(sections)

        return CampaignSeed(
            seed_text=seed_text,
            brief=brief,
            brand_data=brand_data,
            archetype_weights=archetype_weights,
        )
