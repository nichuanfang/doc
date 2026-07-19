#!/usr/bin/env python3
"""
处理 Markdown 文件中的远程图片链接：
- 支持指定目录：python handle_img.py /path/to/dir
- 不指定目录时：默认处理当前目录下的所有子目录

图片会下载到每个 .md 文件同级的 img/ 文件夹中。
"""

import os
import re
import sys
import argparse
import urllib.request
import ssl
from urllib.parse import urlparse, urlunparse, quote, unquote

# ==================== 原有逻辑保持不变 ====================

MD_IMG_PATTERN = re.compile(r'!\[([^\]]*)\]\((https?://[^\)\s]+)\)')
HTML_IMG_PATTERN = re.compile(
    r'(<img\b[^>]*?\bsrc\s*=\s*["\'])(https?://[^"\']+)(["\'][^>]*>)',
    re.IGNORECASE
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = quote(parsed.path, safe='/')
    query = quote(parsed.query, safe='=&?')
    return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, query, parsed.fragment))


def guess_filename(url: str) -> str:
    path = urlparse(url).path
    name = unquote(os.path.basename(path))
    if not name or name == '/':
        name = "image.png"
    elif "." not in name:
        name += ".png"
    return name


def download(url: str, dest_path: str) -> bool:
    try:
        normalized_url = normalize_url(url)
        req = urllib.request.Request(normalized_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=30) as resp:
            data = resp.read()
        with open(dest_path, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"  ✗ 下载失败: {url}\n    错误: {e}")
        return False


def collect_urls(content: str):
    urls = []
    for m in MD_IMG_PATTERN.finditer(content):
        urls.append(m.group(2))
    for m in HTML_IMG_PATTERN.finditer(content):
        urls.append(m.group(2))
    seen, ordered = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    return ordered


def process_md_file(md_path: str):
    if not os.path.isfile(md_path):
        return

    md_dir = os.path.dirname(os.path.abspath(md_path))
    img_dir = os.path.join(md_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    urls = collect_urls(content)
    if not urls:
        return

    replacements = {}
    print(f"[{os.path.basename(md_path)}] 发现 {len(urls)} 个远程图片链接：")

    for url in urls:
        filename = guess_filename(url)
        dest_path = os.path.join(img_dir, filename)
        print(f"  下载: {url} → img/{filename}")
        if download(url, dest_path):
            replacements[url] = f"./img/{filename}"
            print(f"  ✓ 已保存为: img/{filename}")
        else:
            replacements[url] = None

    def md_replace(match):
        alt, url = match.group(1), match.group(2)
        new_path = replacements.get(url)
        return f"![{alt}]({new_path})" if new_path else match.group(0)

    def html_replace(match):
        prefix, url, suffix = match.group(1), match.group(2), match.group(3)
        new_path = replacements.get(url)
        return f"{prefix}{new_path}{suffix}" if new_path else match.group(0)

    new_content = MD_IMG_PATTERN.sub(md_replace, content)
    new_content = HTML_IMG_PATTERN.sub(html_replace, new_content)

    if new_content != content:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[{os.path.basename(md_path)}] 已更新。\n")


def find_all_md_files(root_dir: str):
    """递归查找目录下所有 .md 文件"""
    md_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(".md"):
                md_files.append(os.path.join(dirpath, f))
    return md_files


def main():
    parser = argparse.ArgumentParser(description="下载 Markdown 中的远程图片并本地化")
    parser.add_argument(
        "directory",
        nargs="?",
        default=None,
        help="目标目录（可选）。不指定则处理当前目录下的所有子目录"
    )
    args = parser.parse_args()

    if args.directory:
        # 指定了目录
        target_dir = os.path.abspath(args.directory)
        if not os.path.isdir(target_dir):
            print(f"错误：目录不存在 -> {target_dir}")
            sys.exit(1)
        print(f"正在处理目录: {target_dir}\n")
        md_files = find_all_md_files(target_dir)
    else:
        # 未指定目录 → 处理当前目录下的所有子目录
        current_dir = os.getcwd()
        print(f"未指定目录，默认处理当前目录下的所有子目录: {current_dir}\n")
        subdirs = [
            os.path.join(current_dir, d)
            for d in os.listdir(current_dir)
            if os.path.isdir(os.path.join(current_dir, d))
        ]
        md_files = []
        for subdir in subdirs:
            md_files.extend(find_all_md_files(subdir))

    if not md_files:
        print("未找到任何 .md 文件。")
        return

    for md_file in md_files:
        process_md_file(md_file)


if __name__ == "__main__":
    main()