#!/usr/bin/env python3
"""
ArXiv CS Weekly Paper Fetcher - 增强版
每周抓取 arXiv CS 最新论文并整理成中文报告
"""

import re
import sys
import json
import os
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
from html.parser import HTMLParser

ARXIV_URL = "https://arxiv.org/list/cs/recent"
STATE_FILE = os.path.expanduser("~/.openclaw/workspace/.arxiv-cs-weekly-state.json")

def fetch_arxiv_page():
    """获取 arXiv 页面内容"""
    try:
        req = Request(
            ARXIV_URL,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        with urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except URLError as e:
        print(f"Error fetching arXiv: {e}", file=sys.stderr)
        return None

def fetch_paper_abstract(arxiv_id):
    """获取单篇论文的摘要"""
    try:
        url = f"https://arxiv.org/abs/{arxiv_id}"
        req = Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        with urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            # 提取摘要
            match = re.search(r'<blockquote[^>]*class="abstract mathjax"[^>]*>.*?<span[^>]*>Abstract:</span>(.*?)</blockquote>', html, re.DOTALL)
            if match:
                abstract = re.sub(r'<[^>]+>', '', match.group(1))
                return ' '.join(abstract.split())
    except Exception as e:
        print(f"Error fetching abstract for {arxiv_id}: {e}", file=sys.stderr)
    return None

class ArXivParser(HTMLParser):
    """解析 arXiv 论文列表"""
    
    def __init__(self):
        super().__init__()
        self.papers = []
        self.current_paper = {}
        self.in_item = False
        self.in_title = False
        self.in_authors = False
        self.in_comments = False
        self.in_subjects = False
        self.text_buffer = ""
        self.current_arxiv_id = None
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # 检测论文条目 - 从 arXiv ID 开始
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            if '/abs/' in href:
                arxiv_id = href.split('/abs/')[-1]
                if arxiv_id and not self.in_item:
                    self.in_item = True
                    self.current_paper = {'arxiv_id': arxiv_id}
                    self.current_arxiv_id = arxiv_id
        
        # 论文标题
        if tag == 'div' and attrs_dict.get('class') == 'list-title mathjax':
            self.in_title = True
            self.text_buffer = ""
            
        # 作者
        if tag == 'div' and attrs_dict.get('class') == 'list-authors':
            self.in_authors = True
            self.text_buffer = ""
            
        # 学科分类
        if tag == 'div' and attrs_dict.get('class') == 'list-subjects':
            self.in_subjects = True
            self.text_buffer = ""
            
    def handle_endtag(self, tag):
        if self.in_title and tag == 'div':
            self.in_title = False
            title = re.sub(r'^Title:\s*', '', self.text_buffer.strip())
            self.current_paper['title'] = title
            
        if self.in_authors and tag == 'div':
            self.in_authors = False
            # 提取纯文本作者名
            authors_text = self.text_buffer.strip()
            authors_text = re.sub(r'^Authors:\s*', '', authors_text)
            authors_text = re.sub(r'<[^>]+>', '', authors_text)
            self.current_paper['authors'] = authors_text
            
        if self.in_subjects and tag == 'div':
            self.in_subjects = False
            subjects = re.sub(r'^Subjects:\s*', '', self.text_buffer.strip())
            self.current_paper['subjects'] = subjects
            
        # 条目结束
        if tag == 'dd' and self.in_item and self.current_paper:
            if self.current_paper.get('title'):
                self.papers.append(self.current_paper)
            self.in_item = False
            self.current_paper = {}
            
    def handle_data(self, data):
        if self.in_title or self.in_authors or self.in_subjects:
            self.text_buffer += data

def parse_papers(html_content):
    """解析 HTML 提取论文信息"""
    parser = ArXivParser()
    parser.feed(html_content)
    return parser.papers

def load_previous_state():
    """加载上次记录的论文 ID"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading state: {e}", file=sys.stderr)
    return {'last_paper_ids': [], 'last_check_date': None}

def save_state(paper_ids):
    """保存当前论文 ID 列表"""
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump({
                'last_paper_ids': paper_ids,
                'last_check_date': datetime.now().isoformat()
            }, f)
    except Exception as e:
        print(f"Error saving state: {e}", file=sys.stderr)

def identify_new_papers(papers, previous_ids):
    """识别新论文"""
    current_ids = [p.get('arxiv_id') for p in papers if p.get('arxiv_id')]
    new_papers = [p for p in papers if p.get('arxiv_id') and p.get('arxiv_id') not in previous_ids]
    return new_papers, current_ids

def simplify_subject(subjects_text):
    """简化学科分类显示"""
    if not subjects_text:
        return "计算机科学"
    # 提取括号内的短代码
    codes = re.findall(r'\((cs\.[A-Z]+)\)', subjects_text)
    if codes:
        subject_map = {
            'cs.AI': '人工智能',
            'cs.CL': '计算语言学/NLP',
            'cs.CV': '计算机视觉',
            'cs.LG': '机器学习',
            'cs.RO': '机器人学',
            'cs.DB': '数据库',
            'cs.DC': '分布式计算',
            'cs.SE': '软件工程',
            'cs.CR': '密码学与安全',
            'cs.HC': '人机交互',
            'cs.IR': '信息检索',
            'cs.MM': '多媒体',
            'cs.NE': '神经与进化计算',
            'cs.OS': '操作系统',
            'cs.PF': '性能计算',
            'cs.PL': '编程语言',
            'cs.SC': '科学计算',
            'cs.SY': '系统与控制',
        }
        names = [subject_map.get(c, c) for c in codes[:2]]
        return '、'.join(names) if names else subjects_text
    return subjects_text

def generate_simple_summary(title, abstract):
    """生成通俗化的问题描述"""
    if not abstract:
        return "暂无详细摘要"
    
    # 简化摘要，提取核心问题
    # 通常前两句包含核心贡献
    sentences = abstract.split('. ')
    if len(sentences) >= 2:
        summary = '. '.join(sentences[:2]) + '.'
    else:
        summary = abstract[:300] + '...' if len(abstract) > 300 else abstract
    
    return summary

def generate_report(papers, previous_ids=None, max_papers=15, fetch_abstracts=False):
    """生成中文报告"""
    if not papers:
        return "未找到论文数据。"
    
    # 识别新论文
    if previous_ids:
        new_papers, current_ids = identify_new_papers(papers, previous_ids)
        is_new_mark = lambda pid: "🆕 " if pid not in previous_ids else ""
    else:
        new_papers = papers
        current_ids = [p.get('arxiv_id') for p in papers]
        is_new_mark = lambda pid: ""
    
    now = datetime.now().strftime("%Y年%m月%d日")
    
    report = f"""# 📚 arXiv CS 最新论文周报

> **报告时间**：{now}  
> **来源**：[arXiv CS Recent](https://arxiv.org/list/cs/recent)  
> **本周论文总数**：{len(papers)} 篇  
> **新增论文**：{len(new_papers)} 篇  
> **以下展示前 {min(max_papers, len(papers))} 篇**

---

"""
    
    for i, paper in enumerate(papers[:max_papers], 1):
        title = paper.get('title', '未知标题')
        authors = paper.get('authors', '未知作者')
        arxiv_id = paper.get('arxiv_id', '')
        subjects = simplify_subject(paper.get('subjects', ''))
        
        # 简化作者列表
        author_list = [a.strip() for a in authors.split(',') if a.strip()]
        if len(author_list) > 3:
            authors_short = f"{', '.join(author_list[:3])} 等 {len(author_list)} 位作者"
        else:
            authors_short = authors
        
        # 获取摘要
        abstract = paper.get('abstract', '')
        if not abstract and fetch_abstracts and arxiv_id:
            print(f"正在获取 {arxiv_id} 的摘要...", file=sys.stderr)
            abstract = fetch_paper_abstract(arxiv_id) or "暂无摘要"
        
        summary = generate_simple_summary(title, abstract) if abstract else "暂无摘要"
        new_mark = is_new_mark(arxiv_id)
        
        report += f"""## {i}. {new_mark}{title}

**作者**：{authors_short}  
**arXiv ID**：{arxiv_id}  
**领域**：{subjects}  
**核心问题**：{summary}

---

"""
    
    # 添加页脚
    report += """## 📊 总结

本周 arXiv CS 领域共有 **""" + str(len(papers)) + """** 篇新论文，涵盖 """ + subjects + """ 等方向。

---

*报告由 OpenClaw arxiv-cs-weekly Skill 自动生成*
"""
    
    return report, current_ids

def main():
    """主函数"""
    print("正在获取 arXiv CS 最新论文...", file=sys.stderr)
    
    # 加载上次状态
    state = load_previous_state()
    previous_ids = state.get('last_paper_ids', [])
    last_check = state.get('last_check_date')
    
    if last_check:
        print(f"上次检查时间: {last_check}", file=sys.stderr)
    
    html_content = fetch_arxiv_page()
    if not html_content:
        print("获取失败", file=sys.stderr)
        sys.exit(1)
    
    papers = parse_papers(html_content)
    print(f"找到 {len(papers)} 篇论文", file=sys.stderr)
    
    # 检查是否需要获取详细摘要（命令行参数 --full）
    fetch_abstracts = '--full' in sys.argv
    
    report, current_ids = generate_report(papers, previous_ids, max_papers=15, fetch_abstracts=fetch_abstracts)
    print(report)
    
    # 保存状态
    save_state(current_ids)
    print(f"\n已保存 {len(current_ids)} 篇论文 ID 到状态文件", file=sys.stderr)

if __name__ == "__main__":
    main()
