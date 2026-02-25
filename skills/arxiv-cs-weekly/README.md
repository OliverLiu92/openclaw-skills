# ArXiv CS Weekly Skill 使用指南（中文版+科普版）

## ✅ 功能：周报（含中文翻译+科普解读）+ 按需深度分析

每周五上午9点收到**包含中文翻译和科普解读**的论文周报，看到感兴趣的再深入分析。

---

## 📱 大象推送效果

```
📚 ArXiv CS 论文周报 (2026年02月25日)

本周新增 50 篇论文，🆕 全新 0 篇

💡 提示：回复 "解读第X篇" 获取深度技术分析

---

### 1. Test-Time Training with KV Binding Is Secretly Linear Attention
「注意力 · 测试时 · 训练」
👤 Junchen Liu... | 🏷️ ML、AI | 🆔 2602.21204
🔗 https://arxiv.org/abs/2602.21204

📝 **英文摘要**：Test-time training (TTT) with KV binding...

📖 **中文摘要**：测试时训练（TTT）与KV绑定作为序列建模层，
通常被解释为一种在线元学习形式...

💡 **科普解读**：想象你有一个助手，之前大家都以为他是靠
"临时背答案"来解决新问题的...

---

### 2. Squint: Fast Visual Reinforcement Learning...
...

🤖 OpenClaw 自动生成 | 回复 "解读第N篇" 获取深度技术分析
```

---

## 📋 每篇论文包含

1. **英文标题**（保持原文）
2. **关键词标签**（中文）
3. **作者** + **领域** + **arXiv ID**
4. **直达链接**
5. **📝 英文摘要**（原文，方便对照）
6. **📖 中文摘要**（准确翻译）
7. **💡 科普解读**（面向非技术读者）

### 科普解读风格

- **面向读者**：高中生、非计算机专业背景
- **语言风格**：生活化类比，通俗易懂
- **内容要点**：
  - 这东西是做什么的？
  - 有什么用？能解决什么问题？
  - 为什么重要？

---

## 🚀 使用方法

### 每周五自动接收
无需操作，9点自动推送到大象。

### 获取深度技术分析
看到感兴趣的论文，回复：
```
解读第3篇
解读 arXiv:2602.21204
```

我会生成5模块深度分析：
1. 核心问题（生活类比）
2. 底层逻辑（第一性原理）
3. 技术拆解（3-5步骤）
4. 实验结果（对比+代价）
5. 专家视角（一句话+关键词）

---

## 📁 文件结构

```
arxiv-cs-weekly/
├── SKILL.md
├── README.md
└── scripts/
    ├── generate_report_with_i18n.py  # 🌟 主脚本（含翻译标记）
    ├── generate_full_report.py       # 英文摘要版
    ├── generate_report.py            # 精简版
    └── ...
```

---

## 🎮 常用命令

### 立即测试周报
```bash
python3 ~/.openclaw/workspace/skills/arxiv-cs-weekly/scripts/generate_report_with_i18n.py
```

### 查看定时任务
```bash
openclaw cron list
```

### 手动触发
```bash
openclaw cron run arxiv-cs-weekly
```

---

## ⚙️ 定时任务配置

| 配置项 | 值 |
|--------|-----|
| **任务名称** | arxiv-cs-weekly |
| **执行时间** | 每周五上午 9:00 |
| **Cron** | `0 9 * * 5` |
| **超时** | 300秒（含翻译和科普生成） |
| **内容** | 8篇论文（每篇含英文摘要+中文翻译+科普） |
| **发送方式** | 大象插件推送 |

---

## 💡 科普解读示例

### 示例1：AI论文

**论文**：Test-Time Training with KV Binding Is Secretly Linear Attention

**科普解读**：
> 想象你有一个助手，之前大家都以为他是靠"临时背答案"来解决新问题的
> （像考试前突击背单词）。但这篇研究发现，他其实不是死记硬背，而是
> 用一种更聪明的方式——像我们在嘈杂的餐厅里，能自动"聚焦"到想听的
> 声音一样。这种发现不仅让AI模型变得更简单高效，还统一了之前各种
> 看似不同的技术路线。

### 示例2：机器人论文

**论文**：Squint: Fast Visual Reinforcement Learning for Sim-to-Real Robotics

**科普解读**：
> 教机器人学东西就像教小朋友骑自行车。一种方法是先让他看1000个
> 骑车视频再上车（学得扎实但慢），另一种是直接上车摔了再调整（学得快
> 但摔得惨）。这篇论文的方法像"眯着眼睛学"——先用模糊的画面快速
> 掌握大概，再慢慢看清细节。这样机器人15分钟就能学会一个操作任务。

---

## 🔧 自定义配置

### 修改论文数量

编辑 `generate_report_with_i18n.py`：
```python
display_count = min(8, len(papers))  # 默认8篇（平衡详细度和长度）
```

### 更改发送时间

```bash
# 删除旧任务
openclaw cron rm arxiv-cs-weekly

# 创建新任务（每周一上午10点）
openclaw cron add \
  --name "arxiv-cs-weekly" \
  --cron "0 10 * * 1" \
  --message "请执行 ArXiv CS 周报任务..." \
  --description "每周一上午10点发送ArXiv CS周报" \
  --announce \
  --expect-final \
  --timeout-seconds 300
```

---

## 📝 注意事项

1. **生成时间**：8篇论文 ×（翻译+科普）约需 1-2 分钟
2. **首次运行**：会抓取所有可见论文，之后标记新增为 🆕
3. **解读触发**：看到周报后回复"解读第N篇"获取技术分析
4. **网络要求**：需要能访问 arxiv.org

---

## 📊 Token 消耗估算

| 项目 | 消耗 |
|------|------|
| 周报框架生成 | 0 tokens（脚本运行） |
| 每篇中文翻译 | ~500 tokens |
| 每篇科普解读 | ~800 tokens |
| 8篇总计 | ~10K tokens |
| **每周成本** | **约 ¥0.5-1 元** |

---

## 🎯 使用场景

- **周五晨会前**：快速浏览本周AI热点
- **技术分享**：转发科普解读给非技术同事
- **学习笔记**：根据中文摘要快速了解论文内容
- **深入研究**：看到感兴趣的再要求深度技术分析

---

## 🐛 故障排除

### 周报没收到
```bash
openclaw cron list          # 检查任务
openclaw gateway status     # 检查Gateway
openclaw cron runs arxiv-cs-weekly  # 查看运行日志
```

### 翻译/科普质量不满意
可以调整 cron 任务中的 prompt，修改：
- 翻译风格（更学术 vs 更通俗）
- 科普长度（100字 vs 200字）
- 目标读者（高中生 vs 本科生）

---

*本周五开始，收到第一份带中文翻译和科普解读的周报！* 🎉
