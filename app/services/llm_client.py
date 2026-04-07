from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, LLM_TIMEOUT_SECONDS

SYSTEM_PROMPT = '''
你是 Homie 智能家居 Agent 的意图解析器。
你必须只返回一个 JSON 对象，不要返回 markdown，不要解释。

可用设备：
- light_001: 客厅灯
- aircon_001: 客厅空调
- curtain_001: 客厅窗帘
- door_001: 入户门

只允许三种 mode：
1. instant
2. rule
3. unknown

instant 格式：
{
  "mode": "instant",
  "message": "简短说明",
  "action": {
    "device_id": "aircon_001",
    "command": "set",
    "params": {
      "power": "on",
      "mode": "cool",
      "target_temp": 24
    }
  }
}

rule 格式：
{
  "mode": "rule",
  "message": "简短说明",
  "rule": {
    "name": "规则名称",
    "trigger_type": "time" 或 "condition",
    "trigger": {...},
    "actions": [...]
  }
}

动作命令限制：
- light_001: turn_on, turn_off
- aircon_001: turn_on, turn_off, set
- curtain_001: open, close
- door_001: lock, unlock

condition 触发器限制：
- {"metric": "temperature", "operator": ">", "value": 30}
- {"metric": "temperature", "operator": "<", "value": 24}
- {"metric": "light", "operator": "<", "value": 100}
- {"metric": "presence", "operator": "==", "value": false}

time 触发器格式：
- {"time": "22:00"}

无法理解时输出：
{
  "mode": "unknown",
  "message": "无法理解"
}
'''

_client: OpenAI | None = None


def get_client() -> OpenAI | None:
    global _client
    if not OPENAI_API_KEY:
        return None
    if _client is None:
        _client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
            timeout=LLM_TIMEOUT_SECONDS,
        )
    return _client


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()

    # 1) 直接就是 JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2) 代码块中的 JSON
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        return json.loads(fence_match.group(1))

    # 3) 文本里第一个完整的大括号对象
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        return json.loads(candidate)

    raise ValueError("Model output did not contain a valid JSON object")


def call_llm_for_home_control(user_prompt: str) -> dict[str, Any]:
    client = get_client()
    if client is None:
        return {"mode": "unknown", "message": "未读取到 API Key，请检查 .env"}

    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = completion.choices[0].message.content or ""
        data = extract_json_object(content)
        return data
    except Exception as e:
        return {"mode": "unknown", "message": f"LLM 调用失败: {type(e).__name__}: {e}"}


def llm_health_check() -> dict[str, Any]:
    client = get_client()
    masked_key = ""
    if OPENAI_API_KEY:
        masked_key = OPENAI_API_KEY[:6] + "..." + OPENAI_API_KEY[-4:]

    if client is None:
        return {
            "ok": False,
            "message": "没有读取到 API Key",
            "base_url": OPENAI_BASE_URL,
            "model": OPENAI_MODEL,
            "api_key_preview": masked_key,
        }

    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": "你只返回一个 JSON 对象：{\"ok\": true}"},
                {"role": "user", "content": "测试连接"},
            ],
        )
        content = completion.choices[0].message.content or ""
        parsed = extract_json_object(content)
        return {
            "ok": True,
            "message": "LLM 连接成功",
            "base_url": OPENAI_BASE_URL,
            "model": OPENAI_MODEL,
            "api_key_preview": masked_key,
            "raw_preview": content[:200],
            "parsed": parsed,
        }
    except Exception as e:
        return {
            "ok": False,
            "message": f"LLM 连接失败: {type(e).__name__}: {e}",
            "base_url": OPENAI_BASE_URL,
            "model": OPENAI_MODEL,
            "api_key_preview": masked_key,
        }
