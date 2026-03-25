"""
Campaign Analysis Report Generator
PoC 결과물의 Agent 숙의 과정을 시각적으로 설명하는 인터랙티브 HTML 생성
"""

import json
import os
import sys
from typing import Dict, List, Any

# Archetype labels
ARCHETYPE_LABELS = {
    "mz_trendsetter": "MZ 트렌드세터",
    "student": "학생",
    "fashion_enthusiast": "패션 마니아",
    "office_worker": "직장인",
    "value_shopper": "가성비 소비자",
}

# MLB default weights
DEFAULT_WEIGHTS = {
    "mz_trendsetter": 0.35,
    "student": 0.30,
    "fashion_enthusiast": 0.15,
    "office_worker": 0.10,
    "value_shopper": 0.10,
}

# Sentiment colors
SENTIMENT_COLORS = {
    "very_positive": "#22c55e",
    "positive": "#86efac",
    "neutral": "#94a3b8",
    "negative": "#fca5a5",
    "very_negative": "#ef4444",
}

SENTIMENT_LABELS = {
    "very_positive": "매우 긍정",
    "positive": "긍정",
    "neutral": "중립",
    "negative": "부정",
    "very_negative": "매우 부정",
}


def generate_report_html(data: Dict[str, Any]) -> str:
    """poc_result.json 데이터 → 인터랙티브 HTML 리포트 생성"""
    brief = data.get("brief", {})
    kpi = data.get("kpi_summary", {})
    reactions = data.get("persona_reactions", [])
    risk_flags = data.get("risk_flags", [])
    recommendations = data.get("recommendations", [])
    panel = data.get("panel", {})
    personas = panel.get("personas", [])
    arch_dist = panel.get("archetype_distribution", {})

    brand = brief.get("brand_key", "Unknown")
    product = brief.get("product_name", "Unknown")
    message = brief.get("campaign_message", "")
    season = brief.get("season", "SS")

    # Build sections
    html_parts = [
        _html_head(brand, product),
        _section_header(brief, data),
        _section_mirofish_map(),
        _section_data_sources(brief, data),
        _section_pipeline_map(),
        _section_step1_seed(brief, brand),
        _section_step2_panel(personas, arch_dist, brand, brief),
        _section_step3_reactions(reactions, personas),
        _section_step4_kpi(kpi, reactions),
        _section_step5_risk(risk_flags, kpi, reactions),
        _section_step6_recommendations(recommendations, kpi, risk_flags),
        _html_footer(data),
    ]

    return "\n".join(html_parts)


# ── HTML Head ──

def _html_head(brand, product):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{brand} Campaign Pre-Test Report</title>
<style>
:root {{
  --bg: #0f0f1a;
  --card: rgba(255,255,255,0.05);
  --card-border: rgba(255,255,255,0.1);
  --text: #e2e8f0;
  --text-dim: #94a3b8;
  --accent: #3b82f6;
  --accent2: #8b5cf6;
  --green: #22c55e;
  --red: #ef4444;
  --orange: #f59e0b;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'Pretendard', -apple-system, system-ui, sans-serif;
  line-height: 1.7;
  padding: 2rem;
  max-width: 1100px;
  margin: 0 auto;
}}
h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
h2 {{
  font-size: 1.4rem;
  color: var(--accent);
  margin: 2.5rem 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--card-border);
}}
h3 {{ font-size: 1.1rem; color: var(--accent2); margin: 1.5rem 0 0.5rem; }}
.card {{
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
  backdrop-filter: blur(10px);
}}
.card-accent {{
  border-left: 3px solid var(--accent);
}}
.card-green {{ border-left: 3px solid var(--green); }}
.card-orange {{ border-left: 3px solid var(--orange); }}
.card-red {{ border-left: 3px solid var(--red); }}
.tag {{
  display: inline-block;
  background: rgba(59,130,246,0.2);
  color: var(--accent);
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  margin: 2px;
}}
.tag-green {{ background: rgba(34,197,94,0.2); color: var(--green); }}
.tag-orange {{ background: rgba(245,158,11,0.2); color: var(--orange); }}
.tag-red {{ background: rgba(239,68,68,0.2); color: var(--red); }}
.kpi-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}}
.kpi-box {{
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  padding: 1.2rem;
  text-align: center;
}}
.kpi-value {{
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.kpi-label {{ font-size: 0.85rem; color: var(--text-dim); margin-top: 4px; }}
pre {{
  background: rgba(0,0,0,0.4);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  padding: 1rem;
  overflow-x: auto;
  font-size: 0.82rem;
  line-height: 1.5;
  color: #a5f3fc;
  margin: 0.8rem 0;
}}
.formula {{
  background: rgba(139,92,246,0.1);
  border: 1px solid rgba(139,92,246,0.3);
  border-radius: 8px;
  padding: 1rem;
  margin: 0.8rem 0;
  font-family: monospace;
  font-size: 0.9rem;
}}
.formula .result {{ color: var(--green); font-weight: bold; }}
details {{
  margin: 0.5rem 0;
}}
details > summary {{
  cursor: pointer;
  padding: 0.7rem 1rem;
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  font-weight: 600;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 8px;
}}
details > summary::before {{ content: "\\25B6"; font-size: 0.7rem; transition: transform 0.2s; }}
details[open] > summary::before {{ transform: rotate(90deg); }}
details > .detail-content {{
  padding: 1rem;
  border: 1px solid var(--card-border);
  border-top: none;
  border-radius: 0 0 8px 8px;
  background: rgba(0,0,0,0.2);
}}
.persona-card {{
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1rem;
  padding: 1.2rem;
  margin: 0.8rem 0;
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 12px;
}}
.persona-avatar {{
  width: 50px; height: 50px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
}}
.bar {{
  height: 24px;
  border-radius: 6px;
  background: rgba(255,255,255,0.08);
  overflow: hidden;
  margin: 4px 0;
}}
.bar-fill {{
  height: 100%;
  border-radius: 6px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  transition: width 0.6s ease;
}}
.pipeline {{
  display: flex;
  align-items: center;
  gap: 0;
  margin: 1.5rem 0;
  overflow-x: auto;
  padding: 1rem 0;
}}
.pipe-step {{
  flex-shrink: 0;
  text-align: center;
  padding: 0.8rem 1.2rem;
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  min-width: 120px;
  font-size: 0.82rem;
}}
.pipe-step .step-num {{
  font-size: 0.7rem;
  color: var(--accent);
  font-weight: 700;
}}
.pipe-step .step-label {{ font-weight: 600; margin-top: 2px; }}
.pipe-step .step-type {{
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-top: 2px;
}}
.pipe-arrow {{
  flex-shrink: 0;
  color: var(--accent);
  font-size: 1.2rem;
  padding: 0 0.3rem;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 0.8rem 0;
  font-size: 0.88rem;
}}
th, td {{
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--card-border);
  text-align: left;
}}
th {{
  background: rgba(59,130,246,0.1);
  font-weight: 600;
  color: var(--accent);
}}
.check {{ color: var(--green); }}
.cross {{ color: var(--red); }}
.warn {{ color: var(--orange); }}
.reaction-text {{
  background: rgba(0,0,0,0.3);
  border-radius: 8px;
  padding: 0.8rem 1rem;
  margin: 0.5rem 0;
  font-style: italic;
  border-left: 3px solid var(--accent2);
  font-size: 0.9rem;
}}
.risk-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}}
.risk-high {{ background: rgba(239,68,68,0.2); color: var(--red); }}
.risk-medium {{ background: rgba(245,158,11,0.2); color: var(--orange); }}
.risk-low {{ background: rgba(34,197,94,0.2); color: var(--green); }}
</style>
</head>
<body>"""


# ── Section: Header ──

def _section_header(brief, data):
    brand = brief.get("brand_key", "")
    product = brief.get("product_name", "")
    message = brief.get("campaign_message", "")
    season = brief.get("season", "")
    mode = data.get("mode", "quick")
    cid = data.get("campaign_id", "")
    created = data.get("created_at", "")[:19]

    kpi = data.get("kpi_summary", {})
    eng = kpi.get("predicted_engagement_rate", 0)
    sent = kpi.get("average_sentiment_score", 0)
    viral = kpi.get("viral_probability", 0)
    purchase = kpi.get("average_purchase_intent", 0)

    return f"""
