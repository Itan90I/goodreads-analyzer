"""
模块2：数据预处理
读取合并后的数据，清洗脏数据（文本转数值、日期格式化），处理缺失值
输出干净的 CSV，供后续分析和可视化使用
"""
import pandas as pd
import re

# ==================== 配置 ====================
DATA_DIR = "."
INPUT_FILE = f"{DATA_DIR}/sampled_reviews.csv"   # 原始合并数据
OUTPUT_FILE = f"{DATA_DIR}/cleaned_reviews.csv"  # 清洗后数据

# ==================== 1. 读取数据 ====================
print("[1/5] 读取合并数据 ...")
df = pd.read_csv(INPUT_FILE)
print(f"    原始形状: {df.shape}")
print(f"    原始列数: {len(df.columns)}")

# ==================== 2. 清洗 likes_on_review ====================
print("[2/5] 清洗 likes_on_review（“123 likes” → 123）...")
# 原始值："123 likes" / "1,234 likes" — 提取数字部分，去掉逗号和文字
df['likes_num'] = (
    df['likes_on_review']
    .astype(str)                          # 确保是字符串
    .str.extract(r'([\d,]+)')             # 正则提取数字和逗号部分（如 "1,234"）
    [0]                                    # extract 返回 DataFrame，取第一列
    .str.replace(',', '', regex=True)      # 去掉逗号
)
df['likes_num'] = pd.to_numeric(df['likes_num'], errors='coerce')  # 转数字，失败的变 NaN
print(f"    提取后缺失数: {df['likes_num'].isnull().sum()}")

# ==================== 3. 清洗 review_rating ====================
print("[3/5] 清洗 review_rating（“Rating 4 out of 5” → 4）...")
# 原始值："Rating 4 out of 5" / "Rating 5 out of 5" / NaN — 提取第一个数字
df['rating_num'] = (
    df['review_rating']
    .astype(str)
    .str.extract(r'Rating\s+(\d+)')       # 匹配 "Rating 数字"
    [0]
)
df['rating_num'] = pd.to_numeric(df['rating_num'], errors='coerce')
print(f"    提取后缺失数: {df['rating_num'].isnull().sum()}")

# ==================== 4. 清洗 reviewer_followers ====================
print("[4/5] 清洗 reviewer_followers（“12.1k followers” → 12100）...")
def parse_followers(val):
    """
    把 "12.1k followers" / "7,961 followers" 等格式转成整数
    k 表示千：12.1k → 12100
    无 k 直接去逗号：7,961 → 7961
    """
    if pd.isna(val):
        return None
    val = str(val).lower().replace(',', '')        # 去逗号，统一小写
    match = re.search(r'([\d.]+)\s*k', val)       # 找 "数字k"
    if match:
        return int(float(match.group(1)) * 1000)   # 12.1 * 1000 = 12100
    match = re.search(r'([\d.]+)', val)            # 没 k，直接取数字
    if match:
        return int(float(match.group(1)))
    return None

df['followers_num'] = df['reviewer_followers'].apply(parse_followers)
print(f"    提取后缺失数: {df['followers_num'].isnull().sum()}")

# ==================== 5. 清洗 reviewer_total_reviews ====================
print("[5/5] 清洗 reviewer_total_reviews（“234 reviews” → 234）...")
# 原始值："234 reviews" / "1,802 reviews" — 提取数字部分
df['total_reviews_num'] = (
    df['reviewer_total_reviews']
    .astype(str)
    .str.extract(r'([\d,]+)')
    [0]
    .str.replace(',', '', regex=True)
)
df['total_reviews_num'] = pd.to_numeric(df['total_reviews_num'], errors='coerce')
print(f"    提取后缺失数: {df['total_reviews_num'].isnull().sum()}")

# ==================== 6. 清洗 review_date ====================
print("[6/5] 清洗 review_date（“March 8, 2018” → 2018-03-08）...")
# 用 pandas 的日期解析，自动处理英文月份
df['date_parsed'] = pd.to_datetime(df['review_date'], errors='coerce')
print(f"    解析后缺失数: {df['date_parsed'].isnull().sum()}")

# ==================== 7. 处理缺失值 ====================
print("[7/5] 处理缺失值 ...")
# likes、rating、followers 缺失值都填 0
df['likes_num'] = df['likes_num'].fillna(0).astype(int)
df['rating_num'] = df['rating_num'].fillna(0).astype(int)
df['followers_num'] = df['followers_num'].fillna(0).astype(int)
# total_reviews_num 缺失填 0
df['total_reviews_num'] = df['total_reviews_num'].fillna(0).astype(int)

# ==================== 8. 整理输出列 ====================
# 保留原始列 + 新的清洗后列
output_cols = [
    'book_id', 'book_title', 'author', 'genres',
    'num_pages', 'average_rating', 'num_ratings', 'num_reviews',
    'reviewer_id', 'reviewer_name',
    'likes_num',            # ← 清洗后：点赞数（整数）
    'rating_num',           # ← 清洗后：评分 1-5（整数）
    'followers_num',        # ← 清洗后：粉丝数（整数）
    'total_reviews_num',    # ← 清洗后：用户总评论数（整数）
    'date_parsed',          # ← 清洗后：日期（datetime）
    'review_content',       #   原始评论文本
    'genres'                #   类型标签
]

df_clean = df[output_cols].copy()
df_clean = df_clean.rename(columns={
    'likes_num': 'likes',
    'rating_num': 'rating',
    'followers_num': 'followers',
    'total_reviews_num': 'user_total_reviews',
    'date_parsed': 'review_date'
})

# ==================== 9. 保存清洗后数据 ====================
df_clean.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
print(f"\n✅ 已保存到: {OUTPUT_FILE}")
print(f"    清洗后形状: {df_clean.shape}")
print(f"    清洗后列数: {len(df_clean.columns)}")
print(f"    列名: {df_clean.columns.tolist()}")

# ==================== 10. 快速检查 ====================
print("\n" + "=" * 50)
print("清洗后数据速览（前 3 行）：")
print(df_clean.head(3).to_string())
print(f"\n各列缺失值数量：")
print(df_clean.isnull().sum())