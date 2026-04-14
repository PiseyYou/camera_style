# Camera Style - 镜头数据分析系统

一个综合性的镜头数据采集与分析平台，从多个数据源抓取规格参数、追踪价格、对比镜头并提供智能推荐。

## ✨ 功能特性

### 数据采集
- **真实网页抓取**：使用 Playwright 绕过 403 限制
- **多数据源支持**：DPReview、B&H Photo 等
- **多品牌支持**：佳能、尼康、索尼、富士、松下、奥林巴斯
- **全面规格参数**：焦距、光圈、重量、尺寸、卡口类型、价格等

### 数据分析
- **智能数据合并**：自动去重并合并多源数据
- **价格追踪**：历史价格分析和趋势检测
- **镜头对比**：并排对比与性能评分
- **推荐引擎**：基于需求的个性化镜头推荐
- **交互式仪表板**：精美的 HTML 报告和可视化

## 快速开始

### 方式一：快速演示（首次使用推荐）

```bash
# 自动抓取示例数据并打开预览
./demo_preview.sh
```

### 方式二：完整安装

```bash
# 1. 安装依赖
./setup.sh

# 2. 测试抓取器
python3 test_real_scraper.py

# 3. 抓取数据
python3 scripts/ingest/dpreview_run.py --brand Canon --limit 10

# 4. 运行完整分析
python3 scripts/run_analysis.py

# 5. 打开仪表板
xdg-open reports/dashboard.html
```

## 📊 分析工具

### 1. 完整分析流程

一次运行所有分析工具：

```bash
python3 scripts/run_analysis.py
```

将会执行：
- ✅ 合并所有来源的数据
- ✅ 分析价格趋势并找出优惠
- ✅ 生成镜头对比
- ✅ 创建个性化推荐
- ✅ 构建交互式仪表板

**输出**：`reports/dashboard.html` - 您的一站式分析中心

### 2. 独立分析工具

#### 数据合并与去重

```bash
python3 scripts/analysis/merge_data.py
```

- 合并来自 DPReview、B&H Photo 等的数据
- 智能模糊匹配检测重复项
- 使用来源优先级解决冲突
- **输出**：`data/merged/merged_summary.csv`

#### 价格追踪与趋势分析

```bash
python3 scripts/analysis/price_tracker.py
```

- 追踪历史价格
- 检测趋势（上涨/下跌/稳定）
- 找出最佳优惠（折扣 > 5%）
- 计算价格波动性
- **输出**：`reports/price_analysis.md`、`reports/price_trends.csv`

#### 镜头对比

```bash
python3 scripts/analysis/lens_comparator.py
```

- 并排规格对比
- 性能评分：
  - 🎒 便携性（重量、尺寸）
  - 🔄 多功能性（变焦范围）
  - 🌙 弱光性能（光圈）
  - 💰 性价比（价格 vs 功能）
- **输出**：`reports/lens_comparison.html`

#### 推荐引擎

```bash
python3 scripts/analysis/lens_recommender.py
```

- 基于以下条件的个性化推荐：
  - 预算限制
  - 品牌偏好
  - 卡口类型
  - 焦距需求
  - 功能要求
- 预设配置：
  - ✈️ 旅行摄影
  - 👤 人像摄影
  - 💵 预算友好
- **输出**：`reports/lens_recommendations.html`

### 3. 网页预览界面

浏览所有镜头，支持搜索和过滤：

```bash
python3 scripts/generate_preview.py
xdg-open reports/lens_preview.html
```

**功能：**
- 📊 统计仪表板
- 🔍 实时搜索
- 🏷️ 按品牌/类型过滤
- 📱 响应式设计
- 🎨 精美卡片布局

详见 [PREVIEW_GUIDE.md](PREVIEW_GUIDE.md)

### 示例输出

JSON 格式（`data/parsed/dpreview/canon-rf-24-70mm-f28.json`）：

```json
{
  "brand": "Canon",
  "model_name": "RF 24-70mm F2.8 L IS USM",
  "mount": "Canon RF",
  "prime_or_zoom": "Zoom",
  "focal_length_min": 24.0,
  "focal_length_max": 70.0,
  "max_aperture_wide": 2.8,
  "max_aperture_tele": 2.8,
  "weight": 900.0,
  "diameter": 88.5,
  "length": 125.7,
  "release_date": "2019-08-28",
  "source_url": "https://www.dpreview.com/products/lenses/canon/canon-rf-24-70mm-f28",
  "fetched_at": "2026-04-14T02:30:00.000000+00:00"
}
```

## 📁 项目结构

