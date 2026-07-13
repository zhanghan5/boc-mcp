from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


async def liveness(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"}, status_code=200)


async def readiness(request: Request) -> JSONResponse:
    client = getattr(request.app.state, "boc_client", None)
    if client is None:
        return JSONResponse({"status": "ready"}, status_code=200)
    try:
        await client.get("/upmstreeapi/bocPortal/getMenus")
        return JSONResponse({"status": "ready"}, status_code=200)
    except Exception as e:
        return JSONResponse({"status": "not_ready", "error": str(e)}, status_code=503)
