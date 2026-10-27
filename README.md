# BOSS 岗位技能描述生成器

采集 BOSS 直聘目标岗位的技能标签，交给大模型以「资深简历顾问」的角色生成 100–200 字、可直接用于简历的「专业技能」描述，并支持命令行、REST API 与 Vue3 对话界面三种使用方式。

> 本项目仅供个人学习与技术研究使用，请遵守目标网站的用户协议，控制采集频率，不要用于商业用途或数据分发。

---

## 功能特性

- **职位采集**：按关键词 / 城市 / 薪资 / 学历 / 经验筛选，持久化登录态，翻页限速，空页自动停止。
- **技能标签提取**：技能标签缺失时自动用 `jobLabels` 兜底，字段缺失填空不中断。
- **AI 生成**：LangChain + Pydantic 结构化输出，强制 100–200 字、分级用词、禁止编造标签外技术。
- **模型可切换**：支持 DeepSeek / OpenAI / Ollama 等 OpenAI 兼容服务，改配置即可换模型。
- **批量容错**：单条生成失败不中断整体，已成功部分照常归档。
- **Web 界面**：左侧岗位列表含薪资 / 学历筛选，右侧对话式生成面板。

---

## 架构

```
config.py ──┬── scraper.py（采集层，patchright + Playwright）
            │        └─ BOSS 直聘 wapi 职位列表接口
            └── agent.py（生成层，LangChain + Pydantic 结构化输出）
                     └─ LLM 服务（DeepSeek / OpenAI / Ollama …）
                          │
main.py（编排层）──────────┘
   └─ data/results.json
        │
backend/main.py（FastAPI）── /api/jobs、/api/agent/generate、/api/scrape
        │
frontend/（Vue3 + Vite + Element Plus）
```

采集层与生成层完全解耦：采集层只返回 `list[dict]`，不写文件、不调 AI；生成层只接收「职位名 + 技能标签」。

---

## 目录结构

```
boss_agent/
├─ config.py              # 配置层：pydantic-settings 三组配置 + 单例入口
├─ scraper.py             # 采集层：浏览器登录态、接口采集、字段规范化
├─ agent.py               # 生成层：模型工厂 + 结构化技能描述生成
├─ main.py                # 编排层：采集 → 生成 → 归档（CLI 入口）
├─ requirements.txt       # Python 依赖
├─ .env.example           # 环境变量模板
├─ data/                  # 归档目录（results.json 运行时生成）
├─ backend/
│  ├─ main.py             # FastAPI 应用
│  └─ schemas.py          # 请求 / 响应模型
└─ frontend/              # Vue3 + Vite 前端
   ├─ src/api.js
   ├─ src/App.vue
   └─ src/components/
```

---

## 环境要求

| 依赖 | 版本要求 | 检查命令 |
| --- | --- | --- |
| Python | 3.10 及以上 | `python --version` |
| Node.js | 18 及以上 | `node --version` |
| npm | 随 Node 安装 | `npm --version` |
| 网络 | 能访问 BOSS 直聘与所选 LLM 服务 | — |

Windows / macOS / Linux 均可运行。以下命令以 **Windows PowerShell** 为例，macOS / Linux 的差异在文末给出。

---

## 从零开始部署（本地）

### 第 1 步：进入项目目录

```powershell
cd D:\BaiduNetdiskDownload\boss_agent
```

### 第 2 步：创建虚拟环境并安装 Python 依赖

```powershell
python -m venv .venv
```

激活虚拟环境（每次新开终端都要执行一次）：

```powershell
.\.venv\Scripts\Activate.ps1
```

> 如果报「无法加载文件，因为在此系统上禁止运行脚本」，先执行：
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`

安装依赖：

```powershell
python -m pip install -U pip
pip install -r requirements.txt
```

### 第 3 步：安装浏览器内核

采集依赖 Chromium，首次必须安装（约 150 MB，下载慢请耐心等待）：

```powershell
patchright install chromium
```

> 若提示 `patchright` 命令不存在或安装失败，改用：
> `python -m playwright install chromium`

### 第 4 步：配置环境变量

```powershell
Copy-Item .env.example .env
notepad .env
```

在 `.env` 中至少填写一项：

```dotenv
LLM_API_KEY=你的_API_Key
```

其余配置（搜索关键词、城市、页数、翻页间隔等）可按需修改，留空即使用默认值。

### 第 5 步：首次运行采集（命令行）

```powershell
python main.py
```

运行过程：

1. 自动弹出 Chromium 窗口并打开 BOSS 直聘搜索页；
2. 终端提示「请在浏览器中完成登录」，你有 **20 秒**（`SCRAPER_LOGIN_WAIT`）时间扫码或账号登录；
3. 登录成功后程序自动翻页采集 3 页（`SCRAPER_MAX_PAGES`），对每条职位调用大模型生成描述；
4. 结果写入 `data/results.json`，终端同步打印摘要。

登录态会保存在 `boss_profile/` 目录，**之后再运行无需重复登录**。

成功标志：终端出现 `[完成] 共处理 N 条职位，结果已写入 data/results.json`。

### 第 6 步：启动后端 API（新开一个终端）

```powershell
cd D:\BaiduNetdiskDownload\boss_agent
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000
```

- 接口文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/api/health>
- 职位列表：<http://127.0.0.1:8000/api/jobs>

### 第 7 步：启动前端（再开一个终端）

```powershell
cd D:\BaiduNetdiskDownload\boss_agent\frontend
npm install
npm run dev
```

浏览器打开 <http://localhost:5173> 即可看到界面：

- 左栏：岗位卡片，支持按薪资、学历筛选；
- 右栏：对话式生成，点击岗位卡片上的「生成技能」会自动带入职位名与技能标签并请求生成；
- 也可以直接在输入框手输「职位名 技能1 技能2」后发送（Ctrl+Enter）。

---

## 使用方式

### 方式一：命令行批量生成

```powershell
python main.py
```

按 `.env` 中的筛选条件采集并批量生成，结果归档到 `data/results.json`。

### 方式二：Web 界面按需生成

启动第 6、7 步的后端与前端后，在页面中挑选岗位并即时生成单条描述。

### 方式三：直接调接口

```powershell
curl -X POST http://127.0.0.1:8000/api/agent/generate `
  -H "Content-Type: application/json" `
  -d '{"job_title":"Python后端工程师","skills":["Python","Django","MySQL"]}'
```

