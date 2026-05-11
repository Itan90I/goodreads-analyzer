"""
模块1：数据读取与抽样
从 book_reviews.db 随机抽取 5000 条评论，关联 Book_Details.csv 的书籍信息
输出合并后的 DataFrame，供后续预处理和分析使用
"""
import pandas as pd
import sqlite3

# ==================== 配置 ====================
SAMPLE_SIZE = 5000          # 抽样数量
DATA_DIR = "."              # 数据文件所在目录（当前目录）

# ==================== 1. 读取书籍信息 ====================
print("[1/4] 读取 Book_Details.csv ...")
df_books = pd.read_csv(f"{DATA_DIR}/Book_Details.csv")#./book_Details.csv

# 只保留需要的列（减少内存）
books_cols = [
    'book_id', 'book_title', 'author', 'genres',
    'num_pages', 'average_rating', 'num_ratings', 'num_reviews'
]
df_books = df_books[books_cols]#只保留需要的列
print(f"    书籍表形状: {df_books.shape}")#输出行数列数

# ==================== 2. 连接评论数据库 ====================
print("[2/4] 连接 book_reviews.db ...")
conn = sqlite3.connect(f"{DATA_DIR}/book_reviews.db")#数据库链接对象：1.打开数据库2.传递SQL指令3.关闭数据库

# 先看总共有多少条评论
total = pd.read_sql_query("SELECT COUNT(*) FROM book_reviews", conn).iloc[0, 0]
print(f"    评论总数: {total:,}")
'''
SQL语句：
SELECT 列名 （select *:查所有列，select book_id,review_rating:只查指定两列）
FROM 表名（从哪张表查，FROM book_reveiws)
WHERE 条件（筛选条件：e.g. WHERE num_pages>500）
LIMIT 条数（限制返回行数：LIMIT 5000)
COUNT 总数（count(*)：统计总数）
ORDER BY RANDOM() 随机打乱（SQLite专用）
'''
# ==================== 3. 随机抽样 5000 条 ====================
print(f"[3/4] 随机抽样 {SAMPLE_SIZE} 条评论 ...")

# 方法：用 SQL 的随机采样，跨数据库通用写法
query = f"""
    SELECT * FROM book_reviews
    ORDER BY RANDOM()
    LIMIT {SAMPLE_SIZE}
"""
df_reviews = pd.read_sql_query(query, conn)
conn.close()
print(f"    抽样结果形状: {df_reviews.shape}")

# ==================== 4. 合并两张表 ====================
print("[4/4] 合并评论与书籍信息 ...")

# —— 修复：统一 book_id 类型，CSV 是整数但 SQLite 读出来是字符串 ——
df_books['book_id'] = pd.to_numeric(df_books['book_id'], errors='coerce')
df_reviews['book_id'] = pd.to_numeric(df_reviews['book_id'], errors='coerce')
df_books = df_books.dropna(subset=['book_id'])
df_reviews = df_reviews.dropna(subset=['book_id'])
df_books['book_id'] = df_books['book_id'].astype(int)
df_reviews['book_id'] = df_reviews['book_id'].astype(int)

df_merged = df_reviews.merge(df_books, on='book_id', how='left')
'''
on:按照书的编号book_id配对
how:以左的评论表为主
'''
print(f"    合并后形状: {df_merged.shape}")
print(f"    合并后列数: {len(df_merged.columns)}")
print(f"    列名: {df_merged.columns.tolist()}")

# ==================== 5. 保存 ====================
output_path = f"{DATA_DIR}/sampled_reviews.csv"
df_merged.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n✅ 已保存到: {output_path}")

# ==================== 6. 快速检查 ====================
print("\n" + "=" * 50)
print("数据速览（前 3 行，部分列）：")
preview_cols = ['book_title', 'author', 'review_rating', 'likes_on_review', 'review_date']
print(df_merged[preview_cols].head(3).to_string())
print(f"\n各列缺失值数量：")
print(df_merged.isnull().sum())