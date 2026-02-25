#!/bin/bash
# arxiv-weekly-with-elephant.sh
# 生成报告并发送到大象

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT=$(python3 "$SCRIPT_DIR/generate_report.py" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$REPORT" ]; then
    echo "$REPORT"
    echo ""
    echo "---"
    echo "报告已生成，请使用 message 工具发送到大象："
    echo "message send --channel elephant --message \"$REPORT\""
else
    echo "生成报告失败"
    exit 1
fi
