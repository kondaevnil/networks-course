import httpx
import logging
import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import Response

app = FastAPI()
logging.basicConfig(filename="proxy.log", level=logging.INFO, format="%(asctime)s - %(message)s")

PROXY_PORT = 8888

@app.api_route("/{full_path:path}", methods=["GET", "POST"])
async def proxy(full_path: str, request: Request):
    target_url = f"http://{full_path}"
    headers = {key: value for key, value in request.headers.items() if key.lower() != "host"}
    
    try:
        async with httpx.AsyncClient() as client:
            if request.method == "GET":
                resp = await client.get(target_url, headers=headers)
            elif request.method == "POST":
                body = await request.body()
                resp = await client.post(target_url, headers=headers, content=body)
            else:
                return Response(content="Method Not Allowed", status_code=405)
        
        logging.info(f"{request.method} {target_url} -> {resp.status_code}")
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
    
    except httpx.RequestError as e:
        logging.error(f"Request failed: {str(e)}")
        return Response(content=f"Error: {str(e)}", status_code=502)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return Response(content="Internal Server Error", status_code=500)


uvicorn.run(app, host="0.0.0.0", port=PROXY_PORT)
