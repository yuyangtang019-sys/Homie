# Homie
一个基于 LLM（大模型）驱动的智能家居控制系统，支持通过自然语言控制设备、规则自动化以及本地硬件接入（ESP32）（接口未来可接入）

✨ 项目简介
Homie LLM 是一个融合了：
🧠 大语言模型（OpenAI / DashScope / Qwen）
🏠 智能家居设备控制
⚙️ 规则引擎 & 自动化调度
🔌 硬件接入（ESP32）
的轻量级智能家居系统。
用户可以通过自然语言（例如：“帮我打开客厅灯”）直接控制设备，而无需手动编写规则或操作 UI。

🚀 核心功能
🧠 LLM 智能控制
自然语言 → 结构化指令（JSON）
自动解析用户意图
支持多模型（OpenAI / DashScope / 兼容接口）

⏰ 调度系统
定时任务执行
周期性自动化（如每天开灯）

📊 日志系统
操作日志记录
登录保护（简单密码）
前端日志查看界面

🧱 项目结构

Homie_llm_fixed/
├── app/
│   ├── api/            # API 路由（设备 / 规则 / Agent 等）
│   ├── services/       # 核心服务（LLM / 规则 / 调度）
│   ├── devices/        # 设备抽象层
│   ├── templates/      # 前端页面
│   ├── static/         # 前端资源
│   └── main.py         # FastAPI 入口
│
├── firmware/           # ESP32 示例代码
├── requirements.txt
└── .env.example


⚡ 快速启动
1️⃣ 安装依赖
pip install -r requirements.txt
2️⃣ 配置环境变量

复制 .env.example：
cp .env.example .env

示例：

# LLM 配置
OPENAI_API_KEY=你的key
OPENAI_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen3-max

# 可选（兼容）
DASHSCOPE_API_KEY=你的key

# 日志系统
LOGS_PASSWORD=123456
3️⃣ 启动服务
uvicorn app.main:app --reload

访问：

http://127.0.0.1:8000
