from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import os
import shutil
import requests
import requests_go
from utils import get_tls, get_headers, get_ua
from haruka_parser.extract import extract_text
from haruka_parser.extract import DEFAULT_CONFIG as configuration

import fitz
import logging
import timeout_decorator

logger = logging.getLogger("uvicorn.error")

from uuid import uuid4
from apryse_sdk import *

configuration["readability"] = True

PROXY = os.environ.get("PROXY", "")
BROSWER_API = os.environ.get("BROSWER_API", "")
BROWSER_PROXY_SERVER = os.environ.get("BROWSER_PROXY_SERVER", "")
BROWSER_PROXY_USERNAME = os.environ.get("BROWSER_PROXY_USERNAME", "")
BROWSER_PROXY_PASSWORD = os.environ.get("BROWSER_PROXY_PASSWORD", "")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN", "")

app = FastAPI()

security = HTTPBearer()

def pdf_to_html_fitz(pdf_path):
    doc = fitz.open(pdf_path)
    html_content = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_lines = page.get_text("text").split('\n')
        for line in text_lines:
            html_content += f"<p>{line}</p>"
    doc.close()
    return html_content

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
        fallback_html = pdf_to_html_fitz(pdf_tmp_path)
    except Exception as e:
        logger.error(f"error: fitz {str(e)}")
        pass

    htmlOutputOptions = HTMLOutputOptions()

    htmlOutputOptions.SetConnectHyphens(True)
    htmlOutputOptions.SetEmbedImages(False)
    htmlOutputOptions.SetFileConversionTimeoutSeconds(timeout)

    @timeout_decorator.timeout(timeout)
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

async def fetch_pdf_url(url: str, timeout, source="", params=None, proxy=None):
    try:
        headers = get_headers()
        tls = get_tls()
        if proxy and proxy != "playwright_proxy":
            response = await requests_go.async_get(url, params=params, headers=headers, tls_config=tls, proxies={"http": proxy, "https": proxy}, timeout=timeout)
        else:
            response = await requests_go.async_get(url, params=params, headers=headers, tls_config=tls, timeout=timeout)

        if response.status_code == 200:
            html = pdf_to_html(response.content, timeout)
            return {"html": html, "proxy": proxy is not None, "source": source, "status": 200}
    except Exception as e:
        if proxy:
            logger.error(f"Error fetching {url} with proxy: {e}")
        else:
            logger.error(f"Error fetching {url}: {e}")
        return None

async def fetch_url(url: str, timeout, source="", params=None, proxy=None):
    try:
        headers = get_headers()
        tls = get_tls()
        if proxy and proxy != "playwright_proxy":
            response = await requests_go.async_get(url, params=params, headers=headers, tls_config=tls, proxies={"http": proxy, "https": proxy}, timeout=timeout)
        else:
            response = await requests_go.async_get(url, params=params, headers=headers, tls_config=tls, timeout=timeout)

        if response.status_code == 200:
            if source == "playwright":
                res = response.json()
                res["proxy"] = proxy is not None
                res["source"] = "playwright"
                res["status"] = 200
                return res
            else:
                return {"html": response.text, "proxy": proxy is not None, "source": source, "status": 200}
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

async def get_content_type(url: str):
    try:
        with requests.get(url, stream=True, timeout=3) as response:
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            response.close()
            return content_type
    except requests.RequestException as e:
        pass
    return 'unknown'

@app.get("/browser")
async def browser(credentials: Annotated[str, Depends(security)], url: str, timeout: int = 10, pdf_timeout = None):
    if credentials:
        token = credentials.credentials
        if token == BEARER_TOKEN:
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    
    if not pdf_timeout:
        pdf_timeout = timeout
    
    content_type = await get_content_type(url)

    tasks = []

    if "pdf" in content_type:
        tasks.append(fetch_pdf_url(url, timeout, source="pdf"))

    else:
        tasks.append(fetch_url(url, timeout, source="get"))

        if PROXY:
            tasks.append(fetch_url(url, timeout, source="proxy", proxy=PROXY))

        if BROSWER_API:
            browser_params = {"url": url, "timeout": int(max(timeout-2,2)*1000), "user-agent": get_ua()}
            tasks.append(fetch_url(f"{BROSWER_API}/api/article", timeout, source="playwright", params=browser_params))
            if BROWSER_PROXY_SERVER and BROWSER_PROXY_USERNAME and BROWSER_PROXY_PASSWORD:
                browser_params.update({"proxy-server": BROWSER_PROXY_SERVER, "proxy-username": BROWSER_PROXY_USERNAME, "proxy-password": BROWSER_PROXY_PASSWORD})
                tasks.append(fetch_url(f"{BROSWER_API}/api/article", timeout, source="playwright", params=browser_params, proxy="playwright_proxy"))

    best_result = {}
    for future in asyncio.as_completed(tasks):
        result = await future
        if result:
            if result["source"] == "pdf":
                return result
            try:
                result["content"] = extract_text(result["html"], configuration)[0]
            except:
                result["content"] = ""
            if len(result["content"]) > 100:
                return result
            if len(best_result.get("html", "")) < len(result.get("html", "")):
                best_result = result
    
    if best_result:
        return best_result

    raise HTTPException(status_code=500, detail="No content fetched from any source")
