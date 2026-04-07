# Homie LLM Fixed

这是修复过“能启动但无法和 AI 对话”的版本。

## 这版重点修复
- 不再强依赖 `response_format={"type":"json_object"}`，避免部分兼容接口报错
- 增加更稳的 JSON 提取器，支持从普通文本或 ```json 代码块中提取 JSON
- 增加 `/api/agent/health` 用来检查：
  - API Key 是否读取成功
  - base_url / model 是否生效
  - 是否能成功请求模型
- 增加更详细的错误返回，方便定位到底是：
  - Key 没读到
  - base_url 不对
  - 模型名不对
  - 接口调用失败
  - 模型返回不是 JSON

## 启动
```bash
cd Homie_llm_fixed
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 检查 AI 是否真的通了
启动后先打开：
```text
http://127.0.0.1:8000/api/agent/health
```

如果 `ok=true`，说明 LLM 通了。

## .env 示例
```env
DASHSCOPE_API_KEY=你的key
OPENAI_API_KEY=你的key
OPENAI_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen3-max
LOGS_PASSWORD=123456
```
