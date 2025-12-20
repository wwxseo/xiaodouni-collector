import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

# 精准关键词，避开实物豆子
QUERIES = ["小豆泥 漫画", "小豆泥 表情包", "小豆泥 funny bean cat", "小豆泥 动画", "小豆泥 动态图"]
DOMAIN_BLACKLIST = ["baidu.com", "weibo.com", "sinaimg.cn", "zhimg.com", "csdnimg.cn", "funnybean.com"]

def get_seen_urls():
    seen = set()
    if os.path.exists("history.md"):
        with open("history.md", "r", encoding="utf-8") as f:
            urls = re.findall(r'url=(http[^"\'&\s]+)', f.read())
            for u in urls:
                seen.add(u)
    return seen

def wrap_proxy(url):
    """使用代理并强制缩放裁剪成正方形，让排版极度整齐"""
    # w=200&h=200&fit=cover: 强制裁剪成 200x200 的正方形
    return f"https://wsrv.nl/?url={url}&w=200&h=200&fit=cover&bg=white"

def is_valid_image(url, seen_urls, session_images):
    """验证图片是否真的存在，且不是坏图"""
    if not url.startswith("http"): return False
    if any(bad in url for bad in DOMAIN_BLACKLIST): return False
    if url in seen_urls or url in session_images: return False
    
    try:
        # 发送一个 HEAD 请求，只检查链接是否有效，不下载图片，速度极快
        res = requests.head(url, timeout=3, allow_redirects=True)
        if res.status_code == 200 and int(res.headers.get('Content-Length', 0)) > 5000:
            return True
    except:
        return False
    return False

def fetch_images(query, seen_urls, session_images, needed):
    print(f"🔍 正在从多源搜寻 '{query}'...")
    images = []
    # 轮流尝试 Bing 和 360
    urls = [
        f"https://www.bing.com/images/search?q={query}&form=HDRSC3",
        f"https://image.so.com/i?q={query}"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            # 兼容 Bing 的匹配
            murls = re.findall(r'"murl":"(.*?)"', resp.text)
            # 兼容 360/搜狗 的匹配
            others = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
            
            for link in (murls + others):
                if is_valid_image(link, seen_urls, session_images + images):
                    images.append(link)
                    print(f"✅ 找到一张有效新图: {link[:50]}...")
                if len(images) >= needed: return images
        except: continue
    return images

def get_all_images():
    seen = get_seen_urls()
    final_images = []
    
    # 尝试多次，直到凑满 12 张
    attempts = 0
    while len(final_images) < 12 and attempts < 5:
        query = random.choice(QUERIES)
        needed = 12 - len(final_images)
        batch = fetch_images(query, seen, final_images, needed)
        final_images.extend(batch)
        attempts += 1
    
    return [wrap_proxy(img) for img in final_images]

def update_files(urls):
    if not urls: return
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 强制正方形网格排版
    img_html = '<div align="center">\n'
    for url in urls:
        # 移除了换行，增加等高宽控制
        img_html += f'  <img src="{url}" width="160" height="160" alt="小豆泥" style="margin:2px; border-radius:8px; object-fit:cover;">'
    img_html += '\n  <p><i>🔄 智能过滤 & 自动裁剪，每日发现高清小豆泥</i></p>\n</div>'

    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    replacement = f"<!-- START_SECTION:xiaodouni -->\n{img_html}\n<!-- END_SECTION:xiaodouni -->"
    new_readme = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)

    # 更新 history.md
    today = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists("history.md"):
        with open("history.md", "w", encoding="utf-8") as f:
            f.write("# 📚 小豆泥历史收藏馆\n\n---\n")
            
    with open("history.md", "a", encoding="utf-8") as f:
        f.write(f"\n### 📅 {today}\n<div align='left'>\n")
        for url in urls:
            f.write(f'  <img src="{url}" width="100" height="100" style="margin:2px; border-radius:5px; object-fit:cover;">\n')
        f.write("</div>\n\n---\n")

if __name__ == "__main__":
    imgs = get_all_images()
    update_files(imgs)
