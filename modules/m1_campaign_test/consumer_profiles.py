"""
Consumer Panel Generator
LLM으로 가상 소비자 패널을 생성. 브랜드 아키타입 가중치에 따라 다양한 페르소나 구성.
"""

import json
import math
import os
import re
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any

from core.utils.llm_client import LLMClient
from shared.korean_config import KOREAN_MARKET_CONFIG

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../../templates')


@dataclass
class ConsumerPersona:
    """가상 소비자 페르소나"""
    persona_id: str             # "p01"
    name: str                   # 한국 이름
    age: int
    gender: str
    archetype: str              # "mz_trendsetter" etc.
    occupation: str
    personality: str            # 2-3문장 성격 설명
    fashion_preferences: str
    social_media_habits: str
    brand_awareness: str        # 해당 브랜드에 대한 인지도
    price_sensitivity: str      # "low" | "medium" | "high" | "very_high"
    influence_level: str        # "low" | "medium" | "high"

    def to_dict(self):
        return asdict(self)


@dataclass
class ConsumerPanel:
    """생성된 소비자 패널"""
    personas: List[ConsumerPersona]
    archetype_distribution: dict
    generation_metadata: dict

    def to_dict(self):
        return {
            "personas": [p.to_dict() for p in self.personas],
            "archetype_distribution": self.archetype_distribution,
            "generation_metadata": self.generation_metadata,
        }


