"""后端 Pydantic 请求/响应模型。

字段与 data/boss_jobs_raw.json 完全对应；同时兼容 results.json 的回退字段。
"""
from typing import List

from pydantic import BaseModel, Field


class JobItem(BaseModel):
    """职位条目，字段与 data/boss_jobs_raw.json 完全对应。"""
    job_id: str = Field(default="", description="加密职位ID")
    title: str = Field(default="", description="职位名称")
    company: str = Field(default="", description="公司名称")
    salary: str = Field(default="", description="薪资描述，如 15-25K·13薪")
    city: str = Field(default="", description="城市")
    area: str = Field(default="", description="商圈/区域")
    experience: str = Field(default="", description="经验要求")
    degree: str = Field(default="", description="学历要求")
    skills: List[str] = Field(default_factory=list, description="技能标签列表")


class JobsResponse(BaseModel):
    """职位列表响应（带提示信息，文件缺失时不抛 500）。"""
    jobs: List[JobItem] = Field(default_factory=list)
    message: str = Field(default="")


class GenerateRequest(BaseModel):
    """技能生成请求体。"""
    job_title: str = Field(..., description="职位名称")
    skills: List[str] = Field(..., description="技能标签列表")


class GenerateResponse(BaseModel):
    """技能生成响应。"""
    skills_text: str = Field(default="", description="生成的技能描述")


class ScrapeRequest(BaseModel):
    """爬虫触发请求体。"""
    query: str = Field(default="Python")
    city: str = Field(default="101020100")
    salary: str = Field(default="405")
    degree: str = Field(default="203")


class ScrapeResponse(BaseModel):
    """爬虫触发响应。"""
    message: str = Field(default="")