"""
Campaign Scorer
LLM 기반 소비자 반응 시뮬레이션 + KPI 집계 + 인터뷰 기능
"""

import json
import re
import uuid
from collections import Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any

from core.utils.llm_client import LLMClient
from .consumer_profiles import ConsumerPersona, ConsumerPanel, _parse_json_response
from .campaign_seed import CampaignBrief, CampaignSeed


@dataclass
class PersonaReaction:
    """개별 페르소나의 캠페인 반응"""
    persona_id: str
    engagement_likelihood: float    # 0.0-1.0
    sentiment: str                  # very_positive/positive/neutral/negative/very_negative
    sentiment_score: float          # -1.0 ~ 1.0
    share_probability: float        # 0.0-1.0
    purchase_intent: float          # 0.0-1.0
    reaction_text: str              # 자연어 반응
    concerns: List[str] = field(default_factory=list)
    appeal_points: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class KPISummary:
    """집계된 마케팅 KPI"""
    predicted_engagement_rate: float
    sentiment_distribution: Dict[str, float]
    average_sentiment_score: float
    viral_probability: float
    average_purchase_intent: float
    strongest_archetype: str
    weakest_archetype: str
    top_appeal_points: List[str]
    top_concerns: List[str]

    def to_dict(self):
        return asdict(self)


@dataclass
class CampaignReport:
    """캠페인 사전 테스트 최종 리포트"""
    campaign_id: str
    brief: CampaignBrief
    mode: str                       # "quick" | "full"
    kpi_summary: KPISummary
    persona_reactions: List[PersonaReaction]
    risk_flags: List[Dict[str, str]]
    recommendations: List[str]
    graph_id: Optional[str] = None
    created_at: str = ""

    def to_dict(self):
        return {
            "campaign_id": self.campaign_id,
            "brief": self.brief.to_dict(),
            "mode": self.mode,
            "kpi_summary": self.kpi_summary.to_dict(),
            "persona_reactions": [r.to_dict() for r in self.persona_reactions],
            "risk_flags": self.risk_flags,
            "recommendations": self.recommendations,
            "graph_id": self.graph_id,
            "created_at": self.created_at,
        }


class CampaignScorer:
    """캠페인 반응 시뮬레이션 + KPI 산출"""

    BATCH_SIZE = 5  # 5명씩 배치 처리

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self._llm = llm_client or LLMClient()

    def score_campaign(self, seed: CampaignSeed, panel: ConsumerPanel,
                       mode: str = "quick", graph_entities=None) -> CampaignReport:
        """전체 캠페인 스코어링 파이프라인"""
        campaign_id = str(uuid.uuid4())[:8]

        # Step 1: 배치별 반응 시뮬레이션
        all_reactions = []
        personas = panel.personas

        for i in range(0, len(personas), self.BATCH_SIZE):
            batch = personas[i:i + self.BATCH_SIZE]
            reactions = self._score_batch(batch, seed)
            all_reactions.extend(reactions)

        # Step 2: KPI 집계
        kpi = self._aggregate_kpis(all_reactions, panel)

        # Step 3: 리스크 플래그
        risk_flags = self._detect_risks(kpi, all_reactions, seed)

        # Step 4: 추천사항 생성
        recommendations = self._generate_recommendations(kpi, risk_flags, seed)

        return CampaignReport(
            campaign_id=campaign_id,
            brief=seed.brief,
            mode=mode,
            kpi_summary=kpi,
            persona_reactions=all_reactions,
            risk_flags=risk_flags,
            recommendations=recommendations,
            created_at=datetime.now().isoformat(),
        )

    def interview_persona(self, persona: ConsumerPersona, seed: CampaignSeed,
                          question: str, conversation_history: List[dict] = None) -> str:
        """가상 소비자 인터뷰 — 페르소나 역할극"""
        history = conversation_history or []

        system_prompt = f"""당신은 다음 인물을 연기합니다. 이 인물의 관점에서만 대답하세요.

이름: {persona.name}
나이: {persona.age}세 / 성별: {persona.gender}
직업: {persona.occupation}
성격: {persona.personality}
패션 취향: {persona.fashion_preferences}
SNS 습관: {persona.social_media_habits}
{seed.brief.brand_key} 인지도: {persona.brand_awareness}
가격 민감도: {persona.price_sensitivity}

현재 논의 중인 캠페인:
- 브랜드: {seed.brief.brand_key}
- 제품: {seed.brief.product_name} — {seed.brief.product_description}
- 메시지: {seed.brief.campaign_message}

자연스럽고 현실적인 한국어로 대답하세요. 1인칭으로 답변하세요."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": question})

        response = self._llm.chat(
            messages=messages,
            temperature=0.8,
            max_tokens=1024,
        )
        return response

    # ── Private Methods ──

    def _score_batch(self, batch: List[ConsumerPersona],
                     seed: CampaignSeed) -> List[PersonaReaction]:
        """5명 배치를 한 번의 LLM 호출로 스코어링"""
        persona_descriptions = []
        for p in batch:
            persona_descriptions.append(
                f"[{p.persona_id}] {p.name} ({p.age}세 {p.gender}, {p.occupation})\n"
                f"  성격: {p.personality}\n"
                f"  패션: {p.fashion_preferences}\n"
                f"  {seed.brief.brand_key} 인지도: {p.brand_awareness}\n"
                f"  가격민감도: {p.price_sensitivity}"
            )

        system_prompt = """당신은 한국 패션 마케팅 소비자 반응 시뮬레이터입니다.
