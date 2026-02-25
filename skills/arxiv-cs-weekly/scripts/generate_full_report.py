#!/usr/bin/env python3
"""
ArXiv CS Weekly - 完整版（含摘要）
生成包含论文摘要的周报，方便用户选择感兴趣的论文进行深入解读
"""

import re
import json
import os
from datetime import datetime
from urllib.request import urlopen, Request
from html.parser import HTMLParser

ARXIV_URL = "https://arxiv.org/list/cs/recent"
STATE_FILE = os.path.expanduser("~/.openclaw/workspace/.arxiv-cs-weekly-state.json")

class ArXivParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.papers = []
        self.current_paper = {}
        self.in_item = False
        self.in_title = False
        self.in_authors = False
        self.in_subjects = False
        self.text_buffer = ""
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            if '/abs/' in href:
                arxiv_id = href.split('/abs/')[-1]
                if arxiv_id and not self.in_item:
                    self.in_item = True
                    self.current_paper = {'arxiv_id': arxiv_id}
        
        if tag == 'div' and attrs_dict.get('class') == 'list-title mathjax':
            self.in_title = True
            self.text_buffer = ""
        if tag == 'div' and attrs_dict.get('class') == 'list-authors':
            self.in_authors = True
            self.text_buffer = ""
        if tag == 'div' and attrs_dict.get('class') == 'list-subjects':
            self.in_subjects = True
            self.text_buffer = ""
            
    def handle_endtag(self, tag):
        if self.in_title and tag == 'div':
            self.in_title = False
            self.current_paper['title'] = re.sub(r'^Title:\s*', '', self.text_buffer.strip())
        if self.in_authors and tag == 'div':
            self.in_authors = False
            authors = re.sub(r'^Authors:\s*', '', self.text_buffer.strip())
            self.current_paper['authors'] = re.sub(r'<[^>]+>', '', authors)
        if self.in_subjects and tag == 'div':
            self.in_subjects = False
            self.current_paper['subjects'] = re.sub(r'^Subjects:\s*', '', self.text_buffer.strip())
        if tag == 'dd' and self.in_item and self.current_paper:
            if self.current_paper.get('title'):
                self.papers.append(self.current_paper)
            self.in_item = False
            self.current_paper = {}
            
    def handle_data(self, data):
        if self.in_title or self.in_authors or self.in_subjects:
            self.text_buffer += data