后端另有 `POST /api/scrape` 用于触发采集（以子进程方式执行 `main.py`，会弹出浏览器窗口），可在 <http://127.0.0.1:8000/docs> 中调试。

---

## 配置说明

所有配置集中在 `.env`，由 `config.py` 读取，业务代码无硬编码。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `LLM_API_KEY` | 空 | **必填**，模型服务密钥 |
| `LLM_PROVIDER` | `deepseek` | `deepseek` / `openai` / `ollama` 等 |
| `LLM_MODEL_ID` | `deepseek-chat` | 模型标识 |
| `LLM_API_BASE` | `https://api.deepseek.com/v1` | OpenAI 兼容地址 |
| `LLM_TEMPERATURE` | `0.3` | 采样温度 |
| `SCRAPER_QUERY` | `Python` | 搜索关键词 |
| `SCRAPER_CITY` | `101020100` | 城市代码（上海） |
| `SCRAPER_SALARY` | `405` | 薪资代码（10-20K） |
| `SCRAPER_DEGREE` | `203` | 学历代码（本科） |
| `SCRAPER_EXPERIENCE` | 空 | 经验代码，空为不限 |
| `SCRAPER_MAX_PAGES` | `3` | 最大采集页数 |
| `SCRAPER_PAGE_SIZE` | `30` | 每页条数 |
| `SCRAPER_HEADLESS` | `False` | 是否无头，首次登录必须为 `False` |
| `SCRAPER_USER_DATA_DIR` | `./boss_profile` | 登录态目录 |
| `SCRAPER_LOGIN_WAIT` | `20` | 登录等待秒数 |
| `SCRAPER_PAGE_DELAY` | `2.0` | 翻页间隔秒数 |
| `OUTPUT_PATH` | `data/results.json` | 结果归档路径 |

切换模型示例（以 Ollama 本地模型为例）：

```dotenv
LLM_PROVIDER=ollama
LLM_MODEL_ID=qwen2.5
LLM_API_BASE=http://localhost:11434/v1
LLM_API_KEY=ollama
```

无需改动任何业务代码。

---

## 常见问题

| 现象 | 原因与处理 |
| --- | --- |
| `patchright install chromium` 失败 | 换用 `python -m playwright install chromium`；国内网络可设置镜像后重试 |
| 浏览器没弹出 / 秒退 | 确认 `SCRAPER_HEADLESS=False`；确认已安装浏览器内核 |
| 采集到 0 条数据 | 登录态失效或被风控拦截：删除 `boss_profile/` 目录后重新 `python main.py` 手动登录；适当调大 `SCRAPER_LOGIN_WAIT` |
| `python main.py` 报鉴权错误 | `.env` 中 `LLM_API_KEY` 为空或无效 |
| 前端页面空白 / 提示获取失败 | 后端未启动或端口不是 8000；前端通过 Vite 代理转发 `/api` 到 `http://localhost:8000` |
| 端口被占用 | 后端换 `--port 8001`（同时需改 `frontend/vite.config.js` 的 proxy target）；前端用 `npm run dev -- --port 5174` |
| 终端提示「字数越界」 | 正常告警，生成结果仍会保留，可在归档文件中人工复核 |
| 想重新登录其他账号 | 关闭所有相关浏览器，删除 `boss_profile/` 目录后重跑 |

---


## 已知限制

- 需要**人工完成一次登录**，无法全自动无人值守。
- 单机单用户设计，未做并发控制与任务队列。
- 结果按次覆盖写入单个 JSON 文件，未做去重与增量同步。
- 未包含自动化测试，质量依赖生成后的字数校验与人工复核。

---

## 免责声明

本项目仅用于学习 Python 爬虫、LangChain 应用与前后端联调，不得用于商业用途、批量数据贩卖或其他违反目标网站用户协议及相关法律法规的行为。使用本项目产生的一切后果由使用者自行承担。

## 许可证

MIT
