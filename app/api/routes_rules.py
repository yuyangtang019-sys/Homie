from __future__ import annotations

from fastapi import APIRouter, HTTPException
from app.models import Action, Rule
from app.schemas import PromptRequest, RuleIn
from app.services.prompt_parser import parse_prompt_to_rule
from app.services.rule_engine import evaluate_rules
from app.services.state_store import store

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.get("")
def list_rules():
    return {
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "enabled": r.enabled,
                "trigger_type": r.trigger_type,
                "trigger": r.trigger,
                "actions": [a.__dict__ for a in r.actions],
                "source_prompt": r.source_prompt,
                "cooldown_seconds": r.cooldown_seconds,
                "priority": r.priority,
                "last_triggered_at": r.last_triggered_at,
            }
            for r in store.rules.values()
        ]
    }


@router.post("")
def create_rule(payload: RuleIn):
    rule = Rule(
        id=store.next_rule_id(),
        name=payload.name,
        enabled=payload.enabled,
        trigger_type=payload.trigger_type,
        trigger=payload.trigger,
        actions=[Action(**a.model_dump()) for a in payload.actions],
        source_prompt=payload.source_prompt,
        cooldown_seconds=payload.cooldown_seconds,
        priority=payload.priority,
    )
    store.add_rule(rule)
    return {"rule_id": rule.id}


@router.delete("/{rule_id}")
def delete_rule(rule_id: str):
    if rule_id not in store.rules:
        raise HTTPException(status_code=404, detail="rule not found")
    store.delete_rule(rule_id)
    return {"ok": True}


@router.post("/evaluate")
def run_evaluation():
    fired = evaluate_rules()
    return {"fired_rules": fired}
