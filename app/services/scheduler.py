from __future__ import annotations

import asyncio
from app.services.rule_engine import evaluate_rules


async def scheduler_loop() -> None:
    while True:
        evaluate_rules()
        await asyncio.sleep(5)