<h1>{brand} Campaign Pre-Test Analysis</h1>
<p style="color:var(--text-dim); margin-bottom: 1.5rem;">
  {product} &middot; "{message}" &middot; {season} &middot;
  <span class="tag">{mode.upper()} MODE</span>
  <span class="tag">ID: {cid}</span>
  <span style="font-size:0.8rem; margin-left:8px;">{created}</span>
</p>

<div class="kpi-grid">
  <div class="kpi-box">
    <div class="kpi-value">{eng:.0%}</div>
    <div class="kpi-label">예측 참여율</div>
  </div>
  <div class="kpi-box">
    <div class="kpi-value">{sent:+.2f}</div>
    <div class="kpi-label">감성 점수</div>
  </div>
  <div class="kpi-box">
    <div class="kpi-value">{viral:.0%}</div>
    <div class="kpi-label">바이럴 확률</div>
  </div>
  <div class="kpi-box">
    <div class="kpi-value">{purchase:.0%}</div>
    <div class="kpi-label">구매 의향</div>
  </div>
</div>"""


# ── Section: MiroFish Technology Map ──

def _section_mirofish_map():
    """MiroFish 코어 엔진 기술이 현재 프로젝트에서 어떻게 활용되는지 매핑"""
    return """
<h2>MiroFish 기술 활용 맵</h2>
<p style="color:var(--text-dim);">
  <a href="https://github.com/666ghj/MiroFish" target="_blank" style="color:var(--accent);">MiroFish</a>는
  GitHub 41K+ 스타의 오픈소스 멀티 에이전트 AI 예측 엔진입니다.<br>
  본 프로젝트는 MiroFish 코어를 포크하여 F&amp;F 패션 마케팅에 특화시킨 것입니다.
</p>

<div class="card card-accent">
  <h3>MiroFish 핵심 기능 11개 &rarr; 현재 활용 현황</h3>
  <table style="font-size:0.85rem;">
    <tr><th>MiroFish 코어 모듈</th><th>원래 용도</th><th>F&amp;F 적용</th><th>상태</th><th>사용 위치</th></tr>
    <tr>
      <td><strong>LLMClient</strong><br><code>core/utils/llm_client.py</code></td>
      <td>OpenAI 호환 LLM 래퍼</td>
      <td>Claude Opus 4.6 API 호출<br>(페르소나 생성, 반응 시뮬, 추천)</td>
      <td><span class="tag tag-green">활성</span></td>
      <td>consumer_profiles.py<br>campaign_scorer.py</td>
    </tr>
    <tr>
      <td><strong>OntologyGenerator</strong><br><code>core/ontology_generator.py</code></td>
      <td>텍스트에서 엔티티/관계 타입 추출</td>
      <td>패션 도메인 온톨로지 생성<br>(Template 모드 활성, LLM 모드 준비)</td>
      <td><span class="tag tag-green">활성</span></td>
      <td>fashion_ontology.py</td>
    </tr>
    <tr>
      <td><strong>TextProcessor</strong><br><code>core/text_processor.py</code></td>
      <td>문서 텍스트 추출/청킹</td>
      <td>캠페인 seed 텍스트 처리</td>
      <td><span class="tag" style="background:rgba(59,130,246,0.15);">대기</span></td>
      <td>Full Mode에서 활용 예정</td>
    </tr>
    <tr>
      <td><strong>GraphBuilderService</strong><br><code>core/graph_builder.py</code></td>
      <td>Zep Cloud 지식그래프 구축</td>
      <td>브랜드/경쟁사/트렌드 그래프 구축</td>
      <td><span class="tag tag-orange">M2 계획</span></td>
      <td>trend_predict 모듈</td>
    </tr>
    <tr>
      <td><strong>ZepEntityReader</strong><br><code>core/zep_entity_reader.py</code></td>
      <td>그래프에서 엔티티 추출/필터</td>
      <td>패션 소비자/인플루언서 엔티티 추출</td>
      <td><span class="tag tag-orange">M2 계획</span></td>
      <td>trend_predict 모듈</td>
    </tr>
    <tr>
      <td><strong>OasisProfileGenerator</strong><br><code>core/oasis_profile_generator.py</code></td>
      <td>그래프 엔티티 &rarr; OASIS 에이전트 프로필</td>
      <td>인플루언서/팔로워 에이전트 생성</td>
      <td><span class="tag tag-orange">M3 계획</span></td>
      <td>influencer_sim 모듈</td>
    </tr>
    <tr>
      <td><strong>SimulationConfigGenerator</strong><br><code>core/simulation_config_generator.py</code></td>
      <td>LLM 기반 시뮬레이션 파라미터 자동 생성</td>
      <td>캠페인 시뮬레이션 설정 (타임존, 활동 패턴)</td>
      <td><span class="tag tag-orange">M3 계획</span></td>
      <td>influencer_sim 모듈</td>
    </tr>
    <tr>
      <td><strong>SimulationRunner</strong><br><code>core/simulation_runner.py</code></td>
      <td>OASIS 멀티 에이전트 시뮬레이션 실행</td>
      <td>가상 SNS에서 수백 에이전트 인터랙션</td>
      <td><span class="tag tag-orange">M3 계획</span></td>
      <td>influencer_sim 모듈</td>
    </tr>
    <tr>
      <td><strong>SimulationManager</strong><br><code>core/simulation_manager.py</code></td>
      <td>Twitter+Reddit 듀얼 플랫폼 오케스트레이션</td>
      <td>Instagram/TikTok 시뮬레이션 관리</td>
      <td><span class="tag tag-orange">M3 계획</span></td>
      <td>influencer_sim 모듈</td>
    </tr>
    <tr>
      <td><strong>ReportAgent</strong><br><code>core/report_agent.py</code></td>
      <td>ReACT 패턴 분석 리포트 자동 생성</td>
      <td>경쟁사 워게이밍 심층 분석</td>
      <td><span class="tag tag-orange">M5 계획</span></td>
      <td>competitive_war 모듈</td>
    </tr>
    <tr>
      <td><strong>ZepGraphMemoryUpdater</strong><br><code>core/zep_graph_memory_updater.py</code></td>
      <td>시뮬레이션 후 에이전트 기억 업데이트</td>
      <td>캠페인 반복 시뮬 시 학습 효과</td>
      <td><span class="tag tag-orange">M5 계획</span></td>
      <td>competitive_war 모듈</td>
    </tr>
  </table>
</div>

