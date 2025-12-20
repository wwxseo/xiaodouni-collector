import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

# 搜索关键词
QUERIES = ["小豆泥 高清", "小豆泥 wallpaper", "小豆泥 funny bean", "小豆泥 插画"]
# 域名黑名单：这些网站的图极其容易裂开，即便有代理也难救，直接跳过
DOMAIN_BLACKLIST = ["baidu.com", "weibo.com", "sinaimg.cn", "zhimg.com", "csdnimg.cn"]

def get_seen_urls():
    seen = set()
    if os.path.exists("history.md"):
        with open("history.md", "r", encoding="utf-8") as f:
            # 提取原始链接，排除代理前缀
            urls = re.findall(r'url=(http[^"\'&\s]+)', f.read())
            for u in urls:
                seen.add(u)
    print(f"📜 记忆库已加载: {len(seen)} 张历史图片。")
    return seen

def wrap_proxy(url):
    """使用 wsrv.nl 代理图片，绕过防盗链，强制转换格式并添加白色背景"""
    # &bg=white: 处理透明PNG变黑的问题
    # &we: 绕过某些防盗链错误
    return f"https://wsrv.nl/?url={url}&bg=white"

def is_valid(url, seen_urls):
    """检查图片链接是否有效且不在黑名单"""
    if not url.startswith("http"): return False
    if url in seen_urls: return False
    if any(bad in url for bad in DOMAIN_BLACKLIST): return False
    # 过滤掉一些明显的表情包小图链接
    if any(x in url.lower() for x in ["/100/100", "avatar", "icon"]): return False
    return True

def fetch_from_bing(query, seen_urls, needed):
    print(f"🔍 Bing 搜索: {query}...")
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
                    if is_valid(link, seen_urls):
                        images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def fetch_from_sogou(query, seen_urls, needed):
    print(f"🔍 搜狗图片搜索: {query}...")
    images = []
    url = f"https://pic.sogou.com/pics?query={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        all_urls = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
        for link in all_urls:
            if "sogou.com" not in link and is_valid(link, seen_urls):
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def get_all_images():
    seen = get_seen_urls()
    final_images = []
    fetchers = [fetch_from_bing, fetch_from_sogou]
    random.shuffle(fetchers)
    
    for fetcher in fetchers:
        needed = 12 - len(final_images)
        if needed <= 0: break
        query = random.choice(QUERIES)
        new_batch = fetcher(query, seen, needed)
        final_images.extend(new_batch)
    
    # 将抓到的原始链接全部包装上代理
    proxied_images = [wrap_proxy(img) for img in final_images]
    print(f"✅ 最终获取了 {len(proxied_images)} 张通过代理包装的新图")
    return proxied_images

def update_files(urls):
    if not urls: return
    # 1. 更新 README.md
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="180" alt="小豆泥" style="margin:5px; border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🔄 智能代理加速中，让可爱永不掉线</i></p>\n</div>'

    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    replacement = f"<!-- START_SECTION:xiaodouni -->\n{img_html}\n<!-- END_SECTION:xiaodouni -->"
    new_readme = re.sub(pattern, replacement, content, flags=re.DOTALL) if "<!-- START_SECTION:xiaodouni -->" in content else content + "\n\n" + replacement
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)

    # 2. 更新 history.md
    today = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists("history.md"):
        with open("history.md", "w", encoding="utf-8") as f:
            f.write("# 📚 小豆泥历史收藏馆\n\n---\n")
            
    with open("history.md", "a", encoding="utf-8") as f:
        f.write(f"\n### 📅 {today}\n<div align='left'>\n")
        for url in urls:
            f.write(f'  <img src="{url}" width="120" style="margin:2px; border-radius:5px;">\n')
        f.write("</div>\n\n---\n")

if __name__ == "__main__":
    imgs = get_all_images()
    update_files(imgs)
