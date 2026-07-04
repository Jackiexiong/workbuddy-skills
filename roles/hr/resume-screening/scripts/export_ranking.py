#!/usr/bin/env python3
"""
简历筛选辅助工具集 — export_ranking.py

功能：
  --scan    扫描简历文件夹，统计文件数量和格式分布
  --export  导出排名表为 CSV 文件
  --copy    将选中的简历文件复制到新目录

用法：
  python export_ranking.py --scan "简历文件夹路径"
  python export_ranking.py --export "输出路径/排名表.csv" --rankings "数据" --title "岗位名称"
  python export_ranking.py --copy "源文件夹" --top 10 --files "简历1.docx" "简历2.pdf"
"""

import argparse
import csv
import json
import os
import shutil
import sys
from datetime import datetime


def scan_directory(folder_path):
    """
    扫描文件夹，统计简历文件的数量和格式分布。

    Args:
        folder_path: 简历文件夹路径

    Returns:
        dict: 统计信息
    """
    if not os.path.isdir(folder_path):
        print(f"[错误] 文件夹不存在: {folder_path}")
        sys.exit(1)

    folder_path = os.path.abspath(folder_path)
    stats = {
        "folder": folder_path,
        "total_files": 0,
        "by_format": {},
        "files": [],
        "ignored": 0,
    }

    # 支持的扩展名
    supported_exts = {'.docx', '.pdf', '.html', '.htm', '.txt'}

    for root, dirs, files in os.walk(folder_path):
        # 跳过 _筛选结果_* 目录
        dirs[:] = [d for d in dirs if not d.startswith('_筛选结果_')]

        for fname in files:
            # 跳过隐藏文件和临时文件
            if fname.startswith('.'):
                stats["ignored"] += 1
                continue
            if fname.startswith('~$'):
                stats["ignored"] += 1
                continue

            ext = os.path.splitext(fname)[1].lower()
            rel_path = os.path.relpath(os.path.join(root, fname), folder_path)

            if ext in supported_exts:
                stats["total_files"] += 1
                stats["by_format"][ext] = stats["by_format"].get(ext, 0) + 1
                stats["files"].append({
                    "filename": fname,
                    "path": rel_path,
                    "format": ext,
                    "full_path": os.path.join(root, fname),
                })
            elif ext:
                stats["ignored"] += 1

    return stats


def print_scan_report(stats):
    """打印扫描报告"""
    print("=" * 60)
    print(f"  简历扫描报告")
    print(f"  文件夹: {stats['folder']}")
    print("=" * 60)
    print(f"  简历文件总数: {stats['total_files']}")
    print()
    if stats["by_format"]:
        print(f"  格式分布:")
        fmt_names = {
            '.docx': 'Word 文档',
            '.pdf': 'PDF 文档',
            '.html': 'HTML 文件',
            '.htm': 'HTML 文件',
            '.txt': '纯文本',
        }
        for ext, count in sorted(stats["by_format"].items(), key=lambda x: -x[1]):
            name = fmt_names.get(ext, ext)
            bar = '█' * count if count < 60 else '█' * 60
            print(f"    {name:12s}  {count:4d} 份  {bar}")
    print()
    if stats["ignored"] > 0:
        print(f"  (已忽略 {stats['ignored']} 个非简历文件)")
    print(f"  {'─' * 50}")
    print(f"  提示：以上文件将逐份解析和评分。")
    print(f"       每份简历的解析将由 AI 依次处理。")
    print(f"{'=' * 60}")