<div class="card" style="padding:2rem; overflow-x:auto;">
  <h3 style="margin-bottom:1.5rem;">Module 1 데이터 플로우 — 코어 엔진 연결도</h3>
  <svg viewBox="0 0 900 520" width="100%" style="display:block; font-family:'Pretendard Variable',-apple-system,sans-serif; max-width:900px; margin:0 auto;">
    <defs>
      <linearGradient id="grad-core" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="rgba(59,130,246,0.12)"/>
        <stop offset="100%" stop-color="rgba(59,130,246,0.03)"/>
      </linearGradient>
      <linearGradient id="grad-active" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="rgba(34,197,94,0.15)"/>
        <stop offset="100%" stop-color="rgba(34,197,94,0.05)"/>
      </linearGradient>
      <linearGradient id="grad-planned" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="rgba(245,158,11,0.1)"/>
        <stop offset="100%" stop-color="rgba(245,158,11,0.03)"/>
      </linearGradient>
      <linearGradient id="grad-m1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="rgba(139,92,246,0.15)"/>
        <stop offset="100%" stop-color="rgba(139,92,246,0.05)"/>
      </linearGradient>
      <linearGradient id="grad-output" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="rgba(34,197,94,0.12)"/>
        <stop offset="100%" stop-color="rgba(34,197,94,0.04)"/>
      </linearGradient>
      <filter id="glow-green"><feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#22c55e" flood-opacity="0.4"/></filter>
      <filter id="glow-blue"><feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#3b82f6" flood-opacity="0.3"/></filter>
      <marker id="arrow" viewBox="0 0 10 7" refX="10" refY="3.5" markerWidth="8" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 3.5 L 0 7 z" fill="rgba(255,255,255,0.35)"/>
      </marker>
      <marker id="arrow-green" viewBox="0 0 10 7" refX="10" refY="3.5" markerWidth="8" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 3.5 L 0 7 z" fill="#22c55e"/>
      </marker>
    </defs>

    <!-- ===== LAYER 1: MiroFish Core Engine Box ===== -->
    <rect x="30" y="15" width="840" height="170" rx="16" fill="url(#grad-core)" stroke="rgba(59,130,246,0.25)" stroke-width="1"/>
    <text x="50" y="42" fill="rgba(59,130,246,0.7)" font-size="11" font-weight="700" letter-spacing="0.1em">MIROFISH CORE ENGINE</text>
    <text x="730" y="42" fill="rgba(255,255,255,0.2)" font-size="10">github.com/666ghj/MiroFish</text>

    <!-- Active modules (green) -->
    <rect x="50" y="58" width="175" height="48" rx="10" fill="url(#grad-active)" stroke="rgba(34,197,94,0.35)" stroke-width="1" filter="url(#glow-green)"/>
    <circle cx="68" cy="82" r="5" fill="#22c55e"/>
    <text x="80" y="78" fill="#22c55e" font-size="12" font-weight="700">LLMClient</text>
    <text x="80" y="93" fill="rgba(255,255,255,0.4)" font-size="9">Claude Opus 4.6 API</text>

    <rect x="240" y="58" width="195" height="48" rx="10" fill="url(#grad-active)" stroke="rgba(34,197,94,0.35)" stroke-width="1" filter="url(#glow-green)"/>
    <circle cx="258" cy="82" r="5" fill="#22c55e"/>
    <text x="270" y="78" fill="#22c55e" font-size="12" font-weight="700">OntologyGenerator</text>
    <text x="270" y="93" fill="rgba(255,255,255,0.4)" font-size="9">패션 도메인 엔티티 정의</text>

    <!-- Planned modules (orange, dimmer) -->
    <rect x="450" y="58" width="185" height="48" rx="10" fill="url(#grad-planned)" stroke="rgba(245,158,11,0.2)" stroke-width="1"/>
    <circle cx="468" cy="82" r="5" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="480" y="78" fill="rgba(245,158,11,0.6)" font-size="11" font-weight="600">GraphBuilder</text>
    <text x="480" y="93" fill="rgba(255,255,255,0.25)" font-size="9">Zep 지식그래프 (M2)</text>

    <rect x="650" y="58" width="185" height="48" rx="10" fill="url(#grad-planned)" stroke="rgba(245,158,11,0.2)" stroke-width="1"/>
    <circle cx="668" cy="82" r="5" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="680" y="78" fill="rgba(245,158,11,0.6)" font-size="11" font-weight="600">SimulationRunner</text>
    <text x="680" y="93" fill="rgba(255,255,255,0.25)" font-size="9">OASIS 에이전트 (M3)</text>

    <rect x="50" y="118" width="185" height="48" rx="10" fill="url(#grad-planned)" stroke="rgba(245,158,11,0.2)" stroke-width="1"/>
    <circle cx="68" cy="142" r="5" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="80" y="138" fill="rgba(245,158,11,0.6)" font-size="11" font-weight="600">ProfileGenerator</text>
    <text x="80" y="153" fill="rgba(255,255,255,0.25)" font-size="9">에이전트 프로필 (M3)</text>

    <rect x="250" y="118" width="185" height="48" rx="10" fill="url(#grad-planned)" stroke="rgba(245,158,11,0.2)" stroke-width="1"/>
    <circle cx="268" cy="142" r="5" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="280" y="138" fill="rgba(245,158,11,0.6)" font-size="11" font-weight="600">ReportAgent</text>
    <text x="280" y="153" fill="rgba(255,255,255,0.25)" font-size="9">ReACT 분석 (M5)</text>

    <rect x="450" y="118" width="185" height="48" rx="10" fill="url(#grad-planned)" stroke="rgba(245,158,11,0.2)" stroke-width="1"/>
    <circle cx="468" cy="142" r="5" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="480" y="138" fill="rgba(245,158,11,0.6)" font-size="11" font-weight="600">MemoryUpdater</text>
    <text x="480" y="153" fill="rgba(255,255,255,0.25)" font-size="9">에이전트 기억 (M5)</text>

    <rect x="650" y="118" width="185" height="48" rx="10" fill="url(#grad-planned)" stroke="rgba(245,158,11,0.2)" stroke-width="1"/>
    <circle cx="668" cy="142" r="5" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="680" y="138" fill="rgba(245,158,11,0.6)" font-size="11" font-weight="600">EntityReader</text>
    <text x="680" y="153" fill="rgba(255,255,255,0.25)" font-size="9">엔티티 추출 (M2)</text>

    <!-- ===== ARROWS: Core → M1 Modules ===== -->
    <line x1="137" y1="106" x2="137" y2="235" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="6,4" marker-end="url(#arrow-green)" opacity="0.7"/>
    <line x1="337" y1="106" x2="450" y2="235" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="6,4" marker-end="url(#arrow-green)" opacity="0.7"/>
    <line x1="137" y1="106" x2="700" y2="235" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="6,4" marker-end="url(#arrow-green)" opacity="0.5"/>

    <!-- Label on arrows -->
    <text x="90" y="210" fill="rgba(34,197,94,0.5)" font-size="9" font-weight="600">import</text>
    <text x="370" y="210" fill="rgba(34,197,94,0.5)" font-size="9" font-weight="600">import</text>
    <text x="550" y="210" fill="rgba(34,197,94,0.5)" font-size="9" font-weight="600">import</text>

    <!-- ===== LAYER 2: Module 1 Files ===== -->
    <text x="50" y="260" fill="rgba(139,92,246,0.7)" font-size="11" font-weight="700" letter-spacing="0.1em">MODULE 1 — CAMPAIGN PRE-TEST</text>

    <!-- campaign_seed.py -->
    <rect x="30" y="272" width="240" height="95" rx="12" fill="url(#grad-m1)" stroke="rgba(139,92,246,0.3)" stroke-width="1"/>
    <text x="50" y="296" fill="rgba(139,92,246,0.9)" font-size="12" font-weight="700">campaign_seed.py</text>
    <text x="50" y="314" fill="rgba(255,255,255,0.5)" font-size="10">브랜드 DB + 템플릿 조합</text>
    <text x="50" y="330" fill="rgba(255,255,255,0.35)" font-size="9">LLM 호출 없음 (순수 템플릿)</text>
    <rect x="50" y="340" width="80" height="18" rx="9" fill="rgba(255,255,255,0.06)"/>
    <text x="65" y="353" fill="rgba(255,255,255,0.4)" font-size="8" font-weight="600">NO LLM</text>

    <!-- consumer_profiles.py -->
    <rect x="290" y="272" width="270" height="95" rx="12" fill="url(#grad-m1)" stroke="rgba(139,92,246,0.3)" stroke-width="1"/>
    <text x="310" y="296" fill="rgba(139,92,246,0.9)" font-size="12" font-weight="700">consumer_profiles.py</text>
    <text x="310" y="314" fill="rgba(255,255,255,0.5)" font-size="10">아키타입 가중치 → 페르소나 생성</text>
    <text x="310" y="330" fill="rgba(255,255,255,0.35)" font-size="9">LLMClient로 Claude 호출 (temp=0.8)</text>
    <rect x="310" y="340" width="105" height="18" rx="9" fill="rgba(34,197,94,0.15)"/>
    <text x="325" y="353" fill="#22c55e" font-size="8" font-weight="700">LLMClient ●</text>

    <!-- campaign_scorer.py -->
    <rect x="580" y="272" width="270" height="95" rx="12" fill="url(#grad-m1)" stroke="rgba(139,92,246,0.3)" stroke-width="1"/>
    <text x="600" y="296" fill="rgba(139,92,246,0.9)" font-size="12" font-weight="700">campaign_scorer.py</text>
    <text x="600" y="314" fill="rgba(255,255,255,0.5)" font-size="10">반응 시뮬 + KPI 집계 + 리스크</text>
    <text x="600" y="330" fill="rgba(255,255,255,0.35)" font-size="9">배치 5명/호출 (temp=0.7) + 통계 계산</text>
    <rect x="600" y="340" width="105" height="18" rx="9" fill="rgba(34,197,94,0.15)"/>
    <text x="615" y="353" fill="#22c55e" font-size="8" font-weight="700">LLMClient ●</text>
    <rect x="715" y="340" width="70" height="18" rx="9" fill="rgba(59,130,246,0.15)"/>
    <text x="726" y="353" fill="rgba(59,130,246,0.8)" font-size="8" font-weight="700">Python</text>

    <!-- ===== ARROWS: M1 → Outputs ===== -->
    <line x1="150" y1="367" x2="150" y2="415" stroke="rgba(255,255,255,0.2)" stroke-width="1.5" marker-end="url(#arrow)"/>
    <line x1="425" y1="367" x2="425" y2="415" stroke="rgba(255,255,255,0.2)" stroke-width="1.5" marker-end="url(#arrow)"/>
    <line x1="715" y1="367" x2="715" y2="415" stroke="rgba(255,255,255,0.2)" stroke-width="1.5" marker-end="url(#arrow)"/>

    <!-- ===== LAYER 3: Outputs ===== -->
    <rect x="55" y="420" width="190" height="50" rx="10" fill="url(#grad-output)" stroke="rgba(34,197,94,0.25)" stroke-width="1"/>
    <text x="90" y="443" fill="#22c55e" font-size="11" font-weight="700">CampaignSeed</text>
    <text x="90" y="458" fill="rgba(255,255,255,0.35)" font-size="9">seed_text (799자)</text>

    <rect x="330" y="420" width="190" height="50" rx="10" fill="url(#grad-output)" stroke="rgba(34,197,94,0.25)" stroke-width="1"/>
    <text x="360" y="443" fill="#22c55e" font-size="11" font-weight="700">ConsumerPanel</text>
    <text x="360" y="458" fill="rgba(255,255,255,0.35)" font-size="9">5명 페르소나 프로필</text>

    <rect x="615" y="420" width="200" height="50" rx="10" fill="url(#grad-output)" stroke="rgba(34,197,94,0.25)" stroke-width="1"/>
    <text x="645" y="443" fill="#22c55e" font-size="11" font-weight="700">CampaignReport</text>
    <text x="645" y="458" fill="rgba(255,255,255,0.35)" font-size="9">KPI + 리스크 + 추천</text>

    <!-- Chained arrows between outputs -->
    <line x1="245" y1="445" x2="330" y2="445" stroke="rgba(255,255,255,0.15)" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
    <line x1="520" y1="445" x2="615" y2="445" stroke="rgba(255,255,255,0.15)" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow)"/>

    <!-- ===== LEGEND ===== -->
    <rect x="30" y="490" width="840" height="25" rx="6" fill="rgba(255,255,255,0.02)"/>
    <circle cx="60" cy="502" r="5" fill="#22c55e"/>
    <text x="72" y="507" fill="rgba(255,255,255,0.5)" font-size="10">활성 사용 (M1)</text>
    <circle cx="210" cy="502" r="5" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="222" y="507" fill="rgba(255,255,255,0.5)" font-size="10">향후 활성화 (M2~M5)</text>
    <rect x="390" y="495" width="12" height="12" rx="3" fill="url(#grad-m1)" stroke="rgba(139,92,246,0.3)" stroke-width="1"/>
    <text x="410" y="507" fill="rgba(255,255,255,0.5)" font-size="10">Module 1 파일</text>
    <rect x="540" y="495" width="12" height="12" rx="3" fill="url(#grad-output)" stroke="rgba(34,197,94,0.25)" stroke-width="1"/>
    <text x="560" y="507" fill="rgba(255,255,255,0.5)" font-size="10">출력 데이터</text>
    <line x1="670" y1="502" x2="700" y2="502" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="6,4"/>
    <text x="710" y="507" fill="rgba(255,255,255,0.5)" font-size="10">import 연결</text>
  </svg>
