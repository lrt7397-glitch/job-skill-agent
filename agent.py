"""生成层：使用 LangChain 结构化输出生成专业技能描述。

核心函数 generate_skill_description(job_title, skills, config) -> str，
仅依赖配置层，不感知采集来源或浏览器对象，与采集层完全解耦。

注意：DeepSeek thinking 模型（如 deepseek-v4-flash）不支持 response_format
和 function calling 的 tool_choice，因此使用 with_structured_output(method="json_mode")
实现结构化输出，system prompt 中包含 "json" 关键词以满足 json_mode 要求。
"""
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

from config import LLMConfig


class SkillDescription(BaseModel):
    """结构化输出模型：职位名称 + 生成的专业技能描述文字。"""

    job_title: str = Field(description="职位名称")
    skills_text: str = Field(description="根据岗位需求生成的专业技能描述文字，100-200字")


SYSTEM_PROMPT = """你是一位资深简历顾问。

根据给定的职位名称和技能标签，生成一段该岗位要求的"专业技能"描述。

要求：
1. 用一段连贯文字或分号分隔的条目，控制在 100-200 字。
2. 合理使用"熟练掌握 / 熟悉 / 了解"分级，但不要过度拔高。
3. 不得编造技能标签之外的技术。
4. 语言专业、简洁，符合中文简历风格。

请以 json 格式输出，包含 job_title（职位名称）和 skills_text（专业技能描述文字）两个字段。"""


def get_llm(config: LLMConfig):
    """模型工厂：按 provider 路由返回对应 LLM 实例。

    - provider == "deepseek" → ChatDeepSeek
    - provider == "openai" 或其它 OpenAI 兼容 → ChatOpenAI(base_url=api_base)

    统一传入 model、temperature、api_key，切换 provider 仅改配置不改代码。
    """
    if config.provider == "deepseek":
        from langchain_deepseek import ChatDeepSeek

        return ChatDeepSeek(
            model=config.model_id,
            temperature=config.temperature,
            api_key=config.api_key,
        )
    else:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=config.model_id,
            temperature=config.temperature,
            api_key=config.api_key,
            base_url=config.api_base,
        )


def generate_skill_description(job_title: str, skills: list[str], config: LLMConfig) -> str:
    """根据职位名称与技能标签生成专业技能描述文字。

    Args:
        job_title: 职位名称。
        skills: 技能标签字符串数组。
        config: LLM 配置。

    Returns:
        生成的专业技能描述文字（100-200字）；空技能时返回空串且不调用 LLM。
    """
    if not skills:
        print(f"[跳过] 职位「{job_title}」无技能标签，不生成描述")
        return ""

    llm = get_llm(config)
    structured_llm = llm.with_structured_output(SkillDescription, method="json_mode")

    user_msg = f"职位名称：{job_title}\n技能标签：{', '.join(skills)}"

    result = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ])

    text = result.skills_text

    # 字数校验：100-200 字区间，越界告警但保留原值供复核
    text_len = len(text)
    if not (100 <= text_len <= 200):
        print(f"[告警] 职位「{job_title}」生成文字字数 {text_len} 越界（目标 100-200），保留原值供复核")

    return text