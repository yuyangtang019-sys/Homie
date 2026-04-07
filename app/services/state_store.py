from __future__ import annotations

import time
import uuid
from typing import Any

from app.devices.mock_adapter import MockDeviceAdapter
from app.models import Action, Device, LogEvent, Rule


class StateStore:
    def __init__(self) -> None:
        self.adapter = MockDeviceAdapter()
        self.devices: dict[str, Device] = {
            "light_001": Device(
                id="light_001",
                name="客厅灯",
                type="light",
                room="客厅",
                state={"power": "off"},
                capabilities=["turn_on", "turn_off"],
            ),
            "aircon_001": Device(
                id="aircon_001",
                name="客厅空调",
                type="aircon",
                room="客厅",
                state={"power": "off", "mode": "cool", "target_temp": 24},
                capabilities=["turn_on", "turn_off", "set"],
            ),
            "curtain_001": Device(
                id="curtain_001",
                name="客厅窗帘",
                type="curtain",
                room="客厅",
                state={"position": "open"},
                capabilities=["open", "close"],
            ),
            "door_001": Device(
                id="door_001",
                name="入户门",
                type="door",
                room="玄关",
                state={"lock": "locked"},
                capabilities=["lock", "unlock"],
            ),
        }
        self.environment: dict[str, Any] = {
            "temperature": 28.0,
            "humidity": 55.0,
            "light": 120.0,
            "presence": True,
            "current_time": "09:30",
        }
        self.rules: dict[str, Rule] = {}
        self.logs: list[LogEvent] = []
        self.add_log("system", "Homie 已启动（LLM版）")

    def add_log(self, category: str, message: str) -> None:
        self.logs.insert(0, LogEvent(ts=time.time(), category=category, message=message))
        self.logs = self.logs[:500]

    def list_devices(self) -> list[Device]:
        return list(self.devices.values())

    def get_device(self, device_id: str) -> Device:
        return self.devices[device_id]

    def execute_action(self, action: Action, source: str = "manual") -> Device:
        device = self.get_device(action.device_id)
        updated = self.adapter.execute(device, action.command, action.params)
        self.devices[device.id] = updated
        self.add_log(source, f"设备 {device.name} 执行动作 {action.command} {action.params}")
        return updated

    def add_rule(self, rule: Rule) -> Rule:
        self.rules[rule.id] = rule
        self.add_log("rule", f"新增规则：{rule.name}")
        return rule

    def delete_rule(self, rule_id: str) -> None:
        if rule_id in self.rules:
            name = self.rules[rule_id].name
            del self.rules[rule_id]
            self.add_log("rule", f"删除规则：{name}")

    def next_rule_id(self) -> str:
        return f"rule_{uuid.uuid4().hex[:8]}"

    def update_environment(self, **kwargs: Any) -> dict[str, Any]:
        changed = {}
        for key, value in kwargs.items():
            if value is not None:
                self.environment[key] = value
                changed[key] = value
        if changed:
            self.add_log("environment", f"环境更新：{changed}")
        return self.environment


store = StateStore()