</div>

<details>
  <summary>MiroFish 원본 vs F&amp;F 적용 비교</summary>
  <div class="detail-content">
    <table>
      <tr><th>관점</th><th>MiroFish (원본)</th><th>F&amp;F Marketing Sim (적용)</th></tr>
      <tr>
        <td><strong>도메인</strong></td>
        <td>여론/사회 이슈 시뮬레이션<br>(정치, 대학 분쟁, 소설 결말 예측)</td>
        <td>패션 마케팅 캠페인 사전 테스트<br>(브랜드 반응, 인플루언서, 트렌드)</td>
      </tr>
      <tr>
        <td><strong>에이전트</strong></td>
        <td>Twitter/Reddit 사용자<br>(실제 소셜미디어 행동 시뮬)</td>
        <td>한국 패션 소비자 아키타입<br>(MZ세대, 학생, 직장인, 패션마니아, 가성비)</td>
      </tr>
      <tr>
        <td><strong>지식그래프</strong></td>
        <td>뉴스/보고서에서 자동 추출<br>(Zep Cloud GraphRAG)</td>
        <td>F&amp;F 브랜드/경쟁사/트렌드 데이터<br>(현재 수동 정의, Zep 연동 계획)</td>
      </tr>
      <tr>
        <td><strong>시뮬레이션</strong></td>
        <td>OASIS 프레임워크<br>(수천~100만 에이전트, 멀티플랫폼)</td>
        <td>M1: LLM 기반 경량 시뮬 (5~15명)<br>M3+: OASIS 풀 시뮬레이션 예정</td>
      </tr>
      <tr>
        <td><strong>출력</strong></td>
        <td>ReACT 리포트 에이전트<br>(도구 호출 + 반성 루프)</td>
        <td>M1: HTML 리포트 + JSON<br>M5: ReACT 리포트 에이전트 예정</td>
      </tr>
      <tr>
        <td><strong>LLM</strong></td>
        <td>Qwen-Plus (알리바바 DashScope)</td>
        <td>Claude Opus 4.6 (Anthropic)<br>OpenAI SDK 호환 레이어</td>
      </tr>
    </table>
  </div>
</details>

