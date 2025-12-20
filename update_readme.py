import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_xiaodouni_images():
    print("🚀 开始搜寻高清小豆泥...")
    search_urls = [
        "https://www.bing.com/images/search?q=小豆泥+wallpaper&qft=+filterui:imagesize-large&form=IRFLTR",
        "https://www.bing.com/images/search?q=小豆泥"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    images = []
    for url in search_urls:
        if len(images) >= 12: break
        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            for img_tag in soup.find_all("a", class_="iusc"):
                m_content = img_tag.get("m")
                if m_content:
                    murl_match = re.search(r'"murl":"(.*?)"', m_content)
                    if murl_match:
                        img_url = murl_match.group(1)
                        if img_url.startswith("http") and img_url not in images:
                            images.append(img_url)
                if len(images) >= 12: break
        except: continue
    print(f"🎯 最终捕获小豆泥数量: {len(images)}")
    return images

def update_readme(urls):
    """更新首页 README.md"""
    if not urls: return
    if not os.path.exists("README.md"): return
    
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="180" alt="小豆泥" style="margin:5px; border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🔄 每日自动更新，搜集自全网高清图源</i></p>\n</div>'
    
    start_tag = "<!-- START_SECTION:xiaodouni -->"
    end_tag = "<!-- END_SECTION:xiaodouni -->"
    
    if start_tag in content and end_tag in content:
        pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
        replacement = f"{start_tag}\n{img_html}\n{end_tag}"
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        new_content = content + f"\n\n{start_tag}\n{img_html}\n{end_tag}"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✨ README 已更新！")

def update_history(urls):
    """追加到 history.md"""
    if not urls: return
    
    # 获取当前日期 (例如: 2025-05-20)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 如果文件不存在，先写个标题
    if not os.path.exists("history.md"):
        with open("history.md", "w", encoding="utf-8") as f:
            f.write("# 📚 小豆泥历史收藏馆\n\n这里记录了自本项目启动以来抓取过的所有图片。\n\n---\n")

    # 追加新抓到的图片（使用小缩略图，防止页面太长）
    with open("history.md", "a", encoding="utf-8") as f:
        f.write(f"\n### 📅 {today}\n")
        f.write('<div align="left">\n')
        for url in urls:
            f.write(f'  <img src="{url}" width="120" style="margin:2px; border-radius:5px;">\n')
        f.write('</div>\n\n---\n')
    print(f"📖 已成功归档 {len(urls)} 张图片到 history.md")

if __name__ == "__main__":
    image_list = get_xiaodouni_images()
    update_readme(image_list)
    update_history(image_list)
