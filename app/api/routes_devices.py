from __future__ import annotations

from fastapi import APIRouter, HTTPException
from app.models import Action
from app.schemas import DeviceCommandRequest, EnvironmentUpdate
from app.services.rule_engine import evaluate_rules
from app.services.state_store import store

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("")
def list_devices():
    return {"devices": [device.__dict__ for device in store.list_devices()]}


@router.post("/{device_id}/command")
def command_device(device_id: str, payload: DeviceCommandRequest):
    if device_id not in store.devices:
        raise HTTPException(status_code=404, detail="device not found")
    device = store.execute_action(Action(device_id=device_id, command=payload.command, params=payload.params), source="manual")
    return {"device": device.__dict__}


@router.get("/environment")
def get_environment():
    return {"environment": store.environment}


@router.post("/environment")
def update_environment(payload: EnvironmentUpdate):
    env = store.update_environment(**payload.model_dump())
    fired = evaluate_rules()
    return {"environment": env, "fired_rules": fired}
