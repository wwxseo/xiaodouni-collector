import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 配置：精准关键词，避开实物豆子
QUERIES = ["小豆泥 cat", "小豆泥 funny bean", "小豆泥 漫画", "小豆泥 表情包", "小豆泥 动画"]
# 2. 配置：更强的过滤黑名单（避开流氓源和搜索 UI）
DOMAIN_BLACKLIST = [
    "bing.com/th", "bing.com/sa", "baidu.com", "weibo.com", 
    "sinaimg.cn", "zhimg.com", "csdnimg.cn", "so.com", "sogou.com"
]

def get_seen_urls():
    """【功能：历史去重】从 history.md 中提取原始抓取过的 URL"""
    seen = set()
    if os.path.exists("history.md"):
        with open("history.md", "r", encoding="utf-8") as f:
            content = f.read()
            # 提取代理链接中的原始链接部分 (url=... 之后的内容)
            urls = re.findall(r'url=(http[^"\'&\s]+)', content)
            for u in urls:
                seen.add(u)
    print(f"📜 记忆库加载完成: 已记录 {len(seen)} 张历史图片。")
    return seen

def wrap_proxy(url):
    """【功能：代理保护+防黑块】防盗链克星，强制裁剪并加白底"""
    # w=300&h=300&fit=cover: 强制裁剪为等大正方形
    # bg=white: 解决透明PNG背景变黑的问题
    return f"https://wsrv.nl/?url={url}&w=300&h=300&fit=cover&bg=white"

def is_valid(url, seen_urls, session_images):
    """【功能：多重去重+精准排除】排除黑名单、历史重复、本次重复"""
    if not url.startswith("http"): return False
    if any(bad in url for bad in DOMAIN_BLACKLIST): return False
    if url in seen_urls or url in session_images: return False
    # 过滤掉一些明显的 UI 图标或低质图源标志
    if any(x in url.lower() for x in ["/100/100", "avatar", "icon", "logo", "thumbnail"]): return False
    return True

# --- 三大引擎抓取函数 ---

def fetch_from_bing(query, seen_urls, session_images, needed):
    print(f"🔍 [Source: Bing] 搜索: {query}...")
    images = []
    url = f"https://www.bing.com/images/search?q={query}&safeSearch=Moderate"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # Bing 的图片地址藏在 murl 字段
        links = re.findall(r'"murl":"(.*?)"', resp.text)
        for link in links:
            if is_valid(link, seen_urls, session_images + images):
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def fetch_from_sogou(query, seen_urls, session_images, needed):
    print(f"🔍 [Source: Sogou] 搜索: {query}...")
    images = []
    url = f"https://pic.sogou.com/pics?query={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # 搜狗图片地址匹配
        links = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
        for link in links:
            if is_valid(link, seen_urls, session_images + images):
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def fetch_from_360(query, seen_urls, session_images, needed):
    print(f"🔍 [Source: 360] 搜索: {query}...")
    images = []
    url = f"https://image.so.com/i?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # 360图片地址匹配
        links = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
        for link in links:
            if is_valid(link, seen_urls, session_images + images):
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

# --- 主逻辑 ---

def get_all_images():
    seen = get_seen_urls()
    final_images = []
    
    # 1. 【功能：源顺序随机化】
    fetchers = [fetch_from_bing, fetch_from_sogou, fetch_from_360]
    random.shuffle(fetchers)
    
    # 2. 【功能：强制 12 张 & 极高容错性】
    # 即使一个引擎不行，也会自动切下一个，直到凑齐
    for fetcher in fetchers:
        current_needed = 12 - len(final_images)
        if current_needed <= 0: break
        
        # 每次从关键词库随机抽一个，增加多样性
        query = random.choice(QUERIES)
        new_batch = fetcher(query, seen, final_images, current_needed)
        final_images.extend(new_batch)
    
    print(f"🎯 本次任务共成功捕获 {len(final_images)} 张全新小豆泥。")
    # 3. 【功能：代理包装】统一处理防盗链和黑色块
    return [wrap_proxy(img) for img in final_images]

def update_files(urls):
    if not urls:
        print("❌ 未捕获到新图，跳过更新。")
        return

    # A. 更新 README.md (精准排版优化)
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    img_html = '<div align="center">\n'
    for url in urls:
        # 使用 160x160 统一网格布局
        img_html += f'  <img src="{url}" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🐱 三源联搜 & 智能裁剪代理，让可爱永不掉线</i></p>\n</div>'

    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    replacement = f"<!-- START_SECTION:xiaodouni -->\n{img_html}\n<!-- END_SECTION:xiaodouni -->"
    
    if "<!-- START_SECTION:xiaodouni -->" in content:
        new_readme = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_readme)

    # B. 更新 history.md (归档保存)
    today = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists("history.md"):
        with open("history.md", "w", encoding="utf-8") as f:
            f.write("# 📚 小豆泥历史收藏馆\n\n---\n")
            
    with open("history.md", "a", encoding="utf-8") as f:
        f.write(f"\n### 📅 {today}\n<div align='left'>\n")
        for url in urls:
            f.write(f'  <img src="{url}" width="100" height="100" style="margin:2px; border-radius:6px; object-fit:cover;">\n')
        f.write("</div>\n\n---\n")
    print("✨ 任务成功！README 与 history.md 已同步。")

if __name__ == "__main__":
    imgs = get_all_images()
    update_files(imgs)
