#!/bin/bash
# arxiv-cs-weekly-runner.sh
# 每周运行 arXiv CS 论文抓取

SKILL_DIR="$HOME/.openclaw/workspace/skills/arxiv-cs-weekly"
REPORT_DIR="$HOME/.openclaw/workspace/reports"
DATE=$(date +%Y%m%d)
REPORT_FILE="$REPORT_DIR/arxiv-cs-weekly-$DATE.md"

# 创建报告目录
mkdir -p "$REPORT_DIR"

# 运行抓取脚本
echo "[$DATE] 开始抓取 arXiv CS 论文..." 
cd "$SKILL_DIR"
python3 scripts/fetch_papers.py > "$REPORT_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$DATE] 报告已生成: $REPORT_FILE"
    # 同时输出到 stdout 方便查看
    cat "$REPORT_FILE"
else
    echo "[$DATE] 抓取失败"
    exit 1
fi
