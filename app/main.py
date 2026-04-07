from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes_agent import router as agent_router
from app.api.routes_devices import router as devices_router
from app.api.routes_hardware import router as hardware_router
from app.api.routes_logs import router as logs_router
from app.api.routes_pages import router as pages_router
from app.api.routes_rules import router as rules_router
from app.config import APP_NAME, APP_VERSION, STATIC_DIR
from app.services.scheduler import scheduler_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(scheduler_loop())
    yield
    task.cancel()


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(pages_router)
app.include_router(devices_router)
app.include_router(rules_router)
app.include_router(agent_router)
app.include_router(hardware_router)
app.include_router(logs_router)
