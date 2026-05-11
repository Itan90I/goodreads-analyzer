"""
模块5：智能问答代理（DeepSeek 版）
兼容本地 .env 和 Streamlit Cloud Secrets
"""
import os
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI

# 确保能导入同目录下的 analysis 模块（本地和云端都适用）
sys.path.insert(0, os.path.dirname(__file__))
from analysis import (
    analysis_top_rated_books,
    analysis_monthly_trend,
    analysis_rating_likes,
    analysis_top_authors,
    analysis_length_rating
)

# ---------- 安全加载本地 .env（本地开发用）----------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------- 安全获取 API Key ----------
def get_api_key():
    """
    优先从 Streamlit Secrets（云端）读取，
    若失败则回退到环境变量（本地 .env）
    """
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "DEEPSEEK_API_KEY" in st.secrets:
            return st.secrets["DEEPSEEK_API_KEY"]
    except Exception:
        pass
    return os.getenv("DEEPSEEK_API_KEY")

API_KEY = get_api_key()
if not API_KEY:
    print("⚠️ 警告：未找到 DEEPSEEK_API_KEY，智能问答功能将不可用。")
    API_KEY = None

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

# 初始化 OpenAI 客户端（仅在 Key 存在时）
client = None
if API_KEY:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ==================== 功能描述与映射 ====================
FUNCTION_DESCRIPTIONS = {
    "top_rated_books": {
        "cn": "书籍评分Top 10",
        "desc": "返回平均分最高的10本书"
    },
    "monthly_trend": {
        "cn": "月度评论趋势",
        "desc": "返回每月评论数量的变化趋势"
    },
    "rating_likes": {
        "cn": "评分与点赞分布",
        "desc": "不同评分（1-5星）下点赞数的箱线图"
    },
    "top_authors": {
        "cn": "作者排行榜",
        "desc": "平均点赞最高的Top 10作者（评论数≥5）"
    },
    "length_rating": {
        "cn": "评论字数与评分关系",
        "desc": "评论文本长度与评分的散点图与趋势线"
    }
}

FUNC_MAP = {
    "top_rated_books": analysis_top_rated_books,
    "monthly_trend": analysis_monthly_trend,
    "rating_likes": analysis_rating_likes,
    "top_authors": analysis_top_authors,
    "length_rating": analysis_length_rating
}

# ==================== 核心问答函数 ====================
def ask_ai(question: str, df: pd.DataFrame):
    """解析用户自然语言问题，返回分析结果和图表"""
    if not client:
        return "❌ 智能问答未配置：请设置 DEEPSEEK_API_KEY（本地放在 .env 文件，云端配置 Secrets）", None

    func_list_str = "\n".join(
        f"- {k}: {v['desc']}" for k, v in FUNCTION_DESCRIPTIONS.items()
    )

    system_prompt = f"""你是一个书籍评论数据分析助手。你可以帮用户进行以下分析：
{func_list_str}

请根据用户的问题，判断应该调用哪个功能。以 JSON 格式纯粹返回：
{{"function": "功能英文名", "explanation": "一句话解释为什么选择这个功能"}}

功能英文名只能从上表中的键名选择。如果问题不匹配任何功能，function 字段设为 null。"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        raw = response.choices[0].message.content
        parsed = json.loads(raw)
        func_name = parsed.get("function")
        explanation = parsed.get("explanation", "")

        if func_name and func_name in FUNC_MAP:
            analysis_func = FUNC_MAP[func_name]
            data, fig = analysis_func(df)
            func_cn = FUNCTION_DESCRIPTIONS[func_name]["cn"]
            answer = f"📊 已为您执行【{func_cn}】分析。\n💡 {explanation}"
            return answer, fig
        else:
            return ("🤔 抱歉，我暂时不支持这个问题的分析。"
                    "您可以试试问我：\n"
                    "- 评分最高的书有哪些？\n"
                    "- 最近评论量变化趋势？\n"
                    "- 哪个作者的点赞最多？\n"
                    "- 评论长度和评分有关系吗？"), None

    except Exception as e:
        return f"❌ 智能问答出错：{str(e)}", None


def ask_free_text(question: str, df: pd.DataFrame):
    """让模型基于数据集统计信息自由回答（备选）"""
    if not client:
        return "❌ 智能问答未配置：请设置 DEEPSEEK_API_KEY"

    try:
        most_common_author = df['author'].mode()
        common_author = most_common_author.iloc[0] if not most_common_author.empty else '无'
    except KeyError:
        common_author = '无'

    stats_text = f"""
数据集概况：
- 总评论数：{len(df)}
- 涉及书籍数：{df['book_title'].nunique()}
- 平均评分：{df['rating'].mean():.2f}
- 平均点赞数：{df['likes'].mean():.1f}
- 最常见作者：{common_author}
- 评论日期范围：{df['review_date'].min().date()} 至 {df['review_date'].max().date()}
""".strip()

    prompt = f"""你是一个书籍数据分析助手。以下是你所拥有的数据集统计信息：
{stats_text}

用户问题：{question}

请用自然的语言回答用户。你可以基于上述统计信息，但不要编造不存在的数据。如果无法回答，请诚实告知。"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是一个友好的数据分析助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 对话失败：{str(e)}"