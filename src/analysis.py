"""
模块3：数据分析与可视化（优化版）
从 matplotlib 默认样式升级为现代风格，配色统一，适合演示
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 统一配色方案（取自现代数据可视化调色板）
COLORS = {
    'blue': '#4C72B0',
    'green': '#55A868',
    'red': '#C44E52',
    'purple': '#8172B2',
    'orange': '#CCB974',
    'cyan': '#64B5CD',
    'grey': '#8C8C8C',
    'bg': '#F5F5F5'
}

# 统一样式设置
plt.style.use('seaborn-v0_8-whitegrid')

DATA_FILE = "./cleaned_reviews.csv"

def load_clean_data():
    df = pd.read_csv(DATA_FILE)
    df['review_date'] = pd.to_datetime(df['review_date'])
    return df

# ---- 分析1：书籍评分 Top 10 ----
def analysis_top_rated_books(df):
    top_books = df[['book_title', 'average_rating']].drop_duplicates()
    top_books = top_books.nlargest(10, 'average_rating')

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    # 渐变色条
    colors = [COLORS['blue']] * 10
    bars = ax.barh(top_books['book_title'], top_books['average_rating'], color=colors, height=0.6)

    ax.set_xlabel('Average Rating', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 最高评分书籍', fontsize=14, fontweight='bold', pad=15)
    ax.invert_yaxis()
    ax.tick_params(axis='y', labelsize=10)
    ax.set_xlim(4.5, 5.1)

    for bar, val in zip(bars, top_books['average_rating']):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2, f'{val:.2f}',
                va='center', fontsize=10, fontweight='bold', color='#333333')
    plt.tight_layout()
    return top_books, fig

# ---- 分析2：月度趋势 ----
def analysis_monthly_trend(df):
    monthly = df.set_index('review_date').resample('ME').size().reset_index(name='count')
    # 过滤掉评论数过少的月份（可选）
    monthly = monthly[monthly['count'] > 0]

    fig, ax = plt.subplots(figsize=(14, 5), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    ax.plot(monthly['review_date'], monthly['count'], color=COLORS['red'], linewidth=2.5, marker='o', markersize=6)
    ax.fill_between(monthly['review_date'], 0, monthly['count'], color=COLORS['red'], alpha=0.1)

    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Reviews', fontsize=12, fontweight='bold')
    ax.set_title('月度评论量趋势', fontsize=14, fontweight='bold', pad=15)
    ax.tick_params(axis='x', rotation=45, labelsize=10)

    # 每隔6个月显示一个标签，避免拥挤
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    plt.tight_layout()
    return monthly, fig

# ---- 分析3：评分与点赞分布 ----
def analysis_rating_likes(df):
    valid_df = df[df['rating'] >= 1]

    fig, ax = plt.subplots(figsize=(8, 6), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    ratings_data = [valid_df[valid_df['rating'] == r]['likes'] for r in range(1, 6)]
    bp = ax.boxplot(ratings_data, labels=['1星', '2星', '3星', '4星', '5星'],
                    patch_artist=True, widths=0.5,
                    medianprops={'color': 'black', 'linewidth': 1.5},
                    whiskerprops={'color': COLORS['grey']})

    # 每个箱子不同颜色
    box_colors = [COLORS['red'], COLORS['orange'], COLORS['green'], COLORS['cyan'], COLORS['blue']]
    for patch, color in zip(bp['boxes'], box_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    ax.set_xlabel('Rating', fontsize=12, fontweight='bold')
    ax.set_ylabel('Likes', fontsize=12, fontweight='bold')
    ax.set_title('不同评分等级的点赞数分布', fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    stats = valid_df.groupby('rating')['likes'].describe()
    return stats, fig

# ---- 分析4：高赞作者排行 ----
def analysis_top_authors(df):
    author_stats = df.groupby('author').agg(
        avg_likes=('likes', 'mean'),
        review_count=('reviewer_id', 'count')
    ).reset_index()
    popular_authors = author_stats[author_stats['review_count'] >= 5]
    top_authors = popular_authors.nlargest(10, 'avg_likes')

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    bars = ax.barh(top_authors['author'], top_authors['avg_likes'], color=COLORS['green'], height=0.6)
    ax.set_xlabel('Average Likes', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 高赞作者 (评论数≥5)', fontsize=14, fontweight='bold', pad=15)
    ax.invert_yaxis()
    ax.tick_params(axis='y', labelsize=10)

    for bar, val in zip(bars, top_authors['avg_likes']):
        ax.text(val + 10, bar.get_y() + bar.get_height()/2, f'{val:.1f}',
                va='center', fontsize=10, fontweight='bold', color='#333333')
    plt.tight_layout()
    return top_authors, fig

# ---- 分析5：评论字数 vs 评分 ----
def analysis_length_rating(df):
    df_plot = df.dropna(subset=['review_content', 'rating'])
    df_plot['content_length'] = df_plot['review_content'].apply(lambda x: len(str(x).split()) if pd.notna(x) else 0)
    df_plot = df_plot[(df_plot['content_length'] >= 1) & (df_plot['content_length'] <= 2000)]

    fig, ax = plt.subplots(figsize=(9, 6), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])

    # 散点图
    ax.scatter(df_plot['content_length'], df_plot['rating'], alpha=0.3, color=COLORS['purple'])
    # 趋势线
    z = pd.DataFrame({'length': df_plot['content_length'], 'rating': df_plot['rating']})
    if len(z) > 1:
        coeffs = np.polyfit(z['length'], z['rating'], 1)
        poly = np.poly1d(coeffs)
        x_line = np.linspace(z['length'].min(), z['length'].max(), 100)
        ax.plot(x_line, poly(x_line), color=COLORS['red'], linewidth=2, label='Trend')

    ax.set_xlabel('Review Length (words)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Rating', fontsize=12, fontweight='bold')
    ax.set_title('评论字数与评分的关系', fontsize=14, fontweight='bold', pad=15)
    ax.legend()
    plt.tight_layout()
    return z.describe(), fig
def analysis_recommend_books(df, author=None, genre=None):
    """
    按作者查找书籍列表；若找不到该作者，则推荐热门高分书
    """
    # 如果有作者关键词，先尝试精确查找该作者
    if author:
        author_books = df[df['author'].str.contains(author, case=False, na=False)]
        if not author_books.empty:
            # 找到该作者的所有书籍，去重，按评分排序
            books = author_books[['book_title', 'author', 'average_rating', 'num_reviews']].drop_duplicates()
            books = books.sort_values('average_rating', ascending=False)
            return f"✅ 找到作者“{author}”的 {len(books)} 本书（按评分排序）：", books

    # 如果有类型筛选（没有作者或作者没找到时也可以尝试）
    if genre:
        genre_books = df[df['genres'].str.contains(genre, case=False, na=False)]
        if not genre_books.empty:
            books = genre_books[['book_title', 'author', 'average_rating', 'num_reviews']].drop_duplicates()
            books = books.sort_values('average_rating', ascending=False)
            return f"✅ 找到包含类型“{genre}”的 {len(books)} 本书：", books

    # 什么都没找到，推荐系统里评分最高的10本书
    fallback = df[['book_title', 'author', 'average_rating', 'num_reviews']].drop_duplicates()
    fallback = fallback.nlargest(10, 'average_rating')
    return "🤔 未找到该作者或类型的书籍，以下为您推荐系统里评分最高的10本书：", fallback
# ==================== 创新功能1：书籍对比雷达图 ====================
def analysis_book_compare_radar(df, book1_title, book2_title):
    import numpy as np

    b1 = df[df['book_title'] == book1_title].copy()
    b2 = df[df['book_title'] == book2_title].copy()
    if b1.empty or b2.empty:
        return None, None, "其中一本书在数据中不存在，请检查书名。"

    # 强制转为数值
    numeric_cols = ['average_rating', 'num_reviews', 'likes', 'num_pages', 'followers']
    for col in numeric_cols:
        if col in b1.columns:
            b1[col] = pd.to_numeric(b1[col], errors='coerce')
        if col in b2.columns:
            b2[col] = pd.to_numeric(b2[col], errors='coerce')

    # 指标定义（全部使用英文标签，避免字体缺失导致方框）
    metrics = [
        ('Avg Rating', 'average_rating', 'mean'),
        ('Total Reviews', 'num_reviews', 'max'),
        ('Median Likes', 'likes', 'median'),
        ('Pages', 'num_pages', 'max'),
        ('Avg Followers', 'followers', 'mean')
    ]

    stats = {}
    for label, col, agg in metrics:
        val1 = b1[col].dropna().agg(agg) if not b1[col].dropna().empty else 0
        val2 = b2[col].dropna().agg(agg) if not b2[col].dropna().empty else 0
        if pd.isna(val1):
            val1 = 0
        if pd.isna(val2):
            val2 = 0
        stats[label] = [float(val1), float(val2)]

    # 归一化
    values1, values2 = [], []
    for vals in stats.values():
        max_val = max(vals)
        if max_val > 0:
            values1.append(vals[0] / max_val)
            values2.append(vals[1] / max_val)
        else:
            values1.append(0)
            values2.append(0)

    # 画雷达图
    angles = np.linspace(0, 2 * np.pi, len(stats), endpoint=False).tolist()
    angles += angles[:1]
    values1 += values1[:1]
    values2 += values2[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True), facecolor='#F5F5F5')
    ax.set_facecolor('#F5F5F5')
    ax.plot(angles, values1, 'o-', color='#4C72B0', linewidth=2, label=book1_title[:20])
    ax.fill(angles, values1, color='#4C72B0', alpha=0.1)
    ax.plot(angles, values2, 'o-', color='#C44E52', linewidth=2, label=book2_title[:20])
    ax.fill(angles, values2, color='#C44E52', alpha=0.1)

    # 设置英文刻度标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m[0] for m in metrics], fontsize=12, fontweight='bold')
    ax.set_yticklabels([])
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    plt.tight_layout()

    compare_df = pd.DataFrame(stats, index=[book1_title[:30], book2_title[:30]])
    return compare_df, fig, None

# ==================== 创新功能2：评论关键词词云 ====================
from wordcloud import WordCloud

def analysis_review_wordcloud(df, book_title=None, max_words=100):
    """
    生成评论内容的词云图
    可选：指定某一本书，或全部评论
    """
    if book_title:
        text_data = df[df['book_title'] == book_title]['review_content']
        if text_data.empty:
            return None, "未找到该书的评论。"
        title = f"《{book_title[:30]}》"
    else:
        text_data = df['review_content']
        title = "全部评论"
    
    # 合并所有文本
    all_text = " ".join(text_data.dropna().astype(str).tolist())
    if not all_text.strip():
        return None, "没有可用的评论文本。"
    
    # 生成词云
    wordcloud = WordCloud(width=800, height=400, background_color='white',
                          max_words=max_words, colormap='viridis',
                          stopwords={'the', 'and', 'is', 'in', 'it', 'of', 'to', 'a', 'I', 'this', 'was', 'that', 'for', 'with', 'on', 'as', 'at', 'by', 'an', 'be', 'from', 'or', 'but', 'not', 'are', 'we', 'you', 'he', 'she', 'they', 'his', 'her', 'my', 'me', 'so', 'if', 'no', 'all', 'just', 'like', 'about', 'have', 'been', 'has', 'who', 'can', 'than', 'then', 'also', 'very', 'one', 'only', 'some', 'when', 'its'})
    wordcloud.generate(all_text)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f'{title}评论关键词云', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig, None

# 主入口保持不变
if __name__ == "__main__":
    df = load_clean_data()
    print("数据加载完毕，开始生成优化后图表...\n")
    functions = [
        (analysis_top_rated_books, "top_rated_books"),
        (analysis_monthly_trend, "monthly_trend"),
        (analysis_rating_likes, "rating_likes"),
        (analysis_top_authors, "top_authors"),
        (analysis_length_rating, "length_rating")
    ]
    for func, name in functions:
        _, fig = func(df)
        fig.savefig(f"./{name}.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"✅ 已保存优化图表: {name}.png")