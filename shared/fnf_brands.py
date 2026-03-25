"""
F&F Brand Definitions
F&F 엔터테인먼트 브랜드 포트폴리오 정의
"""

FNF_BRANDS = {
    "MLB": {
        "code": "M",
        "name_ko": "엠엘비",
        "category": "streetwear",
        "positioning": "K-스트릿 캐주얼",
        "target_age": "15-35",
        "target_gender": "unisex",
        "keywords": ["스트릿", "캐주얼", "뉴욕 양키스", "모노그램", "청춘", "K-POP"],
        "competitors": ["New Era", "Nike SB", "Stussy", "Thrasher"],
        "key_products": ["모자", "패딩", "맨투맨", "백팩", "청키 신발"],
        "brand_personality": "젊고 트렌디한 스트릿 감성. K-POP 스타와 MZ세대의 일상 패션.",
        "price_range": "mid",
        "markets": ["Korea", "China", "Southeast Asia", "Japan"],
    },
    "Discovery": {
        "code": "X",
        "name_ko": "디스커버리 익스페디션",
        "category": "outdoor/athleisure",
        "positioning": "어반 아웃도어",
        "target_age": "25-45",
        "target_gender": "unisex",
        "keywords": ["아웃도어", "고프코어", "등산", "캠핑", "윈드브레이커", "카고"],
        "competitors": ["The North Face", "Patagonia", "Columbia", "K2"],
        "key_products": ["윈드브레이커", "카고팬츠", "등산화", "플리스", "다운재킷"],
        "brand_personality": "도시와 자연을 넘나드는 액티브 라이프스타일. 기능성과 패션의 균형.",
        "price_range": "mid-high",
        "markets": ["Korea"],
    },
    "MLB_KIDS": {
        "code": "I",
        "name_ko": "엠엘비 키즈",
        "category": "kids_fashion",
        "positioning": "키즈 스트릿",
        "target_age": "3-13",
        "target_gender": "unisex",
        "keywords": ["키즈", "아동복", "MLB", "스포츠", "캐주얼"],
        "competitors": ["Nike Kids", "Adidas Kids", "Gap Kids"],
        "key_products": ["티셔츠", "운동화", "모자", "트레이닝복"],
        "brand_personality": "MLB의 스트릿 감성을 키즈에 맞게. 부모와 아이가 함께하는 패밀리룩.",
        "price_range": "mid",
        "markets": ["Korea", "China"],
    },
    "Duvetica": {
        "code": "V",
        "name_ko": "듀베티카",
        "category": "premium_outerwear",
        "positioning": "이탈리안 프리미엄 다운",
        "target_age": "30-50",
        "target_gender": "unisex",
        "keywords": ["프리미엄", "다운재킷", "이탈리아", "럭셔리", "미니멀"],
        "competitors": ["Moncler", "Canada Goose", "Herno"],
        "key_products": ["다운재킷", "다운베스트", "경량 다운"],
        "brand_personality": "이탈리안 장인정신의 프리미엄 다운웨어. 심플하고 세련된 럭셔리.",
        "price_range": "high",
        "markets": ["Korea", "Japan", "Europe"],
    },
    "Sergio_Tacchini": {
        "code": "ST",
        "name_ko": "세르지오 타키니",
        "category": "sports_lifestyle",
        "positioning": "테니스 라이프스타일",
        "target_age": "25-40",
        "target_gender": "unisex",
        "keywords": ["테니스", "레트로", "스포츠", "라이프스타일", "이탈리안"],
        "competitors": ["Lacoste", "Fred Perry", "Fila"],
        "key_products": ["트랙수트", "폴로셔츠", "테니스웨어", "스니커즈"],
        "brand_personality": "Tennis like living. 테니스 헤리티지에서 영감받은 세련된 스포츠 라이프스타일.",
        "price_range": "mid-high",
        "markets": ["Korea", "Europe"],
    },
}


def get_brand_context(brand_key: str) -> str:
    """Generate a text description of a brand for use as simulation seed context."""
    brand = FNF_BRANDS.get(brand_key)
    if not brand:
        available = ", ".join(FNF_BRANDS.keys())
        raise ValueError(f"Unknown brand: {brand_key}. Available: {available}")

    return f"""[Brand: {brand_key}]
- 한국명: {brand['name_ko']}
- 카테고리: {brand['category']}
- 포지셔닝: {brand['positioning']}
- 타겟 연령: {brand['target_age']}
- 키워드: {', '.join(brand['keywords'])}
- 주요 경쟁사: {', '.join(brand['competitors'])}
- 주요 제품: {', '.join(brand['key_products'])}
- 브랜드 성격: {brand['brand_personality']}
- 가격대: {brand['price_range']}
- 주요 시장: {', '.join(brand['markets'])}
"""
