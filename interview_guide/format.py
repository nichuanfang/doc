#!/usr/bin/env python3
"""
提取指定 Markdown 文件中的远程图片链接（http/https），下载到该 md 文件
同级目录的 img 文件夹下，并把文中的链接替换为本地相对路径。

用法：
    python3 format.py 文件1.md 文件2.md ...
"""

import os
import re
import sys
import urllib.request
import ssl
from urllib.parse import urlparse, unquote

# 1. Markdown 图片语法: ![alt](http://... 或 https://...)
MD_IMG_PATTERN = re.compile(r'!\[([^\]]*)\]\((https?://[^\)\s]+)\)')

# 2. HTML <img ... src="http(s)://..." ...> 标签，只捕获 src 属性值
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

# 部分图床对 https 证书校验比较严格，这里放宽以避免下载失败
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def guess_filename(url: str, used_names: set) -> str:
    """从 URL 中猜测一个文件名，避免重名覆盖。"""
    path = urlparse(url).path
    name = unquote(os.path.basename(path))
    if not name:
        name = "image"
    if "." not in name:
        name += ".png"  # 没有扩展名时兜底给一个

    base, ext = os.path.splitext(name)
    candidate = name
    i = 1
    while candidate in used_names:
        candidate = f"{base}_{i}{ext}"
        i += 1
    used_names.add(candidate)
    return candidate


def download(url: str, dest_path: str) -> bool:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=30) as resp:
            data = resp.read()
        with open(dest_path, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"  ✗ 下载失败: {url}\n    错误: {e}")
        return False


def collect_urls(content: str):
    """收集文中所有出现的远程图片 URL（markdown + html 两种写法）。"""
    urls = []
    for m in MD_IMG_PATTERN.finditer(content):
        urls.append(m.group(2))
    for m in HTML_IMG_PATTERN.finditer(content):
        urls.append(m.group(2))
    # 去重但保持顺序
    seen = set()
    ordered = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    return ordered


def process_md_file(md_path: str):
    if not os.path.isfile(md_path):
        print(f"文件不存在: {md_path}")
        return

    md_dir = os.path.dirname(os.path.abspath(md_path))
    img_dir = os.path.join(md_dir, "img")
    os.makedirs(img_dir, exist_ok=True)

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    urls = collect_urls(content)
    if not urls:
        print(f"[{os.path.basename(md_path)}] 未发现需要处理的远程图片链接。")
        return

    used_names = set(os.listdir(img_dir))
    replacements = {}  # url -> 本地相对路径 (None 表示下载失败)
    print(f"[{os.path.basename(md_path)}] 发现 {len(urls)} 个远程图片链接：")

    for url in urls:
        filename = guess_filename(url, used_names)
        dest_path = os.path.join(img_dir, filename)
        print(f"  下载: {url}")
        if download(url, dest_path):
            replacements[url] = f"./img/{filename}"
            print(f"  ✓ 已保存为: img/{filename}")
        else:
            replacements[url] = None  # 下载失败则不替换

    def md_replace(match):
        alt, url = match.group(1), match.group(2)
        new_path = replacements.get(url)
        if new_path is None:
            return match.group(0)
        return f"![{alt}]({new_path})"

    def html_replace(match):
        prefix, url, suffix = match.group(1), match.group(2), match.group(3)
        new_path = replacements.get(url)
        if new_path is None:
            return match.group(0)
        return f"{prefix}{new_path}{suffix}"

    new_content = MD_IMG_PATTERN.sub(md_replace, content)
    new_content = HTML_IMG_PATTERN.sub(html_replace, new_content)

    if new_content != content:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[{os.path.basename(md_path)}] 已更新文件中的图片链接。\n")
    else:
        print(f"[{os.path.basename(md_path)}] 没有链接被替换（可能全部下载失败）。\n")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 fetch_md_images.py 文件1.md [文件2.md ...]")
        sys.exit(1)

    for path in sys.argv[1:]:
        process_md_file(path)


if __name__ == "__main__":
    main()