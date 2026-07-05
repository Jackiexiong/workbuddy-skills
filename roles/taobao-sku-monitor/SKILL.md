---
name: taobao-sku-monitor
description: 淘宝竞品监控脚本，用于抓取淘宝商品的所有 SKU 规格和价格。触发词：竞品监控、商品监控、价格监控、SKU抓取、抓取价格、监控商品、抓取规格。
---

# 淘宝竞品监控

## 概述

基于 Playwright + 正则提取的淘宝商品 SKU 价格监控工具。一次页面加载即可提取所有 SKU 的规格和价格，无需逐个访问 SKU 页面。

## 触发场景

当用户提出以下需求时使用此技能：
- 抓取淘宝/天猫商品的 SKU 规格和价格
- 竞品监控、价格监控
- 批量获取商品的多规格价格
- 输入类似 `https://item.taobao.com/item.htm?id=xxx` 的链接

## 核心技术原理

淘宝商品页面响应中已包含完整数据，关键字段：

- `skuBase.skus[]` — 每个 SKU 的 `skuId` + `propPath`（规格属性路径）
- `skuBase.props[]` — 规格属性定义，含 `pid`、`name`、`values[{vid, name}]`
- `skuCore.sku2info[skuId]` — 每个 SKU 的 `price.priceText`（价格，整数字符串，单位元）

## 使用方式

### 前置条件

1. 项目中已有 `browser_manager.py`（浏览器管理类，含登录会话持久化）
2. 项目中已有 `sku_monitor.py`（竞品监控主脚本）
3. 项目中已有 `urls.txt`（配置文件，每行一个商品 URL）

### 运行命令

```bash
# 读取 urls.txt 配置文件批量抓取
PYTHONIOENCODING=utf-8 python sku_monitor.py

# 只抓取单个商品
PYTHONIOENCODING=utf-8 python sku_monitor.py https://item.taobao.com/item.htm?id=xxx
```

### 配置文件格式（urls.txt）

```
# 竞品监控链接列表
# 每行一个商品URL，# 开头的行为注释，空行自动跳过

https://item.taobao.com/item.htm?id=898379064529
https://item.taobao.com/item.htm?id=654321098765
```

## 脚本结构

### 文件清单

| 文件 | 说明 |
|------|------|
| `sku_monitor.py` | 主脚本，含 `SkuMonitor` 类 |
| `browser_manager.py` | 浏览器管理，含登录会话持久化 |
| `urls.txt` | 商品 URL 配置文件 |
| `output/` | 输出目录，生成 `sku_prices_{商品ID}_{时间戳}.txt` |

### SkuMonitor 类核心方法

```python
class SkuMonitor:
    def extract_data(url) -> (sku_base, sku2info)
    # 访问页面，从源码正则提取 skuBase 和 sku2info

    def parse_skus(sku_base) -> List[Dict]
    # 解析 skuBase，构建 vid→规格名映射，返回 SKU 列表

    def get_price_for_sku(sku_id, sku2info) -> str
    # 从 sku2info 中获取指定 SKU 的价格

    def run(url, item_id=None) -> str
    # 主流程：一次页面加载 → 提取 → 解析 → 写入 TXT
```

### BrowserManager 会话持久化

- `save_session()` — 登录成功后保存 cookies + localStorage 到 `browser_data/session.json`
- `load_session()` — 启动时自动恢复登录状态，避免重复扫码
- `ensure_login()` — 检测登录状态，未登录则等待用户扫码

## 输出格式

```
商品ID: 898379064529
商品标题: 二手Huawei/华为 Mate 70 全网通双卡双待华为手机
商品链接: https://item.taobao.com/item.htm?id=898379064529
抓取时间: 2026-06-26 19:36:26
SKU总数: 36

================================================================================
=== SKU 规格与价格 ===
================================================================================

序号    SKU ID                规格                                           价格
------  --------------------  ---------------------------------------------  ------------
1       5986123991730         雪域白/9.9成新/12GB+256GB/中国大陆              ¥3098
2       5986123991731         雪域白/9.9成新/12GB+512GB/中国大陆              ¥3248
...
```

## 扩展指南

### 添加新商品

编辑 `urls.txt`，添加一行淘宝商品 URL：
```
https://item.taobao.com/item.htm?id=新商品ID
```

### 修改输出格式

编辑 `sku_monitor.py` 中 `run()` 方法的 `Step 4: 写入 TXT 文件` 部分。

### 添加新的数据字段

1. 在 `extract_data()` 中添加新的正则提取逻辑
2. 在 `parse_skus()` 或新增方法中解析
3. 在 `run()` 中组装到结果中

## 注意事项

- 需要 `PYTHONIOENCODING=utf-8` 环境变量避免 Windows GBK 编码错误
- 淘宝页面结构可能变化，正则提取有多层 fallback
- 首次运行需在浏览器中扫码登录，后续自动恢复会话
- 批量抓取时每个商品间隔 3 秒防止反爬