<details>
  <summary>모듈 로드맵 — MiroFish 기능 순차 활성화</summary>
  <div class="detail-content">
    <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:8px; font-size:0.8rem; text-align:center;">
      <div class="card" style="border-color:var(--green); padding:0.8rem;">
        <div style="font-weight:700; color:var(--green);">M1</div>
        <div>캠페인 사전테스트</div>
        <div style="margin-top:6px;">
          <span class="tag tag-green" style="font-size:0.7rem;">LLMClient</span><br>
          <span class="tag tag-green" style="font-size:0.7rem;">OntologyGen</span>
        </div>
        <div style="color:var(--green); font-size:0.7rem; margin-top:4px;">완료</div>
      </div>
      <div class="card" style="border-color:var(--accent); padding:0.8rem;">
        <div style="font-weight:700; color:var(--accent);">M2</div>
        <div>트렌드 예측</div>
        <div style="margin-top:6px;">
          <span class="tag" style="font-size:0.7rem;">GraphBuilder</span><br>
          <span class="tag" style="font-size:0.7rem;">EntityReader</span>
        </div>
        <div style="color:var(--text-dim); font-size:0.7rem; margin-top:4px;">계획</div>
      </div>
      <div class="card" style="border-color:var(--accent2); padding:0.8rem;">
        <div style="font-weight:700; color:var(--accent2);">M3</div>
        <div>인플루언서 시뮬</div>
        <div style="margin-top:6px;">
          <span class="tag" style="font-size:0.7rem;">OASIS Runner</span><br>
          <span class="tag" style="font-size:0.7rem;">ProfileGen</span><br>
          <span class="tag" style="font-size:0.7rem;">SimConfig</span>
        </div>
        <div style="color:var(--text-dim); font-size:0.7rem; margin-top:4px;">계획</div>
      </div>
      <div class="card" style="border-color:var(--accent2); padding:0.8rem;">
        <div style="font-weight:700; color:var(--accent2);">M4</div>
        <div>시장 진입</div>
        <div style="margin-top:6px;">
          <span class="tag" style="font-size:0.7rem;">GraphBuilder</span><br>
          <span class="tag" style="font-size:0.7rem;">SimConfig</span>
        </div>
        <div style="color:var(--text-dim); font-size:0.7rem; margin-top:4px;">계획</div>
      </div>
      <div class="card" style="border-color:var(--orange); padding:0.8rem;">
        <div style="font-weight:700; color:var(--orange);">M5</div>
        <div>경쟁사 워게이밍</div>
        <div style="margin-top:6px;">
          <span class="tag" style="font-size:0.7rem;">ReportAgent</span><br>
          <span class="tag" style="font-size:0.7rem;">MemoryUpdater</span><br>
          <span class="tag" style="font-size:0.7rem;">OASIS Full</span>
        </div>
        <div style="color:var(--text-dim); font-size:0.7rem; margin-top:4px;">계획</div>
      </div>
    </div>
    <div class="formula" style="margin-top:1rem;">
      <strong>활용률:</strong> 11개 코어 모듈 중 현재 <span class="result">2개 활성</span> (18%) &rarr; M3 완료 시 <span style="color:var(--accent);">8개 활성</span> (73%) &rarr; M5 완료 시 <span style="color:var(--green);">11개 전체 활성</span> (100%)
    </div>
  </div>
</details>"""


# ── Section: Data Sources ──

def _section_data_sources(brief, data):
    """근거 데이터 대시보드 — 모든 입력 데이터의 출처와 실제/가상 여부를 한눈에 표시"""
    brand = brief.get("brand_key", "")
    panel = data.get("panel", {})
    personas = panel.get("personas", [])
    arch_dist = panel.get("archetype_distribution", {})

    # Brand DB fields
    from shared.fnf_brands import FNF_BRANDS
    brand_data = FNF_BRANDS.get(brand, {})

    brand_rows = ""
    brand_fields = [
        ("브랜드 코드", brand_data.get("code", "")),
        ("한국명", brand_data.get("name_ko", "")),
        ("카테고리", brand_data.get("category", "")),
        ("포지셔닝", brand_data.get("positioning", "")),
        ("타겟 연령", brand_data.get("target_age", "")),
        ("키워드", ", ".join(brand_data.get("keywords", []))),
        ("경쟁사", ", ".join(brand_data.get("competitors", []))),
        ("주요 제품", ", ".join(brand_data.get("key_products", []))),
        ("브랜드 성격", brand_data.get("brand_personality", "")),
        ("가격대", brand_data.get("price_range", "")),
        ("시장", ", ".join(brand_data.get("markets", []))),
    ]
    for field, value in brand_fields:
        brand_rows += f"    <tr><td>{field}</td><td>{value}</td></tr>\n"

    # Archetype config
    from shared.korean_config import KOREAN_MARKET_CONFIG
    archetypes = KOREAN_MARKET_CONFIG.get("consumer_archetypes", {})
    arch_rows = ""
    for key, cfg in archetypes.items():
        label = cfg.get("label", key)
        age = cfg.get("age_range", "")
        desc = cfg.get("description", "")[:80]
        platforms = ", ".join(cfg.get("platforms", []))
        fashion = cfg.get("fashion_interest", "")
        price = cfg.get("price_sensitivity", "")
        loyalty = cfg.get("brand_loyalty", "")
        arch_rows += f"    <tr><td>{label}</td><td>{age}</td><td>{desc}...</td><td>{platforms}</td><td>{fashion}</td><td>{price}</td><td>{loyalty}</td></tr>\n"

    # Brief input data
    brief_rows = ""
    brief_fields = [
        ("brand", brief.get("brand_key", ""), "PoC 테스트용 가상 데이터", "test_campaign.json"),
        ("product_name", brief.get("product_name", ""), "PoC 테스트용 가상 데이터", "test_campaign.json"),
        ("product_description", brief.get("product_description", ""), "PoC 테스트용 가상 데이터 (가격 포함)", "test_campaign.json"),
        ("target_audience", brief.get("target_audience", ""), "PoC 테스트용 가상 데이터", "test_campaign.json"),
        ("campaign_message", brief.get("campaign_message", ""), "PoC 테스트용 가상 데이터", "test_campaign.json"),
        ("season", brief.get("season", ""), "PoC 테스트용 가상 데이터", "test_campaign.json"),
        ("campaign_type", brief.get("campaign_type", ""), "PoC 테스트용 가상 데이터", "test_campaign.json"),
    ]
    for field, value, source, file in brief_fields:
        brief_rows += f'    <tr><td><code>{field}</code></td><td>{value}</td><td><span class="tag tag-orange">{source}</span></td><td><code>{file}</code></td></tr>\n'

    # Data lineage for generated outputs
    gen_rows = ""
    gen_items = [
        ("페르소나 프로필", f"{len(personas)}명 (이름, 나이, 직업, 성격...)", "Claude Opus 4.6 생성", "LLM이 브리프+아키타입을 기반으로 창작"),
        ("반응 시뮬레이션", "참여율, 감성, 공유확률, 구매의향, SNS 반응", "Claude Opus 4.6 생성", "LLM이 페르소나 역할극으로 반응 추정"),
        ("KPI 집계", "참여율 83%, 감성 +0.63, 바이럴 60%...", "통계 계산 (Python)", "개별 반응값의 산술 평균/카운팅"),
        ("리스크 플래그", "가격 민감도 리스크", "규칙 기반 (Python)", "5가지 임계값 규칙으로 자동 판정"),
        ("추천사항", "3가지 실행 가능한 제안", "Claude Opus 4.6 생성", "KPI 결과를 LLM에 제공하여 생성"),
    ]
    for item, content, source, method in gen_items:
        if "LLM" in source or "Claude" in source:
            tag_class = "tag-red"
            tag_text = "AI 생성"
        elif "Python" in source:
            tag_class = "tag-green"
            tag_text = "계산"
        else:
            tag_class = ""
            tag_text = source
        gen_rows += f'    <tr><td>{item}</td><td style="font-size:0.82rem;">{content}</td><td><span class="tag {tag_class}">{tag_text}</span></td><td style="font-size:0.82rem; color:var(--text-dim);">{method}</td></tr>\n'

    return f"""
<h2>근거 데이터 대시보드</h2>
<p style="color:var(--text-dim);">이 리포트의 모든 데이터 출처와 실제/가상 여부를 투명하게 공개합니다.</p>

<div class="card card-orange">
  <h3 style="color:var(--orange);">&#9888; 데이터 신뢰도 안내</h3>
  <p>현재 PoC 단계로, <strong>실제 F&amp;F 시스템과 연결되지 않은 가상 데이터</strong>를 사용합니다.</p>
  <table>
    <tr><th>데이터 유형</th><th>출처</th><th>신뢰도</th><th>프로덕션 연결 시</th></tr>
    <tr><td>캠페인 브리프 (제품, 가격, 메시지)</td><td>test_campaign.json (PoC용 가상 데이터)</td><td><span class="tag tag-red">가상</span></td><td>마케팅팀 브리프 DB / Notion</td></tr>
    <tr><td>브랜드 메타데이터</td><td>shared/fnf_brands.py (하드코딩)</td><td><span class="tag tag-orange">수동 정의</span></td><td>fnf_kg (Snowflake KG)</td></tr>
    <tr><td>소비자 아키타입 설정</td><td>shared/korean_config.py (하드코딩)</td><td><span class="tag tag-orange">수동 정의</span></td><td>fnf_enter 크롤 데이터 기반 보정</td></tr>
    <tr><td>페르소나 &amp; 반응</td><td>Claude Opus 4.6 (LLM 생성)</td><td><span class="tag tag-red">AI 추정</span></td><td>실제 소비자 설문/FGI로 검증</td></tr>
    <tr><td>KPI 수치</td><td>Python 통계 계산</td><td><span class="tag tag-green">계산값</span></td><td>과거 캠페인 실적 대비 백테스트</td></tr>
  </table>
