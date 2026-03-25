"""
FnF Marketing Simulator — Flask Entry Point
MiroFish 코어 엔진 기반 F&F 마케팅 시뮬레이터
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore", message=".*resource_tracker.*")

from flask import Flask, request, jsonify
from flask_cors import CORS

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core.config import Config
from core.utils.logger import setup_logger, get_logger


def create_app(config_class=Config):
    """Flask app factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # JSON: allow Korean/Chinese characters directly
    if hasattr(app, 'json') and hasattr(app.json, 'ensure_ascii'):
        app.json.ensure_ascii = False

    logger = setup_logger('fnf-mkt-sim')

    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    debug_mode = app.config.get('DEBUG', False)
    should_log_startup = not debug_mode or is_reloader_process

    if should_log_startup:
        logger.info("=" * 50)
        logger.info("FnF Marketing Simulator 시작...")
        logger.info("=" * 50)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register simulation cleanup (requires camel-oasis)
    try:
        from core.simulation_runner import SimulationRunner
        SimulationRunner.register_cleanup()
    except ImportError:
        if should_log_startup:
            logger.info("  [--] OASIS not installed — simulation cleanup skipped")

    # Request logging
    @app.before_request
    def log_request():
        req_logger = get_logger('fnf-mkt-sim.request')
        req_logger.debug(f"Request: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        req_logger = get_logger('fnf-mkt-sim.request')
        req_logger.debug(f"Response: {response.status_code}")
        return response

    # ── Health Check ──
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'ok',
            'service': 'FnF Marketing Simulator',
            'version': '0.1.0',
            'modules': _get_active_modules()
        })

    # ── Register module blueprints (순차 개발 — 구현된 모듈만 등록) ──
    _register_modules(app, logger, should_log_startup)

    if should_log_startup:
        logger.info("FnF Marketing Simulator 시작 완료")

    return app


def _get_active_modules():
    """Return list of implemented modules"""
    modules = []
    try:
        from modules.m1_campaign_test.api import campaign_bp  # noqa: F401
        modules.append('m1_campaign_test')
    except ImportError:
        pass
    try:
        from modules.m2_trend_predict.api import trend_bp  # noqa: F401
        modules.append('m2_trend_predict')
    except ImportError:
        pass
    try:
        from modules.m3_influencer_sim.api import influencer_bp  # noqa: F401
        modules.append('m3_influencer_sim')
    except ImportError:
        pass
    try:
        from modules.m4_market_entry.api import market_bp  # noqa: F401
        modules.append('m4_market_entry')
    except ImportError:
        pass
    try:
        from modules.m5_competitive_war.api import competitive_bp  # noqa: F401
        modules.append('m5_competitive_war')
    except ImportError:
        pass
    return modules


def _register_modules(app, logger, should_log):
    """Register available module blueprints"""
    module_registry = [
        ('modules.m1_campaign_test.api', 'campaign_bp', '/api/campaign', 'M1: Campaign Test'),
        ('modules.m2_trend_predict.api', 'trend_bp', '/api/trend', 'M2: Trend Predict'),
        ('modules.m3_influencer_sim.api', 'influencer_bp', '/api/influencer', 'M3: Influencer Sim'),
        ('modules.m4_market_entry.api', 'market_bp', '/api/market', 'M4: Market Entry'),
        ('modules.m5_competitive_war.api', 'competitive_bp', '/api/competitive', 'M5: Competitive War'),
    ]

    for module_path, bp_name, url_prefix, label in module_registry:
        try:
            mod = __import__(module_path, fromlist=[bp_name])
            bp = getattr(mod, bp_name)
            app.register_blueprint(bp, url_prefix=url_prefix)
            if should_log:
                logger.info(f"  [OK] {label} registered at {url_prefix}")
        except ImportError:
            if should_log:
                logger.info(f"  [--] {label} not yet implemented")
        except Exception as e:
            if should_log:
                logger.warning(f"  [!!] {label} failed to load: {e}")


def main():
    errors = Config.validate()
    if errors:
        print("Configuration errors:")
        for e in errors:
            print(f"  - {e}")
        print("\nCopy .env.example to .env and fill in your API keys.")
        sys.exit(1)

    app = create_app()
    app.run(host='0.0.0.0', port=5002, debug=True, threaded=True)


if __name__ == '__main__':
    main()
