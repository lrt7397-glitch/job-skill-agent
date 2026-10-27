"""全局配置模块：集中管理爬虫参数、LLM 参数与应用参数。

使用 pydantic-settings BaseSettings，支持 .env 文件与环境变量覆盖。
提供 get_config() 单例入口，业务代码统一通过该函数获取配置。
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ScraperConfig(BaseSettings):
    """爬虫配置：BOSS 直聘职位采集参数。"""

    model_config = SettingsConfigDict(env_prefix="SCRAPER_", env_file=".env", extra="ignore")

    query: str = "Python"
    city: str = "101020100"
    salary: str = "405"
    degree: str = "203"
    experience: str = ""
    max_pages: int = 3
    page_size: int = 30
    headless: bool = False
    user_data_dir: str = "./boss_profile"
    login_wait: int = 20
    page_delay: float = 2.0


class LLMConfig(BaseSettings):
    """LLM 配置：模型工厂路由参数，支持 DeepSeek / OpenAI / Ollama 等。"""

    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=".env", extra="ignore")

    provider: str = "deepseek"
    model_id: str = "deepseek-chat"
    api_base: str = "https://api.deepseek.com/v1"
    api_key: str = ""
    temperature: float = 0.3


class AppConfig(BaseSettings):
    """应用总配置：组合爬虫配置与 LLM 配置，附加输出路径。"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    scraper: ScraperConfig = ScraperConfig()
    llm: LLMConfig = LLMConfig()
    output_path: str = "data/results.json"


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """获取应用配置单例。

    首次调用构造 AppConfig 实例并缓存，后续调用返回同一实例。
    业务代码统一通过本函数获取配置，避免重复 IO。

    注意：显式传入 ScraperConfig() / LLMConfig() 以确保嵌套配置
    在调用时点重新从环境变量读取，避免类定义时默认值提前求值导致
    环境变量覆盖失效。
    """
    return AppConfig(
        scraper=ScraperConfig(),
        llm=LLMConfig(),
    )