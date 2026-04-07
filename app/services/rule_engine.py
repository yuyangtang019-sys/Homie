from __future__ import annotations

import time
from app.models import Rule
from app.services.state_store import store


def compare(left, operator: str, right):
    if operator == ">":
        return left > right
    if operator == "<":
        return left < right
    if operator == ">=":
        return left >= right
    if operator == "<=":
        return left <= right
    return left == right


def should_trigger(rule: Rule, env: dict) -> bool:
    if not rule.enabled:
        return False

    if rule.last_triggered_at is not None and time.time() - rule.last_triggered_at < rule.cooldown_seconds:
        return False

    if rule.trigger_type == "time":
        return env.get("current_time") == rule.trigger.get("time")

    if rule.trigger_type == "condition":
        metric = rule.trigger.get("metric")
        operator = rule.trigger.get("operator")
        value = rule.trigger.get("value")
        return compare(env.get(metric), operator, value)

    return False


def evaluate_rules() -> list[str]:
    fired = []
    rules = sorted(store.rules.values(), key=lambda x: x.priority, reverse=True)
    for rule in rules:
        if should_trigger(rule, store.environment):
            for action in rule.actions:
                store.execute_action(action, source="agent")
            rule.last_triggered_at = time.time()
            fired.append(rule.name)
            store.add_log("agent", f"触发规则：{rule.name}")
    return fired
