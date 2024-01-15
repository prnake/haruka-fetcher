from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import os
import random
import shutil
import requests
import requests_go
from utils import get_tls, get_headers, get_ua
from haruka_parser.extract import extract_text
from haruka_parser.extract import DEFAULT_CONFIG as configuration
import charset_mnbvc.api

import socket
socket.setdefaulttimeout(20)

import fitz
import logging
import time
import timeout_decorator

logger = logging.getLogger("uvicorn.error")

from uuid import uuid4
from apryse_sdk import *

configuration["readability"] = True

PROXY = os.environ.get("PROXY", "").split(",")
BROSWER_API = os.environ.get("BROSWER_API", "")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "")

def get_proxy_config(proxy):
    protocol, proxy = proxy.split('://', 1)
    parts = proxy.split('@')
    if len(parts) == 2:
        auth = parts[0].split(':')
        server = parts[1]
        if len(auth) == 2:
            username = auth[0]
            password = auth[1]
        else:
            username = ""
            password = ""
    else:
        server = proxy
        username = ""
        password = ""
    return f"{protocol}://{server}", username, password

for proxy in PROXY:
    get_proxy_config(proxy)

app = FastAPI()

security = HTTPBearer()

def pdf_to_html_fitz(pdf_path):
    doc = fitz.open(pdf_path)
    html_content = ""
    page_cnt = len(doc)
    for page_num in range(page_cnt):
        page = doc.load_page(page_num)
        text_lines = page.get_text("text").split('\n')
        for line in text_lines:
            html_content += f"<p>{line}</p>"
    doc.close()
    return html_content, page_cnt

def pdf_to_html(pdf_content, timeout):
    pdf_tmp_id = str(uuid4())
    tmp_path = f'tmp_pdf_data/{pdf_tmp_id}'
    os.makedirs(tmp_path, exist_ok=True)
    pdf_tmp_path = f'{tmp_path}/tmp.pdf'
    html_tmp_path = f'{tmp_path}/tmp.html'
    open(pdf_tmp_path, "wb").write(pdf_content)

    html = ""
    fallback_html = ""

    try:
        fallback_html, page_cnt = pdf_to_html_fitz(pdf_tmp_path)
    except Exception as e:
        logger.error(f"error: fitz {str(e)}")
        pass

    if page_cnt <= 5:
        htmlOutputOptions = HTMLOutputOptions()

        htmlOutputOptions.SetConnectHyphens(True)
        htmlOutputOptions.SetEmbedImages(False)
        htmlOutputOptions.SetFileConversionTimeoutSeconds(timeout)

        # @timeout_decorator.timeout(timeout)
        def convert_to_html():
            html = ""
            try:
                htmlOutputOptions.SetContentReflowSetting(HTMLOutputOptions.e_reflow_full)
                Convert.ToHtml(pdf_tmp_path, html_tmp_path, htmlOutputOptions)
                html = open(html_tmp_path, encoding="utf-8").read()
            except Exception as e:
                logger.error(f"error: e_reflow_full {str(e)}")
                pass

            if not html:
                try:
                    htmlOutputOptions.SetContentReflowSetting(HTMLOutputOptions.e_reflow_paragraphs)
                    Convert.ToHtml(pdf_tmp_path, html_tmp_path, htmlOutputOptions)
                    html = open(html_tmp_path, encoding="utf-8").read()
                except Exception as e:
                    logger.error(f"error: e_reflow_paragraphs {str(e)}")
                    pass
            return html
        
        try:
            html = convert_to_html()
        except Exception as e:
            logger.error(f"error: apryse {str(e)}")
    
    if not html:
        html = fallback_html

    try:
        shutil.rmtree(tmp_path)
    except:
        pass
    return html