```
camera_style/
├── scripts/
│   ├── ingest/                    # 数据采集
│   │   ├── base_scraper.py        # 基础抓取框架
│   │   ├── dpreview_*.py          # DPReview 抓取器
│   │   └── bhphoto_scraper.py     # B&H Photo 抓取器
│   ├── analysis/                  # 数据分析
│   │   ├── merge_data.py          # 数据合并与去重
│   │   ├── price_tracker.py       # 价格追踪与趋势
│   │   ├── lens_comparator.py     # 镜头对比工具
│   │   └── lens_recommender.py    # 推荐引擎
│   ├── generate_preview.py        # 网页预览生成器
│   └── run_analysis.py            # 完整分析流程
├── data/
│   ├── raw/                       # 原始 HTML 页面
│   ├── parsed/                    # 解析后的 JSON 数据
│   └── merged/                    # 合并与去重后的数据
├── reports/                       # 生成的报告
│   ├── dashboard.html             # 主仪表板
│   ├── lens_preview.html          # 镜头目录
│   ├── price_analysis.md          # 价格分析
│   ├── lens_comparison.html       # 对比报告
│   └── lens_recommendations.html  # 推荐报告
├── tests/                         # 测试文件
├── docs/                          # 文档
├── setup.sh                       # 安装脚本
├── quickstart.sh                  # 快速启动脚本
├── demo_preview.sh                # 演示脚本
└── requirements.txt               # Python 依赖
```

## 故障排除

### 403 禁止访问错误

抓取器使用 Playwright 真实浏览器来绕过 403 限制。如果仍然遇到 403 错误：

1. 增加延迟：编辑 `dpreview_fetch.py` 并增加 `wait_seconds`
2. 检查 DPReview 是否更新了反爬虫措施
3. 尝试使用不同的 user agent

### 数据缺失

如果解析的数据不完整：

1. 检查 `data/raw/dpreview/` 中的原始 HTML 文件
2. DPReview 可能已更改其 HTML 结构
3. 更新 `dpreview_parser.py` 中的 CSS 选择器

### Playwright 安装问题

```bash
# 重新安装 Playwright 浏览器
python3 -m playwright install --force chromium

# 检查 Playwright 安装
python3 -m playwright --version
```

## 🎯 使用场景

### 摄影师

- **研究**：对比多个镜头的规格参数
- **购物**：追踪价格并找到最佳优惠
- **决策**：根据需求获得个性化推荐
- **预算规划**：分析价格趋势以选择购买时机

### 开发者

- **数据源**：干净、结构化的 JSON/CSV 格式镜头数据
- **API 集成**：使用抓取的数据构建应用
- **机器学习**：基于镜头规格和价格训练模型
- **市场分析**：分析摄影器材市场趋势

### 研究人员

- **市场研究**：研究定价模式和趋势
- **产品分析**：跨品牌对比技术规格
- **消费者行为**：分析镜头流行度和偏好
- **数据可视化**：从数据创建图表和图形

## 📚 文档

- **[README.md](README.md)** - 本文件（项目概览）
- **[USAGE_CN.md](USAGE_CN.md)** - 中文使用指南
- **[CHANGES.md](CHANGES.md)** - Mock vs Real 对比
- **[SUMMARY.md](SUMMARY.md)** - 完整项目总结
- **[PREVIEW_GUIDE.md](PREVIEW_GUIDE.md)** - 预览界面指南

## 🔧 高级用法

### 自定义抓取

```python
from scripts.ingest.bhphoto_scraper import BHPhotoScraper

scraper = BHPhotoScraper()
lenses = scraper.scrape_brand("Canon", limit=20)

for lens in lenses:
    print(f"{lens.model_name}: ${lens.current_price}")
```

### 自定义推荐

```python
from scripts.analysis.lens_recommender import LensRecommender, UserRequirements

recommender = LensRecommender()

requirements = UserRequirements(
    max_budget=1000,
    mount="Canon RF",
    max_weight=600,
    portability_priority=0.9,
    low_light_priority=0.7
)

recommendations = recommender.recommend(requirements, top_n=5)
```

### 价格提醒

```python
from scripts.analysis.price_tracker import PriceTracker

tracker = PriceTracker()
deals = tracker.find_best_deals(min_discount_pct=10)

for deal in deals:
    print(f"🔥 {deal['model_name']}: 节省 ${deal['savings']:.2f}!")
```

## 数据质量

### 当前状态

- ✓ 真实网络抓取（非模拟数据）
- ✓ Playwright 绕过 403 限制
- ✓ 保存原始 HTML 以便重新解析
- ✓ 结构化 JSON 输出
- ⚠ 受限于 DPReview 数据可用性
- ⚠ 需要手动验证准确性

### 验证

始终对照制造商规格验证抓取的数据：

1. 检查 `reports/dpreview_manual_review.csv`
2. 与官方规格表对比
3. 交叉引用多个来源

## 许可证

本工具仅用于教育和研究目的。请尊重 DPReview 的服务条款和 robots.txt。不要用过多请求使其服务器过载。

## 贡献

欢迎贡献！请：

1. 遵循现有代码结构
2. 为新功能添加测试
3. 更新文档
4. 验证数据准确性

## 更新日志

### 2026-04-14 - 真实抓取器实现

- ✓ 用真实 Playwright 抓取器替换模拟数据
- ✓ 添加 403 绕过功能
- ✓ 实现真实网络请求
- ✓ 添加全面错误处理
- ✓ 创建安装和测试脚本

### 2026-04-14 - 高级功能

- ✓ 添加 B&H Photo 抓取器
- ✓ 实现数据合并和去重
- ✓ 创建价格追踪系统
- ✓ 构建镜头对比工具
- ✓ 开发推荐引擎
- ✓ 生成交互式仪表板
