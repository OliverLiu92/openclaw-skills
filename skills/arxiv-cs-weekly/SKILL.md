---
name: arxiv-cs-weekly
description: 每周自动抓取 arXiv CS (计算机科学) 最新论文，整理成中文报告。包括论文标题、作者、发表时间和通俗化的问题描述。Use when user wants to (1) automatically track new CS papers from arXiv, (2) generate weekly summaries of arXiv papers in Chinese, (3) monitor recent research trends in computer science.
---

# ArXiv CS Weekly Paper Tracker

自动追踪 arXiv 计算机科学领域最新论文，每周生成中文简报。

## 功能

1. **自动抓取**：访问 https://arxiv.org/list/cs/recent 获取最新论文
2. **信息提取**：提取论文标题、作者、摘要、学科分类
3. **中文整理**：生成结构化的中文周报，包括：
   - 论文标题（英文原文）
   - 作者列表
   - 研究领域
   - 通俗化的问题描述（基于摘要）

## 使用方法

### 手动运行

```bash
python3 scripts/fetch_papers.py
```

输出 Markdown 格式的周报内容。

### 定时自动运行（推荐）

每周五自动发送含**中文翻译+科普解读**的论文周报：

```bash
openclaw cron add \
  --name "arxiv-cs-weekly" \
  --cron "0 9 * * 5" \
  --message "请执行 ArXiv CS 周报任务（含翻译和科普）：\n\n1. 运行脚本生成周报框架：\n   python3 ~/.openclaw/workspace/skills/arxiv-cs-weekly/scripts/generate_report_with_i18n.py\n\n2. 捕获输出，处理每篇论文的 [TRANSLATE_AND_EXPLAIN] 标记：\n   - 生成中文摘要（准确翻译）\n   - 生成科普解读（面向非技术读者，100-150字，生活化类比）\n\n3. 将完整周报（英文摘要+中文翻译+科普）发送到大象\n\n用户看到周报后，如感兴趣可回复\"解读第X篇\"获取深度技术分析。" \
  --description "每周五上午9点发送ArXiv CS周报（含中文翻译和科普）" \
  --announce \
  --expect-final \
  --timeout-seconds 300
```

### 手动运行

```bash
# 生成含翻译标记的周报框架
python3 ~/.openclaw/workspace/skills/arxiv-cs-weekly/scripts/generate_report_with_i18n.py

# 其他版本
python3 ~/.openclaw/workspace/skills/arxiv-cs-weekly/scripts/generate_full_report.py
python3 ~/.openclaw/workspace/skills/arxiv-cs-weekly/scripts/fetch_papers.py
```

## 输出格式

报告包含以下信息（中文）：

```markdown
# 📚 arXiv CS 最新论文周报

## 1. [论文标题]
**作者**：[作者列表]
**领域**：[CS学科分类]
**摘要**：[英文摘要原文]
```

## 自定义

修改 `scripts/fetch_papers.py` 中的参数：

- `max_papers`：控制每份报告展示的论文数量（默认 10 篇）
- `ARXIV_URL`：可改为其他 arXiv 分类链接，如：
  - `https://arxiv.org/list/cs.AI/recent` - 仅 AI
  - `https://arxiv.org/list/cs.LG/recent` - 仅机器学习
  - `https://arxiv.org/list/cs.CL/recent` - 仅计算语言学/NLP

## 依赖

- Python 3.6+
- 仅使用标准库（urllib, html.parser, re, datetime）
- 无需额外安装包

## 注意事项

1. 请尊重 arXiv 服务，不要频繁抓取（建议每周一次）
2. 摘要使用英文原文，保持学术准确性
3. 如需翻译摘要，建议使用 LLM 进一步处理
