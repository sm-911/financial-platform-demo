import os
import threading
import uuid
import hashlib
import pickle
import traceback
from pathlib import Path
from datetime import datetime

# Place cache folder inside intelligent-financial-platform-expanded/app/cache
CACHE_DIR = Path(__file__).resolve().parent / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _hash_request(ticker, model_names, params):
    # deterministic hash of request parameters
    hash_input = f"{ticker}|{'|'.join(sorted(model_names))}|{sorted(params.items())}".encode('utf-8')
    return hashlib.md5(hash_input).hexdigest()

def get_cached_result(ticker, model_names, params):
    h = _hash_request(ticker, model_names, params)
    cache_path = CACHE_DIR / f"{h}.pkl"
    if cache_path.exists():
        with cache_path.open('rb') as f:
            return pickle.load(f)
    return None

def set_cached_result(ticker, model_names, params, result_obj):
    h = _hash_request(ticker, model_names, params)
    cache_path = CACHE_DIR / f"{h}.pkl"
    with cache_path.open('wb') as f:
        pickle.dump(result_obj, f)
    return str(cache_path)

def run_background_task(func, *args, **kwargs):
    """Run *func* in a daemon thread and return a run_id.
    The *func* should return a dictionary with all data needed for the result page.
    """
    run_id = str(uuid.uuid4())
    def wrapper():
        try:
            result = func(*args, **kwargs)
            result_path = CACHE_DIR / f"{run_id}.pkl"
            with result_path.open('wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            traceback.print_exc()
            err_path = CACHE_DIR / f"{run_id}_error.txt"
            with err_path.open('w') as f:
                f.write(traceback.format_exc())
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    return run_id

def load_run_result(run_id):
    result_path = CACHE_DIR / f"{run_id}.pkl"
    if not result_path.exists():
        return None
    with result_path.open('rb') as f:
        return pickle.load(f)
