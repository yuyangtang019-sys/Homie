from __future__ import annotations

from fastapi import APIRouter

from app.models import Action
from app.schemas import HardwareSensorPayload
from app.services.rule_engine import evaluate_rules
from app.services.state_store import store

router = APIRouter(prefix="/api/hardware", tags=["hardware"])


@router.post("/sensor")
def ingest_sensor_data(payload: HardwareSensorPayload):
    store.update_environment(
        temperature=payload.temp,
        light=payload.light,
        humidity=payload.humidity,
    )

    if payload.button_pressed:
        store.execute_action(Action(device_id="door_001", command="unlock"), source="hardware")
        store.add_log("hardware", "硬件按钮触发：门解锁")

    fired = evaluate_rules()

    decision = {
        "ac_on": store.devices["aircon_001"].state.get("power") == "on",
        "curtain_open": store.devices["curtain_001"].state.get("position") == "open",
        "door_open": store.devices["door_001"].state.get("lock") == "unlocked",
        "ac_temp": store.devices["aircon_001"].state.get("target_temp", 24),
    }

    return {"ok": True, "environment": store.environment, "fired_rules": fired, "decision": decision}
