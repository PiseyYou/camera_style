# Camera Style - 镜头数据分析系统

一个综合性的相机镜头数据采集、分析和可视化平台。支持从 DPReview 等网站抓取镜头规格参数，提供智能对比、价格追踪和个性化推荐功能。

## ✨ 核心功能

### 📥 数据采集
- **DPReview 抓取器**：使用 Playwright 真实浏览器抓取镜头数据
- **多品牌支持**：佳能、尼康、索尼、富士、松下、奥林巴斯等
- **完整规格**：焦距、光圈、重量、尺寸、卡口类型、发布日期等
- **数据持久化**：保存原始 HTML 和解析后的 JSON 数据

### 📊 数据分析
- **智能合并**：自动合并多源数据并去重
- **价格追踪**：历史价格分析和趋势检测
- **镜头对比**：并排对比多个镜头的规格和性能
- **推荐引擎**：基于预算、用途和偏好的智能推荐
- **交互式仪表板**：实时数据可视化和筛选

### 🎨 可视化报告
- **增强仪表板**：统计概览、数据表格、快速筛选
- **动态目录**：可搜索、可排序的镜头目录
- **对比报告**：24-70mm 和 50mm 镜头专项对比
- **推荐报告**：旅行、人像、预算等场景推荐

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 依赖包：beautifulsoup4, playwright, lxml, pyyaml, pytest, flask

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/PiseyYou/camera_style.git
cd camera_style

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器
python3 -m playwright install chromium

# 4. 运行完整分析（使用现有数据）
python3 scripts/run_analysis.py

# 5. 启动交互式仪表板
./start_dashboard.sh
# 或手动启动
python3 dashboard_server_simple.py
```

浏览器将自动打开 http://localhost:5000

## 📖 使用指南

### 1. 数据抓取

#### 抓取 DPReview 镜头数据

```bash
# 抓取指定品牌的镜头（限制数量）
python3 scripts/ingest/dpreview_run.py --brand Canon --limit 10

# 抓取多个品牌
python3 scripts/ingest/dpreview_run.py --brand Sony --limit 5
python3 scripts/ingest/dpreview_run.py --brand Nikon --limit 5
```

**输出位置：**
- 原始 HTML：`data/raw/dpreview/`
- 解析 JSON：`data/parsed/dpreview/`
- 汇总 CSV：`data/parsed/dpreview/summary.csv`

### 2. 数据分析

#### 运行完整分析流程

```bash
python3 scripts/run_analysis.py
```

这将执行：
1. ✅ 数据同步（统一数据源）
2. ✅ 数据合并（去重和整合）
3. ✅ 价格分析（趋势和优惠）
4. ✅ 镜头对比（24-70mm 和 50mm）
5. ✅ 生成推荐（旅行、人像、预算）
6. ✅ 构建仪表板

**生成的报告：**
- `reports/dashboard_enhanced.html` - 主仪表板
- `reports/lens_catalog.html` - 动态镜头目录
- `reports/comparison_*.html` - 对比报告
- `reports/recommendations_*.html` - 推荐报告
- `reports/price_analysis.md` - 价格分析

#### 独立分析工具

**数据合并与去重：**
```bash
python3 scripts/analysis/merge_data.py
```

**价格追踪：**
```bash
python3 scripts/analysis/price_tracker.py
```

**镜头对比：**
```bash
python3 scripts/analysis/lens_comparator.py
```

**推荐引擎：**
```bash
python3 scripts/analysis/lens_recommender.py
```

### 3. 一键更新

更新所有数据和报告：

```bash
python3 scripts/update_all.py
```

这将依次执行：
1. 数据同步
2. 生成动态目录
3. 运行完整分析

### 4. 交互式仪表板

启动本地 Web 服务器：

```bash
./start_dashboard.sh
```

或手动启动：

```bash
python3 dashboard_server_simple.py
```

访问 http://localhost:5000 查看：
- 📊 统计概览（总数、品牌分布、价格范围）
- 🔍 实时搜索和筛选
- 📋 完整数据表格
- 📈 价格趋势图表
- 🔗 快速访问各类报告

## 📁 项目结构

```
camera_style/
├── scripts/
│   ├── ingest/                          # 数据采集模块
│   │   ├── base_scraper.py              # 抓取器基类
│   │   ├── dpreview_discovery.py        # DPReview 发现器
│   │   ├── dpreview_fetch.py            # DPReview 抓取器
│   │   ├── dpreview_parser.py           # DPReview 解析器
│   │   ├── dpreview_run.py              # DPReview 运行器
│   │   ├── bhphoto_scraper.py           # B&H Photo 抓取器
│   │   └── simple_scraper.py            # 简单抓取器
│   ├── analysis/                        # 数据分析模块
│   │   ├── merge_data.py                # 数据合并与去重
│   │   ├── price_tracker.py             # 价格追踪与趋势
│   │   ├── lens_comparator.py           # 镜头对比工具
│   │   └── lens_recommender.py          # 推荐引擎
│   ├── generate_dynamic_catalog.py      # 动态目录生成器
│   ├── run_analysis.py                  # 完整分析流程
│   ├── sync_data.py                     # 数据同步工具
│   └── update_all.py                    # 一键更新脚本
├── data/
│   ├── raw/dpreview/                    # 原始 HTML 文件
│   ├── parsed/dpreview/                 # 解析后的 JSON 数据
│   │   └── summary.csv                  # DPReview 汇总 CSV
│   ├── merged/                          # 合并后的数据
│   │   └── merged_summary.csv           # 统一数据源（31 个镜头）
│   └── analysis_history.json            # 分析历史记录
├── reports/                             # 生成的报告
│   ├── dashboard_enhanced.html          # 增强仪表板（主入口）
│   ├── dashboard.html                   # 基础仪表板
│   ├── lens_catalog.html                # 动态镜头目录
│   ├── lens_data_table.html             # 数据表格视图
│   ├── comparison_24_70.html            # 24-70mm 对比
│   ├── comparison_50.html               # 50mm 对比
│   ├── recommendations_travel.html      # 旅行推荐
│   ├── recommendations_portrait.html    # 人像推荐
│   ├── recommendations_budget.html      # 预算推荐
│   └── price_analysis.md                # 价格分析报告
├── tests/                               # 测试文件
│   ├── config/                          # 配置测试
│   └── ingest/                          # 抓取器测试
├── dashboard_server_simple.py           # 仪表板服务器
├── start_dashboard.sh                   # 启动脚本
├── test_enhanced_dashboard.sh           # 测试脚本
├── requirements.txt                     # Python 依赖
└── README.md                            # 本文件
```

## 🎯 使用场景

### 摄影爱好者
- 📷 **选购镜头**：对比不同品牌和型号的规格参数
- 💰 **价格追踪**：监控价格趋势，找到最佳购买时机
- 🎨 **场景推荐**：根据拍摄需求（旅行、人像等）获取推荐
- 📊 **数据对比**：并排对比多个镜头的性能指标

### 开发者
- 🔧 **数据源**：结构化的镜头数据（JSON/CSV 格式）
- 🤖 **API 开发**：基于抓取数据构建应用
- 📈 **数据分析**：分析摄影器材市场趋势
- 🧪 **测试数据**：用于机器学习和数据科学项目

### 研究人员
- 📊 **市场研究**：分析镜头定价策略和市场趋势
- 🔬 **产品分析**：跨品牌技术规格对比
- 📉 **价格模型**：研究价格波动和影响因素
- 📚 **数据可视化**：生成图表和报告

## 🔧 高级功能

### 自定义抓取

```python
from scripts.ingest.dpreview_run import DPReviewRunner