def _parse_json_response(text: str) -> Any:
    """LLM 응답에서 JSON을 추출. Claude는 response_format을 무시하므로 수동 파싱."""
    cleaned = text.strip()
    # Strip markdown code fences
    cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\n?```\s*$', '', cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to extract first JSON array or object
    for pattern in [r'(\[[\s\S]*\])', r'(\{[\s\S]*\})']:
        match = re.search(pattern, cleaned)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

    raise ValueError(f"Failed to parse JSON from LLM response: {cleaned[:200]}...")


class ConsumerPanelGenerator:
    """가상 소비자 패널 생성기"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self._llm = llm_client or LLMClient()
        self._archetypes_template = self._load_archetypes()

    def _load_archetypes(self) -> dict:
        path = os.path.join(_TEMPLATES_DIR, 'consumer_archetypes.json')
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        return data.get('archetypes', {})

    def generate_panel(self, seed, panel_size: int = 15,
                       graph_entities=None) -> ConsumerPanel:
        """
        가상 소비자 패널 생성.
        seed: CampaignSeed 객체
        panel_size: 패널 크기 (기본 15명)
        graph_entities: Full Mode 시 그래프 엔티티 (Optional)
        """
        # 아키타입별 인원 수 계산
        distribution = self._calculate_distribution(seed.archetype_weights, panel_size)

        personas = []
        persona_idx = 1

        for archetype_key, count in distribution.items():
            if count == 0:
                continue

            batch = self._generate_archetype_batch(
                archetype_key=archetype_key,
                count=count,
                seed=seed,
                start_idx=persona_idx,
                graph_entities=graph_entities,
            )
            personas.extend(batch)
            persona_idx += count

        return ConsumerPanel(
            personas=personas,
            archetype_distribution=distribution,
            generation_metadata={
                "panel_size": len(personas),
                "requested_size": panel_size,
                "brand": seed.brief.brand_key,
            },
        )

    def _calculate_distribution(self, weights: dict, total: int) -> dict:
        """가중치 → 실제 인원 수 변환 (반올림 보정)"""
        raw = {k: v * total for k, v in weights.items()}
        floored = {k: math.floor(v) for k, v in raw.items()}
        remainder = total - sum(floored.values())

        # 소수점이 큰 순서대로 나머지 배분
        fractions = {k: raw[k] - floored[k] for k in raw}
        for k in sorted(fractions, key=fractions.get, reverse=True):
            if remainder <= 0:
                break
            floored[k] += 1
            remainder -= 1

        return floored

    def _generate_archetype_batch(self, archetype_key: str, count: int,
                                  seed, start_idx: int,
                                  graph_entities=None) -> List[ConsumerPersona]:
        """아키타입별 페르소나 배치 생성 (1회 LLM 호출)"""
        archetype_config = KOREAN_MARKET_CONFIG['consumer_archetypes'].get(archetype_key, {})
        archetype_template = self._archetypes_template.get(archetype_key, {})

        label = archetype_config.get('label', archetype_key)
        age_range = archetype_config.get('age_range', '20-35')
        description = archetype_config.get('description', '')
        persona_tmpl = archetype_template.get('persona_template', '')
        behavior_traits = archetype_template.get('behavior_traits', [])
        posting_style = archetype_template.get('posting_style', '')

        # 그래프 엔티티 컨텍스트 (Full Mode)
        entity_context = ""
        if graph_entities:
            entities_summary = []
            for e in getattr(graph_entities, 'entities', [])[:5]:
                entities_summary.append(f"- {getattr(e, 'name', 'unknown')}: {getattr(e, 'description', '')[:100]}")
            if entities_summary:
                entity_context = "\n시장 엔티티 참고:\n" + "\n".join(entities_summary)

        system_prompt = f"""당신은 한국 패션 시장의 소비자 페르소나 생성 전문가입니다.
다음 아키타입에 맞는 가상 소비자 {count}명을 생성하세요.

아키타입: {label}
연령대: {age_range}
특징: {description}
행동 특성: {', '.join(behavior_traits)}
SNS 스타일: {posting_style}

브랜드: {seed.brief.brand_key} ({seed.brand_data.get('positioning', '')})
캠페인: {seed.brief.campaign_message}
제품: {seed.brief.product_name}
타겟: {seed.brief.target_audience}
{entity_context}

각 페르소나는 고유한 이름, 나이, 성격, 직업을 가져야 합니다.
같은 아키타입이라도 각자 다른 개성을 부여하세요."""

        user_prompt = f"""아래 JSON 배열 형식으로 정확히 {count}명의 페르소나를 생성하세요.

```json
[
  {{
    "name": "한국 이름",
    "age": 숫자,
    "gender": "남성" 또는 "여성",
    "occupation": "직업",
    "personality": "2-3문장 성격 설명",
    "fashion_preferences": "패션 스타일 선호",
    "social_media_habits": "주 사용 SNS와 활동 패턴",
    "brand_awareness": "{seed.brief.brand_key} 브랜드에 대한 현재 인지도와 태도",
    "price_sensitivity": "low/medium/high/very_high 중 하나",
    "influence_level": "low/medium/high 중 하나"
  }}
]
```

반드시 유효한 JSON 배열로만 응답하세요. 다른 텍스트는 포함하지 마세요."""

        # LLM 호출 (chat_json() 대신 chat() 사용 — Claude 호환 이슈)
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = self._llm.chat(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.8,
                    max_tokens=4096,
                )
                parsed = _parse_json_response(response)

                if not isinstance(parsed, list):
                    parsed = [parsed]

                personas = []
                for i, p in enumerate(parsed[:count]):
                    personas.append(ConsumerPersona(
                        persona_id=f"p{start_idx + i:02d}",
                        name=p.get('name', f'소비자{start_idx + i}'),
                        age=int(p.get('age', 25)),
                        gender=p.get('gender', '여성'),
                        archetype=archetype_key,
                        occupation=p.get('occupation', '미정'),
                        personality=p.get('personality', ''),
                        fashion_preferences=p.get('fashion_preferences', ''),
                        social_media_habits=p.get('social_media_habits', ''),
                        brand_awareness=p.get('brand_awareness', ''),
                        price_sensitivity=p.get('price_sensitivity', 'medium'),
                        influence_level=p.get('influence_level', 'medium'),
                    ))
                return personas

            except (ValueError, json.JSONDecodeError, KeyError) as e:
                if attempt < max_retries:
                    continue
                # 최종 실패 시 기본 페르소나 생성
                return [
                    ConsumerPersona(
                        persona_id=f"p{start_idx + i:02d}",
                        name=f"소비자{start_idx + i}",
                        age=25,
                        gender="여성",
                        archetype=archetype_key,
                        occupation="미정",
                        personality=f"{label} 아키타입의 일반적인 소비자",
                        fashion_preferences="일반적",
                        social_media_habits="Instagram 사용",
                        brand_awareness="보통",
                        price_sensitivity=archetype_config.get('price_sensitivity', 'medium'),
                        influence_level=archetype_config.get('influence_level', 'medium'),
                    )
                    for i in range(count)
                ]
