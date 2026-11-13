# jacksu-xhs-pipeline

小红书图文/视频内容流水线：把已有长文（少数派文章等）拆成卡片图文，本地渲染成 1080×1440 图片，再通过浏览器自动化填表发布，并追踪数据表现。

账号定位：`@JackS.u · 爱丁堡 CS` — 留学 / 思考成长 / 效率习惯 / CS 项目 / 网球。

## 目录结构

```
posts/            # 每篇内容的源文件（标题、正文、标签、slides）
  NNN-name.json
template.html     # 卡片模板，主题 A（杂志纸本）/ B（瑞士黑）/ C（渐变玻璃）
render_cards.py   # JSON -> output/<name>/slide_N.png（Playwright 截图）
publish.py        # 通过 Arc 的 CDP(:9222) 上传图片、填标题正文标签
output/           # 渲染结果与预览图
metrics.csv       # 发布后 24h / 7d 数据记录
PLAN.md           # 4 周实验计划与决策规则
bin/              # 登录用二进制 / cookies（xiaohongshu-mcp）
article_*.md      # 原始长文素材
```

## 环境

- Python 3 + 虚拟环境 `.venv`
- Python 包：`playwright`、`websocket-client`
- Playwright Chromium：`python -m playwright install chromium`
- 发布依赖 Arc 浏览器开启远程调试端口 9222，并已登录小红书创作者中心

```bash
python -m venv .venv && source .venv/bin/activate
pip install playwright websocket-client
python -m playwright install chromium
```

## 使用流程

1. **写内容**：新建 `posts/NNN-name.json`

   ```json
   {
     "title": "标题（≤20 字）",
     "source": "原文链接",
     "caption": "正文，第一人称，段落用 \\n 分隔",
     "tags": ["#标签1", "#标签2"],
     "slides": [
       {"type": "cover", "kicker": "眉题", "heading": "大标题", "sub": "副标题"},
       {"type": "content", "no": "01", "heading": "小标题", "bullets": ["要点", "..."]}
     ],
     "theme": "A"
   }
   ```

   支持的 slide 类型：`cover` `content` `quote` `table` `steps` `code` `end`。

2. **渲染卡片**

   ```bash
   python render_cards.py posts/003-study-abroad.json          # 默认主题 A
   python render_cards.py posts/003-study-abroad.json B        # 指定主题
   python render_cards.py posts/003-study-abroad.json A 1,2,3  # 只渲染指定页
   ```

   输出到 `output/<name>/slide_N.png`，检查缩略图有无文字溢出。

3. **填表预览**

   ```bash
   python publish.py posts/003-study-abroad.json
   ```

   仅上传图片并填写表单，截图保存为 `output/<name>/preview_form.png`，**不会发布**。

4. **确认后发布**

   ```bash
   python publish.py posts/003-study-abroad.json --publish
   ```

5. **记录数据**：发布后 24h / 72h / 7d 在 `metrics.csv` 填写观看、点赞、收藏、评论、涨粉；收藏率 = 收藏 / 观看，是判断内容是否有用的核心指标。

## 内容与风控约束

- 素材只用真实经历与观点，不编造数据或故事
- 每天最多 1 篇，不批量刷发
- 小红书简介等部分操作需手动完成，自动化只覆盖图文发布
