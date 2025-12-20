import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

# 配置
QUERIES = ["小豆泥 高清", "小豆泥 wallpaper", "小豆泥 funny bean", "小豆泥 插画", "小豆泥 萌"]
DOMAIN_BLACKLIST = ["baidu.com", "weibo.com", "sinaimg.cn", "zhimg.com", "csdnimg.cn"]

def get_seen_urls():
    """从 history.md 中提取原始抓取过的 URL，实现永久记忆去重"""
    seen = set()
    if os.path.exists("history.md"):
        with open("history.md", "r", encoding="utf-8") as f:
            content = f.read()
            # 提取代理链接中的原始链接部分
            urls = re.findall(r'url=(http[^"\'&\s]+)', content)
            for u in urls:
                seen.add(u)
    print(f"📜 记忆库加载完成: 已记录 {len(seen)} 张历史图片。")
    return seen

def wrap_proxy(url):
    """防盗链克星：通过代理访问图片，强制白底并压缩"""
    return f"https://wsrv.nl/?url={url}&bg=white"

def is_valid(url, seen_urls, session_images):
    """多重过滤：链接合法性、黑名单、历史重复、本次任务重复"""
    if not url.startswith("http"): return False
    if any(bad in url for bad in DOMAIN_BLACKLIST): return False
    if url in seen_urls or url in session_images: return False
    if any(x in url.lower() for x in ["/100/100", "avatar", "icon", "thumbnail"]): return False
    return True

# --- 三大引擎抓取函数 ---

def fetch_from_bing(query, seen_urls, session_images, needed):
    print(f"🔍 [Source: Bing] 搜索: {query}...")
    images = []
    url = f"https://www.bing.com/images/search?q={query}&qft=+filterui:imagesize-large&form=IRFLTR"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all("a", class_="iusc"):
            m = a.get("m")
            if m:
                murl = re.search(r'"murl":"(.*?)"', m)
                if murl:
                    link = murl.group(1)
                    if is_valid(link, seen_urls, session_images + images):
                        images.append(link)
            if len(images) >= needed: break
    except Exception as e: print(f"⚠️ Bing 异常: {e}")
    return images

def fetch_from_sogou(query, seen_urls, session_images, needed):
    print(f"🔍 [Source: Sogou] 搜索: {query}...")
    images = []
    url = f"https://pic.sogou.com/pics?query={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        all_urls = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
        for link in all_urls:
            if "sogou.com" not in link and is_valid(link, seen_urls, session_images + images):
                images.append(link)
            if len(images) >= needed: break
    except Exception as e: print(f"⚠️ Sogou 异常: {e}")
    return images

def fetch_from_360(query, seen_urls, session_images, needed):
    print(f"🔍 [Source: 360] 搜索: {query}...")
    images = []
    url = f"https://image.so.com/i?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # 360的图片地址通常也在页面文本中
        all_urls = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
        for link in all_urls:
            if not any(x in link for x in ["so.com", "qhimg.com"]) and is_valid(link, seen_urls, session_images + images):
                images.append(link)
            if len(images) >= needed: break
    except Exception as e: print(f"⚠️ 360 异常: {e}")
    return images

# --- 主逻辑 ---

def get_all_images():
    seen = get_seen_urls()
    final_images = []
    
    # 1. 引擎列表 & 随机排序 (源顺序随机化)
    fetchers = [fetch_from_bing, fetch_from_sogou, fetch_from_360]
    random.shuffle(fetchers)
    
    # 2. 依次尝试 (极高容错性)
    for fetcher in fetchers:
        needed = 12 - len(final_images)
        if needed <= 0: break
        
        # 随机选一个词
        query = random.choice(QUERIES)
        new_batch = fetcher(query, seen, final_images, needed)
        final_images.extend(new_batch)
        print(f"✅ 当前引擎贡献了 {len(new_batch)} 张图")

    # 3. 统一使用代理包装 (解决裂图 & 黑块)
    return [wrap_proxy(img) for img in final_images]

def update_files(urls):
    if not urls:
        print("⚠️ 没搜到新图，今日暂不更新。")
        return

    # 更新 README.md
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="180" alt="小豆泥" style="margin:5px; border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🔄 三源联搜 & 智能代理加速，每日发现新惊喜</i></p>\n</div>'

    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    replacement = f"<!-- START_SECTION:xiaodouni -->\n{img_html}\n<!-- END_SECTION:xiaodouni -->"
    new_readme = re.sub(pattern, replacement, content, flags=re.DOTALL) if "<!-- START_SECTION:xiaodouni -->" in content else content + "\n\n" + replacement
    
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
            f.write(f'  <img src="{url}" width="120" style="margin:2px; border-radius:5px;">\n')
        f.write("</div>\n\n---\n")
    print(f"✨ 任务完成：更新了 README 并归档了 {len(urls)} 张新图。")

if __name__ == "__main__":
    imgs = get_all_images()
    update_files(imgs)
