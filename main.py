"""编排层：串联采集 → 生成 → 归档全流程。

流程：加载配置 → 采集职位 → 逐条生成描述 → 汇总 → 归档 JSON → 终端展示。
单条生成失败不中断整体，已成功部分仍可归档。
"""
import json
import os

from agent import generate_skill_description
from config import get_config
from scraper import fetch_jobs


def main() -> None:
    """主流程入口。"""
    config = get_config()

    # 1. 采集职位
    print("=" * 60)
    print("[流程] 开始采集 BOSS 直聘职位")
    print("=" * 60)
    jobs = fetch_jobs(config.scraper)

    if not jobs:
        print("[流程] 未采集到任何职位，流程结束")
        return

    print(f"[流程] 共采集 {len(jobs)} 条职位，开始生成技能描述")

    # 2. 逐条生成描述
    results = []
    for idx, job in enumerate(jobs, 1):
        print(f"\n[{idx}/{len(jobs)}] 处理职位：{job['title']}")

        try:
            generated_text = generate_skill_description(
                job["title"], job["skills"], config.llm
            )
        except Exception as e:
            print(f"[错误] 职位「{job['title']}」生成失败：{e}")
            generated_text = ""

        result = {
            "job_title": job["title"],
            "company": job["company"],
            "salary": job["salary"],
            "city": job["city"],
            "skills": job["skills"],
            "generated_skills_text": generated_text,
        }
        results.append(result)

        # 终端打印摘要
        if generated_text:
            print(f"  → {generated_text}")

    # 3. 归档写入
    output_dir = os.path.dirname(config.output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(config.output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"[完成] 共处理 {len(results)} 条职位，结果已写入 {config.output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()