def fetch_url(url: str, timeout, source="", params=None, proxy=None):
    # @timeout_decorator.timeout(timeout)
    def _fetch_url_timeout():
        try:
            headers = get_headers()
            tls = get_tls()
            if proxy and proxy != "playwright_proxy":
                response = requests_go.get(url, params=params, headers=headers, proxies={"http": proxy, "https": proxy}, tls_config=tls, timeout=timeout)
            else:
                response = requests.get(url, params=params, headers=headers, timeout=timeout)

            if response.status_code == 200:
                if source == "playwright":
                    res = response.json()
                    res["proxy"] = proxy is not None
                    res["source"] = "playwright"
                    res["status"] = 200
                    return res
                
                content = response.content
                content_type = response.headers.get('content-type', '')
                if 'pdf' in content_type or content.startswith(b'%PDF-'):
                    html = pdf_to_html(content, timeout)
                    return {"html": html, "proxy": proxy is not None, "source": "pdf", "status": 200}
                elif b'\x00' in content:
                    return None
                else:
                    encoding = "UNKNOWN"
                    try:
                        encoding = charset_mnbvc.api.from_data(data=content, mode=2)
                    except:
                        pass
                    if encoding == "UNKNOWN":
                        encoding = "utf-8"
                    html_result = ""
                    try:
                        html_result = content.decode(encoding)
                    except Exception as e:
                        logger.error(f"Error parse url {url} {e}")
                        pass
                    if not html_result:
                        try:
                            encoding = "utf-8"
                            html_result = content.decode(encoding, errors='ignore')
                        except Exception as e:
                            logger.error(f"Error parse url {url} {e}")
                            pass
                    if html_result:
                        return {"html": html_result, "proxy": proxy is not None, "encoding": encoding, "source": source, "status": 200}
                    else:
                        return None
        except Exception as e:
            if proxy:
                logger.error(f"Error fetching {url} with proxy: {e}")
            else:
                logger.error(f"Error fetching {url}: {e}")
            return None
    try:
        start_time = time.time()
        retry_time = 1 if source == "playwright" else 5
        for _ in range(retry_time):
            res = _fetch_url_timeout()
            if res:
                return res
            if time.time() - start_time > timeout:
                return None
        return None
    except Exception as e:
        if proxy:
            logger.error(f"Error fetching {url} with proxy: {e}")
        else:
            logger.error(f"Error fetching {url}: {e}")
        return None

def get_content_type(url: str):
    try:
        with requests.get(url, stream=True, timeout=3) as response:
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            response.close()
            return content_type
    except requests.RequestException as e:
        pass
    return 'unknown'

async def wait_for_thread(func, args=(), timeout=10):
    """
    Runs 'func' in a separate thread with 'args' and waits for at most 'timeout' seconds.
    If 'func' does not complete within 'timeout', asyncio.TimeoutError is raised.
    """
    try:
        return await asyncio.wait_for(asyncio.to_thread(func, *args), timeout)
    except asyncio.TimeoutError:
        logger.info(f"The url {args[0]} took too long and was cancelled.")
        return None
    except Exception as e:
        # Handle other exceptions that the function might raise
        logger.error(f"Error thread url {args[0]}: {e}")
        return None

@app.get("/browser")
async def browser(credentials: Annotated[str, Depends(security)], url: str, timeout: int = 10):

    # gracefully reduce timeout
    timeout = timeout - 1
    
    start_time = time.time()

    def remaining_timeout(real=False):
        if real:
            return timeout + start_time - time.time()
        return int(max(timeout + start_time - time.time(), 2))
    def spending_time():
        return time.time() - start_time
    
    # def remaining_pdf_timeout(real=False):
    #     if real:
    #         return remaining_pdf_timeout + start_time - time.time()
    #     return int(max(timeout + start_time - time.time(), 2))

    if credentials:
        token = credentials.credentials
        if token == BEARER_TOKEN:
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    
    # content_type = await get_content_type(url)

    tasks = []

    # if "pdf" in content_type:
    #     tasks.append(fetch_pdf_url(url, remaining_timeout(), source="pdf"))
    #     if PROXY:
    #         tasks.append(fetch_pdf_url(url, remaining_timeout(), source="pdf", proxy=PROXY))

    # else:

    if PROXY:
        proxy = random.choice(PROXY)
        proxy_server, proxy_username, proxy_password = get_proxy_config(proxy)

    tasks.append(wait_for_thread(fetch_url, (url, timeout, "get"), timeout))

    if proxy:
        tasks.append(wait_for_thread(fetch_url, (url, timeout, "proxy", None, proxy), timeout))

    if BROSWER_API:
        browser_params = {"url": url, "timeout": int(timeout*1000), "user-agent": get_ua()}
        tasks.append(wait_for_thread(fetch_url, (f"{BROSWER_API}/api/article", timeout, "playwright", browser_params), timeout))
        browser_params.update({"proxy-server": proxy_server, "proxy-username": proxy_username, "proxy-password": proxy_password})
        # tasks.append(wait_for_thread(fetch_url, (f"{BROSWER_API}/api/article", timeout, "playwright", browser_params, "playwright_proxy"), timeout))
    def cancel_all_task():
        pass
        # for task in tasks:
        #     if task and not task.done():
        #         task.cancel()
    best_result = {}
    try:
        for future in asyncio.as_completed(tasks):
            result = await future
            if result:
                if result["source"] == "pdf":
                    logger.info(f"{spending_time()} {url}")
                    cancel_all_task()
                    return result
                try:
                    result["content"] = extract_text(result["html"], configuration)[0]
                except:
                    result["content"] = ""
                if len(result["content"]) > 100:
                    logger.info(f"{spending_time()} {url}")
                    cancel_all_task()
                    return result
                if len(best_result.get("html", "")) < len(result.get("html", "")):
                    best_result = result
    except:
        cancel_all_task()
    
    if best_result:
        logger.info(f"{spending_time()} {url}")
        return best_result

    raise HTTPException(status_code=500, detail="No content fetched from any source")
