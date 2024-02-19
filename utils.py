import requests_go
from fake_useragent import UserAgent

ua = UserAgent(min_percentage=4.2)
tls = requests_go.tls_config.TLS_CHROME_110_LATEST

def get_tls():
    tls.force_http1 = True
    return tls

def get_headers():
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': ua.random,
    }

def get_ua():
    return ua.random