</div>

<details>
  <summary>&#128202; 캠페인 브리프 입력 데이터 (사용자 입력)</summary>
  <div class="detail-content">
    <p>API에 전달된 원본 JSON 데이터입니다. 이 값들이 전체 분석의 시작점입니다.</p>
    <table>
      <tr><th>필드</th><th>값</th><th>출처</th><th>파일</th></tr>
{brief_rows}
    </table>
    <pre>
// test_campaign.json (API 호출 시 전달된 원본)
{{
  "brand": "{brief.get('brand_key','')}",
  "product_name": "{brief.get('product_name','')}",
  "product_description": "{brief.get('product_description','')}",
  "target_audience": "{brief.get('target_audience','')}",
  "campaign_message": "{brief.get('campaign_message','')}",
  "season": "{brief.get('season','')}",
  "campaign_type": "{brief.get('campaign_type','')}"
}}</pre>
  </div>
</details>

<details>
  <summary>&#127959; 브랜드 DB: {brand} (하드코딩 — shared/fnf_brands.py)</summary>
  <div class="detail-content">
    <p><code>FNF_BRANDS["{brand}"]</code>에서 로드된 브랜드 메타데이터입니다.</p>
    <table>
      <tr><th>항목</th><th>값</th></tr>
{brand_rows}
    </table>
    <div class="formula">
      출처: <code>shared/fnf_brands.py</code> (수동 정의)<br>
      프로덕션: <code>fnf_kg</code> Snowflake KG에서 실시간 조회로 교체 필요
    </div>
  </div>
</details>

<details>
  <summary>&#128101; 소비자 아키타입 설정 (하드코딩 — shared/korean_config.py)</summary>
  <div class="detail-content">
    <p>한국 패션 시장 소비자를 5가지 아키타입으로 분류한 설정값입니다.</p>
    <table style="font-size:0.82rem;">
      <tr><th>아키타입</th><th>연령대</th><th>특징</th><th>주 플랫폼</th><th>패션관심</th><th>가격민감</th><th>충성도</th></tr>
{arch_rows}
    </table>
    <div class="formula">
      출처: <code>shared/korean_config.py</code> (수동 정의)<br>
      프로덕션: <code>fnf_enter</code> 실제 SNS 크롤 데이터의 오디언스 인사이트로 보정 필요
    </div>
  </div>
</details>

<details>
  <summary>&#129302; 생성된 데이터 계보 (AI 생성 vs 계산)</summary>
  <div class="detail-content">
    <p>각 결과물이 어떤 방법으로 생성되었는지 추적합니다.</p>
    <table>
      <tr><th>결과물</th><th>내용</th><th>생성 방법</th><th>상세</th></tr>
{gen_rows}
    </table>
    <div class="formula" style="border-color: var(--red);">
      <strong style="color:var(--red);">&#9888; AI 생성 데이터 주의</strong><br>
      <span class="tag tag-red">AI 생성</span> 표시된 항목은 Claude Opus 4.6의 학습 패턴 기반 추정이며,<br>
      실제 시장 데이터가 아닙니다. 의사결정 참고용으로만 활용하세요.
    </div>
  </div>
</details>"""


# ── Section: Pipeline Map ──

def _section_pipeline_map():
    steps = [
        ("STEP 1", "Seed 생성", "템플릿"),
        ("STEP 2", "패널 구성", "LLM"),
        ("STEP 3", "반응 시뮬", "LLM"),
        ("STEP 4", "KPI 집계", "통계"),
        ("STEP 5", "리스크 감지", "규칙"),
        ("STEP 6", "추천 생성", "LLM"),
    ]
    html = '<h2>Agent 숙의 파이프라인</h2>\n<div class="pipeline">\n'
    for i, (num, label, typ) in enumerate(steps):
        html += f'  <div class="pipe-step"><div class="step-num">{num}</div><div class="step-label">{label}</div><div class="step-type">{typ}</div></div>\n'
        if i < len(steps) - 1:
            html += '  <div class="pipe-arrow">&rarr;</div>\n'
    html += '</div>'
    return html


# ── Section: Step 1 — Seed ──

def _section_step1_seed(brief, brand):
    desc = brief.get("product_description", "")
    target = brief.get("target_audience", "")
    msg = brief.get("campaign_message", "")
    season = brief.get("season", "")
    ctype = brief.get("campaign_type", "")

    return f"""
<h2>Step 1: Seed 생성 (템플릿 조합, LLM 없음)</h2>
<div class="card card-accent">
  <h3>입력된 캠페인 브리프</h3>
  <table>
    <tr><th>항목</th><th>값</th></tr>
    <tr><td>브랜드</td><td><strong>{brand}</strong></td></tr>
    <tr><td>제품</td><td>{brief.get('product_name','')}</td></tr>
    <tr><td>설명</td><td>{desc}</td></tr>
    <tr><td>타겟</td><td>{target}</td></tr>
    <tr><td>메시지</td><td>"{msg}"</td></tr>
    <tr><td>시즌</td><td>{season} ({'봄/여름' if season=='SS' else '가을/겨울'})</td></tr>
    <tr><td>유형</td><td>{ctype}</td></tr>
  </table>
</div>

<div class="card">
  <h3>Seed 생성 로직</h3>
  <p>LLM을 호출하지 않고 순수 템플릿 조합으로 생성합니다:</p>
  <pre>
1. FNF_BRANDS["{brand}"] 에서 브랜드 메타데이터 로드
   &rarr; 포지셔닝, 경쟁사, 가격대, 주요 시장 등

2. templates/brand_contexts.json 에서 브랜드 소개문 + 시즌 키워드 추출
   &rarr; {season} 시즌 키워드 포함

3. 5개 섹션을 조합하여 ~800자 seed_text 생성:
   [브랜드 개요] + [제품 정보] + [캠페인 브리프] + [시장 컨텍스트] + [추가 컨텍스트]

4. get_archetype_distribution("{brand}") 로 소비자 아키타입 가중치 로드
</pre>
</div>"""


# ── Section: Step 2 — Panel ──

def _section_step2_panel(personas, arch_dist, brand, brief):
    weights = DEFAULT_WEIGHTS
    panel_size = len(personas)

    # Weight table
    weight_rows = ""
    for key, w in weights.items():
        label = ARCHETYPE_LABELS.get(key, key)
        actual = arch_dist.get(key, 0)
        raw = w * panel_size
        weight_rows += f"    <tr><td>{label}</td><td>{w:.0%}</td><td>{raw:.2f}</td><td><strong>{actual}명</strong></td></tr>\n"

    # Persona cards
    persona_cards = ""
    emojis = {"mz_trendsetter": "🔥", "student": "📚", "fashion_enthusiast": "👗", "office_worker": "💼", "value_shopper": "💰"}
    for p in personas:
        emoji = emojis.get(p.get("archetype", ""), "👤")
        arch_label = ARCHETYPE_LABELS.get(p.get("archetype", ""), p.get("archetype", ""))
        persona_cards += f"""
    <div class="persona-card">
      <div class="persona-avatar">{emoji}</div>
      <div>
        <strong>{p.get('name','')}</strong>
        <span class="tag">{p.get('persona_id','')}</span>
        <span class="tag">{arch_label}</span>
        <span style="color:var(--text-dim); font-size:0.85rem;"> &middot; {p.get('age','')}세 {p.get('gender','')} &middot; {p.get('occupation','')[:50]}</span>
        <div style="margin-top:6px; font-size:0.85rem; color:var(--text-dim);">{p.get('personality','')[:150]}...</div>
      </div>
    </div>"""

    return f"""
