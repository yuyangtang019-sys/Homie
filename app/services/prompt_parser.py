from __future__ import annotations

import re
from typing import Any

from app.models import Action, Rule
from app.schemas import LLMStructuredResponse
from app.services.llm_client import call_llm_for_home_control
from app.services.state_store import store


def _fallback_parse_prompt_to_rule(prompt: str) -> Rule | None:
    text = prompt.strip()

    time_match = re.search(
        r"(每天|明天|今晚|早上|晚上)?\s*(\d{1,2})[:点](\d{0,2})?.*(关灯|开灯|开空调|关空调|开窗帘|关窗帘|锁门|开门|解锁)",
        text,
    )
    if time_match:
        hour = str(int(time_match.group(2))).zfill(2)
        minute = str(int(time_match.group(3) or 0)).zfill(2)
        action = action_from_text(time_match.group(4), text)
        if not action:
            return None
        return Rule(
            id=store.next_rule_id(),
            name=text,
            enabled=True,
            trigger_type="time",
            trigger={"time": f"{hour}:{minute}"},
            actions=[action],
            source_prompt=text,
        )

    temp_match = re.search(r"(温度|室温).*(超过|高于|大于)\s*(\d{1,2}).*(开空调|打开空调)", text)
    if temp_match:
        threshold = int(temp_match.group(3))
        target_temp_match = re.search(r"(设置|调到)\s*(\d{1,2})\s*度?", text)
        target_temp = int(target_temp_match.group(2)) if target_temp_match else 24
        return Rule(
            id=store.next_rule_id(),
            name=text,
            enabled=True,
            trigger_type="condition",
            trigger={"metric": "temperature", "operator": ">", "value": threshold},
            actions=[Action(device_id="aircon_001", command="set", params={"power": "on", "mode": "cool", "target_temp": target_temp})],
            source_prompt=text,
        )

    light_match = re.search(r"(光照|亮度).*(低于|小于)\s*(\d{1,4}).*(开窗帘|打开窗帘)", text)
    if light_match:
        threshold = int(light_match.group(3))
        return Rule(
            id=store.next_rule_id(),
            name=text,
            enabled=True,
            trigger_type="condition",
            trigger={"metric": "light", "operator": "<", "value": threshold},
            actions=[Action(device_id="curtain_001", command="open")],
            source_prompt=text,
        )

    away_match = re.search(r"(没人|离家|外出).*(锁门|关窗帘|关闭窗帘)", text)
    if away_match:
        actions = []
        if "锁门" in text:
            actions.append(Action(device_id="door_001", command="lock"))
        if "窗帘" in text:
            actions.append(Action(device_id="curtain_001", command="close"))
        return Rule(
            id=store.next_rule_id(),
            name=text,
            enabled=True,
            trigger_type="condition",
            trigger={"metric": "presence", "operator": "==", "value": False},
            actions=actions,
            source_prompt=text,
        )
    return None


def _fallback_parse_text_to_action(text: str) -> Action | None:
    raw = text.strip()
    target_temp_match = re.search(r"(\d{1,2})\s*度", raw)
    target_temp = int(target_temp_match.group(1)) if target_temp_match else 24

    if re.search(r"(把)?空调.*(打开|开启|开机)", raw):
        return Action("aircon_001", "set", {"power": "on", "mode": "cool", "target_temp": target_temp})
    if re.search(r"(把)?空调.*(关闭|关掉|关机)", raw):
        return Action("aircon_001", "turn_off")
    if re.search(r"(空调).*(调到|设置).*(\d{1,2})\s*度", raw):
        return Action("aircon_001", "set", {"power": "on", "mode": "cool", "target_temp": target_temp})
    if re.search(r"(打开|开启|开).*(窗帘)", raw):
        return Action("curtain_001", "open")
    if re.search(r"(关闭|关上|关).*(窗帘)", raw):
        return Action("curtain_001", "close")
    if re.search(r"(打开|开).*(灯)", raw):
        return Action("light_001", "turn_on")
    if re.search(r"(关闭|关掉|关).*(灯)", raw):
        return Action("light_001", "turn_off")
    if re.search(r"(锁门)", raw):
        return Action("door_001", "lock")
    if re.search(r"(开门|解锁)", raw):
        return Action("door_001", "unlock")
    return action_from_text(raw, raw)


def action_from_text(action_text: str, raw: str) -> Action | None:
    target_temp_match = re.search(r"(\d{1,2})\s*度", raw)
    target_temp = int(target_temp_match.group(1)) if target_temp_match else 24

    if "关灯" in action_text:
        return Action(device_id="light_001", command="turn_off")
    if "开灯" in action_text:
        return Action(device_id="light_001", command="turn_on")
    if "关空调" in action_text or "关闭空调" in action_text:
        return Action(device_id="aircon_001", command="turn_off")
    if "开空调" in action_text or "打开空调" in action_text:
        return Action(device_id="aircon_001", command="set", params={"power": "on", "mode": "cool", "target_temp": target_temp})
    if "开窗帘" in action_text or "打开窗帘" in action_text:
        return Action(device_id="curtain_001", command="open")
    if "关窗帘" in action_text or "关闭窗帘" in action_text:
        return Action(device_id="curtain_001", command="close")
    if "锁门" in action_text:
        return Action(device_id="door_001", command="lock")
    if "开门" in action_text or "解锁" in action_text:
        return Action(device_id="door_001", command="unlock")
    return None


def _normalize_llm_response(data: dict[str, Any]) -> LLMStructuredResponse | None:
    try:
        return LLMStructuredResponse.model_validate(data)
    except Exception:
        return None


def explain_prompt(prompt: str) -> dict[str, Any]:
    raw = call_llm_for_home_control(prompt)
    parsed = _normalize_llm_response(raw)

    if parsed is not None and parsed.mode != "unknown":
        return parsed.model_dump()

    rule = _fallback_parse_prompt_to_rule(prompt)
    if rule:
        return {
            "mode": "rule",
            "message": raw.get("message", "LLM 不可用，已走本地规则解析"),
            "rule": {
                "name": rule.name,
                "trigger_type": rule.trigger_type,
                "trigger": rule.trigger,
                "actions": [a.__dict__ for a in rule.actions],
            },
        }

    action = _fallback_parse_text_to_action(prompt)
    if action:
        return {
            "mode": "instant",
            "message": raw.get("message", "LLM 不可用，已走本地动作解析"),
            "action": action.__dict__,
        }

    if parsed is not None:
        return parsed.model_dump()
    return raw if isinstance(raw, dict) else {"mode": "unknown", "message": "暂时无法理解这条指令"}


def parse_prompt_to_rule(prompt: str) -> Rule | None:
    data = explain_prompt(prompt)
    if data.get("mode") != "rule" or not data.get("rule"):
        return None
    rule_data = data["rule"]
    return Rule(
        id=store.next_rule_id(),
        name=rule_data["name"],
        enabled=True,
        trigger_type=rule_data["trigger_type"],
        trigger=rule_data["trigger"],
        actions=[Action(**a) for a in rule_data["actions"]],
        source_prompt=prompt,
    )


def parse_text_to_action(text: str) -> Action | None:
    data = explain_prompt(text)
    if data.get("mode") != "instant" or not data.get("action"):
        return None
    return Action(**data["action"])
