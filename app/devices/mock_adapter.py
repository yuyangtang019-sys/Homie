from __future__ import annotations

from app.devices.base import DeviceAdapter
from app.models import Device


class MockDeviceAdapter(DeviceAdapter):
    def execute(self, device: Device, command: str, params: dict) -> Device:
        state = dict(device.state)

        if device.type == "light":
            if command in {"turn_on", "on"}:
                state["power"] = "on"
            elif command in {"turn_off", "off"}:
                state["power"] = "off"

        elif device.type == "aircon":
            if command in {"turn_on", "on"}:
                state["power"] = "on"
            elif command in {"turn_off", "off"}:
                state["power"] = "off"
            elif command == "set":
                state["power"] = params.get("power", state.get("power", "on"))
                state["mode"] = params.get("mode", state.get("mode", "cool"))
                state["target_temp"] = params.get("target_temp", state.get("target_temp", 24))

        elif device.type == "curtain":
            if command in {"open", "turn_on"}:
                state["position"] = "open"
            elif command in {"close", "turn_off"}:
                state["position"] = "closed"

        elif device.type == "door":
            if command in {"lock", "turn_on"}:
                state["lock"] = "locked"
            elif command in {"unlock", "turn_off"}:
                state["lock"] = "unlocked"

        device.state = state
        return device
