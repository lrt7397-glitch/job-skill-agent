"""FastAPI 应用：为前端提供职位列表与技能生成接口。

复用根目录现有 agent.py / config.py，不重写爬虫与 Agent 逻辑。
启动：uvicorn backend.main:app --reload --port 8000
"""
import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 把项目根目录加入 sys.path，确保能 import 到根目录的 agent.py / config.py
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from agent import generate_skill_description  # noqa: E402
from config import get_config  # noqa: E402

from backend.schemas import (  # noqa: E402
    JobItem,
    JobsResponse,
    GenerateRequest,
    GenerateResponse,
    ScrapeRequest,
    ScrapeResponse,
)

app = FastAPI(title="BOSS 职位技能生成器 API", version="1.0.0")

# CORS：允许 Vite 默认端口（localhost 与 127.0.0.1 都放行）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据文件路径：优先 boss_jobs_raw.json，回退 results.json
DATA_DIR = ROOT_DIR / "data"
RAW_JOBS_FILE = DATA_DIR / "boss_jobs_raw.json"
RESULTS_FILE = DATA_DIR / "results.json"


def _normalize_job(raw: dict) -> JobItem:
    """把原始 dict 归一化为 JobItem。

    兼容两种数据源：
    - boss_jobs_raw.json：title/company/salary/city/area/experience/degree/skills/job_id
    - results.json（回退）：job_title/company/salary/city/skills/generated_skills_text
      其中 area/experience/degree/job_id 缺失，补空串。
    """
    return JobItem(
        job_id=raw.get("job_id", raw.get("encryptJobId", "")),
        title=raw.get("title", raw.get("job_title", "")),
        company=raw.get("company", raw.get("brandName", "")),
        salary=raw.get("salary", raw.get("salaryDesc", "")),
        city=raw.get("city", raw.get("cityName", "")),
        area=raw.get("area", raw.get("areaDistrict", "")),
        experience=raw.get("experience", raw.get("jobExperience", "")),
        degree=raw.get("degree", raw.get("jobDegree", "")),
        skills=raw.get("skills", []) or [],
    )


@app.get("/api/jobs", response_model=JobsResponse)
def get_jobs():
    """读取职位数据文件并返回列表。

    优先读 data/boss_jobs_raw.json；不存在则回退 data/results.json。
    文件不存在或解析失败时返回空列表 + 提示信息，不抛 500。
    """
    try:
        target = RAW_JOBS_FILE if RAW_JOBS_FILE.exists() else RESULTS_FILE
        if not target.exists():
            return JobsResponse(
                jobs=[],
                message="未找到数据文件，请先运行 python main.py 生成 data/results.json",
            )

        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            return JobsResponse(jobs=[], message=f"数据文件 {target.name} 格式异常，期望列表")

        jobs = [_normalize_job(item) for item in data]
        source = "boss_jobs_raw.json" if target == RAW_JOBS_FILE else "results.json（回退）"
        return JobsResponse(jobs=jobs, message=f"已加载 {len(jobs)} 条职位（来源：{source}）")
    except json.JSONDecodeError:
        return JobsResponse(jobs=[], message="数据文件 JSON 解析失败，请检查文件内容")
    except Exception as e:
        return JobsResponse(jobs=[], message=f"读取数据文件失败：{e}")


@app.post("/api/agent/generate", response_model=GenerateResponse)
def generate_skills(req: GenerateRequest):
    """调用现有 Agent 生成技能描述。

    复用 agent.generate_skill_description(job_title, skills, config.llm)，不重新实现。
    skills 为空时返回 400 + 中文提示。
    """
    if not req.skills or not any(s.strip() for s in req.skills):
        raise HTTPException(status_code=400, detail="技能标签列表不能为空，请选择带技能标签的职位")

    try:
        config = get_config()
        # 现有 agent 签名为三参：(job_title, skills, llm_config)
        text = generate_skill_description(req.job_title, req.skills, config.llm)
        return GenerateResponse(skills_text=text or "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"技能生成失败：{e}")


@app.post("/api/scrape", response_model=ScrapeResponse)
def trigger_scrape(req: ScrapeRequest):
    """触发爬虫（异步子进程，不等待完成）。

    scraper.py 无 __main__ 块，故调用 main.py（采集+生成完整流程）。
    通过环境变量传参，subprocess.Popen 不阻塞主线程。
    """
    try:
        main_script = ROOT_DIR / "main.py"
        if not main_script.exists():
            raise HTTPException(status_code=501, detail="未找到 main.py，请手动运行 python main.py 完成采集")

        env = os.environ.copy()
        env["SCRAPER_QUERY"] = req.query
        env["SCRAPER_CITY"] = req.city
        env["SCRAPER_SALARY"] = req.salary
        env["SCRAPER_DEGREE"] = req.degree

        subprocess.Popen(
            [sys.executable, str(main_script)],
            cwd=str(ROOT_DIR),
            env=env,
        )
        return ScrapeResponse(message="爬虫已触发，请查看弹出的浏览器窗口完成登录")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"触发爬虫失败：{e}")


@app.get("/api/health")
def health():
    """健康检查。"""
    return {"status": "ok"}