def fetch_page():
    try:
        req = Request(ARXIV_URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
        with urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error: {e}", file=os.sys.stderr)
        return None

def fetch_abstract(arxiv_id):
    """获取单篇论文的摘要"""
    try:
        url = f"https://arxiv.org/abs/{arxiv_id}"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
        with urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            # 提取摘要
            match = re.search(r'<blockquote[^>]*class="abstract mathjax"[^>]*>.*?<span[^>]*>Abstract:</span>(.*?)</blockquote>', html, re.DOTALL)
            if match:
                abstract = re.sub(r'<[^>]+>', '', match.group(1))
                abstract = ' '.join(abstract.split())  # 清理空白
                return abstract[:500] + "..." if len(abstract) > 500 else abstract
    except Exception as e:
        print(f"获取摘要失败 {arxiv_id}: {e}", file=os.sys.stderr)
    return "[摘要获取失败]"

def load_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {'last_paper_ids': [], 'last_check_date': None}

def save_state(paper_ids):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump({'last_paper_ids': paper_ids, 'last_check_date': datetime.now().isoformat()}, f)
    except:
        pass

def simplify_subject(text):
    if not text:
        return "CS"
    codes = re.findall(r'\((cs\.[A-Z]+)\)', text)
    if codes:
        mapping = {
            'cs.AI': 'AI', 'cs.CL': 'NLP', 'cs.CV': 'CV',
            'cs.LG': 'ML', 'cs.RO': '机器人', 'cs.DB': '数据库',
            'cs.SE': '软件工程', 'cs.CR': '安全', 'cs.IR': 'IR',
            'cs.MM': '多媒体', 'cs.DC': '分布式', 'cs.OS': '系统',
            'cs.PL': '编程语言', 'cs.SC': '科学计算'
        }
        names = [mapping.get(c, c) for c in codes[:2]]
        return '、'.join(names)
    return text

def get_keywords(title):
    keywords = []
    t = title.lower()
    maps = {
        'llm': 'LLM', 'language model': 'LLM', 'transformer': 'Transformer',
        'diffusion': '扩散', 'vision': '视觉', 'image': '图像',
        'video': '视频', 'robot': '机器人', 'reinforcement': 'RL',
        'multimodal': '多模态', '3d': '3D', 'optimization': '优化',
        'attention': '注意力', 'embedding': 'Embedding', 'rag': 'RAG',
        'agent': 'Agent', 'prompt': 'Prompt', 'fine-tuning': '微调',
        'zero-shot': '零样本', 'chain-of-thought': 'CoT',
        'test-time': 'TTT', 'training': '训练', 'inference': '推理'
    }
    for k, v in maps.items():
        if k in t and v not in keywords:
            keywords.append(v)
    return keywords[:3]

def generate_full_report():
    """生成完整报告，包含摘要"""
    html = fetch_page()
    if not html:
        return None, []
    
    parser = ArXivParser()
    parser.feed(html)
    papers = parser.papers
    
    state = load_state()
    prev_ids = state.get('last_paper_ids', [])
    
    current_ids = [p.get('arxiv_id') for p in papers if p.get('arxiv_id')]
    new_papers = [p for p in papers if p.get('arxiv_id') and p.get('arxiv_id') not in prev_ids]
    
    now = datetime.now().strftime("%Y年%m月%d日")
    
    lines = [
        f"📚 **ArXiv CS 论文周报** ({now})",
        "",
        f"本周新增 *{len(papers)}* 篇论文，🆕 全新 *{len(new_papers)}* 篇",
        "",
        "💡 **提示**：如对某篇论文感兴趣，可回复 \"解读第X篇\" 或 \"解读 arXiv:ID\"",
        "",
        "---",
        ""
    ]
    
    # 取前10篇，每篇都获取摘要
    display_count = min(10, len(papers))
    
    for i, p in enumerate(papers[:display_count], 1):
        title = p.get('title', '未知')
        authors = p.get('authors', '未知')
        aid = p.get('arxiv_id', '')
        subj = simplify_subject(p.get('subjects', ''))
        
        alist = [a.strip() for a in authors.split(',') if a.strip()]
        if len(alist) > 3:
            authors_short = f"{', '.join(alist[:3])} 等{len(alist)}人"
        else:
            authors_short = authors
        
        kws = get_keywords(title)
        kw_str = f"「{' · '.join(kws)}」" if kws else ""
        is_new = "🆕 " if aid not in prev_ids else ""
        
        # 获取摘要
        print(f"正在获取论文 {i}/{display_count} 的摘要...", file=os.sys.stderr)
        abstract = fetch_abstract(aid)
        
        lines.append(f"### {i}. {is_new}{title}")
        if kw_str:
            lines.append(kw_str)
        lines.append(f"👤 {authors_short} | 🏷️ {subj} | 🆔 {aid}")
        lines.append(f"🔗 https://arxiv.org/abs/{aid}")
        lines.append("")
        lines.append(f"📝 **摘要**：{abstract}")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # 其他论文简单列出
    if len(papers) > display_count:
        lines.append("### 📎 更多论文")
        lines.append("")
        for i, p in enumerate(papers[display_count:display_count+10], display_count+1):
            title = p.get('title', '未知')[:50] + "..." if len(p.get('title', '')) > 50 else p.get('title', '未知')
            aid = p.get('arxiv_id', '')
            subj = simplify_subject(p.get('subjects', ''))
            is_new = "🆕 " if aid not in prev_ids else ""
            lines.append(f"{i}. {is_new}*{title}* ({subj}) - [arXiv:{aid}](https://arxiv.org/abs/{aid})")
        lines.append("")
        if len(papers) > display_count + 10:
            lines.append(f"...还有 {len(papers) - display_count - 10} 篇")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("🤖 *OpenClaw 自动生成* | 回复 \"解读第N篇\" 获取深度分析")
    
    save_state(current_ids)
    return "\n".join(lines), papers[:display_count]

if __name__ == "__main__":
    report, papers = generate_full_report()
    if report:
        print(report)
        print("\n" + "="*60, file=os.sys.stderr)
        print(f"周报生成完成！共 {len(papers)} 篇论文带摘要", file=os.sys.stderr)
        print("="*60, file=os.sys.stderr)
    else:
        print("获取论文失败")
        exit(1)
