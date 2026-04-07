from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Literal


class ActionIn(BaseModel):
    device_id: str
    command: str
    params: dict[str, Any] = Field(default_factory=dict)


class RuleIn(BaseModel):
    name: str
    enabled: bool = True
    trigger_type: Literal["time", "condition"]
    trigger: dict[str, Any]
    actions: list[ActionIn]
    source_prompt: str = ""
    cooldown_seconds: int = 300
    priority: int = 10


class PromptRequest(BaseModel):
    prompt: str


class EnvironmentUpdate(BaseModel):
    temperature: float | None = None
    humidity: float | None = None
    light: float | None = None
    presence: bool | None = None
    current_time: str | None = None


class DeviceCommandRequest(BaseModel):
    command: str
    params: dict[str, Any] = Field(default_factory=dict)


class PasswordRequest(BaseModel):
    password: str


class HardwareSensorPayload(BaseModel):
    temp: float
    light: float
    humidity: float | None = None
    button_pressed: bool = False


class LLMStructuredAction(BaseModel):
    device_id: str
    command: str
    params: dict[str, Any] = Field(default_factory=dict)


class LLMStructuredRule(BaseModel):
    name: str
    trigger_type: Literal["time", "condition"]
    trigger: dict[str, Any]
    actions: list[LLMStructuredAction]


class LLMStructuredResponse(BaseModel):
    mode: Literal["instant", "rule", "unknown"]
    message: str = ""
    action: LLMStructuredAction | None = None
    rule: LLMStructuredRule | None = None
