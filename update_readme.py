import os
import re
import requests
from bs4 import BeautifulSoup

def get_xiaodouni_images():
    print("正在通过 Bing 搜索小豆泥图片...")
    # Bing 搜索的网页版 URL，不需要 API Key
    url = "https://www.bing.com/images/search?q=小豆泥&form=HDRSC3"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Bing 的图片地址通常藏在 m 属性的 JSON 里
        images = []
        # 寻找带有 m 属性的候选节点
        for img_tag in soup.find_all("a", class_="iusc"):
            m_content = img_tag.get("m")
            if m_content:
                # 使用正则提取 murl (图片真实地址)
                match = re.search(r'"murl":"(.*?)"', m_content)
                if match:
                    images.append(match.group(1))
            
            if len(images) >= 5: # 只要 5 张
                break
        
        print(f"成功搜到 {len(images)} 张图片")
        return images
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def update_readme(urls):
    if not urls:
        print("没有搜到图片，不更新 README。")
        return

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # 生成图片 HTML
    img_html = "\n"
    for url in urls:
        # 使用 HTML 标签可以更好地控制大小，并增加一个加载失败的文字说明
        img_html += f'<img src="{url}" width="180" alt="小豆泥" style="margin:5px; border-radius:10px;">\n'
    
    # 替换标记
    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    replacement = f"<!-- START_SECTION:xiaodouni -->{img_html}<!-- END_SECTION:xiaodouni -->"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README 已更新完毕！")

if __name__ == "__main__":
    # 修正了之前的变量名拼写错误
    image_list = get_xiaodouni_images()
    update_readme(image_list)
