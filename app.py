"""
主程序：智能问数 Web 应用 (Goodreads 书籍评论分析)
基于 Streamlit，支持中英文双语切换 + 自定义数据上传（鲁棒性测试）
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# 确保可以导入 src 目录下的模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from analysis import (
    load_clean_data,
    analysis_top_rated_books,
    analysis_monthly_trend,
    analysis_rating_likes,
    analysis_top_authors,
    analysis_length_rating,
    analysis_recommend_books,
    analysis_book_compare_radar,
    analysis_review_wordcloud
)

# 尝试导入智能问答模块
try:
    from QA_agent import ask_ai
    qa_available = True
except Exception as e:
    qa_available = False
    qa_error_msg = str(e)

# ----------------- 页面配置 -----------------
st.set_page_config(
    page_title="Goodreads 智能问数",
    page_icon=":book:",
    layout="wide"
)

# ----------------- 语言选择 -----------------
LANG = st.sidebar.selectbox(
    "语言 / Language",
    ["中文", "English"]
)

# ----------------- 自定义数据上传（20%鲁棒性测试核心）-----------------
st.sidebar.markdown("---")
st.sidebar.subheader("上传自定义数据" if LANG == '中文' else "Upload Custom Data")
uploaded_file = st.sidebar.file_uploader(
    "选择文件（支持 CSV / Excel / JSON）" if LANG == '中文' else "Choose a file (CSV / Excel / JSON)",
    type=["csv", "xlsx", "json"]
)

# 定义系统必需的列名（你所有分析用到的列）
REQUIRED_COLS = [
    'book_title', 'author', 'genres',
    'average_rating', 'num_reviews', 'num_pages',
    'rating', 'likes', 'followers',
    'review_content', 'review_date'
]

def validate_and_load(uploaded_file):
    """
    支持 CSV / Excel / JSON 多种格式，带完整的文件异常处理。
    返回 (DataFrame, error_message)
    """
    filename = uploaded_file.name.lower()
    df_up = None
    
    # ---- 1. 按扩展名尝试读取文件 ----
    try:
        if filename.endswith('.csv'):
            # 自动尝试多种编码
            for enc in ['utf-8', 'utf-8-sig', 'gbk', 'latin1']:
                try:
                    df_up = pd.read_csv(uploaded_file, encoding=enc)
                    break
                except UnicodeDecodeError:
                    continue
            if df_up is None:
                return None, "无法读取 CSV 文件，请检查文件编码（建议保存为 UTF-8）。"
        
        elif filename.endswith(('.xlsx', '.xls')):
            df_up = pd.read_excel(uploaded_file, engine='openpyxl')
        
        elif filename.endswith('.json'):
            df_up = pd.read_json(uploaded_file)
        
        else:
            # 未知扩展名也试着用 CSV 读一次
            try:
                df_up = pd.read_csv(uploaded_file)
            except Exception:
                return None, "不支持的文件类型。请上传 CSV、Excel 或 JSON 文件。"
    
    except Exception as e:
        return None, f"文件读取失败：{str(e)}。请检查文件是否损坏或格式是否正确。"

    # ---- 2. 基础验证 ----
    if df_up is None or df_up.empty:
        return None, "文件内容为空，请上传包含有效数据的文件。"

    if len(df_up) < 50:
        return None, "数据行数太少（至少需要 50 行），请上传包含更多记录的数据。"

    # ---- 3. 列名验证 ----
    missing = [col for col in REQUIRED_COLS if col not in df_up.columns]
    if missing:
        return None, f"缺少必要列：{', '.join(missing)}。\n请确保数据包含以下列：{', '.join(REQUIRED_COLS)}"

    # ---- 4. 数据清洗 ----
    try:
        if 'review_date' in df_up.columns:
            df_up['review_date'] = pd.to_datetime(df_up['review_date'], errors='coerce')
        for col in ['rating', 'likes', 'followers', 'average_rating', 'num_reviews', 'num_pages']:
            if col in df_up.columns:
                df_up[col] = pd.to_numeric(df_up[col], errors='coerce')
        if 'review_content' in df_up.columns:
            df_up = df_up[df_up['review_content'].notna()]
        if len(df_up) < 10:
            return None, "数据清洗后可用记录不足（少于10条），请检查数据质量。"
        return df_up, None
    except Exception as e:
        return None, f"数据清洗过程中出现错误：{str(e)}"

# 默认数据缓存加载（与原来一致）
@st.cache_data
def load_default_data(lang='en'):
    if lang == '中文':
        path = "cleaned_reviews_zh.csv"
        if not os.path.exists(path):
            st.warning("中文数据文件未生成，当前使用英文数据")
            path = "cleaned_reviews.csv"
    else:
        path = "cleaned_reviews.csv"
    if not os.path.exists(path):
        st.error(f"未找到 {path}，请先运行 preprocess.py")
        st.stop()
    df = pd.read_csv(path)
    df['review_date'] = pd.to_datetime(df['review_date'])
    return df

# 实际使用的数据源
use_custom = False
if uploaded_file is not None:
    custom_df, error_msg = validate_and_load(uploaded_file)
    if error_msg:
        st.sidebar.error(error_msg)
        df = load_default_data('zh' if LANG == '中文' else 'en')
    else:
        df = custom_df
        use_custom = True
        st.sidebar.success(f"已加载自定义数据，共 {len(df)} 行")
else:
    df = load_default_data('zh' if LANG == '中文' else 'en')

# 根据是否为自定义数据决定双语列
if use_custom:
    # 自定义数据没有中文翻译列，直接使用英文列名
    TITLE_COL = 'book_title'
    AUTHOR_COL = 'author'
    GENRE_COL = 'genres'
    title_to_original = None
else:
    # 默认数据的中英文切换
    if LANG == '中文':
        TITLE_COL = 'book_title_zh' if 'book_title_zh' in df.columns else 'book_title'
        AUTHOR_COL = 'author_zh' if 'author_zh' in df.columns else 'author'
        GENRE_COL = 'genres_zh' if 'genres_zh' in df.columns else 'genres'
    else:
        TITLE_COL = 'book_title'
        AUTHOR_COL = 'author'
        GENRE_COL = 'genres'
    title_to_original = None
    if 'book_title_zh' in df.columns and 'book_title' in df.columns:
        title_to_original = dict(zip(df['book_title_zh'], df['book_title']))

def get_original_title(display_title):
    if title_to_original and display_title in title_to_original:
        return title_to_original[display_title]
    return display_title

# ----------------- 侧边栏导航 -----------------

st.sidebar.markdown("---")
st.sidebar.title("Goodreads 分析")
st.sidebar.markdown(f"已加载 {len(df):,} 条评论数据")

if LANG == '中文':
    options = [
        "数据预览",
        "书籍评分 Top 10",
        "月度评论趋势",
        "评分与点赞分布",
        "作者平均点赞排行",
        "评论字数 vs 评分",
        "作者 & 类型查书",
        "书籍对比图",
        "评论词云",
        "智能问答 (AI)"
    ]
else:
    options = [
        "Data Preview",
        "Top 10 Rated Books",
        "Monthly Review Trend",
        "Rating vs Likes",
        "Top Authors by Likes",
        "Review Length vs Rating",
        "Find Books by Author / Genre",
        "Book vs Book Radar",
        "Review Word Cloud",
        "AI Q&A"
    ]

# 用 expander 包裹导航，点击可折叠
with st.sidebar.expander("选择功能" if LANG == '中文' else "Select", expanded=True):
    option = st.radio(
        "选择功能" if LANG == '中文' else "Select",
        options,
        label_visibility="collapsed"   # 隐藏 radio 自带的标题，避免重复
    )

# ----------------- 主标题 -----------------
if LANG == '中文':
    st.title("Goodreads 书籍评论智能分析系统")
else:
    st.title("Goodreads Book Review Analysis System")

# ----------------- 各功能实现 -----------------
# 数据预览
if option in ["数据预览", "Data Preview"]:
    if LANG == '中文':
        st.subheader("清洗后数据预览")
    else:
        st.subheader("Cleaned Data Preview")

    display_cols = [TITLE_COL, AUTHOR_COL, GENRE_COL, 'rating', 'likes', 'review_date', 'review_content']
    available_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[available_cols].head(50))
    st.caption(f"{'数据集共' if LANG=='中文' else 'Total'} {len(df)} {'行' if LANG=='中文' else 'rows'}, {len(df.columns)} {'列' if LANG=='中文' else 'columns'}, {'展示前 50 行' if LANG=='中文' else 'showing first 50 rows'}")

# 书籍 Top 10
elif option in ["书籍评分 Top 10", "Top 10 Rated Books"]:
    if LANG == '中文':
        st.subheader("平均评分最高的 10 本书")
    else:
        st.subheader("Top 10 Highest Rated Books")
    result, fig = analysis_top_rated_books(df)
    if LANG == '中文' and TITLE_COL != 'book_title' and TITLE_COL in df.columns:
        title_map = df[['book_title', TITLE_COL]].drop_duplicates().set_index('book_title')[TITLE_COL].to_dict()
        result['book_title'] = result['book_title'].map(title_map).fillna(result['book_title'])
    st.pyplot(fig)
    st.dataframe(result.rename(columns={'book_title': '书名' if LANG=='中文' else 'Book Title',
                                        'average_rating': '均分' if LANG=='中文' else 'Avg Rating'}))

# 月度趋势
elif option in ["月度评论趋势", "Monthly Review Trend"]:
    if LANG == '中文':
        st.subheader("评论数量月度变化趋势")
    else:
        st.subheader("Monthly Review Trend")
    result, fig = analysis_monthly_trend(df)
    st.pyplot(fig)
    st.dataframe(result.rename(columns={'review_date': '日期' if LANG=='中文' else 'Date',
                                        'count': '评论数' if LANG=='中文' else 'Reviews'}))

# 评分与点赞
elif option in ["评分与点赞分布", "Rating vs Likes"]:
    if LANG == '中文':
        st.subheader("不同评分等级下的点赞数箱线图")
    else:
        st.subheader("Likes Distribution by Rating")
    result, fig = analysis_rating_likes(df)
    st.pyplot(fig)
    st.dataframe(result)

# 作者排行
elif option in ["作者平均点赞排行", "Top Authors by Likes"]:
    if LANG == '中文':
        st.subheader("平均点赞最高的作者 Top 10 (评论数>=5)")
    else:
        st.subheader("Top 10 Authors by Average Likes (>=5 reviews)")
    result, fig = analysis_top_authors(df)
    if LANG == '中文' and AUTHOR_COL != 'author' and AUTHOR_COL in df.columns:
        author_map = df[['author', AUTHOR_COL]].drop_duplicates().set_index('author')[AUTHOR_COL].to_dict()
        result['author'] = result['author'].map(author_map).fillna(result['author'])
    st.pyplot(fig)
    st.dataframe(result.rename(columns={'author': '作者' if LANG=='中文' else 'Author',
                                        'avg_likes': '平均点赞' if LANG=='中文' else 'Avg Likes',
                                        'review_count': '评论数' if LANG=='中文' else 'Reviews'}))

# 评论长度 vs 评分
elif option in ["评论字数 vs 评分", "Review Length vs Rating"]:
    if LANG == '中文':
        st.subheader("评论长度与评分的关系")
    else:
        st.subheader("Review Length vs Rating")
    result, fig = analysis_length_rating(df)
    st.pyplot(fig)
    st.write("描述统计：" if LANG == '中文' else "Descriptive Statistics:")
    st.dataframe(result)

# 作者 & 类型查书
elif option in ["作者 & 类型查书", "Find Books by Author / Genre"]:
    if LANG == '中文':
        st.subheader("作者 & 类型查书")
        st.markdown("输入**作者名**或**类型标签**，查看该作者/类型的全部书籍（按评分排序）。")
    else:
        st.subheader("Find Books by Author / Genre")
        st.markdown("Enter an author name or genre to view their books, sorted by rating.")

    col1, col2 = st.columns(2)
    with col1:
        author_input = st.text_input("作者名" if LANG == '中文' else "Author", placeholder="如 Orwell")
    with col2:
        genre_input = st.text_input("类型" if LANG == '中文' else "Genre", placeholder="如 Fantasy")

    if st.button("查找" if LANG == '中文' else "Search"):
        if not author_input and not genre_input:
            st.warning("请至少输入作者名或类型。" if LANG == '中文' else "Please enter at least one search term.")
        else:
            with st.spinner("正在查找..." if LANG == '中文' else "Searching..."):
                msg, books = analysis_recommend_books(
                    df,
                    author=author_input.strip() if author_input else None,
                    genre=genre_input.strip() if genre_input else None
                )
                st.markdown(msg)
                if books is not None and not books.empty:
                    if LANG == '中文' and 'book_title_zh' in df.columns:
                        title_map = df[['book_title', 'book_title_zh']].drop_duplicates().set_index('book_title')['book_title_zh'].to_dict()
                        books['book_title'] = books['book_title'].map(title_map).fillna(books['book_title'])
                    if LANG == '中文' and 'author_zh' in df.columns:
                        author_map = df[['author', 'author_zh']].drop_duplicates().set_index('author')['author_zh'].to_dict()
                        books['author'] = books['author'].map(author_map).fillna(books['author'])
                    st.dataframe(books.rename(columns={
                        'book_title': '书名' if LANG == '中文' else 'Title',
                        'author': '作者' if LANG == '中文' else 'Author',
                        'average_rating': '评分' if LANG == '中文' else 'Rating',
                        'num_reviews': '评论数' if LANG == '中文' else 'Reviews'
                    }))

# 雷达图
elif option in ["书籍对比图", "Book vs Book Radar"]:
    if LANG == '中文':
        st.subheader("两本书多维对比")
    else:
        st.subheader("Book vs Book Radar Chart")
    display_books = sorted(df[TITLE_COL].dropna().unique().tolist())
    book1_display = st.selectbox("第一本书" if LANG=='中文' else "Book 1", display_books)
    book2_display = st.selectbox("第二本书" if LANG=='中文' else "Book 2", display_books)
    if st.button("开始对比" if LANG=='中文' else "Compare"):
        if book1_display == book2_display:
            st.warning("请选两本不同的书" if LANG=='中文' else "Please select two different books")
        else:
            book1_original = get_original_title(book1_display)
            book2_original = get_original_title(book2_display)
            with st.spinner("绘制雷达图..."):
                comp_df, fig, msg = analysis_book_compare_radar(df, book1_original, book2_original)
                if msg:
                    st.error(msg)
                else:
                    st.pyplot(fig)
                    st.dataframe(comp_df)

# 词云
elif option in ["评论词云", "Review Word Cloud"]:
    if LANG == '中文':
        st.subheader("读者评论关键词云")
    else:
        st.subheader("Review Word Cloud")
    display_books = ["全部评论"] + sorted(df[TITLE_COL].dropna().unique().tolist())
    selected_book_display = st.selectbox("选择书籍" if LANG=='中文' else "Choose a book", display_books)
    if selected_book_display == "全部评论":
        book = None
    else:
        book = get_original_title(selected_book_display)
    if st.button("生成词云"):
        with st.spinner("分析评论关键词..."):
            fig, msg = analysis_review_wordcloud(df, book_title=book)
            if msg:
                st.error(msg)
            else:
                st.pyplot(fig)

# 智能问答
elif option in ["智能问答 (AI)", "AI Q&A"]:
    if LANG == '中文':
        st.subheader("智能问数")
    else:
        st.subheader("AI Q&A")
    if not qa_available:
        st.error(f"智能问答模块不可用：{qa_error_msg}")
    else:
        user_question = st.text_input(
            "请输入您的问题" if LANG == '中文' else "Ask a question about the data",
            placeholder="试试：评分最高的书有哪些？" if LANG == '中文' else "e.g. Which books have the highest ratings?"
        )
        if user_question:
            with st.spinner("AI 正在思考..." if LANG == '中文' else "AI thinking..."):
                answer, fig = ask_ai(user_question, df)
                st.markdown(answer)
                if fig:
                    st.pyplot(fig)
                    plt.close(fig)

# ----------------- 底部信息 -----------------
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="
        background-color: #d1ecf1;
        border: 2px solid #17a2b8;
        border-radius: 10px;
        padding: 15px 18px;
        font-size: 14px;
        line-height: 1.7;
        color: #0c5460;
    ">
        <b>项目：</b> 高级Python程序设计期末大作业<br>
        <b>作者：</b> 张益僮 &emsp; <b>学号：</b> 2025201757<br>
        <b>数据来源：</b> Goodreads 书籍评论数据集
    </div>
    """,
    unsafe_allow_html=True
)