<h2>Step 2: 소비자 패널 구성 (LLM 기반)</h2>

<div class="card card-accent">
  <h3>아키타입 가중치 &rarr; 인원 배분</h3>
  <p>{brand} 브랜드의 타겟 소비자 분포에 따라 패널을 구성합니다:</p>
  <table>
    <tr><th>아키타입</th><th>가중치</th><th>가중치 &times; {panel_size}</th><th>실제 배분</th></tr>
{weight_rows}
  </table>
  <div class="formula">
    배분 로직: floor(가중치 &times; 패널크기) 후, 소수점이 큰 순서대로 나머지 1명씩 추가
  </div>
</div>

<details>
  <summary>LLM 프롬프트 (소비자 생성용)</summary>
  <div class="detail-content">
    <h3>System Prompt</h3>
    <pre>당신은 한국 패션 시장의 소비자 페르소나 생성 전문가입니다.
다음 아키타입에 맞는 가상 소비자 N명을 생성하세요.

아키타입: [MZ 트렌드세터 / 학생 / 패션 마니아 / ...]
연령대: [20-29 / 15-22 / ...]
특징: [한국 시장 아키타입 설명]
행동 특성: [early_adopter, social_sharer, ...]
SNS 스타일: [비주얼 중심, 해시태그 활용, ...]

브랜드: {brand}
캠페인: {brief.get('campaign_message','')}
제품: {brief.get('product_name','')}
타겟: {brief.get('target_audience','')}</pre>
    <h3>User Prompt</h3>
    <pre>JSON 배열 형식으로 N명의 페르소나를 생성하세요.
각 페르소나: name, age, gender, occupation, personality,
fashion_preferences, social_media_habits, brand_awareness,
price_sensitivity, influence_level

temperature=0.8 (다양성 확보) | max_tokens=4096 | 파싱 실패 시 2회 재시도</pre>
  </div>
</details>

<h3>생성된 소비자 패널 ({panel_size}명)</h3>
{persona_cards}"""


# ── Section: Step 3 — Reactions ──

def _section_step3_reactions(reactions, personas):
    persona_map = {p.get("persona_id"): p for p in personas}

    reaction_cards = ""
    for r in reactions:
        pid = r.get("persona_id", "")
        p = persona_map.get(pid, {})
        name = p.get("name", pid)
        arch = ARCHETYPE_LABELS.get(p.get("archetype", ""), "")
        eng = r.get("engagement_likelihood", 0)
        sent = r.get("sentiment", "neutral")
        sent_score = r.get("sentiment_score", 0)
        share = r.get("share_probability", 0)
        purchase = r.get("purchase_intent", 0)
        text = r.get("reaction_text", "")
        appeals = r.get("appeal_points", [])
        concerns = r.get("concerns", [])

        sent_color = SENTIMENT_COLORS.get(sent, "#94a3b8")
        sent_label = SENTIMENT_LABELS.get(sent, sent)

        appeal_tags = " ".join(f'<span class="tag tag-green">{a[:40]}</span>' for a in appeals[:3])
        concern_tags = " ".join(f'<span class="tag tag-orange">{c[:40]}</span>' for c in concerns[:3])

        bar_color = f"hsl({int(eng*120)}, 70%, 50%)"
        share_color = f"hsl({int(share*120)}, 70%, 50%)"
        purchase_color = f"hsl({int(purchase*120)}, 70%, 50%)"

        reaction_cards += f"""
    <details>
      <summary>{pid} {name} ({arch}) &mdash; 참여 {eng:.0%} | 감성 <span style="color:{sent_color}">{sent_label}</span> | 공유 {share:.0%} | 구매 {purchase:.0%}</summary>
      <div class="detail-content">
        <div class="reaction-text">&ldquo;{text}&rdquo;</div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:0.8rem;">
          <div>
            <strong>참여 가능성</strong>
            <div class="bar"><div class="bar-fill" style="width:{eng:.0%}; background:{bar_color};">{eng:.0%}</div></div>
            <strong>공유 확률</strong>
            <div class="bar"><div class="bar-fill" style="width:{share:.0%}; background:{share_color};">{share:.0%}</div></div>
            <strong>구매 의향</strong>
            <div class="bar"><div class="bar-fill" style="width:{purchase:.0%}; background:{purchase_color};">{purchase:.0%}</div></div>
            <strong>감성</strong>
            <div class="bar"><div class="bar-fill" style="width:{max(0,(sent_score+1)/2):.0%}; background:{sent_color};">{sent_label} ({sent_score:+.2f})</div></div>
          </div>
          <div>
            <strong style="color:var(--green);">매력 포인트</strong><br>{appeal_tags or '<span class="tag">없음</span>'}
            <br><br>
            <strong style="color:var(--orange);">우려사항</strong><br>{concern_tags or '<span class="tag">없음</span>'}
          </div>
        </div>
      </div>
    </details>"""

    return f"""
<h2>Step 3: 반응 시뮬레이션 (LLM 기반)</h2>

