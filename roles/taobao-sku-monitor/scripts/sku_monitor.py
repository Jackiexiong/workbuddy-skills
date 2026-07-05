"""
竞品监控脚本 - 基于页面源码一次提取 skuBase + skuCore.sku2info
无需逐个访问 SKU 页面，一次页面加载即可获取所有规格和价格。
"""

import os
import re
import sys
import json
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from browser_manager import BrowserManager


class SkuMonitor:
    """SKU 竞品监控器"""

    def __init__(self, browser_manager: BrowserManager):
        self.bm = browser_manager
        self.page = browser_manager.page

    def _extract_json_from_page(self, content: str, key: str, fallback_end: str = r'\}\s*[,}]') -> Optional[Dict]:
        """从页面源码中正则提取指定 key 的 JSON 对象"""
        # 使用贪婪匹配找到完整的 JSON 块
        pattern = rf'"{key}"\s*:\s*(\{{[\s\S]*?\}})\s*{fallback_end}'
        match = re.search(pattern, content)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        return None

    def extract_data(self, url: str) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        访问商品页面，从页面源码中提取 skuBase 和 sku2info。
        返回 (sku_base, sku2info) 或 (None, None)
        """
        print(f"正在访问商品页面: {url}")
        self.bm.go_to_product(url)
        time.sleep(3)

        content = self.page.content()
        print(f"页面内容长度: {len(content)}")

        # 提取 skuBase
        sku_base = None
        # 先尝试完整的 skuBase（含 skus + props）
        match = re.search(
            r'"skuBase"\s*:\s*(\{[\s\S]*?"skus"\s*:\s*\[[\s\S]*?\][\s\S]*?"props"\s*:\s*\[[\s\S]*?\]\s*\})',
            content
        )
        if match:
            try:
                sku_base = json.loads(match.group(1))
                print("✓ 提取到 skuBase（含 skus + props）")
            except json.JSONDecodeError:
                pass

        if not sku_base:
            # 备选：只提取 skus 部分
            match = re.search(r'"skuBase"\s*:\s*(\{[\s\S]*?"skus"\s*:\s*\[[\s\S]*?\])', content)
            if match:
                try:
                    raw = match.group(1)
                    if not raw.endswith('}'):
                        raw += '}'
                    sku_base = json.loads(raw)
                    print("✓ 提取到 skuBase（仅 skus）")
                except json.JSONDecodeError:
                    pass

        # 提取 sku2info
        sku2info = None
        match = re.search(r'"sku2info"\s*:\s*(\{[\s\S]*?\})\s*,\s*"skuItem"', content)
        if match:
            try:
                sku2info = json.loads(match.group(1))
                print(f"✓ 提取到 sku2info（{len(sku2info)} 条记录）")
            except json.JSONDecodeError:
                # 尝试更精确的提取：逐个 skuId 的价格块
                pass

        if not sku2info:
            # 备选：直接从页面中提取所有 priceText 与 skuId 的对应关系
            print("尝试从页面源码逐个提取价格...")
            sku2info = {}
            # 匹配 "skuId": { ... "priceText": "xxx" ... } 模式
            price_blocks = re.findall(
                r'"(\d{10,})"\s*:\s*\{[^}]*"price"\s*:\s*\{[^}]*"priceText"\s*:\s*"(\d+)"',
                content
            )
            for sku_id, price_text in price_blocks:
                sku2info[sku_id] = {"price": {"priceText": price_text}}
            if sku2info:
                print(f"✓ 逐个提取到 {len(sku2info)} 个 SKU 的价格")

        return sku_base, sku2info

    def parse_skus(self, sku_base: Dict) -> List[Dict]:
        """
        解析 skuBase 数据，返回 SKU 列表。
        每个 SKU 包含: skuId, specs(规格描述)
        """
        # 构建 vid → 规格名称 映射
        vid_map = {}
        props = sku_base.get("props", [])
        for prop in props:
            prop_name = prop.get("name", "")
            for val in prop.get("values", []):
                vid = str(val.get("vid", ""))
                val_name = val.get("name", "")
                vid_map[vid] = val_name

        # 解析 skus
        skus = sku_base.get("skus", [])
        result = []
        for sku in skus:
            sku_id = str(sku.get("skuId", ""))
            prop_path = sku.get("propPath", "")

            # 解析 propPath: "1627207:54081874;20879:32557;12304035:3017674673"
            specs = []
            if prop_path:
                for part in prop_path.split(";"):
                    part = part.strip()
                    if ":" in part:
                        pid, vid = part.split(":", 1)
                        if vid in vid_map:
                            specs.append(vid_map[vid])
                        else:
                            specs.append(part)

            spec_str = "/".join(specs) if specs else "默认规格"
            result.append({
                "skuId": sku_id,
                "specs": spec_str,
            })

        return result

    def get_price_for_sku(self, sku_id: str, sku2info: Dict) -> str:
        """从 sku2info 中获取指定 SKU 的价格"""
        info = sku2info.get(sku_id, {})
        price_obj = info.get("price", {})
        price_text = price_obj.get("priceText", "")
        if price_text:
            return f"¥{price_text}"
        return "价格未知"

    def run(self, url: str, item_id: str = None):
        """
        主流程: 一次页面加载 → 提取 skuBase + sku2info → 解析 → 写入 TXT
        """
        # 提取商品ID
        if item_id is None:
            match = re.search(r'id=(\d+)', url)
            item_id = match.group(1) if match else "unknown"

        print(f"\n{'='*60}")
        print(f"  竞品监控 - 商品ID: {item_id}")
        print(f"{'='*60}")

        # Step 1: 一次页面加载，提取所有数据
        sku_base, sku2info = self.extract_data(url)
        if not sku_base:
            print("× 无法获取 skuBase 数据，程序退出")
            return

        # Step 2: 解析 SKU 列表
        skus = self.parse_skus(sku_base)
        if not skus:
            print("× 未解析到 SKU 数据，程序退出")
            return

        print(f"\n共解析到 {len(skus)} 个 SKU:")
        for i, sku in enumerate(skus[:10], 1):
            price = self.get_price_for_sku(sku["skuId"], sku2info) if sku2info else "价格未知"
            print(f"  {i}. {sku['skuId']} - {sku['specs']} - {price}")
        if len(skus) > 10:
            print(f"  ... 还有 {len(skus) - 10} 个 SKU")

        # Step 3: 组装结果
        results = []
        for sku in skus:
            price = self.get_price_for_sku(sku["skuId"], sku2info) if sku2info else "价格未知"
            results.append({
                "skuId": sku["skuId"],
                "specs": sku["specs"],
                "price": price,
            })

        # Step 4: 写入 TXT 文件
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sku_prices_{item_id}_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)

        # 获取商品标题（从页面 title 标签中提取，去掉末尾的 "-淘宝网"）
        page_title = self.page.title()
        title = re.sub(r'\s*-\s*淘宝网\s*$', '', page_title).strip()
        if not title:
            title_match = re.search(r'"title"\s*:\s*"([^"]{5,})"', self.page.content())
            title = title_match.group(1) if title_match else "未知商品"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"商品ID: {item_id}\n")
            f.write(f"商品标题: {title}\n")
            f.write(f"商品链接: {url}\n")
            f.write(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"SKU总数: {len(results)}\n")
            f.write(f"\n{'='*80}\n")
            f.write("=== SKU 规格与价格 ===\n")
            f.write(f"{'='*80}\n\n")

            # 表头
            f.write(f"{'序号':<6}{'SKU ID':<22}{'规格':<45}{'价格':<12}\n")
            f.write(f"{'-'*6}{'-'*22}{'-'*45}{'-'*12}\n")

            # 数据行
            for idx, item in enumerate(results, 1):
                f.write(f"{idx:<6}{item['skuId']:<22}{item['specs']:<45}{item['price']:<12}\n")

            f.write(f"\n{'='*80}\n")
            f.write("--- 抓取完成 ---\n")

        print(f"\n{'='*60}")
        print(f"✓ 结果已保存至: {os.path.abspath(filepath)}")
        print(f"  共 {len(results)} 个 SKU 的规格和价格")
        print(f"{'='*60}")

        return filepath


def load_urls_from_config(config_path: str) -> List[str]:
    """从配置文件读取 URL 列表（支持 # 注释和空行）"""
    urls = []
    if not os.path.exists(config_path):
        return urls
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    return urls


