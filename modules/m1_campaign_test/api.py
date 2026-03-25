"""
Campaign Pre-Test API Blueprint
/api/campaign/* 엔드포인트
"""

import threading
from flask import Blueprint, request, jsonify

from core.utils.llm_client import LLMClient
from .campaign_seed import CampaignBrief, CampaignSeedGenerator
from .fashion_ontology import FashionOntologyService
from .consumer_profiles import ConsumerPanelGenerator
from .campaign_scorer import CampaignScorer

campaign_bp = Blueprint('campaign', __name__)

# In-memory session store (PoC)
_sessions = {}  # campaign_id → { status, seed, panel, report, error }


def _run_pipeline(campaign_id: str, brief: CampaignBrief, mode: str, panel_size: int):
    """백그라운드 스레드에서 파이프라인 실행"""
    session = _sessions[campaign_id]
    try:
        llm = LLMClient()

        # Step 1: Seed 생성
        session['status'] = 'generating_seed'
        session['progress'] = 5
        gen = CampaignSeedGenerator()
        seed = gen.generate_seed(brief)
        session['seed'] = seed

        # Step 2: Full Mode — 그래프 구축 (TODO: 추후 구현)
        graph_entities = None
        if mode == 'full':
            session['status'] = 'building_graph'
            session['progress'] = 10
            # FashionOntologyService + GraphBuilder + ZepEntityReader
            # 현재 PoC에서는 quick mode와 동일하게 처리
            session['message'] = 'Full mode 그래프 구축은 추후 구현 예정. Quick 분석으로 진행합니다.'

        # Step 3: 소비자 패널 생성
        session['status'] = 'generating_panel'
        session['progress'] = 30
        session['message'] = f'{panel_size}명 가상 소비자 패널 생성 중...'
        panel_gen = ConsumerPanelGenerator(llm_client=llm)
        panel = panel_gen.generate_panel(seed, panel_size=panel_size, graph_entities=graph_entities)
        session['panel'] = panel
        session['progress'] = 60

        # Step 4: 반응 시뮬레이션 + KPI
        session['status'] = 'scoring'
        session['message'] = '캠페인 반응 시뮬레이션 중...'
        scorer = CampaignScorer(llm_client=llm)
        report = scorer.score_campaign(seed, panel, mode=mode, graph_entities=graph_entities)
        session['report'] = report
        session['progress'] = 95

        # Step 5: 완료
        session['status'] = 'completed'
        session['progress'] = 100
        session['message'] = '분석 완료'

    except Exception as e:
        session['status'] = 'failed'
        session['error'] = str(e)
        session['message'] = f'오류 발생: {str(e)}'


# ── Endpoints ──

@campaign_bp.route('/test', methods=['POST'])
def start_campaign_test():
    """캠페인 사전 테스트 시작"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    try:
        brief = CampaignBrief(
            brand_key=data.get('brand', ''),
            product_name=data.get('product_name', ''),
            product_description=data.get('product_description', ''),
            target_audience=data.get('target_audience', ''),
            campaign_message=data.get('campaign_message', ''),
            season=data.get('season', 'SS'),
            campaign_type=data.get('campaign_type', 'launch'),
            budget_level=data.get('budget_level', 'mid'),
            additional_context=data.get('additional_context', ''),
        )
        brief.validate()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    mode = data.get('mode', 'quick')
    panel_size = min(int(data.get('panel_size', 15)), 30)  # max 30

    # 세션 초기화
    import uuid
    campaign_id = str(uuid.uuid4())[:8]
    _sessions[campaign_id] = {
        'status': 'started',
        'progress': 0,
        'message': '분석 시작...',
        'mode': mode,
        'brief': brief.to_dict(),
        'seed': None,
        'panel': None,
        'report': None,
        'error': None,
    }

    # 백그라운드 스레드 시작
    thread = threading.Thread(
        target=_run_pipeline,
        args=(campaign_id, brief, mode, panel_size),
        daemon=True,
    )
    thread.start()

    return jsonify({
        "campaign_id": campaign_id,
        "status": "processing",
        "mode": mode,
        "panel_size": panel_size,
    }), 202


@campaign_bp.route('/status/<campaign_id>', methods=['GET'])
def get_campaign_status(campaign_id):
    """캠페인 테스트 진행 상태"""
    session = _sessions.get(campaign_id)
    if not session:
        return jsonify({"error": f"Campaign {campaign_id} not found"}), 404

    return jsonify({
        "campaign_id": campaign_id,
        "status": session['status'],
        "progress": session.get('progress', 0),
        "message": session.get('message', ''),
        "mode": session.get('mode', 'quick'),
    })


@campaign_bp.route('/result/<campaign_id>', methods=['GET'])
def get_campaign_result(campaign_id):
    """캠페인 테스트 결과 조회"""
    session = _sessions.get(campaign_id)
    if not session:
        return jsonify({"error": f"Campaign {campaign_id} not found"}), 404

    if session['status'] == 'failed':
        return jsonify({
            "campaign_id": campaign_id,
            "status": "failed",
            "error": session.get('error', 'Unknown error'),
        }), 500

    if session['status'] != 'completed':
        return jsonify({
            "campaign_id": campaign_id,
            "status": session['status'],
            "progress": session.get('progress', 0),
            "message": "분석이 아직 진행 중입니다. /status 엔드포인트를 확인하세요.",
        }), 202

    report = session.get('report')
    if not report:
        return jsonify({"error": "Report not found"}), 500

    return jsonify({
        "campaign_id": campaign_id,
        "status": "completed",
        "report": report.to_dict(),
    })


@campaign_bp.route('/interview', methods=['POST'])
def interview_persona():
    """가상 소비자 인터뷰"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    campaign_id = data.get('campaign_id', '')
    persona_id = data.get('persona_id', '')
    question = data.get('question', '')
    history = data.get('conversation_history', [])

    if not all([campaign_id, persona_id, question]):
        return jsonify({"error": "campaign_id, persona_id, question are required"}), 400

    session = _sessions.get(campaign_id)
    if not session or session['status'] != 'completed':
        return jsonify({"error": "Campaign not found or not yet completed"}), 404

    panel = session.get('panel')
    seed_obj = session.get('seed')
    if not panel or not seed_obj:
        return jsonify({"error": "Panel or seed data not available"}), 500

    # 페르소나 찾기
    persona = None
    for p in panel.personas:
        if p.persona_id == persona_id:
            persona = p
            break

    if not persona:
        available = [p.persona_id for p in panel.personas]
        return jsonify({"error": f"Persona {persona_id} not found. Available: {available}"}), 404

    llm = LLMClient()
    scorer = CampaignScorer(llm_client=llm)
    response_text = scorer.interview_persona(persona, seed_obj, question, history)

    # 대화 기록 업데이트
    updated_history = list(history)
    updated_history.append({"role": "user", "content": question})
    updated_history.append({"role": "assistant", "content": response_text})

    return jsonify({
        "persona_id": persona_id,
        "persona_name": persona.name,
        "archetype": persona.archetype,
        "response": response_text,
        "conversation_history": updated_history,
    })
