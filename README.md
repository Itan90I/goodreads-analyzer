# Goodreads 智能问数系统

基于 Streamlit + DeepSeek 的书籍评论智能分析 Web 应用。  
支持**自然语言问答**、**多维度数据可视化**、**中英文双语切换**、**自定义数据上传与鲁棒性测试**。

---

## 在线体验

🔗 [https://itan90i-goodreads-analyzer.streamlit.app](https://itan90i-goodreads-analyzer.streamlit.app)

> 注意：云端部署的智能问答功能未配置 API Key（保护额度），如需体验完整问答，请在本地运行。

---

## 功能一览

| 模块 | 功能 | 说明 |
|------|------|------|
| 数据预览 | 交互式表格 | 支持浏览、搜索、排序，展示前50行 |
| 书籍评分 Top 10 | 横向柱状图 | 平均评分最高的10本书 |
| 月度评论趋势 | 折线图 + 面积填充 | 评论数量随时间变化 |
| 评分与点赞分布 | 彩色箱线图 | 1-5星评分的点赞数分布 |
| 作者平均点赞排行 | 横向柱状图 | Top 10 作者（评论数≥5） |
| 评论字数 vs 评分 | 散点图 + 趋势线 | 评论长度与评分的关系 |
| 作者 & 类型查书 | 智能检索 | 输入作者/类型查书，查不到自动推荐 |
| 书籍对比雷达图 | 五维雷达图 | 两本书在评分、评论、点赞、页数、粉丝的对比 |
| 评论关键词词云 | 词云图 | 可指定某本书或全部评论 |
| 智能问答 | AI 对话 | 自然语言提问 → 自动出图（DeepSeek API） |
| 中英文切换 | 双语界面 | 书名/作者随语言切换（字典映射） |
| 自定义数据上传 | 鲁棒性验证 | 上传 CSV 自动验证列名/行数/格式，失败自动回退 |

---

## 技术栈

- **前端/后端**：Streamlit
- **数据处理**：Pandas, NumPy
- **可视化**：Matplotlib, WordCloud
- **AI 接口**：OpenAI SDK（兼容 DeepSeek API）
- **部署**：Git, GitHub, Streamlit Cloud

---

## 本地运行

### 1. 环境要求

- Python ≥ 3.10
- Git（可选，用于克隆仓库）

### 2. 克隆仓库

```bash
git clone https://github.com/Itan90I/goodreads-analyzer.git
cd goodreads-analyzer
