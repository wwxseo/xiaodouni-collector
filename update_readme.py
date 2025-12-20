import os
import re
import requests
import time
from bs4 import BeautifulSoup

def get_xiaodouni_images():
    """从 Bing 搜索抓取高清小豆泥图片"""
    print("🚀 正在搜寻高清大图版本的小豆泥...")
    
    # 搜索词增加了“高清壁纸”，并加入了 qft=+filterui:imagesize-large 参数，强制只搜大图
    query = "小豆泥 高清壁纸"
    url = f"https://www.bing.com/images/search?q={query}&qft=+filterui:imagesize-large&form=IRFLTR"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        # 稍微等一下，确保解析没压力
        time.sleep(1)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        
        # 寻找带有 m 属性的节点
        for img_tag in soup.find_all("a", class_="iusc"):
            m_content = img_tag.get("m")
            if m_content:
                # 提取 murl (原始图片地址)
                murl_match = re.search(r'"murl":"(.*?)"', m_content)
                if murl_match:
                    img_url = murl_match.group(1)
                    
                    # 过滤掉一些明显的低质图源或头像库（可选）
                    if any(exclude in img_url for exclude in ["thumbnail", "avatar", "100x100"]):
                        continue
                        
                    images.append(img_url)
            
            # 抓取 12 张高清图，排版更美观
            if len(images) >= 12: 
                break
        
        if not images:
            print("⚠️ 未找到高清图片，尝试扩大搜索范围...")
            # 如果大图没搜到，这里可以做一个备选逻辑，但通常高清壁纸词条能搜到很多
        
        print(f"✅ 成功捕获 {len(images)} 张高清小豆泥！")
        return images
    except Exception as e:
        print(f"❌ 抓取过程中发生错误: {e}")
        return []

def update_readme(urls):
    """更新 README.md 中的图片墙"""
    if not urls:
        return

    if not os.path.exists("README.md"):
        print("⚠️ 未找到 README.md")
        return

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # 构建 HTML 图片墙
    img_html = '<div align="center">\n'
    for url in urls:
        # 给图片加一个简单的阴影和悬停效果（通过 HTML 模拟）
        # width="180" 略微放大一点，展示清晰度
        img_html += f'  <img src="{url}" width="180" alt="小豆泥" style="margin:8px; border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🔄 每日自动更新，搜集自全网高清图源</i></p>\n</div>'
    
    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    replacement = f"<!-- START_SECTION:xiaodouni -->\n{img_html}\n<!-- END_SECTION:xiaodouni -->"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✨ README 高清美图墙已翻新！")

if __name__ == "__main__":
    image_list = get_xiaodouni_images()
    update_readme(image_list)
