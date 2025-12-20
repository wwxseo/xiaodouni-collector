import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote  # <--- 关键引入：用于给链接打包

# --- 1. 配置区域 ---
QUERIES = ["小豆泥 cat", "小豆泥 funny bean", "小豆泥 漫画", "小豆泥 表情包", "小豆泥 动画"]

# 黑名单：过滤掉容易坏的图源
ENGINE_DOMAINS = ["bing.com", "sogou.com", "so.com", "qhimg.com", "qhimgs.com", "baidu.com"]
DOMAIN_BLACKLIST = ["weibo.com", "sinaimg.cn", "zhimg.com", "csdnimg.cn", "127.net"]

# --- 2. 工具函数 ---

def clean_url(url):
    """清洗 URL 中的转义字符"""
    if not url: return ""
    # 修复 JSON 转义
    url = url.replace(r'\/', '/')
    # 修复 unicode 编码
    try:
        url = url.encode('utf-8').decode('unicode_escape')
    except:
        pass
    # 修复 HTML 实体
    url = url.replace('&amp;', '&')
    return url

def wrap_proxy(url):
    """【修复核心】对 URL 进行编码，防止参数丢失导致 Not Found"""
    clean = clean_url(url)
    # quote 将链接中的 & ? 等符号转义，确保代理服务器能读懂完整链接
    encoded_url = quote(clean, safe='')
    # output=jpg: 强制转换为 jpg 格式，兼容性最好
    return f"https://wsrv.nl/?url={encoded_url}&w=300&h=300&fit=cover&bg=white&output=jpg"

def is_valid(url, seen_urls, session_images):
    """过滤器"""
    if not url: return False
    url_lower = url.lower()
    
    if not url.startswith("http"): return False
    # 必须是常见图片格式，避开奇怪的动态脚本
    if not any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', 'webp']): 
        # 有些图床链接不带后缀，如果是 bing/搜狗 搜出来的通常没问题，放宽一点
        if 'http' not in url_lower[4:]: # 简单检查是不是正常的 url
            pass
        else:
            return False

    if any(engine in url_lower for engine in ENGINE_DOMAINS): return False
    if any(bad in url_lower for bad in DOMAIN_BLACKLIST): return False
    if url in seen_urls or url in session_images: return False
    if any(x in url_lower for x in ["logo", "icon", "avatar", "sign", "symbol", "loading"]): return False
    
    return True

# --- 3. 抓取逻辑 ---

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
            link = clean_url(link)
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
            link = clean_url(link)
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
            link = clean_url(link)
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
    
    # 补货机制
    if len(final_images) < 12:
        print("💡 补货模式...")
        for q in QUERIES:
            if len(final_images) >= 12: break
            final_images.extend(fetch_f