각 소비자가 아래 캠페인을 접했을 때의 반응을 시뮬레이션하세요.
현실적이고 다양한 반응을 생성하세요. 모든 사람이 긍정적일 필요는 없습니다."""

        user_prompt = f"""## 캠페인 정보
- 브랜드: {seed.brief.brand_key} ({seed.brand_data.get('positioning', '')})
- 제품: {seed.brief.product_name}
- 설명: {seed.brief.product_description}
- 메시지: "{seed.brief.campaign_message}"
- 타겟: {seed.brief.target_audience}
- 시즌: {seed.brief.season}

## 소비자 프로필
{chr(10).join(persona_descriptions)}

## 응답 형식
각 소비자의 반응을 아래 JSON 배열로 생성하세요:
```json
[
  {{
    "persona_id": "p01",
    "engagement_likelihood": 0.0~1.0,
    "sentiment": "very_positive/positive/neutral/negative/very_negative",
    "sentiment_score": -1.0~1.0,
    "share_probability": 0.0~1.0,
    "purchase_intent": 0.0~1.0,
    "reaction_text": "이 소비자가 SNS에 쓸 법한 2-3문장 반응",
    "concerns": ["우려사항1", "우려사항2"],
    "appeal_points": ["매력포인트1", "매력포인트2"]
  }}
]
```
반드시 {len(batch)}명 전원의 반응을 포함하세요. 유효한 JSON 배열로만 응답하세요."""

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = self._llm.chat(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=4096,
                )
                parsed = _parse_json_response(response)
                if not isinstance(parsed, list):
                    parsed = [parsed]

                reactions = []
                for i, r in enumerate(parsed[:len(batch)]):
                    reactions.append(PersonaReaction(
                        persona_id=batch[i].persona_id if i < len(batch) else r.get('persona_id', f'p{i}'),
                        engagement_likelihood=self._clamp(float(r.get('engagement_likelihood', 0.5)), 0, 1),
                        sentiment=r.get('sentiment', 'neutral'),
                        sentiment_score=self._clamp(float(r.get('sentiment_score', 0.0)), -1, 1),
                        share_probability=self._clamp(float(r.get('share_probability', 0.2)), 0, 1),
                        purchase_intent=self._clamp(float(r.get('purchase_intent', 0.3)), 0, 1),
                        reaction_text=r.get('reaction_text', ''),
                        concerns=r.get('concerns', []),
                        appeal_points=r.get('appeal_points', []),
                    ))
                return reactions

            except (ValueError, json.JSONDecodeError, KeyError, TypeError):
                if attempt < max_retries:
                    continue
                # 최종 실패 시 기본 반응
                return [
                    PersonaReaction(
                        persona_id=p.persona_id,
                        engagement_likelihood=0.5,
                        sentiment="neutral",
                        sentiment_score=0.0,
                        share_probability=0.2,
                        purchase_intent=0.3,
                        reaction_text="(분석 실패 — 기본 반응)",
                        concerns=[],
                        appeal_points=[],
                    )
                    for p in batch
                ]

    def _aggregate_kpis(self, reactions: List[PersonaReaction],
                        panel: ConsumerPanel) -> KPISummary:
        """개별 반응 → 집계 KPI"""
        if not reactions:
            return KPISummary(
                predicted_engagement_rate=0.0,
                sentiment_distribution={},
                average_sentiment_score=0.0,
                viral_probability=0.0,
                average_purchase_intent=0.0,
                strongest_archetype="N/A",
                weakest_archetype="N/A",
                top_appeal_points=[],
                top_concerns=[],
            )

        n = len(reactions)

        # 기본 평균
        avg_engagement = sum(r.engagement_likelihood for r in reactions) / n
        avg_sentiment = sum(r.sentiment_score for r in reactions) / n
        avg_share = sum(r.share_probability for r in reactions) / n
        avg_purchase = sum(r.purchase_intent for r in reactions) / n

        # 감성 분포
        sentiment_counts = Counter(r.sentiment for r in reactions)
        sentiment_dist = {k: round(v / n, 2) for k, v in sentiment_counts.items()}

        # 바이럴 확률 (share_probability > 0.6인 비율)
        viral_prob = sum(1 for r in reactions if r.share_probability > 0.6) / n

        # 아키타입별 참여율
        archetype_engagement = {}
        persona_map = {p.persona_id: p for p in panel.personas}
        for r in reactions:
            persona = persona_map.get(r.persona_id)
            if persona:
                arch = persona.archetype
                if arch not in archetype_engagement:
                    archetype_engagement[arch] = []
                archetype_engagement[arch].append(r.engagement_likelihood)

        archetype_avg = {k: sum(v) / len(v) for k, v in archetype_engagement.items() if v}
        strongest = max(archetype_avg, key=archetype_avg.get) if archetype_avg else "N/A"
        weakest = min(archetype_avg, key=archetype_avg.get) if archetype_avg else "N/A"

        # 상위 매력 포인트 / 우려사항
        all_appeals = []
        all_concerns = []
        for r in reactions:
            all_appeals.extend(r.appeal_points)
            all_concerns.extend(r.concerns)

        top_appeals = [item for item, _ in Counter(all_appeals).most_common(5)]
        top_concerns = [item for item, _ in Counter(all_concerns).most_common(5)]

        return KPISummary(
            predicted_engagement_rate=round(avg_engagement, 3),
            sentiment_distribution=sentiment_dist,
            average_sentiment_score=round(avg_sentiment, 3),
            viral_probability=round(viral_prob, 3),
            average_purchase_intent=round(avg_purchase, 3),
            strongest_archetype=strongest,
            weakest_archetype=weakest,
            top_appeal_points=top_appeals,
            top_concerns=top_concerns,
        )

    def _detect_risks(self, kpi: KPISummary, reactions: List[PersonaReaction],
                      seed: CampaignSeed) -> List[Dict[str, str]]:
        """리스크 플래그 자동 감지"""
        flags = []

        if kpi.average_sentiment_score < 0.0:
            flags.append({
                "level": "high",
                "flag": "부정적 감성 우세",
                "detail": f"평균 감성 점수 {kpi.average_sentiment_score:.2f} (0 미만)",
            })

        if kpi.predicted_engagement_rate < 0.3:
            flags.append({
                "level": "medium",
                "flag": "낮은 참여율 예측",
                "detail": f"예측 참여율 {kpi.predicted_engagement_rate:.1%}",
            })

        if kpi.viral_probability < 0.1:
            flags.append({
                "level": "medium",
                "flag": "낮은 바이럴 가능성",
                "detail": f"바이럴 확률 {kpi.viral_probability:.1%}",
            })

        if kpi.average_purchase_intent < 0.3:
            flags.append({
                "level": "high",
                "flag": "낮은 구매 의향",
                "detail": f"평균 구매 의향 {kpi.average_purchase_intent:.1%}",
            })

        # 가격 우려 비율
        price_concerns = sum(
            1 for r in reactions
            if any('가격' in c or '비싸' in c or '비쌈' in c for c in r.concerns)
        )
        if price_concerns / max(len(reactions), 1) > 0.3:
            flags.append({
                "level": "medium",
                "flag": "가격 민감도 리스크",
                "detail": f"{price_concerns}/{len(reactions)}명이 가격 우려 언급",
            })

        return flags

    def _generate_recommendations(self, kpi: KPISummary,
                                  risk_flags: List[dict],
                                  seed: CampaignSeed) -> List[str]:
        """LLM으로 추천사항 생성"""
        prompt = f"""다음 캠페인 사전 테스트 결과를 바탕으로 3가지 핵심 추천사항을 제시하세요.

