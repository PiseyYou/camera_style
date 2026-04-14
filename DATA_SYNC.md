# 数据同步架构 / Data Synchronization Architecture

## 统一数据源 / Unified Data Source

所有页面现在使用同一个数据源：`data/merged/merged_summary.csv`

All pages now use a single data source: `data/merged/merged_summary.csv`

### 数据流 / Data Flow

```
data/parsed/dpreview/summary.csv (主数据源 / Primary Source)
           ↓
    [同步 / Sync]
           ↓
data/merged/merged_summary.csv (统一数据库 / Unified Database)
           ↓
    [动态加载 / Dynamic Loading]
           ↓
┌──────────────────────────────────────────┐
│  所有HTML页面 / All HTML Pages           │
├──────────────────────────────────────────┤
│  • dashboard_enhanced.html               │
│  • lens_catalog.html                     │
│  • lens_data_table.html                  │
│  • comparison_*.html                     │
│  • recommendations_*.html                │
└──────────────────────────────────────────┘
```

## 当前数据 / Current Data

- **总镜头数 / Total Lenses**: 31
- **品牌数 / Brands**: 10 (Canon, Nikon, Sony, Sigma, Tamron, Fujifilm, Olympus, Panasonic, Leica, Pentax)
- **定焦镜头 / Prime Lenses**: 19
- **变焦镜头 / Zoom Lenses**: 12

## 更新数据 / Update Data

### 方法1：完整更新 / Method 1: Complete Update

运行完整更新脚本，同步数据并重新生成所有页面：

Run the complete update script to sync data and regenerate all pages:

```bash
python3 scripts/update_all.py
```

这将执行：
This will execute:

1. 同步数据源 / Sync data sources
2. 生成动态目录 / Generate dynamic catalog
3. 运行完整分析 / Run full analysis
4. 更新所有HTML页面 / Update all HTML pages

### 方法2：仅同步数据 / Method 2: Sync Data Only

如果只需要同步数据而不重新生成报告：

If you only need to sync data without regenerating reports:

```bash
python3 scripts/sync_data.py
```

### 方法3：手动同步 / Method 3: Manual Sync

```bash
cp data/parsed/dpreview/summary.csv data/merged/merged_summary.csv
```

## 添加新数据 / Adding New Data

1. 更新主数据文件 / Update the primary data file:
   ```bash
   # 编辑或替换 / Edit or replace
   data/parsed/dpreview/summary.csv
   ```

2. 运行同步 / Run sync:
   ```bash
   python3 scripts/update_all.py
   ```

3. 所有页面自动更新 / All pages automatically update

## 页面特性 / Page Features

### Dashboard Enhanced (dashboard_enhanced.html)
- ✅ 动态加载所有31个镜头 / Dynamically loads all 31 lenses
- ✅ 实时统计 / Real-time statistics
- ✅ 中英文切换 / Chinese/English toggle
- ✅ 显示镜头总数 / Shows total lens count

### Lens Catalog (lens_catalog.html)
- ✅ 动态从CSV加载 / Dynamically loads from CSV
- ✅ 品牌筛选 / Brand filtering
- ✅ 类型筛选 / Type filtering
- ✅ 搜索功能 / Search functionality
- ✅ 实时计数 / Real-time counting

### Data Table (lens_data_table.html)
- ✅ 表格形式显示 / Table format display
- ✅ 品牌颜色编码 / Brand color coding
- ✅ 完整规格信息 / Complete specifications

### Comparisons (comparison_*.html)
- ✅ 从统一数据源读取 / Reads from unified source
- ✅ 自动筛选相关镜头 / Auto-filters relevant lenses

### Recommendations (recommendations_*.html)
- ✅ 基于统一数据源 / Based on unified source
- ✅ 智能评分系统 / Intelligent scoring system

## 技术实现 / Technical Implementation

### 动态加载 / Dynamic Loading

所有页面使用JavaScript Fetch API从CSV加载数据：

All pages use JavaScript Fetch API to load data from CSV:

```javascript
// 尝试加载合并数据 / Try loading merged data
let response = await fetch('/data/merged/merged_summary.csv');

// 失败时回退到解析数据 / Fallback to parsed data on failure
if (!response.ok) {
    response = await fetch('/data/parsed/dpreview/summary.csv');
}
```

### 数据解析 / Data Parsing

CSV数据被解析为JavaScript对象：

CSV data is parsed into JavaScript objects:

```javascript
const lines = csvText.trim().split('\n');
const headers = lines[0].split(',');
const lenses = lines.slice(1).map(line => {
    const parts = line.split(',');
    return {
        brand: parts[0],
        model_name: parts[1],
        // ... 更多字段 / more fields
    };
});
```

## 维护 / Maintenance

### 定期检查 / Regular Checks

```bash
# 检查数据同步状态 / Check data sync status
wc -l data/parsed/dpreview/summary.csv data/merged/merged_summary.csv

# 应该显示相同行数 / Should show same line count
```

### 故障排除 / Troubleshooting

**问题：页面显示数据不完整**
Problem: Pages show incomplete data

解决方案：
Solution:
```bash
python3 scripts/update_all.py
```

**问题：数据不同步**
Problem: Data out of sync

解决方案：
Solution:
```bash
python3 scripts/sync_data.py
```

## 未来改进 / Future Improvements

- [ ] 实时价格数据集成 / Real-time price data integration
- [ ] 自动化数据爬取 / Automated data scraping
- [ ] 数据库后端 / Database backend
- [ ] API接口 / API endpoints
- [ ] 用户评论系统 / User review system
