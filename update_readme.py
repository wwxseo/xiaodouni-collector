import os
import re
import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime

def get_xiaodouni_images():
    print("🚀 开启随机探索模式，搜寻新鲜的小豆泥...")
    # 增加几个不同的搜索词，每次运行随机选一个，增加多样性
    queries = ["小豆泥 高清", "小豆泥 壁纸", "小豆泥 插画", "小豆泥 funny bean"]
    selected_query = random.choice(queries)
    
    url = f"https://www.bing.com/images/search?q={selected_query}&qft=+filterui:imagesize-large&form=IRFLTR"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        pool = []
        for img_tag in soup.find_all("a", class_="iusc"):
            m_content = img_tag.get("m")
            if m_content:
                murl_match = re.search(r'"murl":"(.*?)"', m_content)
                if murl_match:
                    img_url = murl_match.group(1)
                    if img_url.startswith("http"):
                        pool.append(img_url)
        
        # 从搜到的几十张图中随机抽取 12 张
        sample_size = min(len(pool), 12)
        images = random.sample(pool, sample_size)
        
        print(f"🎯 从 {len(pool)} 张候选图中随机选中了 {len(images)} 张")
        return images
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return []

def update_readme(urls):
    if not urls: return
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="180" alt="小豆泥" style="margin:5px; border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
    img_html += f'\n  <p><i>🔄 每日随机更新，当前主题：高清搜罗</i></p>\n</div>'
    
    start_tag = "<!-- START_SECTION:xiaodouni -->"
    end_tag = "<!-- END_SECTION:xiaodouni -->"
    
    if start_tag in content and end_tag in content:
        pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
        replacement = f"{start_tag}\n{img_html}\n{end_tag}"
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✨ README 已更新！")

def update_history(urls):
    if not urls: return
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 检查是否今天已经记录过了，避免重复运行导致的一天多条
    if os.path.exists("history.md"):
        with open("history.md", "r", encoding="utf-8") as f:
            if f"### 📅 {today}" in f.read():
                # 如果你想一天存多份，就把下面这行删掉
                print("📅 今天已经归档过了，为了保持简洁，不再重复添加。")
                return

    if not os.path.exists("history.md"):
        with open("history.md", "w", encoding="utf-8") as f:
            f.write("# 📚 小豆泥历史收藏馆\n\n---\n")

    with open("history.md", "a", encoding="utf-8") as f:
        f.write(f"\n### 📅 {today}\n")
        f.write('<div align="left">\n')
        for url in urls:
            f.write(f'  <img src="{url}" width="120" style="margin:2px; border-radius:5px;">\n')
        f.write('</div>\n\n---\n')
    print("📖 已成功归档到 history.md")

if __name__ == "__main__":
    image_list = get_xiaodouni_images()
    update_readme(image_list)
    update_history(image_list)
