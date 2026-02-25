#!/usr/bin/env python3
"""
ArXiv CS Weekly - 报告生成器
生成适合大象发送的格式化报告
"""

import re
import json
import os
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
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
        return "计算机科学"
    codes = re.findall(r'\((cs\.[A-Z]+)\)', text)
    if codes:
        mapping = {
            'cs.AI': 'AI', 'cs.CL': 'NLP', 'cs.CV': 'CV',
            'cs.LG': 'ML', 'cs.RO': '机器人', 'cs.DB': '数据库',
            'cs.SE': '软件工程', 'cs.CR': '安全', 'cs.IR': '信息检索'
        }
        names = [mapping.get(c, c) for c in codes[:2]]
        return '、'.join(names)
    return text

def get_keywords(title):
    keywords = []
    t = title.lower()
    maps = {
        'llm': 'LLM', 'language model': 'LLM', 'transformer': 'Transformer',
        'diffusion': '扩散模型', 'vision': '视觉', 'image': '图像',
        'video': '视频', 'robot': '机器人', 'reinforcement': 'RL',
        'multimodal': '多模态', '3d': '3D', 'optimization': '优化',
        'attention': '注意力', 'embedding': 'Embedding', 'rag': 'RAG',
        'agent': 'Agent', 'prompt': 'Prompt', 'fine-tuning': '微调',
        'zero-shot': '零样本', 'chain-of-thought': 'CoT'
    }
    for k, v in maps.items():
        if k in t and v not in keywords:
            keywords.append(v)
    return keywords[:3]

def generate_report():
    html = fetch_page()
    if not html:
        return None
    
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
        f"本周新增 *{len(papers)}* 篇，🆕 全新 *{len(new_papers)}* 篇",
        ""
    ]
    
    for i, p in enumerate(papers[:10], 1):
        title = p.get('title', '未知')
        authors = p.get('authors', '未知')
        aid = p.get('arxiv_id', '')
        subj = simplify_subject(p.get('subjects', ''))
        
        alist = [a.strip() for a in authors.split(',') if a.strip()]
        if len(alist) > 2:
            authors_short = f"{', '.join(alist[:2])} 等{len(alist)}人"
        else:
            authors_short = authors
        
        kws = get_keywords(title)
        kw_str = f"【{' · '.join(kws)}】" if kws else ""
        is_new = "🆕 " if aid not in prev_ids else ""
        
        lines.append(f"{i}. {is_new}*{title}* {kw_str}")
        lines.append(f"   👤 {authors_short} | 🏷️ {subj}")
        lines.append(f"   🔗 https://arxiv.org/abs/{aid}")
        lines.append("")
    
    if len(papers) > 10:
        lines.append(f"📎 还有 {len(papers)-10} 篇: https://arxiv.org/list/cs/recent")
        lines.append("")
    
    lines.append("---")
    lines.append("🤖 *OpenClaw 自动生成*")
    
    save_state(current_ids)
    return "\n".join(lines)

if __name__ == "__main__":
    report = generate_report()
    if report:
        print(report)
    else:
        print("获取论文失败")
        exit(1)
