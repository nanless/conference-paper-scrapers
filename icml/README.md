# ICML 2026 Paper Scraper (Authenticated)

使用 OpenReview 账号认证爬取 ICML 2026 录用论文元数据。ICML 投稿不公开，必须登录后才能获取。

## 功能

- `scraper.py` — 用 OpenReview 账号登录，拉取全部录用论文元数据
- `filter_audio.py` — 按关键词筛选语音/音频相关论文
- `download_pdfs.py` — 批量下载 PDF（可选）

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 方式 1：环境变量（推荐，密码不会出现在命令历史中）
export OPENREVIEW_USERNAME="your@email.com"
export OPENREVIEW_PASSWORD="your_password"
python scraper.py

# 方式 2：命令行参数
python scraper.py --username "your@email.com" --password "your_password"
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `data/icml2026_accepted.json` | 全部录用论文元数据 |
| `data/icml2026_accepted.csv` | 同上，CSV 格式 |
| `data/icml2026_audio_papers.json` | 语音/音频相关论文（关键词过滤后）|
| `data/pdfs/` | 下载的 PDF 文件（可选）|

## 注意事项

- ICML 2026 使用 OpenReview API v2，必须提供有效账号密码
- 爬取全部约 1-2 万篇投稿需要 1-3 分钟
- OpenReview 有速率限制，脚本已内置 0.3s 间隔
