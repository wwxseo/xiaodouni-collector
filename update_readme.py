import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote

# --- 1. 配置区域 ---
QUERIES = ["小豆泥 cat", "小豆泥 funny bean", "小豆泥 漫画", "小豆泥 表情包", "小豆泥 动画"]

# 严格黑名单
ENGINE_DOMAINS = ["bing.com", "sogou.com", "so.com", "qhimg.com", "qhimgs.com", "baidu.com"]
DOMAIN_BLACKLIST = ["weibo.com", "sinaimg.cn", "zhimg.com", "csdnimg.cn", "127.net"]

# --- 2. 工具函数 ---

def clean_url(url):
    """清洗 URL"""
    if not url: return ""
    url = url.replace(r'\/', '/')
    try:
        url = url.encode('utf-8').decode('unicode_escape')
    except:
        pass
    url = url.replace('&amp;', '&')
    return url

def wrap_proxy(url):
    """生成代理链接"""
    clean = clean_url(url)
    encoded_url = quote(clean, safe='')
    # 使用 images.weserv.nl (wsrv.nl 的全称域名，有时更稳定)
    # output=jpg 统一格式，w=300&h=300&fit=cover 统一排版
    return f"https://images.weserv.nl/?url={encoded_url}&w=300&h=300&fit=cover&bg=white&output=jpg"

def check_image_availability(proxy_url):
    """【核心修复】质检员：亲自验证图片能不能打开"""
    try:
        # 设置 3 秒超时，模拟浏览器访问
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(proxy_url, headers=headers, timeout=3)
        if resp.status_code == 200:
            return True
        else:
            print(f"⚠️ 图片无效 (状态码 {resp.status_code}): {proxy_url[:50]}...")
            return False
    except Exception:
        print(f"⚠️ 图片连接超时/错误: {proxy_url[:50]}...")
        return False

def is_valid_basic(url, seen_urls, session_images):
    """基础过滤器（不联网）"""
    if not url: return False
    url_lower = url.lower()
    if not url.startswith("http"): return False
    
    if any(engine in url_lower for engine in ENGINE_DOMAINS): return False
    if any(bad in url_lower for bad in DOMAIN_BLACKLIST): return False
    if url in seen_urls or url in session_images: return False
    if any(x in url_lower for x in ["logo", "icon", "avatar", "sign", "symbol", "loading", "gif"]): return False
    
    return True

def get_seen_urls():
    seen = set()
    if os.path.exists("history.md"):
        try:
            with open("history.md", "r", encoding="utf-8") as f:
                content = f.read()
                # 提取 encoded 的 url 参数，避免解码错误
                matches = re.findall(r'url=([^&"\s]+)', content)
                for m in matches:
                    # 简单记录特征即可，不需要完美解码
                    seen.add(m)
        except Exception:
            pass
    return seen

# --- 3. 抓取逻辑 ---

def fetch_images(engine_name, url_template, regex_pattern, query, seen_urls, session_images, needed):
    print(f"🔍 [{engine_name}] 搜: {query}")
    images = []
    
    # 随机偏移
    search_url = url_template.format(query=query, random_first=random.randint(1, 5))
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        resp = requests.get(search_url, headers=headers, timeout=10)
        links = re.findall(regex_pattern, resp.text)
        
        for link in links:
            link = clean_url(link)
            
            # 1. 基础检查
            if not is_valid_basic(link, seen_urls, session_images + images):
                continue
            
            # 2. 生成代理链接
            proxy_link = wrap_proxy(link)
            
            # 3. 【质检】联网验证！只有能打开的才收录
            if check_image_availability(proxy_link):
                print(f"✅ 有效: {link[:30]}...")
                images.append(link) # 存原始链接避免重复
            
            if len(images) >= needed: break
            
    except Exception as e:
        print(f"❌ {engine_name} 错误: {e}")
        pass
    
    return images

# --- 4. 主流程 ---

def get_all_images():
    seen = get_seen_urls()
    final_raw_links = [] # 存原始链接用于去重
    
    # 定义引擎
    engines = [
        ("Bing", "https://www.bing.com/images/search?q={query}&first={random_first}&safeSearch=Moderate", r'"murl":"(.*?)"'),
        ("Sogou", "https://pic.sogou.com/pics?query={query}", r'"thumbUrl":"(http[^"]+)"'),
        ("360", "https://image.so.com/i?q={query}", r'"img":"(http[^"]+)"')
    ]
    random.shuffle(engines)
    
    for name, url_tmpl, pattern in engines:
        needed = 12 - len(final_raw_links)
        if needed <= 0: break
        
        query = random.choice(QUERIES)
        # 注意：这里直接把验证通过的图加进来
        new_batch = fetch_images(name, url_tmpl, pattern, query, seen, final_raw_links, needed)
        final_raw_links.extend(new_batch)
    
    # 补货
    if len(final_raw_links) < 12:
        print("💡 补货模式...")
        for q in QUERIES:
            if len(final_raw_links) >= 12: break
            # 默认用 Bing 补货
            new_batch = fetch_images("Bing", engines[0][1], engines[0][2], q, seen, final_raw_links, 12 - len(final_raw_links))
            final_raw_links.extend(new_batch)

    print(f"🎯 本次最终捕获 {len(final_raw_links)} 张有效图片")
    # 最后统一转为代理链接
    return [wrap_proxy(url) for url in final_raw_links]

def update_files(urls):
    if not urls:
        print("❌ 无有效图片，跳过更新。")
        return

    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🐱 每日随机三源搜罗，只选高清猫猫头</i></p>\n</div>'

    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        marker_start = "<!-- START_SECTION:xiaodouni -->"
        marker_end = "<!-- END_SECTION:xiaodouni -->"
        
        if marker_start in content and marker_end in content:
            s = content.find(marker_start) + len(marker_start)
            e = content.find(marker_end)
            new_content = content[:s] + "\n" + img_html + "\n" + content[e:]
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(new_content)
        else:
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(f"# 小豆泥收集器\n\n{marker_start}\n{img_html}\n{marker_end}")
        print("✅ README 更新成功")

    today = datetime.now().strftime("%Y-%m-%d")
    mode = "a" if os.path.exists("history.md") else "w"
    with open("history.md", mode, encoding="utf-8") as f:
        if mode == "w": f.write("# 📚 小豆泥历史收藏馆\n\n---\n")
        f.write(f"\n### 📅 {today}\n<div align='left'>\n")
        for url in urls:
            f.write(f'  <img src="{url}" width="100" height="100" style="margin:2px; border-radius:6px; object-fit:cover;">\n')
        f.write("</div>\n\n---\n")
    print("✅ History 归档成功")

if __name__ == "__main__":
    imgs = get_all_images()
    update_files(imgs)