def export_ranking_csv(output_path, rankings_data, title=""):
    """
    导出排名表为 CSV 文件。

    Args:
        output_path: 输出 CSV 文件路径
        rankings_data: 排名数据的字符串或列表
            字符串格式: "姓名1:92,姓名2:87,姓名3:85,..."
            或列表格式: [{"name": "张三", "score": 92, ...}, ...]
        title: 岗位名称（可选）
    """
    # 解析排名数据
    records = []
    if isinstance(rankings_data, str):
        # 字符串格式: "姓名1:92,姓名2:87"
        items = rankings_data.split(',')
        for i, item in enumerate(items):
            parts = item.strip().split(':')
            if len(parts) >= 2:
                records.append({
                    "排名": i + 1,
                    "候选人": parts[0].strip(),
                    "总分": parts[1].strip(),
                })
    elif isinstance(rankings_data, list):
        for i, item in enumerate(rankings_data):
            if isinstance(item, dict):
                record = {"排名": i + 1}
                for key, value in item.items():
                    record[key] = value
                records.append(record)
            elif isinstance(item, str):
                records.append({"排名": i + 1, "候选人": item})

    if not records:
        print("[错误] 排名数据为空或格式不正确")
        return False

    # 确定 CSV 字段
    fieldnames = list(records[0].keys())

    # 写入 CSV
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if title:
                f.write(f"# 岗位: {title}\n")
            f.write(f"# 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            writer.writeheader()
            writer.writerows(records)
        print(f"[OK] 排名表已导出: {output_path}")
        return True
    except Exception as e:
        print(f"[错误] 导出 CSV 失败: {e}")
        return False


def copy_selected_files(source_folder, target_folder, filenames):
    """
    将选中的文件复制到目标文件夹。

    Args:
        source_folder: 源文件夹路径
        target_folder: 目标文件夹路径（将自动创建）
        filenames: 要复制的文件名列表
    """
    source_folder = os.path.abspath(source_folder)

    # 创建目标文件夹
    os.makedirs(target_folder, exist_ok=True)

    copied = 0
    not_found = []

    for fname in filenames:
        # 在源文件夹中搜索文件（支持子目录）
        found_path = None
        for root, dirs, files in os.walk(source_folder):
            # 跳过已有的筛选结果目录
            dirs[:] = [d for d in dirs if not d.startswith('_筛选结果_')]

            if fname in files:
                found_path = os.path.join(root, fname)
                break
            # 也尝试匹配文件名（不区分路径）
            for f in files:
                if f == fname or os.path.basename(fname) == f:
                    found_path = os.path.join(root, f)
                    break
            if found_path:
                break

        if found_path:
            shutil.copy2(found_path, os.path.join(target_folder, os.path.basename(fname)))
            copied += 1
            print(f"  ✓ {os.path.basename(fname)}")
        else:
            not_found.append(fname)
            print(f"  ✗ {fname} (未找到)")

    print(f"\n结果: 成功复制 {copied}/{len(filenames)} 份简历")

    if not_found:
        print(f"以下 {len(not_found)} 个文件未找到:")
        for nf in not_found:
            print(f"  - {nf}")

    return copied


def main():
    parser = argparse.ArgumentParser(
        description="简历筛选辅助工具 — 扫描/导出/复制",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --scan "./简历库"
  %(prog)s --export "./排名表.csv" --rankings "张三:92,李四:87" --title "Java后端"
  %(prog)s --copy "./简历库" --top 10 --files "张三.docx" "李四.pdf"
        """
    )

    # 扫描模式
    parser.add_argument('--scan', metavar='文件夹路径',
                        help='扫描简历文件夹，统计格式分布')

    # 导出模式
    parser.add_argument('--export', metavar='输出CSV路径',
                        help='导出排名表为 CSV 文件')
    parser.add_argument('--rankings', metavar='"数据"',
                        help='排名数据 (格式: "姓名1:92,姓名2:87" 或 JSON)')
    parser.add_argument('--title', metavar='"岗位名称"',
                        help='岗位名称（可选）')

    # 复制模式
    parser.add_argument('--copy', metavar='源文件夹',
                        help='复制选中简历到新文件夹')
    parser.add_argument('--top', metavar='N', type=int, default=10,
                        help='选出的份数（用于命名目标文件夹）')
    parser.add_argument('--files', metavar='文件名', nargs='+',
                        help='要复制的文件名列表')

    args = parser.parse_args()

    # 执行对应操作
    if args.scan:
        stats = scan_directory(args.scan)
        print_scan_report(stats)

    elif args.export:
        if not args.rankings:
            print("[错误] 导出模式需要 --rankings 参数")
            sys.exit(1)
        export_ranking_csv(args.export, args.rankings, args.title or "")

    elif args.copy:
        if not args.files:
            print("[错误] 复制模式需要 --files 参数")
            sys.exit(1)

        source = os.path.abspath(args.copy)
        target_dir = os.path.join(source, f"_筛选结果_Top{args.top}")

        print(f"复制简历到: {target_dir}")
        print("-" * 40)
        copy_selected_files(source, target_dir, args.files)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
