"""
利用字典映射生成中文版 cleaned_reviews_zh.csv
"""
import pandas as pd
from translate_dict import translate_title, translate_author

df = pd.read_csv("cleaned_reviews.csv")
df['book_title_zh'] = df['book_title'].apply(translate_title)
df['author_zh'] = df['author'].apply(translate_author)
df['genres_zh'] = df['genres']  # 类型暂不翻译，保持原文

df.to_csv("cleaned_reviews_zh.csv", index=False, encoding='utf-8-sig')
print(f"✅ 中文数据已生成，共 {len(df)} 条")
print("未翻译的书名示例：")
untranslated = df[df['book_title_zh'] == df['book_title']]['book_title'].unique()[:5]
for title in untranslated:
    print(f"  - {title}")