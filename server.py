#!/usr/bin/env python3
"""
TQQQ Signal App - Yahoo Finance Proxy Server
解決 CORS 問題：作為本地代理，轉發 Yahoo Finance 請求
"""

from flask import Flask, jsonify, request
import urllib.request
import os
import urllib.parse
import os
import json
import os
import http.cookiejar
import os
import threading
import os
import time
import os
app = Flask(__name__, static_folder='.', static_url_path='')

# Cookie jar for session management
_cj = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_cj))
_lock = threading.Lock()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://finance.yahoo.com',
    'Referer': 'https://finance.yahoo.com/',
}

# Simple in-memory cache (5 min TTL)
_cache = {}
_cache_ttl = 300  # 5 minutes

def get_cached(key):
    if key in _cache:
        data, ts = _cache[key]
        if time.time() - ts < _cache_ttl:
            return data
    return None

def set_cache(key, data):
    _cache[key] = (data, time.time())


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/chart/<ticker>')
def chart(ticker):
    """Proxy Yahoo Finance v8 chart API"""
    range_ = request.args.get('range', '1y')
    interval = request.args.get('interval', '1d')
    
    cache_key = f'{ticker}_{range_}_{interval}'
    cached = get_cached(cache_key)
    if cached:
        resp = jsonify(cached)
        resp.headers['X-Cache'] = 'HIT'
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval={interval}&range={range_}&includePrePost=false'
    
    # Try query1 and query2
    for host in ['query1', 'query2']:
        url = f'https://{host}.finance.yahoo.com/v8/finance/chart/{ticker}?interval={interval}&range={range_}&includePrePost=false'
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with _lock:
                with _opener.open(req, timeout=15) as r:
                    data = json.loads(r.read().decode())
            
            if data.get('chart', {}).get('result'):
                set_cache(cache_key, data)
                resp = jsonify(data)
                resp.headers['Access-Control-Allow-Origin'] = '*'
                resp.headers['X-Cache'] = 'MISS'
                return resp
        except Exception as e:
            print(f'Error fetching {ticker} from {host}: {e}')
            continue
    
    resp = jsonify({'error': f'Failed to fetch {ticker}', 'chart': {'result': None, 'error': {'code': 'PROXY_ERROR'}}})
    resp.status_code = 502
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/health')
def health():
    resp = jsonify({'status': 'ok', 'time': time.time()})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8090))
    print(f'🚀 TQQQ Signal Proxy Server starting on http://0.0.0.0:{port}')
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
