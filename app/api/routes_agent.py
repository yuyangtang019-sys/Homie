from __future__ import annotations

from fastapi import APIRouter

from app.schemas import PromptRequest
from app.services.llm_client import llm_health_check
from app.services.prompt_parser import explain_prompt, parse_prompt_to_rule, parse_text_to_action
from app.services.state_store import store

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.get("/health")
def agent_health():
    return llm_health_check()


@router.post("/preview")
def preview_agent(payload: PromptRequest):
    return explain_prompt(payload.prompt)


@router.post("/chat")
def chat_agent(payload: PromptRequest):
    prompt = payload.prompt.strip()
    info = explain_prompt(prompt)

    if info.get("mode") == "rule":
        rule = parse_prompt_to_rule(prompt)
        if rule is None:
            return {"ok": False, "message": info.get("message", "无法生成规则"), "debug": info}
        store.add_rule(rule)
        return {
            "ok": True,
            "mode": "rule",
            "message": f"Homie 已保存自动化规则：{rule.name}",
            "rule": {
                "id": rule.id,
                "name": rule.name,
                "trigger_type": rule.trigger_type,
                "trigger": rule.trigger,
                "actions": [a.__dict__ for a in rule.actions],
            },
            "debug": info,
        }

    if info.get("mode") == "instant":
        action = parse_text_to_action(prompt)
        if action is None:
            return {"ok": False, "message": info.get("message", "无法执行命令"), "debug": info}
        device = store.execute_action(action, source="chat")
        return {
            "ok": True,
            "mode": "instant",
            "message": f"Homie 已执行指令：{prompt}",
            "action": action.__dict__,
            "device": device.__dict__,
            "debug": info,
        }

    store.add_log("chat", f"未理解的输入：{prompt}")
    return {"ok": False, "mode": "unknown", "message": info.get("message", "Homie 还无法理解这条指令"), "debug": info}


@router.get("/snapshot")
def snapshot():
    return {
        "devices": [device.__dict__ for device in store.list_devices()],
        "environment": store.environment,
        "rules_count": len(store.rules),
        "logs_count": len(store.logs),
    }