<div class="card card-accent">
  <h3>시뮬레이션 방식</h3>
  <p>각 페르소나에게 캠페인 정보를 보여주고, LLM이 해당 인물의 관점에서 반응을 시뮬레이션합니다.</p>
  <div class="formula">
    배치 처리: {len(reactions)}명을 5명씩 묶어 {max(1, (len(reactions)+4)//5)}회 LLM 호출<br>
    temperature=0.7 (현실적 다양성) | "모든 사람이 긍정적일 필요는 없습니다" 지시
  </div>
</div>

<details>
  <summary>LLM 프롬프트 (반응 시뮬레이션용)</summary>
  <div class="detail-content">
    <pre>
[System] 당신은 한국 패션 마케팅 소비자 반응 시뮬레이터입니다.
각 소비자가 아래 캠페인을 접했을 때의 반응을 시뮬레이션하세요.
현실적이고 다양한 반응을 생성하세요. 모든 사람이 긍정적일 필요는 없습니다.

[User] 캠페인 정보 + 각 페르소나의 프로필 요약을 제공
&rarr; 각 페르소나별로:
   engagement_likelihood (0-1), sentiment, sentiment_score (-1~1),
   share_probability (0-1), purchase_intent (0-1),
   reaction_text (SNS 반응), concerns[], appeal_points[]</pre>
  </div>
</details>

<h3>개별 페르소나 반응 상세</h3>
{reaction_cards}"""


# ── Section: Step 4 — KPI ──

def _section_step4_kpi(kpi, reactions):
    eng_values = [r.get("engagement_likelihood", 0) for r in reactions]
    sent_values = [r.get("sentiment_score", 0) for r in reactions]
    share_values = [r.get("share_probability", 0) for r in reactions]
    purchase_values = [r.get("purchase_intent", 0) for r in reactions]
    n = len(reactions)

    eng_calc = " + ".join(f"{v:.2f}" for v in eng_values)
    sent_calc = " + ".join(f"{v:.2f}" for v in sent_values)
    purchase_calc = " + ".join(f"{v:.2f}" for v in purchase_values)

    viral_count = sum(1 for v in share_values if v > 0.6)
    viral_detail = ", ".join(f"{v:.2f}{'✓' if v > 0.6 else ''}" for v in share_values)

    # Sentiment distribution
    sent_dist = kpi.get("sentiment_distribution", {})
    sent_bars = ""
    for key in ["very_positive", "positive", "neutral", "negative", "very_negative"]:
        pct = sent_dist.get(key, 0)
        if pct > 0:
            color = SENTIMENT_COLORS.get(key, "#94a3b8")
            label = SENTIMENT_LABELS.get(key, key)
            sent_bars += f'<div class="bar"><div class="bar-fill" style="width:{pct:.0%}; background:{color};">{label} {pct:.0%}</div></div>\n'

    strongest = ARCHETYPE_LABELS.get(kpi.get("strongest_archetype", ""), kpi.get("strongest_archetype", ""))
    weakest = ARCHETYPE_LABELS.get(kpi.get("weakest_archetype", ""), kpi.get("weakest_archetype", ""))

    return f"""
<h2>Step 4: KPI 집계 (통계적 계산)</h2>
<p>LLM 호출 없이, 개별 반응 데이터를 순수 Python으로 집계합니다.</p>

<div class="card card-accent">
  <h3>예측 참여율</h3>
  <div class="formula">
    ({eng_calc}) / {n}<br>
    = <span class="result">{kpi.get('predicted_engagement_rate',0):.3f} ({kpi.get('predicted_engagement_rate',0):.0%})</span>
  </div>
</div>

<div class="card card-accent">
  <h3>평균 감성 점수</h3>
  <div class="formula">
    ({sent_calc}) / {n}<br>
    = <span class="result">{kpi.get('average_sentiment_score',0):+.3f}</span> (범위: -1.0 ~ +1.0)
  </div>
  <h3>감성 분포</h3>
  {sent_bars}
</div>

<div class="card card-accent">
  <h3>바이럴 확률</h3>
  <div class="formula">
    share_probability &gt; 0.6 인 페르소나 수 / 전체<br>
    [{viral_detail}]<br>
    = {viral_count} / {n} = <span class="result">{kpi.get('viral_probability',0):.0%}</span>
  </div>
</div>

<div class="card card-accent">
  <h3>평균 구매 의향</h3>
  <div class="formula">
    ({purchase_calc}) / {n}<br>
    = <span class="result">{kpi.get('average_purchase_intent',0):.3f} ({kpi.get('average_purchase_intent',0):.0%})</span>
  </div>
</div>

<div class="card">
  <h3>아키타입별 비교</h3>
  <div style="display:flex; gap:1rem; justify-content:center; margin:1rem 0;">
    <div class="kpi-box" style="border:1px solid var(--green);">
      <div style="font-size:1.5rem;">🏆</div>
      <div style="font-weight:700; color:var(--green);">{strongest}</div>
      <div class="kpi-label">가장 반응 좋은 세그먼트</div>
    </div>
    <div class="kpi-box" style="border:1px solid var(--orange);">
      <div style="font-size:1.5rem;">⚠️</div>
      <div style="font-weight:700; color:var(--orange);">{weakest}</div>
      <div class="kpi-label">가장 반응 약한 세그먼트</div>
    </div>
  </div>
</div>"""


# ── Section: Step 5 — Risk ──

def _section_step5_risk(risk_flags, kpi, reactions):
    n = len(reactions)
    price_count = sum(1 for r in reactions if any(
        kw in c for c in r.get("concerns", []) for kw in ["가격", "비싸", "비쌈", "부담", "89000", "89,000"]
    ))

    rules = [
        ("부정적 감성 우세", f"avg_sentiment < 0.0", f"{kpi.get('average_sentiment_score',0):+.3f}", kpi.get("average_sentiment_score", 0) < 0.0, "high"),
        ("낮은 참여율", f"engagement_rate < 0.3", f"{kpi.get('predicted_engagement_rate',0):.3f}", kpi.get("predicted_engagement_rate", 0) < 0.3, "medium"),
        ("낮은 바이럴 가능성", f"viral_probability < 0.1", f"{kpi.get('viral_probability',0):.3f}", kpi.get("viral_probability", 0) < 0.1, "medium"),
        ("낮은 구매 의향", f"purchase_intent < 0.3", f"{kpi.get('average_purchase_intent',0):.3f}", kpi.get("average_purchase_intent", 0) < 0.3, "high"),
        ("가격 민감도 리스크", f"가격우려 비율 > 30%", f"{price_count}/{n} ({price_count/max(n,1):.0%})", price_count / max(n, 1) > 0.3, "medium"),
    ]

    rows = ""
    for name, condition, actual, triggered, level in rules:
        icon = '<span class="cross">TRIGGERED</span>' if triggered else '<span class="check">PASS</span>'
        rows += f"    <tr><td>{name}</td><td><code>{condition}</code></td><td>{actual}</td><td>{icon}</td></tr>\n"

    flag_html = ""
    if risk_flags:
        for f in risk_flags:
            level = f.get("level", "medium")
            flag_html += f'<div class="risk-badge risk-{level}">⚠ {f.get("flag","")} — {f.get("detail","")}</div><br>'
    else:
        flag_html = '<span class="tag tag-green">리스크 없음</span>'

    return f"""
<h2>Step 5: 리스크 감지 (규칙 기반)</h2>
<p>5가지 규칙을 순차 평가하여 자동으로 리스크 플래그를 생성합니다.</p>

<div class="card card-accent">
  <table>
    <tr><th>규칙</th><th>임계값</th><th>실제 값</th><th>판정</th></tr>
{rows}
  </table>
</div>

<div class="card {'card-orange' if risk_flags else 'card-green'}">
  <h3>감지된 리스크</h3>
  {flag_html}
</div>"""


# ── Section: Step 6 — Recommendations ──

def _section_step6_recommendations(recommendations, kpi, risk_flags):
    rec_html = ""
    for i, rec in enumerate(recommendations, 1):
        rec_html += f"""
    <div class="card card-green">
      <strong>추천 {i}</strong>
      <p style="margin-top:6px;">{rec}</p>
    </div>"""

    risk_summary = ", ".join(f.get("flag", "") for f in risk_flags) if risk_flags else "특이사항 없음"
    strongest = ARCHETYPE_LABELS.get(kpi.get("strongest_archetype", ""), kpi.get("strongest_archetype", ""))
    weakest = ARCHETYPE_LABELS.get(kpi.get("weakest_archetype", ""), kpi.get("weakest_archetype", ""))
    appeals = kpi.get("top_appeal_points", [])[:3]
    concerns = kpi.get("top_concerns", [])[:3]

    return f"""
<h2>Step 6: 추천사항 생성 (LLM 기반)</h2>

<details>
  <summary>LLM 프롬프트 (추천 생성용)</summary>
  <div class="detail-content">
    <pre>다음 캠페인 사전 테스트 결과를 바탕으로 3가지 핵심 추천사항을 제시하세요.

KPI 결과:
- 예측 참여율: {kpi.get('predicted_engagement_rate',0):.1%}
- 평균 감성: {kpi.get('average_sentiment_score',0):.2f}
- 바이럴 확률: {kpi.get('viral_probability',0):.1%}
- 구매 의향: {kpi.get('average_purchase_intent',0):.1%}
- 가장 반응 좋은 세그먼트: {strongest}
- 가장 반응 약한 세그먼트: {weakest}
- 주요 매력 포인트: {', '.join(appeals)}
- 주요 우려사항: {', '.join(concerns)}

리스크: {risk_summary}

temperature=0.5 (일관성) | 각 추천사항은 1-2문장으로 구체적이고 실행 가능하게</pre>
  </div>
</details>

{rec_html}"""


# ── Footer ──

def _html_footer(data):
    created = data.get("created_at", "")[:19]
    cid = data.get("campaign_id", "")
    n_personas = len(data.get("persona_reactions", []))

    return f"""
<div style="margin-top:3rem; padding:1.5rem; text-align:center; color:var(--text-dim); font-size:0.8rem; border-top:1px solid var(--card-border);">
  FnF Marketing Simulator &middot; Campaign Pre-Test Report<br>
  Campaign ID: {cid} &middot; {n_personas} personas &middot; Generated: {created}<br>
  Powered by Claude Opus 4.6 + MiroFish Core Engine
</div>
</body>
</html>"""


# ── CLI Entry Point ──

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <poc_result.json> [output.html]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path.replace(".json", "_report.html")

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    html = generate_report_html(data)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report generated: {output_path} ({len(html):,} chars)")
