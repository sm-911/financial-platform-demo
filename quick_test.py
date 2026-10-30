import sys, pathlib
sys.path.append(str(pathlib.Path('C:/Users/soham/.gemini/antigravity/scratch/intelligent-financial-platform-expanded').resolve()))
from app.pipeline import run_pipeline
payload = run_pipeline(ticker='AAPL', news_query='', selected_models=['rf'], lookback=60, horizon=30, extra_params={})
print('Models returned:', len(payload.get('model_results', [])))
if payload.get('model_results'):
    m = payload['model_results'][0]
    print('First model name:', m['name'])
    print('Metrics:', m['metrics'])
    print('forecast_img length', len(m.get('forecast_img','')))
