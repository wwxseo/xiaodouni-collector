import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

# --- 1. 配置区域 ---

# 关键词：加上 cat/comic 确保搜到猫
QUERIES = ["小豆泥 cat", "小豆泥 funny bean", "小豆泥 漫画", "小豆泥 表情包", "小豆泥 动画"]

# 严格黑名单
ENGINE_DOMAINS = ["bing.com", "sogou.com", "so.com", "qhimg.com", "qhimgs.com", "baidu.com"]
DOMAIN_BLACKLIST = ["weibo.com", "sinaimg.cn", "zhimg.com", "csdnimg.cn", "127.net"]

# --- 2. 工具函数 ---

def clean_url(url):
    """【关键修复】清洗 URL 中的转义字符"""
    if not url: return ""
    # 修复 JSON 中的转义斜杠 https:\/\/ -> https://
    url = url.replace(r'\/', '/')
    # 修复 unicode 转义符
    url = url.encode('utf-8').decode('unicode_escape')
    # 修复 HTML 实体
    url = url.replace('&amp;', '&')
    return url

def get_seen_urls():
    """从历史记录提取 URL，用于去重"""
    seen = set()
    if os.path.exists("history.md"):
        try:
            with open("history.md", "r", encoding="utf-8") as f:
                content = f.read()
                urls = re.findall(r'url=(http[^"\'&\s]+)', content)
                for u in urls:
                    seen.add(u)
        except Exception:
            pass
    print(f"📜 记忆库加载: {len(seen)} 张历史图片。")
    return seen

def wrap_proxy(url):
    """防盗链代理 + 强制正方形 + 白底"""
    return f"https://wsrv.nl/?url={url}&w=300&h=300&fit=cover&bg=white"

def is_valid(url, seen_urls, session_images):
    """过滤器"""
    if not url: return False
    url_lower = url.lower()
    
    if not url.startswith("http"): return False
    if any(engine in url_lower for engine in ENGINE_DOMAINS): return False
    if any(bad in url_lower for bad in DOMAIN_BLACKLIST): return False
    if url in seen_urls or url in session_images: return False
    if any(x in url_lower for x in ["logo", "icon", "avatar", "sign", "symbol", "loading", "gif"]): return False
    
    return True

# --- 3. 抓取逻辑 (三源) ---

def fetch_from_bing(query, seen_urls, session_images, needed):
    print(f"🔍 [Bing] 搜: {query}")
    images = []
    first = random.randint(1, 10)
    url = f"https://www.bing.com/images/search?q={query}&first={first}&safeSearch=Moderate"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        links = re.findall(r'"murl":"(.*?)"', resp.text)
        for link in links:
            link = clean_url(link) # 清洗
            if is_valid(link, seen_urls, session_images + images):
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def fetch_from_sogou(query, seen_urls, session_images, needed):
    print(f"🔍 [Sogou] 搜: {query}")
    images = []
    url = f"https://pic.sogou.com/pics?query={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        links = re.findall(r'"thumbUrl":"(http[^"]+)"', resp.text)
        if not links:
            links = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
        for link in links:
            link = clean_url(link) # 清洗
            if is_valid(link, seen_urls, session_images + images):
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def fetch_from_360(query, seen_urls, session_images, needed):
    print(f"🔍 [360] 搜: {query}")
    images = []
    url = f"https://image.so.com/i?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        links = re.findall(r'"img":"(http[^"]+)"', resp.text)
        if not links:
            links = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
        for link in links:
            link = clean_url(link) # 清洗
            if is_valid(link, seen_urls, session_images + images):
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

# --- 4. 主流程 ---

def get_all_images():
    seen = get_seen_urls()
    final_images = []
    fetchers = [fetch_from_bing, fetch_from_sogou, fetch_from_360]
    random.shuffle(fetchers)
    
    for fetcher in fetchers:
        needed = 12 - len(final_images)
        if needed <= 0: break
        query = random.choice(QUERIES)
        new_batch = fetcher(query, seen, final_images, needed)
        final_images.extend(new_batch)
    
    if len(final_images) < 12:
        print("💡 补货模式...")
        for q in QUERIES:
            if len(final_images) >= 12: break
            final_images.extend(fetch_from_bing(q, seen, final_images, 12 - len(final_images)))

    print(f"🎯 本次捕获 {len(final_images)} 张图片")
    return [wrap_proxy(img) for img in final_images]

def update_files(urls):
    if not urls:
        print("❌ 无图，结束。")
        return

    # 构建 HTML
    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🐱 每日随机三源搜罗，只选高清猫猫头</i></p>\n</div>'

    # 使用字符串拼接模式更新 README
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
            
        start_marker = "<!-- START_SECTION:xiaodouni -->"
        end_marker = "<!-- END_SECTION:xiaodouni -->"
        
        if start_marker in content and end_marker in content:
            start_idx = content.find(start_marker) + len(start_marker)
            end_idx = content.find(end_marker)
            new_content = content[:start_idx] + "\n" + img_html + "\n" + content[end_idx:]
            
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(new_content)
            print("✅ README 更新成功")
        else:
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(f"# 小豆泥收集器\n\n{start_marker}\n{img_html}\n{end_marker}")

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
    print("✅ History 归档成功")

if __name__ == "__main__":
    imgs = get_all_images()
    update_files(imgs)
