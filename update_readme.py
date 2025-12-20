import os
import re
import requests
from bs4 import BeautifulSoup

def get_xiaodouni_images():
    """更稳健的图片抓取逻辑"""
    print("🚀 开始搜寻小豆泥...")
    
    # 尝试两个搜索源，第一个是高清过滤，第二个是普通搜索
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
            print(f"🔍 尝试从源抓取: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"⚠️ 访问失败，状态码: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # 尝试解析 Bing 的图片元数据 m 属性
            tags = soup.find_all("a", class_="iusc")
            print(f"找到候选标签数: {len(tags)}")
            
            for img_tag in tags:
                m_content = img_tag.get("m")
                if m_content:
                    murl_match = re.search(r'"murl":"(.*?)"', m_content)
                    if murl_match:
                        img_url = murl_match.group(1)
                        # 简单过滤一些无效链接
                        if img_url.startswith("http") and not any(x in img_url for x in ["example.com", "thumbnail"]):
                            if img_url not in images:
                                images.append(img_url)
                if len(images) >= 12: break
        except Exception as e:
            print(f"❌ 当前源抓取异常: {e}")
            
    print(f"🎯 最终捕获小豆泥数量: {len(images)}")
    return images

def update_readme(urls):
    """更新 README.md 中的图片墙"""
    if not urls:
        print("⚠️ 警告：未找到任何图片，跳过 README 更新。")
        return

    if not os.path.exists("README.md"):
        print("❌ 错误：README.md 文件不存在")
        return

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # 构建 HTML 图片墙
    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="180" alt="小豆泥" style="margin:5px; border-radius:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🔄 每日自动更新，搜集自全网图源</i></p>\n</div>'
    
    # 严格匹配 README 中的标记
    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    if not re.search(pattern, content, flags=re.DOTALL):
        print("❌ 错误：在 README.md 中没找到 <!-- START_SECTION:xiaodouni --> 标记")
        return

    replacement = f"<!-- START_SECTION:xiaodouni -->\n{img_html}\n<!-- END_SECTION:xiaodouni -->"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✨ README 已成功更新！")

if __name__ == "__main__":
    image_list = get_xiaodouni_images()
    update_readme(image_list)
