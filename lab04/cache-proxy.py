import os
import json
import hashlib
import logging
import uvicorn
from datetime import datetime
import httpx
from fastapi import FastAPI, Request
from starlette.responses import Response

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

app = FastAPI()
logging.basicConfig(filename="proxy.log", level=logging.INFO, format="%(asctime)s - %(message)s")

PROXY_PORT = 8888

def get_cache_path(url: str) -> str:
    """Генерирует путь к файлу кэша на основе хэша URL."""
    hashed_url = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{hashed_url}.json")

def load_cache(url: str):
    """Загружает кэшированные данные, если они существуют."""
    cache_path = get_cache_path(url)
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_cache(url: str, response):
    """Сохраняет ответ сервера в кэше."""
    cache_path = get_cache_path(url)
    cache_data = {
        "url": url,
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": response.content.decode("utf-8", errors="ignore")
    }
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f)

@app.api_route("/{full_path:path}", methods=["GET", "POST"])
async def proxy(full_path: str, request: Request):
    target_url = f"http://{full_path}"
    headers = {key: value for key, value in request.headers.items() if key.lower() != "host"}
    
    cached_data = load_cache(target_url)
    if cached_data:
        if "Last-Modified" in cached_data["headers"]:
            headers["If-Modified-Since"] = cached_data["headers"]["Last-Modified"]
        if "ETag" in cached_data["headers"]:
            headers["If-None-Match"] = cached_data["headers"]["ETag"]

    try:
        async with httpx.AsyncClient() as client:
            if request.method == "GET":
                resp = await client.get(target_url, headers=headers)
            elif request.method == "POST":
                body = await request.body()
                resp = await client.post(target_url, headers=headers, content=body)
            else:
                return Response(content="Method Not Allowed", status_code=405)

        if resp.status_code == 304 and cached_data:
            logging.info(f"{request.method} {target_url} -> 304 Not Modified (cache used)")
            return Response(content=cached_data["body"], status_code=200, headers=cached_data["headers"])

        if resp.status_code == 200:
            save_cache(target_url, resp)

        logging.info(f"{request.method} {target_url} -> {resp.status_code}")
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))

    except httpx.RequestError as e:
        logging.error(f"Request failed: {str(e)}")
        return Response(content=f"Error: {str(e)}", status_code=502)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return Response(content="Internal Server Error", status_code=500)

    
uvicorn.run(app, host="0.0.0.0", port=PROXY_PORT)
