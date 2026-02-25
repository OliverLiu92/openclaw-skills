#!/usr/bin/env python3
"""
Paper Insights Deep - 论文深度解读助手
读取论文内容并生成结构化解读报告
"""

import sys
import re
from urllib.request import urlopen, Request
from urllib.error import URLError

def fetch_arxiv_abstract(arxiv_id):
    """获取 arXiv 论文摘要"""
    try:
        url = f"https://arxiv.org/abs/{arxiv_id}"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            # 提取标题
            title_match = re.search(r'<h1[^>]*class="title mathjax"[^>]*>.*?<span[^>]*>Title:</span>(.*?)</h1>', html, re.DOTALL)
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else "Unknown"
            # 提取摘要
            abs_match = re.search(r'<blockquote[^>]*class="abstract mathjax"[^>]*>.*?<span[^>]*>Abstract:</span>(.*?)</blockquote>', html, re.DOTALL)
            abstract = re.sub(r'<[^>]+>', '', abs_match.group(1)).strip() if abs_match else ""
            return title, abstract
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None, None

def extract_arxiv_id(text):
    """从文本中提取 arXiv ID"""
    # 匹配 2602.12345 或 arxiv:2602.12345 或 arxiv.org/abs/2602.12345
    patterns = [
        r'arxiv[\.:]\s*(\d{4}\.\d{4,5})',
        r'arxiv\.org/abs/(\d{4}\.\d{4,5})',
        r'/(\d{4}\.\d{4,5})',
        r'^(\d{4}\.\d{4,5})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def main():
    if len(sys.argv) < 2:
        print("用法: python3 paper_insights.py <arxiv_id_or_url>")
        print("示例: python3 paper_insights.py 2602.21204")
        print("       python3 paper_insights.py https://arxiv.org/abs/2602.21204")
        sys.exit(1)
    
    input_text = sys.argv[1]
    arxiv_id = extract_arxiv_id(input_text)
    
    if not arxiv_id:
        print(f"无法从输入中提取 arXiv ID: {input_text}")
        sys.exit(1)
    
    print(f"正在获取论文 {arxiv_id} 的信息...", file=sys.stderr)
    title, abstract = fetch_arxiv_abstract(arxiv_id)
    
    if not title or not abstract:
        print("获取论文信息失败", file=sys.stderr)
        sys.exit(1)
    
    print(f"\n论文标题: {title}\n")
    print(f"摘要:\n{abstract}\n")
    print("="*60)
    print("请使用 paper-insights-deep skill 对以上论文进行深度解读")

if __name__ == "__main__":
    main()
