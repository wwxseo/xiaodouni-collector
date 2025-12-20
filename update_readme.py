import os
import re
from duckduckgo_search import DDGS

def get_xiaodouni_images():
    print("正在搜索小豆泥图片...")
    urls = []
    try:
        # 使用 DuckDuckGo 搜索小豆泥图片
        with DDGS() as ddgs:
            # keywords: 搜索关键词
            # max_results: 每次拿 5 张图
            results = ddgs.images("小豆泥", max_results=5)
            for r in results:
                urls.append(r['image'])
        return urls
    except Exception as e:
        print(f"搜索出错: {e}")
        return []

def update_readme(urls):
    if not urls:
        print("没有找到图片，跳过更新。")
        return

    # 1. 读取当前的 README
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # 2. 制作图片 HTML（让它们排成一排）
    img_html = "\n"
    for url in urls:
        img_html += f'<img src="{url}" width="180" style="margin:5px; border-radius:10px;">\n'
    
    # 3. 使用正则替换占位符中间的内容
    pattern = r"<!-- START_SECTION:xiaodouni -->.*?<!-- END_SECTION:xiaodouni -->"
    replacement = f"<!-- START_SECTION:xiaodouni -->{img_html}<!-- END_SECTION:xiaodouni -->"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 4. 写回文件
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README 已成功更新！")

if __name__ == "__main__":
   imade_urls = get_xiaodouni_images()
update_readme(image_urls)
