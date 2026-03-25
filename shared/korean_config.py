"""
Korean Market Configuration
한국 시장 소비자/타임존/행동 기본 설정
"""

KOREAN_MARKET_CONFIG = {
    # 한국 타임존 활동 패턴 (시간대별 SNS 활동 비중)
    "timezone": "Asia/Seoul",
    "activity_pattern": {
        "morning_peak": {"hours": "07:00-09:00", "weight": 0.15},    # 출근 시간
        "lunch_peak": {"hours": "12:00-13:00", "weight": 0.12},      # 점심시간
        "afternoon": {"hours": "13:00-18:00", "weight": 0.18},       # 오후
        "evening_peak": {"hours": "19:00-23:00", "weight": 0.40},    # 퇴근 후 최대 활동
        "late_night": {"hours": "23:00-01:00", "weight": 0.10},      # 야간
        "off_hours": {"hours": "01:00-07:00", "weight": 0.05},       # 비활동
    },

    # 한국 소비자 아키타입
    "consumer_archetypes": {
        "mz_trendsetter": {
            "label": "MZ 트렌드세터",
            "age_range": "20-29",
            "description": "패션 트렌드에 민감한 MZ세대. SNS 활발, 신제품 얼리어답터.",
            "platforms": ["Instagram", "TikTok", "YouTube"],
            "fashion_interest": "high",
            "price_sensitivity": "medium",
            "brand_loyalty": "low",
            "influence_level": "medium-high",
            "mbti_distribution": {"E": 0.55, "I": 0.45, "N": 0.6, "S": 0.4},
        },
        "office_worker": {
            "label": "직장인",
            "age_range": "30-45",
            "description": "실용성과 스타일 균형. 주말 아웃도어 활동, 브랜드 충성도 높음.",
            "platforms": ["Instagram", "Naver Blog"],
            "fashion_interest": "medium",
            "price_sensitivity": "medium",
            "brand_loyalty": "high",
            "influence_level": "low",
            "mbti_distribution": {"E": 0.45, "I": 0.55, "N": 0.4, "S": 0.6},
        },
        "student": {
            "label": "학생",
            "age_range": "15-22",
            "description": "또래 영향력 크고, 가성비 중시. K-POP 팬덤 활발.",
            "platforms": ["TikTok", "Instagram", "YouTube"],
            "fashion_interest": "high",
            "price_sensitivity": "high",
            "brand_loyalty": "low",
            "influence_level": "medium",
            "mbti_distribution": {"E": 0.6, "I": 0.4, "N": 0.55, "S": 0.45},
        },
        "fashion_enthusiast": {
            "label": "패션 마니아",
            "age_range": "22-38",
            "description": "패션을 취미이자 자기표현으로. 하이엔드~스트릿 넘나듦. 리뷰/언박싱 생산.",
            "platforms": ["Instagram", "YouTube", "Naver Cafe"],
            "fashion_interest": "very_high",
            "price_sensitivity": "low",
            "brand_loyalty": "medium",
            "influence_level": "high",
            "mbti_distribution": {"E": 0.5, "I": 0.5, "N": 0.65, "S": 0.35},
        },
        "value_shopper": {
            "label": "가성비 소비자",
            "age_range": "25-50",
            "description": "가격 대비 품질 중시. 할인/프로모션에 민감. 실용 위주.",
            "platforms": ["Naver Cafe", "Coupang Review"],
            "fashion_interest": "low-medium",
            "price_sensitivity": "very_high",
            "brand_loyalty": "medium",
            "influence_level": "low",
            "mbti_distribution": {"E": 0.4, "I": 0.6, "N": 0.35, "S": 0.65},
        },
    },

    # 한국 SNS 플랫폼 특성
    "platform_dynamics": {
        "Instagram": {
            "content_type": "visual",
            "viral_threshold": 0.3,
            "echo_chamber_strength": 0.4,
            "primary_age": "20-35",
        },
        "TikTok": {
            "content_type": "short_video",
            "viral_threshold": 0.15,  # 알고리즘 추천으로 바이럴 쉬움
            "echo_chamber_strength": 0.2,
            "primary_age": "15-30",
        },
        "YouTube": {
            "content_type": "long_video",
            "viral_threshold": 0.5,
            "echo_chamber_strength": 0.5,
            "primary_age": "15-45",
        },
        "Naver": {
            "content_type": "text_review",
            "viral_threshold": 0.6,
            "echo_chamber_strength": 0.7,
            "primary_age": "30-50",
        },
    },
}


def get_archetype_distribution(brand_key: str) -> dict:
    """Return recommended archetype distribution weights for a brand."""
    distributions = {
        "MLB": {
            "mz_trendsetter": 0.35,
            "student": 0.30,
            "fashion_enthusiast": 0.15,
            "office_worker": 0.10,
            "value_shopper": 0.10,
        },
        "Discovery": {
            "office_worker": 0.35,
            "mz_trendsetter": 0.20,
            "fashion_enthusiast": 0.15,
            "value_shopper": 0.20,
            "student": 0.10,
        },
        "Duvetica": {
            "fashion_enthusiast": 0.35,
            "office_worker": 0.30,
            "mz_trendsetter": 0.20,
            "value_shopper": 0.10,
            "student": 0.05,
        },
        "Sergio_Tacchini": {
            "fashion_enthusiast": 0.30,
            "mz_trendsetter": 0.25,
            "office_worker": 0.25,
            "value_shopper": 0.10,
            "student": 0.10,
        },
        "MLB_KIDS": {
            "office_worker": 0.45,  # 부모 구매자
            "value_shopper": 0.30,
            "mz_trendsetter": 0.15,
            "fashion_enthusiast": 0.05,
            "student": 0.05,
        },
    }
    return distributions.get(brand_key, distributions["MLB"])
