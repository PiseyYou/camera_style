# 💰 价格数据说明

## 当前状态

目前价格分析显示 **0个镜头**,这是正常的。

## 为什么没有价格数据?

### DPReview的限制
- DPReview主要提供镜头的**技术规格**和**评测**
- **不提供**实时价格信息
- 只有产品发布时的建议零售价(MSRP)

### 当前数据包含
✅ 镜头规格(焦距、光圈、重量等)
✅ 发布日期
✅ 技术细节
✅ 卡口类型
✅ 对焦和防抖信息

❌ 当前市场价格
❌ 历史价格趋势
❌ 优惠信息

## 如何获取价格数据?

### 方案1: 零售商API (推荐)
集成主流零售商的API:
- **B&H Photo** - 提供API访问
- **Adorama** - 提供价格数据
- **Amazon** - Product Advertising API
- **Best Buy** - Open API

### 方案2: 网页抓取
从零售商网站抓取价格:
- 需要处理反爬虫机制
- 需要定期更新
- 可能违反服务条款

### 方案3: 价格追踪服务
使用第三方价格追踪服务:
- **CamelCamelCamel** (Amazon)
- **Keepa** (Amazon)
- **PriceGrabber**

## 实现价格追踪的步骤

### 1. 选择数据源
```python
# 示例: B&H Photo API
import requests

def get_bhphoto_price(product_id):
    api_url = f"https://api.bhphotovideo.com/products/{product_id}"
    response = requests.get(api_url, headers={'API-Key': 'YOUR_KEY'})
    return response.json()['price']
```

### 2. 添加价格字段到CSV
在 `summary.csv` 中添加:
- `current_price` - 当前价格
- `msrp` - 建议零售价
- `currency` - 货币单位
- `price_source` - 价格来源
- `price_updated_at` - 价格更新时间

### 3. 定期更新
设置定时任务每天更新价格:
```bash
# crontab
0 2 * * * python3 scripts/update_prices.py
```

### 4. 价格历史
保存价格历史到数据库:
```python
# price_history.json
{
  "Canon RF 50mm F1.8": [
    {"date": "2026-04-14", "price": 199.99, "source": "bhphoto"},
    {"date": "2026-04-13", "price": 199.99, "source": "bhphoto"}
  ]
}
```

## 临时解决方案

在没有实时价格数据的情况下,你可以:

### 1. 手动添加价格
编辑CSV文件,添加价格列:
```csv
brand,model_name,...,current_price,currency
Canon,RF 50mm F1.8,...,199.99,USD
```

### 2. 使用MSRP
从制造商网站获取建议零售价

### 3. 社区众包
让用户提交他们看到的价格

## 当前可用功能

虽然没有价格数据,但你仍然可以:

✅ **浏览镜头目录** - 查看所有镜头规格
✅ **对比镜头** - 比较技术参数
✅ **获取推荐** - 基于规格的推荐
✅ **查看评分** - 如果有评测数据

## 下一步计划

1. **短期** (1-2周)
   - 集成B&H Photo API
   - 添加价格字段到数据模型
   - 实现基本价格显示

2. **中期** (1-2月)
   - 添加多个零售商
   - 实现价格历史追踪
   - 添加价格提醒功能

3. **长期** (3-6月)
   - 价格趋势分析
   - 最佳购买时机预测
   - 价格对比工具

## 相关文件

- `scripts/analysis/price_tracker.py` - 价格追踪脚本
- `reports/price_analysis.md` - 价格分析报告
- `data/price_history.json` - 价格历史数据

## 常见问题

**Q: 为什么不从DPReview获取价格?**
A: DPReview不提供价格API,只有产品规格。

**Q: 可以手动添加价格吗?**
A: 可以,编辑CSV文件添加`current_price`列。

**Q: 多久更新一次价格?**
A: 目前没有自动更新,需要实现后可以每天更新。

**Q: 支持哪些货币?**
A: 目前设计支持USD,可以扩展到其他货币。

## 贡献

如果你想帮助实现价格追踪功能:
1. Fork项目
2. 实现价格数据源集成
3. 提交Pull Request

---

**更新日期**: 2026-04-14
**状态**: 价格功能待实现
