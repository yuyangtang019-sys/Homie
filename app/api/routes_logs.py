from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import LOGS_PASSWORD, TEMPLATES_DIR
from app.schemas import PasswordRequest
from app.services.state_store import store

router = APIRouter(tags=["logs"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/logs", response_class=HTMLResponse)
def logs_login_page(request: Request):
    return templates.TemplateResponse("logs_login.html", {"request": request})


@router.get("/logs/view", response_class=HTMLResponse)
def logs_page(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})


@router.post("/api/logs/auth")
def auth_logs(payload: PasswordRequest):
    return {"ok": payload.password == LOGS_PASSWORD}


@router.get("/api/logs")
def get_logs():
    return {"logs": [{"ts": log.ts, "category": log.category, "message": log.message} for log in store.logs]}
