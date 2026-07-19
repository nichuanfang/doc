#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
format.py

用途：
    清洗 + 格式化指定文件夹内的所有 Markdown（.md）文件。

用法：
    python format.py <目标文件夹名>

    例如同目录下有 docs/ 文件夹：
        python format.py docs

    会递归处理 docs/ 下所有 .md 文件（原地修改，直接覆盖原文件）。
"""

import argparse
import os
import re
import sys

# ---------- 正则定义 ----------

# ATX 标题 + 跳转链接： "### [文字](#锚点)"
ATX_LINK_HEADING_RE = re.compile(r"^(#{1,6})\s*\[(.+?)\]\(#[^)]*\)\s*$")

# 缺失空格的 ATX 标题： "###文字"（后面紧跟非 # 非空白字符）
ATX_MISSING_SPACE_RE = re.compile(r"^(#{1,6})([^#\s].*)$")

# Setext 标题的第一行： "[文字](#锚点)"（整行只有这个链接）
SETEXT_LINK_LINE_RE = re.compile(r"^\[(.+?)\]\(#[^)]*\)\s*$")

# Setext 下划线：只由 '-' 组成的一行（至少 1 个），或只由 '=' 组成的一行
SETEXT_DASH_RE = re.compile(r"^-+\s*$")
SETEXT_EQUAL_RE = re.compile(r"^=+\s*$")

# 代码围栏（``` 或 ~~~ 开头，允许前导空格与语言标注）
FENCE_RE = re.compile(r"^(\s*)(```|~~~)")


def clean_markdown_text(text: str):
    """
    对 Markdown 文本做清洗，返回 (新文本, 是否发生变化)
    """
    lines = text.split("\n")
    out_lines = []
    changed = False

    in_fence = False
    fence_marker = None

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        # ---- 代码围栏状态跟踪：围栏内的内容原样保留，不做任何处理 ----
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(2)
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = None
            out_lines.append(line)
            i += 1
            continue

        if in_fence:
            out_lines.append(line)
            i += 1
            continue

        # ---- 规则 2：Setext 风格链接标题（两行) ----
        # 必须是 "[文字](#锚点)" 紧跟着下一行是纯 '-' 或纯 '=' 行
        if i + 1 < n:
            setext_match = SETEXT_LINK_LINE_RE.match(line)
            if setext_match:
                next_line = lines[i + 1]
                if SETEXT_DASH_RE.match(next_line):
                    out_lines.append("## " + setext_match.group(1))
                    changed = True
                    i += 2
                    continue
                if SETEXT_EQUAL_RE.match(next_line):
                    out_lines.append("# " + setext_match.group(1))
                    changed = True
                    i += 2
                    continue

        # ---- 规则 1：ATX 风格链接标题（单行） ----
        atx_match = ATX_LINK_HEADING_RE.match(line)
        if atx_match:
            hashes = atx_match.group(1)
            title = atx_match.group(2)
            new_line = f"{hashes} {title}"
            if new_line != line:
                changed = True
            out_lines.append(new_line)
            i += 1
            continue

        # ---- 规则 3：补齐 # 与文字之间缺失的空格（幂等） ----
        missing_space_match = ATX_MISSING_SPACE_RE.match(line)
        if missing_space_match:
            hashes = missing_space_match.group(1)
            rest = missing_space_match.group(2)
            new_line = f"{hashes} {rest}"
            out_lines.append(new_line)
            changed = True
            i += 1
            continue

        # ---- 其他行原样保留 ----
        out_lines.append(line)
        i += 1

    new_text = "\n".join(out_lines)
    return new_text, changed


def find_markdown_files(folder: str):
    """递归查找目标文件夹下所有 .md 文件"""
    md_files = []
    for root, _dirs, files in os.walk(folder):
        for fname in files:
            if fname.lower().endswith(".md"):
                md_files.append(os.path.join(root, fname))
    return sorted(md_files)


def process_folder(folder: str, dry_run: bool = False):
    if not os.path.isdir(folder):
        print(f"错误：文件夹不存在 -> {folder}", file=sys.stderr)
        sys.exit(1)

    md_files = find_markdown_files(folder)
    if not md_files:
        print(f"未在 {folder} 下找到任何 .md 文件。")
        return

    changed_count = 0
    for path in md_files:
        with open(path, "r", encoding="utf-8") as f:
            original_text = f.read()

        new_text, changed = clean_markdown_text(original_text)

        if changed:
            changed_count += 1
            print(f"[已修改] {path}")
            if not dry_run:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_text)
        else:
            print(f"[无需修改] {path}")

    print(f"\n处理完成：共 {len(md_files)} 个文件，{changed_count} 个被修改。")
    if dry_run:
        print("（dry-run 模式，未实际写入文件）")


def main():
    parser = argparse.ArgumentParser(description="清洗 + 格式化指定文件夹内的 Markdown 文件")
    parser.add_argument("folder", help="目标文件夹路径（相对于脚本所在目录，或绝对路径）")
    parser.add_argument("--dry-run", action="store_true", help="只预览会修改哪些文件，不实际写入")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = args.folder
    if not os.path.isabs(folder_path):
        folder_path = os.path.join(script_dir, folder_path)

    process_folder(folder_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()