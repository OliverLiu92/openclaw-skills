#!/usr/bin/env python3
"""
ArXiv CS Weekly Paper Fetcher - 大象插件发送版
每周抓取 arXiv CS 最新论文并通过大象插件发送
"""

import re
import sys
import json
import os
import subprocess
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

class ArXivParser(HTMLParser):
    """解析 arXiv 论文列表"""
    
    def __init__(self):
        super().__init__()
        self.papers = []
        self.current_paper = {}
        self.in_item = False
        self.in_title = False
        self.in_authors = False
        self.in_subjects = False
        self.text_buffer = ""
        self.current_arxiv_id = None
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            if '/abs/' in href:
                arxiv_id = href.split('/abs/')[-1]
                if arxiv_id and not self.in_item:
                    self.in_item = True
                    self.current_paper = {'arxiv_id': arxiv_id}
                    self.current_arxiv_id = arxiv_id
        
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
            title = re.sub(r'^Title:\s*', '', self.text_buffer.strip())
            self.current_paper['title'] = title
            
        if self.in_authors and tag == 'div':
            self.in_authors = False
            authors_text = self.text_buffer.strip()
            authors_text = re.sub(r'^Authors:\s*', '', authors_text)
            authors_text = re.sub(r'<[^>]+>', '', authors_text)
            self.current_paper['authors'] = authors_text
            
        if self.in_subjects and tag == 'div':
            self.in_subjects = False
            subjects = re.sub(r'^Subjects:\s*', '', self.text_buffer.strip())
            self.current_paper['subjects'] = subjects
            
        if tag == 'dd' and self.in_item and self.current_paper:
            if self.current_paper.get('title'):
                self.papers.append(self.current_paper)
            self.in_item = False
            self.current_paper = {}
            
    def handle_data(self, data):
        if self.in_title or self.in_authors or self.in_subjects:
            self.text_buffer += data

def parse_papers(html_content):
    parser = ArXivParser()
    parser.feed(html_content)
    return parser.papers

def load_previous_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading state: {e}", file=sys.stderr)
    return {'last_paper_ids': [], 'last_check_date': None}

def save_state(paper_ids):
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
    current_ids = [p.get('arxiv_id') for p in papers if p.get('arxiv_id')]
    new_papers = [p for p in papers if p.get('arxiv_id') and p.get('arxiv_id') not in previous_ids]
    return new_papers, current_ids

def simplify_subject(subjects_text):
    if not subjects_text:
        return "计算机科学"
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

def generate_simple_summary(title):
    """从标题生成通俗化描述"""
    # 尝试提取关键信息
    keywords = []
    
    # 常见关键词映射
    keyword_map = {
        'llm': '大语言模型',
        'large language model': '大语言模型',
        'transformer': 'Transformer架构',
        'diffusion': '扩散模型',
        'gpt': 'GPT模型',
        'bert': 'BERT模型',
        'vision': '视觉',
        'image': '图像',
        'video': '视频',
        'robot': '机器人',
        'reinforcement': '强化学习',
        'fine-tuning': '微调',
        'pre-training': '预训练',
        'multimodal': '多模态',
        '3d': '3D',
        'generation': '生成',
        'understanding': '理解',
        'reasoning': '推理',
        'planning': '规划',
        'segmentation': '分割',
        'detection': '检测',
        'classification': '分类',
        'optimization': '优化',
        'efficient': '高效',
        'memory': '内存',
        'training': '训练',
        'inference': '推理',
        'sampling': '采样',
        'attention': '注意力机制',
        'embedding': '嵌入',
        'retrieval': '检索',
        'indexing': '索引',
        'compression': '压缩',
        'distillation': '知识蒸馏',
        'pruning': '剪枝',
        'quantization': '量化',
        'federated': '联邦学习',
        'adversarial': '对抗学习',
        'self-supervised': '自监督',
        'contrastive': '对比学习',
        'zero-shot': '零样本',
        'few-shot': '少样本',
        'prompt': '提示词',
        'chain-of-thought': '思维链',
        'rag': 'RAG检索增强',
        'agent': '智能体',
    }
    
    title_lower = title.lower()
    for en, cn in keyword_map.items():
        if en in title_lower and cn not in keywords:
            keywords.append(cn)
    
    if keywords:
        return f"研究{'、'.join(keywords[:3])}相关问题"
    return "探索计算机科学领域的新方法"

def format_paper_for_elephant(paper, index, is_new=False):
    """格式化单篇论文为大象消息格式"""
    title = paper.get('title', '未知标题')
    authors = paper.get('authors', '未知作者')
    arxiv_id = paper.get('arxiv_id', '')
    subjects = simplify_subject(paper.get('subjects', ''))
    
    # 简化作者列表
    author_list = [a.strip() for a in authors.split(',') if a.strip()]
    if len(author_list) > 3:
        authors_short = f"{', '.join(author_list[:3])} 等{len(author_list)}人"
    else:
        authors_short = authors
    
    summary = generate_simple_summary(title)
    new_mark = "🆕 " if is_new else ""
    
    return f"""{index}. {new_mark}*{title}*
   👤 {authors_short}
   🏷️ {subjects}
   💡 {summary}
   🔗 https://arxiv.org/abs/{arxiv_id}
"""

def generate_elephant_message(papers, new_papers_count, total_count):
    """生成大象消息格式"""
    now = datetime.now().strftime("%Y年%m月%d日")
    
    # 取前10篇
    display_papers = papers[:10]
    
    message = f"""📚 **ArXiv CS 论文周报** ({now})

本周新增 *{total_count}* 篇论文，其中 🆕 *{new_papers_count}* 篇为全新发布

---

"""
    
    # 加载上次状态以标记新论文
    state = load_previous_state()
    previous_ids = state.get('last_paper_ids', [])
    
    for i, paper in enumerate(display_papers, 1):
        is_new = paper.get('arxiv_id') not in previous_ids
        message += format_paper_for_elephant(paper, i, is_new) + "\n"
    
    if len(papers) > 10:
        message += f"\n...还有 {len(papers) - 10} 篇论文，查看完整列表：https://arxiv.org/list/cs/recent\n"
    
    message += """
---
🤖 *由 OpenClaw 自动生成*"""
    
    return message

def send_to_elephant(message):
    """通过大象插件发送消息 - 使用 cron 的 announce 模式自动发送"""
    # 实际发送由 OpenClaw cron 任务的 --announce 参数处理
    # 这里只打印消息内容供 cron 捕获
    print("\n" + "="*60, file=sys.stderr)
    print("📱 大象消息内容已生成（将由 cron 任务自动发送）", file=sys.stderr)
    print("="*60 + "\n", file=sys.stderr)
    return True

def main():
    print("正在获取 arXiv CS 最新论文...", file=sys.stderr)
    
    state = load_previous_state()
    previous_ids = state.get('last_paper_ids', [])
    
    html_content = fetch_arxiv_page()
    if not html_content:
        print("获取失败", file=sys.stderr)
        sys.exit(1)
    
    papers = parse_papers(html_content)
    print(f"找到 {len(papers)} 篇论文", file=sys.stderr)
    
    # 识别新论文
    new_papers, current_ids = identify_new_papers(papers, previous_ids)
    
    # 生成大象消息
    message = generate_elephant_message(papers, len(new_papers), len(papers))
    
    # 打印到 stdout（用于调试）
    print(message)
    
    # 发送到大象
    send_to_elephant(message)
    
    # 保存状态
    save_state(current_ids)
    print(f"已保存 {len(current_ids)} 篇论文 ID", file=sys.stderr)

if __name__ == "__main__":
    main()
