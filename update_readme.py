import os
import re
import requests
import random
import time
from datetime import datetime
from urllib.parse import quote

# --- 1. 配置区域 ---

# 关键词：堆糖上的热门标签
KEYWORDS = ["小豆泥", "funny bean", "小豆泥头像", "小豆泥壁纸", "小豆泥表情包"]

# --- 2. 工具函数 ---

def get_seen_urls():
    """从 history.md 加载记忆，使用文件名进行指纹识别，去重更狠"""
    seen = set()
    if os.path.exists("history.md"):
        try:
            with open("history.md", "r", encoding="utf-8") as f:
                content = f.read()
                # 提取链接
                urls = re.findall(r'url=(http[^"\'&\s]+)', content)
                for u in urls:
                    seen.add(u)
                    # 额外提取文件名作为指纹
                    filename = u.split('/')[-1].split('?')[0]
                    if len(filename) > 5:
                        seen.add(filename)
        except Exception:
            pass
    print(f"📜 记忆库加载完毕，包含 {len(seen)} 个指纹。")
    return seen

def wrap_proxy(url):
    """加上 wsrv.nl 代理，修复防盗链，统一裁剪"""
    # 清洗链接
    url = url.replace(r'\/', '/')
    encoded_url = quote(url, safe='')
    return f"https://wsrv.nl/?url={encoded_url}&w=300&h=300&fit=cover&bg=white&output=jpg"

# --- 3. 核心抓取逻辑：堆糖 API ---

def fetch_from_duitang(needed, seen_fingerprints):
    print("🚀 正在潜入堆糖图库 (Duitang)...")
    images = []
    
    kw = random.choice(KEYWORDS)
    # 随机翻页策略：0-50页随机跳伞
    start_page = random.randint(0, 50) 
    start_index = start_page * 24
    
    print(f"🔍 关键词: [{kw}] | 随机空降至第 {start_page} 页...")

    api_url = f"https://www.duitang.com/napi/blog/list/by_search/?kw={kw}&start={start_index}&limit=100"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.duitang.com/search/?kw=" + quote(kw)
    }

    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        data = resp.json()
        object_list = data.get('data', {}).get('object_list', [])
        
        if not object_list:
            print("⚠️ 当前页没数据，可能是翻页翻太深了。")
            return []

        random.shuffle(object_list)

        for item in object_list:
            img_url = item.get('photo', {}).get('path')
            if not img_url: continue
            
            # 去重
            if img_url in seen_fingerprints: continue
            filename = img_url.split('/')[-1]
            if filename in seen_fingerprints: continue
            
            images.append(img_url)
            if len(images) >= needed: break
            
    except Exception as e:
        print(f"❌ 连接堆糖失败: {e}")
    
    return images

# --- 4. 主流程 ---

def get_all_images():
    seen = get_seen_urls()
    final_images = []
    
    attempts = 0
    while len(final_images) < 12 and attempts < 3:
        needed = 12 - len(final_images)
        new_batch = fetch_from_duitang(needed, seen)
        
        for img in new_batch:
            final_images.append(img)
            seen.add(img)
            seen.add(img.split('/')[-1])
            
        attempts += 1
        if len(final_images) < 12:
            time.sleep(1)

    print(f"🎯 最终捕获 {len(final_images)} 张稀有图片")
    return [wrap_proxy(img) for img in final_images]

def update_files(urls):
    if not urls:
        print("❌ 颗粒无收，今天休息。")
        return

    # 1. 更新 README (始终展示最新的)
    img_html = '<div align="center">\n'
    for url in urls:
        img_html += f'  <img src="{url}" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">'
    img_html += '\n  <p><i>🧶 图片采集自堆糖社区，每日随机挖掘</i></p>\n</div>'

    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        s_tag = "<!-- START_SECTION:xiaodouni -->"
        e_tag = "<!-- END_SECTION:xiaodouni -->"
        
        if s_tag in content and e_tag in content:
            s = content.find(s_tag) + len(s_tag)
            e = content.find(e_tag)
            new_content = content[:s] + "\n" + img_html + "\n" + content[e:]
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(new_content)
        else:
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(f"# 小豆泥收集器\n\n{s_tag}\n{img_html}\n{e_tag}")
        print("✅ README 更新完成")

    # 2. 更新 History (倒序插入)
    today = datetime.now().strftime("%Y-%m-%d %H:%M") # 精确到分钟，方便一天跑多次区分
    header = "# 📚 小豆泥历史收藏馆\n\n这里记录了自本项目启动以来抓取过的所有图片。\n\n---\n"
    
    # 构建今日的新内容块
    new_block = f"\n### 📅 {today}\n<div align='left'>\n"
    for url in urls:
        new_block += f'  <img src="{url}" width="100" height="100" style="margin:2px; border-radius:6px; object-fit:cover;">\n'
    new_block += "</div>\n\n---\n"

    # 读取旧文件内容
    old_content = ""
    if os.path.exists("history.md"):
        with open("history.md", "r", encoding="utf-8") as f:
            content = f.read()
            # 如果文件里已经有标题，去掉它，只保留后面的记录，防止标题重复
            if content.strip().startswith("# 📚"):
                # 尝试找到第一个分割线，分割线之后的就是旧记录
                parts = content.split("---\n", 1)
                if len(parts) > 1:
                    old_content = parts[1]
                else:
                    # 如果找不到分割线，说明文件可能只有标题，或者格式乱了，直接作为旧内容
                    old_content = content.replace(header, "")
            else:
                old_content = content

    # 拼接：标题 + 新内容 + 旧内容
    final_history = header + new_block + old_content
    
    with open("history.md", "w", encoding="utf-8") as f:
        f.write(final_history)
    print("✅ History 归档完成 (已倒序)")

if __name__ == "__main__":
    imgs = get_all_images()
    update_files(imgs)
