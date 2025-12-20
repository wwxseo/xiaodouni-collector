import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 精准搜索词库
QUERIES = ["小豆泥 cat", "小豆泥 funny bean", "小豆泥 漫画", "小豆泥 表情包", "小豆泥 funnybean"]

# 2. 严格黑名单：绝对禁止包含搜索平台自身的任何链接
ENGINE_DOMAINS = ["bing.com", "sogou.com", "so.com", "qhimg.com", "qhimgs.com", "baidu.com"]
DOMAIN_BLACKLIST = ["weibo.com", "sinaimg.cn", "zhimg.com", "csdnimg.cn", "127.net"]

def get_seen_urls():
    """从历史记录中提取已抓取的原始URL"""
    seen = set()
    if os.path.exists("history.md"):
        with open("history.md", "r", encoding="utf-8") as f:
            content = f.read()
            urls = re.findall(r'url=(http[^"\'&\s]+)', content)
            for u in urls:
                seen.add(u)
    print(f"📜 记忆库已加载: {len(seen)} 张历史图片。")
    return seen

def wrap_proxy(url):
    """防盗链代理 + 强制正方形裁剪 + 白底修复"""
    return f"https://wsrv.nl/?url={url}&w=300&h=300&fit=cover&bg=white"

def is_valid(url, seen_urls, session_images):
    """【核心修正】极其严格的过滤逻辑"""
    url_lower = url.lower()
    # 必须是 http 开头
    if not url.startswith("http"): return False
    # 绝对禁止搜索引擎自家的素材（彻底解决抓到 Bing Logo 的问题）
    if any(engine in url_lower for engine in ENGINE_DOMAINS): return False
    # 排除已知坏图域名
    if any(bad in url_lower for bad in DOMAIN_BLACKLIST): return False
    # 排除已抓取的重复图
    if url in seen_urls or url in session_images: return False
    # 排除常见的 UI 元素关键词
    if any(x in url_lower for x in ["logo", "icon", "avatar", "sign", "symbol", "loading"]): return False
    return True

# --- 增强版三大引擎抓取 ---

def fetch_from_bing(query, seen_urls, session_images, needed):
    print(f"🔍 [Bing] 正在搜寻: {query}")
    images = []
    # 随机偏移，避开前几个可能存在的固定图标
    first = random.randint(1, 10)
    url = f"https://www.bing.com/images/search?q={query}&first={first}&safeSearch=Moderate"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # 提取 murl 属性
        links = re.findall(r'"murl":"(.*?)"', resp.text)
        for link in links:
            if is_valid(link, seen_urls, session_images + images):
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def fetch_from_sogou(query, seen_urls, session_images, needed):
    print(f"🔍 [Sogou] 正在搜寻: {query}")
    images = []
    url = f"https://pic.sogou.com/pics?query={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # 解析搜狗 JSON 格式中的图片链接
        links = re.findall(r'"thumbUrl":"(http[^"]+)"', resp.text)
        if not links:
            links = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
        for link in links:
            if is_valid(link, seen_urls, session_images + images):
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def fetch_from_360(query, seen_urls, session_images, needed):
    print(f"🔍 [360] 正在搜寻: {query}")
    images = []
    url = f"https://image.so.com/i?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # 解析 360 图片链接
        links = re.findall(r'"img":"(http[^"]+)"', resp.text)
        if not links:
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
    
    # 随机打乱源顺序
    fetchers = [fetch_from_bing, fetch_from_sogou, fetch_from_360]
    random.shuffle(fetchers)
    
    # 循环尝试，直到凑够 12 张
    for fetcher in fetchers:
        needed = 12 - len(final_images)
        if needed <= 0: break
        
        query = random.choice(QUERIES)
        new_batch = fetcher(query, seen, final_images, needed)
        final_images.extend(new_batch)
    
    # 如果三大引擎一轮下来还没凑够，换个词再来一轮（保底机制）
    if len(final_images) < 12:
        print("💡 正在尝试第二轮深度搜索以凑齐 12 张...")
        for q in random.sample(QUERIES, len(QUERIES)):
            if len(final_images) >= 12: break
            final_images.extend(fetch_from_bing(q, seen, final_images, 12 - len(final_images)))

    print(f"🎯 本次任务共捕获 {len(final_images)} 张纯净小豆泥图。")
    return [wrap_proxy(img) for img in final_images]

def update_files(urls):
    if not urls:
        print("❌ 未捕获到新图，跳过。")
        return

    # A. 更新 README.md
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🐱 三源联搜 + 智能去噪代理，让可爱永不重复</i></p>\n</div>'

    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    replacement = f"<!-- START_SECTION:xiaodouni -->\n{img_html}\n<!-- END_SECTION:xiaodouni -->"
    
    new_readme = re.sub(pattern, replacement, content, flags=re.DOTALL) if "<!-- START_SECTION:xiaodouni -->" in content else content + "\n\n" + replacement
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)

    # B. 更新 history.md
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
