from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


DeviceType = Literal["light", "aircon", "curtain", "door"]
RuleTriggerType = Literal["time", "condition"]


@dataclass
class Device:
    id: str
    name: str
    type: DeviceType
    room: str
    online: bool = True
    state: dict[str, Any] = field(default_factory=dict)
    capabilities: list[str] = field(default_factory=list)


@dataclass
class Action:
    device_id: str
    command: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class Rule:
    id: str
    name: str
    enabled: bool
    trigger_type: RuleTriggerType
    trigger: dict[str, Any]
    actions: list[Action]
    source_prompt: str = ""
    cooldown_seconds: int = 300
    priority: int = 10
    last_triggered_at: float | None = None


@dataclass
class LogEvent:
    ts: float
    category: str
    message: str