캠페인: {seed.brief.brand_key} - {seed.brief.product_name}
메시지: {seed.brief.campaign_message}

KPI 결과:
- 예측 참여율: {kpi.predicted_engagement_rate:.1%}
- 평균 감성: {kpi.average_sentiment_score:.2f}
- 바이럴 확률: {kpi.viral_probability:.1%}
- 구매 의향: {kpi.average_purchase_intent:.1%}
- 가장 반응 좋은 세그먼트: {kpi.strongest_archetype}
- 가장 반응 약한 세그먼트: {kpi.weakest_archetype}
- 주요 매력 포인트: {', '.join(kpi.top_appeal_points[:3])}
- 주요 우려사항: {', '.join(kpi.top_concerns[:3])}

리스크: {', '.join(f['flag'] for f in risk_flags) if risk_flags else '특이사항 없음'}

각 추천사항은 1-2문장으로 구체적이고 실행 가능하게 작성하세요.
JSON 배열로 응답하세요: ["추천1", "추천2", "추천3"]"""

        try:
            response = self._llm.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1024,
            )
            parsed = _parse_json_response(response)
            if isinstance(parsed, list):
                return [str(r) for r in parsed[:5]]
        except Exception:
            pass

        # 폴백 추천사항
        recs = []
        if kpi.weakest_archetype != "N/A":
            recs.append(f"{kpi.weakest_archetype} 세그먼트 대상 메시지를 강화하세요.")
        if kpi.top_concerns:
            recs.append(f"'{kpi.top_concerns[0]}' 우려를 해소하는 콘텐츠를 추가하세요.")
        if kpi.top_appeal_points:
            recs.append(f"'{kpi.top_appeal_points[0]}' 포인트를 캠페인 전면에 배치하세요.")
        return recs or ["캠페인 메시지를 타겟 세그먼트에 맞게 세분화하세요."]

    @staticmethod
    def _clamp(value: float, min_val: float, max_val: float) -> float:
        return max(min_val, min(max_val, value))
