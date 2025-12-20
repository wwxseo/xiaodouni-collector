import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

# 搜索关键词列表，增加多样性
QUERIES = ["小豆泥 高清", "小豆泥 壁纸", "小豆泥 funny bean", "小豆泥 插画"]

def get_seen_urls():
    """从 history.md 加载已见过的图片"""
    seen = set()
    if os.path.exists("history.md"):
        with open("history.md", "r", encoding="utf-8") as f:
            urls = re.findall(r'src="(.*?)"', f.read())
            for u in urls:
                seen.add(u)
    print(f"📜 记忆库已加载: {len(seen)} 张历史图片。")
    return seen

def fetch_from_bing(query, seen_urls, needed):
    """从 Bing 抓取"""
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
                    if link not in seen_urls:
                        images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def fetch_from_sogou(query, seen_urls, needed):
    """从 搜狗 抓取"""
    print(f"🔍 搜狗图片搜索: {query}...")
    images = []
    url = f"https://pic.sogou.com/pics?query={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        # 搜狗的图片地址通常直接在页面文本中以 URL 形式存在
        all_urls = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png|gif)', resp.text)
        for link in all_urls:
            if "sogou.com" not in link and link not in seen_urls:
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def fetch_from_360(query, seen_urls, needed):
    """从 360图片 抓取"""
    print(f"🔍 360图片搜索: {query}...")
    images = []
    url = f"https://image.so.com/i?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        all_urls = re.findall(r'https?://[^"\'\s]+\.(?:jpg|jpeg|png|gif)', resp.text)
        for link in all_urls:
            if "so.com" not in link and "qhimg.com" not in link and link not in seen_urls:
                images.append(link)
            if len(images) >= needed: break
    except: pass
    return images

def get_all_images():
    seen = get_seen_urls()
    final_images = []
    
    # 定义抓取函数列表
    fetchers = [fetch_from_bing, fetch_from_sogou, fetch_from_360]
    random.shuffle(fetchers) # 随机化来源顺序，每天的主力图源都不一样
    
    for fetcher in fetchers:
        needed = 12 - len(final_images)
        if needed <= 0: break
        
        query = random.choice(QUERIES)
        new_batch = fetcher(query, seen, needed)
        final_images.extend(new_batch)
        print(f"✅ 从当前源获取了 {len(new_batch)} 张新图")

    return final_images

def update_files(urls):
    if not urls:
        print("⚠️ 没有任何新图，跳过更新。")
        return

    # 1. 更新 README.md
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="180" alt="小豆泥" style="margin:5px; border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🔄 多源随机发现，让可爱永不重复</i></p>\n</div>'

    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    replacement = f"<!-- START_SECTION:xiaodouni -->\n{img_html}\n<!-- END_SECTION:xiaodouni -->"
    
    if "<!-- START_SECTION:xiaodouni -->" in content:
        new_readme = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        new_readme = content + "\n\n" + replacement
        
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
