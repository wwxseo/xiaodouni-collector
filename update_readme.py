import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

# 更加精准的搜索词，增加 cat 关键词防止搜到豆子
QUERIES = ["小豆泥 cat", "小豆泥 漫画", "funny bean cat", "小豆泥 表情包", "小豆泥 wallpaper"]
# 域名黑名单：排除搜索引擎自家的 Logo 和已知的坏源
BLACKLIST = ["bing.com/th", "bing.com/sa", "sogou.com", "so.com", "baidu.com", "weibo.com", "sinaimg.cn"]

def get_seen_urls():
    seen = set()
    if os.path.exists("history.md"):
        with open("history.md", "r", encoding="utf-8") as f:
            # 提取所有 http 链接，忽略代理前缀
            urls = re.findall(r'url=(http[^"\'&\s]+)', f.read())
            for u in urls:
                seen.add(u)
    return seen

def wrap_proxy(url):
    """防盗链+裁剪+强制白底"""
    return f"https://wsrv.nl/?url={url}&w=300&h=300&fit=cover&bg=white"

def fetch_images(query, seen_urls, session_images, needed):
    print(f"🔍 正在搜寻: {query}...")
    found = []
    # 使用 Bing 搜索
    url = f"https://www.bing.com/images/search?q={query}&safeSearch=Moderate"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # 用正则抓取 murl (原始图片地址)
        links = re.findall(r'"murl":"(.*?)"', resp.text)
        
        for link in links:
            # 过滤黑名单、重复项、以及 Bing 自己的 UI 图标
            if not link.startswith("http"): continue
            if any(b in link for b in BLACKLIST): continue
            if link in seen_urls or link in session_images or link in found: continue
            
            found.append(link)
            if len(found) >= needed: break
    except Exception as e:
        print(f"⚠️ 抓取出错: {e}")
        
    return found

def get_all_images():
    seen = get_seen_urls()
    final_images = []
    
    # 随机打乱关键词，增加新鲜度
    random.shuffle(QUERIES)
    
    for q in QUERIES:
        needed = 12 - len(final_images)
        if needed <= 0: break
        
        batch = fetch_images(q, seen, final_images, needed)
        final_images.extend(batch)
    
    print(f"🎯 本次任务共抓取到 {len(final_images)} 张新图")
    return [wrap_proxy(img) for img in final_images]

def update_files(urls):
    if not urls: 
        print("❌ 没搜到图，不更新。")
        return
        
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 构建 3x4 或 4x3 的精美网格
    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🐱 每日自动搜集高清小豆泥，排版已优化</i></p>\n</div>'

    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    replacement = f"<!-- START_SECTION:xiaodouni -->\n{img_html}\n<!-- END_SECTION:xiaodouni -->"
    
    if "<!-- START_SECTION:xiaodouni -->" in content:
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
            f.write(f'  <img src="{url}" width="100" height="100" style="margin:2px; border-radius:6px; object-fit:cover;">\n')
        f.write("</div>\n\n---\n")

if __name__ == "__main__":
    imgs = get_all_images()
    update_files(imgs)
