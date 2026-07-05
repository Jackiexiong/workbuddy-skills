# 淘宝商品页面数据结构参考

## 页面数据位置

数据通过 SSR 嵌入在页面 HTML 中，位于 `<script>` 标签内。

## 关键数据节点

### skuBase

```json
{
  "skuBase": {
    "skus": [
      {
        "propPath": "1627207:54081874;20879:32557;12304035:3017674673;122216431:27772",
        "skuId": "5986123991730"
      }
    ],
    "props": [
      {
        "pid": "1627207",
        "name": "机身颜色",
        "values": [
          { "vid": "54081874", "name": "雪域白 Mate 70/直屏送88w快充" },
          { "vid": "381198578", "name": "曜石黑 Mate 70/直屏送88w快充" }
        ]
      }
    ]
  }
}
```

### skuCore.sku2info

```json
{
  "skuCore": {
    "sku2info": {
      "5986123991730": {
        "quantity": 10,
        "price": {
          "priceTitle": "优惠前",
          "priceText": "3098",
          "priceMoney": "309800"
        },
        "quantityText": "有货"
      },
      "0": {
        "price": {
          "priceText": "2948",
          "priceDesc": "起"
        }
      }
    }
  }
}
```

## 字段说明

| 字段 | 说明 |
|------|------|
| `propPath` | 规格属性路径，格式 `pid:vid;pid:vid;...` |
| `skuId` | SKU 唯一标识 |
| `props[].name` | 规格属性名（如"机身颜色"、"存储容量"） |
| `props[].values[].vid` | 规格值 ID |
| `props[].values[].name` | 规格值名称（如"雪域白"、"12GB+256GB"） |
| `priceText` | 价格，整数字符串，单位为元 |
| `priceMoney` | 价格，整数字符串，单位为分 |
| `quantity` | 库存数量 |
| `quantityText` | 库存状态文字（"有货"、"即将售罄"等） |

## 正则提取模式

```python
# 提取 skuBase（含 skus + props）
r'"skuBase"\s*:\s*(\{[\s\S]*?"skus"\s*:\s*\[[\s\S]*?\][\s\S]*?"props"\s*:\s*\[[\s\S]*?\]\s*\})'

# 提取 sku2info
r'"sku2info"\s*:\s*(\{[\s\S]*?\})\s*,\s*"skuItem"'

# 逐个提取价格（备选方案）
r'"(\d{10,})"\s*:\s*\{[^}]*"price"\s*:\s*\{[^}]*"priceText"\s*:\s*"(\d+)"'
```