runner = DPReviewRunner()
lenses = runner.run(brand="Canon", limit=20)
print(f"抓取了 {len(lenses)} 个镜头")
```

### 自定义推荐

```python
from scripts.analysis.lens_recommender import LensRecommender, UserRequirements

recommender = LensRecommender()

# 定义需求
requirements = UserRequirements(
    max_budget=8000,           # 最高预算（元）
    mount="Canon RF",          # 卡口类型
    max_weight=600,            # 最大重量（克）
    portability_priority=0.9,  # 便携性优先级
    low_light_priority=0.7     # 弱光性能优先级
)

# 获取推荐
recommendations = recommender.recommend(requirements, top_n=5)
for lens in recommendations:
    print(f"{lens['model_name']}: 评分 {lens['score']:.2f}")
```

### 价格监控

```python
from scripts.analysis.price_tracker import PriceTracker

tracker = PriceTracker()

# 找出最佳优惠（折扣 > 10%）
deals = tracker.find_best_deals(min_discount_pct=10)
for deal in deals:
    print(f"🔥 {deal['model_name']}: 节省 ¥{deal['savings']:.2f}")
```

## 📊 当前数据状态

- ✅ **数据源**：DPReview（真实网络抓取）
- ✅ **镜头数量**：31 个（6 个来自 DPReview pilot）
- ✅ **品牌覆盖**：佳能、尼康、索尼
- ✅ **数据格式**：JSON + CSV
- ✅ **报告类型**：HTML 交互式报告

### 示例数据

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
  "source_url": "https://www.dpreview.com/products/lenses/...",
  "fetched_at": "2026-04-14T02:30:00.000000+00:00"
}
```

## 🐛 故障排除

### 403 禁止访问错误

抓取器使用 Playwright 真实浏览器绕过反爬虫限制。如果仍遇到 403：

1. 增加延迟：编辑 `scripts/ingest/dpreview_fetch.py`，增加 `wait_seconds`
2. 检查网站是否更新了反爬虫策略
3. 尝试更换 User-Agent

### 数据解析失败

如果解析的数据不完整：

1. 检查 `data/raw/dpreview/` 中的原始 HTML
2. 网站可能更改了 HTML 结构
3. 更新 `scripts/ingest/dpreview_parser.py` 中的 CSS 选择器

### Playwright 安装问题

```bash
# 重新安装 Playwright 浏览器
python3 -m playwright install --force chromium

# 验证安装
python3 -m playwright --version
```

### 仪表板无法启动

```bash
# 检查端口占用
lsof -i :5000

# 使用其他端口
# 编辑 dashboard_server_simple.py，修改 PORT 变量
```

## 📝 开发计划

### 已完成
- ✅ DPReview 真实数据抓取
- ✅ 数据合并与去重
- ✅ 价格追踪系统
- ✅ 镜头对比工具
- ✅ 推荐引擎
- ✅ 交互式仪表板
- ✅ 动态目录生成

### 计划中
- ⏳ 更多数据源（Adorama、制造商官网）
- ⏳ 价格提醒功能
- ⏳ 用户评论抓取
- ⏳ 图片样张分析
- ⏳ RESTful API 接口
- ⏳ 数据库持久化

## 📄 许可证

本项目仅用于教育和研究目的。请遵守数据源网站的服务条款和 robots.txt。不要用过多请求使服务器过载。

## 🤝 贡献

欢迎贡献代码！请：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📧 联系方式

- GitHub: [@PiseyYou](https://github.com/PiseyYou)
- 项目地址: https://github.com/PiseyYou/camera_style

## 🙏 致谢

- [DPReview](https://www.dpreview.com) - 镜头数据来源
- [Playwright](https://playwright.dev) - 网页抓取工具
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML 解析库

---

**最后更新**: 2026-04-14
