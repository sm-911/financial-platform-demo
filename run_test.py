import sys, pathlib
sys.path.append(str(pathlib.Path('C:/Users/soham/.gemini/antigravity/scratch/intelligent-financial-platform-expanded').resolve()))
from app.pipeline import run_pipeline
payload = run_pipeline(ticker='AAPL', news_query='', selected_models=['rf','lstm','xgb'], lookback=60, horizon=30, extra_params={})
print('model_results count:', len(payload.get('model_results', [])))
for m in payload.get('model_results', []):
    print('model', m['name'], 'metrics keys', list(m['metrics'].keys()))
    print('forecast_img length', len(m.get('forecast_img','')))
