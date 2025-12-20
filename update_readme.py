import os
import re
import requests
from bs4 import BeautifulSoup

def get_xiaodouni_images():
    print("🚀 开始搜寻小豆泥...")
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
    if not urls:
        print("⚠️ 未找到图片，跳过。")
        return
    
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="180" alt="小豆泥" style="margin:5px; border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🔄 每日自动更新，搜集自全网高清图源</i></p>\n</div>'
    
    # 更加宽松的正则匹配，允许标记内部有空格
    start_tag = "<!-- START_SECTION:xiaodouni -->"
    end_tag = "<!-- END_SECTION:xiaodouni -->"
    
    if start_tag in content and end_tag in content:
        print("✅ 找到标记，正在替换内容...")
        pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
        replacement = f"{start_tag}\n{img_html}\n{end_tag}"
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        print("⚠️ 未找到标准标记，将在文件末尾追加内容...")
        new_content = content + f"\n\n{start_tag}\n{img_html}\n{end_tag}"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✨ README 已更新！")

if __name__ == "__main__":
    image_list = get_xiaodouni_images()
    update_readme(image_list)
