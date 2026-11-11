"""Flask routes for the Intelligent Financial Platform web UI.

All heavy work (model training / prediction) is delegated to ``app.pipeline.run_pipeline``
which is executed in a background thread via ``app.cache_utils.run_background_task``.
The UI polls ``/status/<run_id>`` to know when the job is done.
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file, abort
import base64
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from . import cache_utils
from .cache_utils import run_background_task, load_run_result, get_cached_result, set_cached_result
from .logger import get_logger
from . import pipeline

bp = Blueprint('main', __name__)
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _parse_model_list(form):
    """Return a list of model identifiers selected by the user.
    The HTML form submits checkboxes named ``model_<name>``; we collect those that are "on".
    """
    models = []
    for key, value in form.items():
        if key.startswith('model_') and value == 'on':
            models.append(key.replace('model_', ''))
    return models

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@bp.route('/', methods=['GET'])
def index():
    # Load universe metadata (exchanges, indices, index_stocks)
    from pathlib import Path
    data_path = Path(__file__).parent.parent / 'data' / 'market_universe.json'
    exchanges = [
        {"key": "NSE", "label": "National Stock Exchange (NSE)"},
        {"key": "BSE", "label": "Bombay Stock Exchange (BSE)"},
        {"key": "NYSE", "label": "New York Stock Exchange (NYSE)"},
        {"key": "NASDAQ", "label": "Nasdaq Stock Market (NASDAQ)"}
    ]
    indices = {
        "NSE": [
            {"key": "ALL", "label": "All NSE Stocks (No Index Filter)"},
            {"key": "NIFTY_50", "label": "NIFTY 50 (Benchmark)"},
            {"key": "NIFTY_NEXT_50", "label": "Nifty Next 50"},
            {"key": "NIFTY_100", "label": "Nifty 100"},
            {"key": "NIFTY_200", "label": "Nifty 200"},
            {"key": "NIFTY_500", "label": "Nifty 500"}
        ],
        "BSE": [
            {"key": "ALL", "label": "All BSE Stocks (No Index Filter)"},
            {"key": "SENSEX", "label": "BSE SENSEX (Benchmark 30)"},
            {"key": "BSE_100", "label": "BSE 100"},
            {"key": "BSE_200", "label": "BSE 200"},
            {"key": "BSE_500", "label": "BSE 500"},
            {"key": "BSE_MIDCAP", "label": "BSE MidCap"},
            {"key": "BSE_SMALLCAP", "label": "BSE SmallCap"}
        ],
        "NYSE": [
            {"key": "ALL", "label": "All NYSE Stocks (No Index Filter)"},
            {"key": "NYSE_COMPOSITE", "label": "NYSE Composite Index"},
            {"key": "DJIA", "label": "Dow Jones Industrial Average (DJIA)"},
            {"key": "SP500_NYSE", "label": "S&P 500 (NYSE Constituents)"}
        ],
        "NASDAQ": [
            {"key": "ALL", "label": "All Nasdaq Stocks (No Index Filter)"},
            {"key": "NASDAQ_COMPOSITE", "label": "Nasdaq Composite"},
            {"key": "NASDAQ_100", "label": "Nasdaq-100"},
            {"key": "SP500_NASDAQ", "label": "S&P 500 (Nasdaq Constituents)"}
        ]
    }
    index_stocks = {}
    if data_path.exists():
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                raw_u = json.load(f)
                exchanges = raw_u.get("exchanges", exchanges)
                indices = raw_u.get("indices", indices)
                index_stocks = raw_u.get("index_stocks", {})
        except Exception as e:
            logger.warning(f"Error loading market universe data: {e}")

    return render_template(
        'index.html',
        exchanges=exchanges,
        indices=indices,
        index_stocks=json.dumps(index_stocks)
    )

@bp.route('/api/stocks', methods=['GET'])
def search_stocks():
    """Live search endpoint querying stocks by exchange, index and query string."""
    exchange = request.args.get('exchange', '').upper().strip()
    index_key = request.args.get('index', '').strip()
    q = request.args.get('q', '').lower().strip()
    limit = int(request.args.get('limit', 50))

    from pathlib import Path
    data_path = Path(__file__).parent.parent / 'data' / 'market_universe.json'
    if not data_path.exists():
        return jsonify([])

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            universe = json.load(f)

        candidates = []
        if index_key and index_key != 'ALL':
            candidates = universe.get("index_stocks", {}).get(index_key, [])
        elif exchange:
            candidates = universe.get("exchange_stocks", {}).get(exchange, [])

        if not q:
            return jsonify(candidates[:limit])

        results = []
        for s in candidates:
            sym = s.get("id", "").lower()
            ticker = s.get("ticker", "").lower()
            name = s.get("name", "").lower()
            if q in sym or q in ticker or q in name:
                results.append(s)
                if len(results) >= limit:
                    break
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in search_stocks API: {e}")
        return jsonify([])

@bp.route('/run', methods=['POST'])
def run():
    form = request.form
    ticker = form.get('ticker')
    news_query = form.get('news_query') or ticker
    # Advanced settings – fall back to defaults if missing
    lookback = int(form.get('lookback', 60))
    horizon = int(form.get('horizon', 30))
    # Build a dict of any extra hyper‑parameters supplied per model
    extra_params = {}
    # For brevity we only parse a few generic params; UI can be expanded later.
    # Example: "xgb_learning_rate" will be stored under extra_params['xgb']['learning_rate']
    for key, value in form.items():
        if '_' in key and key.split('_')[0] in ['xgb', 'lgbm', 'catboost', 'gru', 'cnn', 'transformer', 'arima', 'svm']:
            model_key, param_name = key.split('_', 1)
            extra_params.setdefault(model_key, {})[param_name] = float(value) if value.replace('.','',1).isdigit() else value
    selected_models = _parse_model_list(form)
    if not selected_models:
        # default to random forest if nothing selected
        selected_models = ['rf']
    # Enforce maximum of 3 models
    if len(selected_models) > 3:
        import random
        selected_models = random.sample(selected_models, 3)
    # Check disk cache first
    cached = get_cached_result(ticker, selected_models, {
        "lookback": lookback,
        "horizon": horizon,
        "extra_params": extra_params,
    })
    if cached:
        run_id = str(uuid.uuid4())
        # store the cached payload under a temporary run_id so the result page works uniformly
        set_cached_result(ticker, selected_models, {"lookback": lookback, "horizon": horizon, "extra_params": extra_params}, cached)
        logger.info(f"Cache hit for {ticker} / {selected_models}")
        return redirect(url_for('.result', run_id=run_id))
    # No cache – start background task
    run_id = run_background_task(
        pipeline.run_pipeline,
        ticker=ticker,
        news_query=news_query,
        selected_models=selected_models,
        lookback=lookback,
        horizon=horizon,
        extra_params=extra_params,
    )
    logger.info(f"Started background run {run_id} for ticker {ticker}, models {selected_models}")
    return redirect(url_for('.result', run_id=run_id))

@bp.route('/status/<run_id>', methods=['GET'])
def status(run_id):
    err_file = cache_utils.CACHE_DIR / f"{run_id}_error.txt"
    if err_file.exists():
        with err_file.open("r") as f:
            return jsonify({"status": "error", "error": f.read()})
    result = load_run_result(run_id)
    if result is None:
        return jsonify({"status": "running"})
    else:
        return jsonify({"status": "finished"})

@bp.route('/result/<run_id>', methods=['GET'])
def result(run_id):
    payload = load_run_result(run_id)
    if payload is None:
        # still processing – show a simple waiting page that polls /status
        return render_template('waiting.html', run_id=run_id)
    # payload is a dict prepared by pipeline.run_pipeline
    return render_template('result.html', data=payload, run_id=run_id)

@bp.route('/download/<run_id>/<filename>', methods=['GET'])
def download(run_id, filename):
    # The pipeline stores images as base64 strings; we reconstruct a temporary file for download.
    import csv, io as _io
    payload = load_run_result(run_id)
    if not payload:
        abort(404)
    content = None
    # forecast_<model_name>.png  e.g. forecast_rf.png, forecast_lstm.png
    if filename.startswith('forecast_') and filename.endswith('.png'):
        model_name = filename[len('forecast_'):-len('.png')]
        for r in payload.get('model_results', []):
            if r['name'] == model_name:
                content = r.get('forecast_img')
                break
        # fallback: first model
        if content is None and payload.get('model_results'):
            content = payload['model_results'][0].get('forecast_img')
    elif filename == 'metrics.csv':
        # Build a small CSV from the metrics dicts
        out = _io.StringIO()
        writer = csv.writer(out)
        writer.writerow(['model', 'RMSE', 'MAE', 'MAPE', 'R2'])
        for r in payload.get('model_results', []):
            m = r['metrics']
            writer.writerow([r['name'], m.get('rmse'), m.get('mae'), m.get('mape'), m.get('r2')])
        out.seek(0)
        return send_file(_io.BytesIO(out.getvalue().encode()), mimetype='text/csv',
                         as_attachment=True, download_name='metrics.csv')
    if content is None:
        abort(404)
    # decode base64 to bytes and serve as PNG
    img_bytes = base64.b64decode(content)
    return send_file(_io.BytesIO(img_bytes), mimetype='image/png',
                     as_attachment=True, download_name=filename)
