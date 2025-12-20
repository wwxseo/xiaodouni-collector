# 🐱 小豆泥自动收集器 (Xiaodouni HD Collector)

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Quality](https://img.shields.io/badge/Quality-HD_Only-orange.svg)

这个项目是专为**小豆泥**（Funny Bean）爱好者设计的自动化收集器。利用 GitHub Actions 每天在全网搜寻高清的小豆泥壁纸和插画。

---

## 📸 今日份高清小豆泥

<!-- START_SECTION:xiaodouni -->
<div align="center">
  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi02piccdn.sogoucdn.com%2F3e0eac05ee5dda76&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi01piccdn.sogoucdn.com%2Ffa6d74bc06a38fb4&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi02piccdn.sogoucdn.com%2F3a6264e52831495d&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi03piccdn.sogoucdn.com%2F1444cf01302cca53&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi01piccdn.sogoucdn.com%2F625711f2e84d88fe&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi04piccdn.sogoucdn.com%2Fcdf81ee01e0b3b1c&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi03piccdn.sogoucdn.com%2Feb7b752a2203dc1d&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi01piccdn.sogoucdn.com%2F8a7b8fc3ac023834&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi02piccdn.sogoucdn.com%2Fc5188e2a0576d082&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi03piccdn.sogoucdn.com%2F708ad3fcb40261c5&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi02piccdn.sogoucdn.com%2F9e04e4690c9ff99c&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">  <img src="https://wsrv.nl/?url=https%3A%2F%2Fi04piccdn.sogoucdn.com%2Fb0ccf8bfdae62023&w=300&h=300&fit=cover&bg=white&output=jpg" width="160" height="160" alt="小豆泥" style="margin:4px; border-radius:12px; object-fit:cover; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <p><i>🐱 每日随机三源搜罗，只选高清猫猫头</i></p>
</div>
<!-- END_SECTION:xiaodouni -->

---

## 🌟 项目亮点
- **高清优先**：自动过滤低分辨率缩略图，只展示大尺寸壁纸级图片。
- **智能排版**：自适应瀑布流展示，PC 和手机端浏览体验良好。
- **全自动流水线**：基于 GitHub Actions，无需任何服务器维护成本。
- **开源精神**：欢迎 Fork 并在你的主页展示这些可爱的小家伙。

## ⚙️ 如何部署到你的账号？
1. **Fork 本项目**。
2. 进入仓库的 **Actions** 选项卡，手动启用并运行一次 `Xiaodouni Daily Update`。
3. 如果你想修改抓取频率，可以编辑 `.github/workflows/main.yml` 中的 `cron` 表达式。

## ⚖️ 版权说明
本项目仅供技术交流和个人爱好展示。图片版权归原作者（小豆泥官方/画师）所有，请勿用于商业用途。

---
<div align="center">
  Made with ❤️ for Xiaodouni Fans
</div>

> 🔗 [点击这里查看往期所有收藏 (History)](./history.md)