def main():
    """入口函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "urls.txt")

    # 优先使用命令行参数（单个URL），否则读取配置文件
    if len(sys.argv) > 1:
        urls = [sys.argv[1]]
    else:
        urls = load_urls_from_config(config_path)

    print("=" * 60)
    print("       淘宝竞品监控 - SKU 价格抓取工具")
    print("=" * 60)

    if not urls:
        print(f"\n× 未找到监控链接，请编辑配置文件添加URL：")
        print(f"  {config_path}")
        print(f"\n  格式示例（每行一个URL）：")
        print(f"  https://item.taobao.com/item.htm?id=898379064529")
        return

    print(f"\n共 {len(urls)} 个商品待监控：")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")

    try:
        with BrowserManager(headless=False) as bm:
            print("\n✓ 浏览器启动成功")

            print("\n检查登录状态...")
            if not bm.ensure_login():
                print("\n× 登录超时，请重新运行程序")
                return

            monitor = SkuMonitor(bm)
            result_files = []
            for i, url in enumerate(urls, 1):
                print(f"\n>>> [{i}/{len(urls)}] 开始抓取...")
                filepath = monitor.run(url)
                if filepath:
                    result_files.append(filepath)
                if i < len(urls):
                    print("等待 3 秒后继续下一个商品...")
                    time.sleep(3)

            # 汇总
            print(f"\n{'='*60}")
            print(f"  全部完成！共监控 {len(urls)} 个商品")
            print(f"  结果文件：")
            for f in result_files:
                print(f"    → {os.path.abspath(f)}")
            print(f"{'='*60}")

    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n× 程序出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
