"""采集层：使用 patchright + Playwright 同步 API 采集 BOSS 直聘职位。

核心函数 fetch_jobs(config) -> list[dict]，仅负责拿数据，不写文件、不调 AI。
使用 launch_persistent_context 持久化登录态，返回值为 BrowserContext。
"""
import time
from urllib.parse import urlencode

from patchright.sync_api import sync_playwright

from config import ScraperConfig


def _build_search_url(config: ScraperConfig) -> str:
    """组装搜索页 URL。"""
    params = {
        "query": config.query,
        "city": config.city,
        "salary": config.salary,
        "degree": config.degree,
    }
    if config.experience:
        params["experience"] = config.experience
    return f"https://www.zhipin.com/web/geek/jobs?{urlencode(params)}"


def _build_api_url(config: ScraperConfig, page: int) -> str:
    """组装职位列表接口 URL。"""
    params = {
        "query": config.query,
        "city": config.city,
        "salary": config.salary,
        "degree": config.degree,
        "page": page,
        "pageSize": config.page_size,
    }
    if config.experience:
        params["experience"] = config.experience
    return f"https://www.zhipin.com/wapi/zpgeek/search/joblist.json?{urlencode(params)}"


def _extract_job(job: dict) -> dict:
    """从原始职位 dict 提取规范化字段，技能标签空时用 jobLabels 兜底。"""
    skills = job.get("skills", [])
    if not skills:
        skills = job.get("jobLabels", [])

    return {
        "title": job.get("jobName", ""),
        "company": job.get("brandName", ""),
        "salary": job.get("salaryDesc", ""),
        "city": job.get("cityName", ""),
        "area": job.get("areaDistrict", ""),
        "experience": job.get("jobExperience", ""),
        "degree": job.get("jobDegree", ""),
        "skills": skills if isinstance(skills, list) else [],
        "job_id": job.get("encryptJobId", ""),
    }


def fetch_jobs(config: ScraperConfig) -> list[dict]:
    """采集 BOSS 直聘职位列表。

    流程：启动持久化浏览器上下文 → 打开搜索页 → 等待手动登录 →
          翻页循环用 page.evaluate fetch 调用接口 → 提取规范化职位 → 关闭上下文。

    Args:
        config: 爬虫配置。

    Returns:
        职位列表，每条含 title/company/salary/city/area/experience/degree/skills/job_id。
    """
    jobs: list[dict] = []

    with sync_playwright() as p:
        # launch_persistent_context 返回 BrowserContext，非 Browser
        context = p.chromium.launch_persistent_context(
            user_data_dir=config.user_data_dir,
            headless=config.headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.new_page()

        # 打开搜索页
        search_url = _build_search_url(config)
        page.goto(search_url)

        # 等待用户手动登录
        print(f"[采集] 请在浏览器中完成登录，等待 {config.login_wait} 秒...")
        time.sleep(config.login_wait)

        # 翻页采集
        for page_num in range(1, config.max_pages + 1):
            api_url = _build_api_url(config, page_num)

            try:
                result = page.evaluate(
                    """async (url) => {
                        const resp = await fetch(url);
                        return await resp.json();
                    }""",
                    api_url,
                )
            except Exception as e:
                print(f"[采集] 第 {page_num} 页请求失败：{e}，停止采集")
                break

            job_list = result.get("zpData", {}).get("jobList", [])

            if not job_list:
                print(f"[采集] 第 {page_num} 页无数据，停止采集")
                break

            for job in job_list:
                jobs.append(_extract_job(job))

            print(f"[采集] 第 {page_num} 页采集 {len(job_list)} 条职位，累计 {len(jobs)} 条")

            if page_num < config.max_pages:
                time.sleep(config.page_delay)

        context.close()

    return jobs