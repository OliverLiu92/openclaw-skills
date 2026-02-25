#!/usr/bin/env python3
"""
Video Download Tool - 多平台视频下载器
支持: Bilibili, YouTube, Twitter/X, Instagram, TikTok 及更多 yt-dlp 支持的平台
"""

import subprocess
import sys
import os
import re
from pathlib import Path
from urllib.parse import urlparse

# 支持的平台配置
PLATFORMS = {
    'bilibili': {
        'name': '哔哩哔哩',
        'domains': ['bilibili.com', 'b23.tv'],
        'default_dir': '~/Downloads/bilibili',
        'emoji': '📺'
    },
    'youtube': {
        'name': 'YouTube',
        'domains': ['youtube.com', 'youtu.be', 'youtube-nocookie.com'],
        'default_dir': '~/Downloads/youtube',
        'emoji': '▶️'
    },
    'twitter': {
        'name': 'Twitter/X',
        'domains': ['twitter.com', 'x.com'],
        'default_dir': '~/Downloads/twitter',
        'emoji': '🐦'
    },
    'instagram': {
        'name': 'Instagram',
        'domains': ['instagram.com'],
        'default_dir': '~/Downloads/instagram',
        'emoji': '📷'
    },
    'tiktok': {
        'name': 'TikTok',
        'domains': ['tiktok.com'],
        'default_dir': '~/Downloads/tiktok',
        'emoji': '🎵'
    },
    'generic': {
        'name': '通用视频',
        'domains': [],
        'default_dir': '~/Downloads/videos',
        'emoji': '🎬'
    }
}

def detect_platform(url):
    """检测视频平台"""
    domain = urlparse(url).netloc.lower()
    
    for platform, config in PLATFORMS.items():
        if platform == 'generic':
            continue
        for pd in config['domains']:
            if pd in domain:
                return platform
    
    return 'generic'

def run_command(cmd, cwd=None):
    """运行命令并返回输出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr

def get_ytdlp_path():
    """获取yt-dlp的路径"""
    ret, stdout, _ = run_command("command -v yt-dlp")
    if ret == 0:
        return stdout.strip()
    
    # 常见安装路径
    paths = [
        os.path.expanduser("~/Library/Python/3.9/bin/yt-dlp"),
        os.path.expanduser("~/Library/Python/3.11/bin/yt-dlp"),
        os.path.expanduser("~/.local/bin/yt-dlp"),
        "/usr/local/bin/yt-dlp",
        "/opt/homebrew/bin/yt-dlp",
    ]
    
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def ensure_ytdlp():
    """确保yt-dlp已安装"""
    if get_ytdlp_path() is None:
        print("📦 正在安装 yt-dlp...")
        ret, _, _ = run_command("pip3 install --user yt-dlp")
        if ret != 0:
            run_command("python3 -m pip install --user yt-dlp")
    return True

def validate_url(url):
    """验证URL是否为有效视频链接"""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False
    return True

def list_formats(url):
    """列出视频可用的所有格式"""
    ytdlp_path = get_ytdlp_path()
    if not ytdlp_path:
        return None
    
    print("🔍 正在获取可用格式列表...")
    cmd = [ytdlp_path, "-F", "--no-warnings", url]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 获取格式列表失败: {result.stderr}")
        return None
    
    return result.stdout

def parse_video_formats(format_output):
    """解析yt-dlp的格式输出"""
    formats = []
    lines = format_output.split('\n')
    
    for line in lines:
        # 跳过表头和分隔线
        if '─' in line or line.strip().startswith('ID') or not line.strip():
            continue
        
        # 解析格式行
        parts = line.split()
        if len(parts) >= 3 and parts[0].isdigit():
            fmt_id = parts[0]
            ext = parts[1]
            resolution = parts[2] if 'x' in parts[2] or 'p' in parts[2] else 'audio'
            
            # 提取文件大小
            size = ""
            for p in parts:
                if 'MiB' in p or 'GiB' in p or 'KiB' in p:
                    size = p
                    break
            
            # 提取codec
            codec = ""
            line_lower = line.lower()
            if 'avc' in line_lower or 'h264' in line_lower:
                codec = "H.264"
            elif 'hev' in line_lower or 'h265' in line_lower:
                codec = "H.265"
            elif 'av01' in line_lower:
                codec = "AV1"
            elif 'vp9' in line_lower:
                codec = "VP9"
            elif 'opus' in line_lower:
                codec = "Opus"
            elif 'aac' in line_lower:
                codec = "AAC"
            
            # 只保留视频格式
            if 'video' in line or ('x' in resolution and 'audio' not in line):
                formats.append({
                    'id': fmt_id,
                    'ext': ext,
                    'resolution': resolution,
                    'size': size,
                    'codec': codec
                })
    
    return formats

def select_quality(formats, auto_select=False):
    """选择画质"""
    if not formats:
        return None
    
    # 按分辨率排序
    def get_height(fmt):
        res = fmt['resolution']
        if 'x' in res:
            try:
                return int(res.split('x')[1])
            except:
                return 0
        elif res.endswith('p'):
            try:
                return int(res[:-1])
            except:
                return 0
        return 0
    
    formats = sorted(formats, key=get_height, reverse=True)
    
    # 去重（同分辨率只保留第一个）
    unique_formats = []
    seen_res = set()
    for fmt in formats:
        if fmt['resolution'] not in seen_res:
            seen_res.add(fmt['resolution'])
            unique_formats.append(fmt)
    
    if auto_select:
        return None  # 使用yt-dlp默认最佳
    
    # 显示选项
    print("\n" + "="*70)
    print("📺 可用画质选项:")
    print("="*70)
    print(f"{'编号':<6} {'格式ID':<8} {'分辨率':<12} {'编码':<8} {'大小':<10}")
    print("-"*70)
    
    for i, fmt in enumerate(unique_formats[:15]):
        print(f"{i+1:<6} {fmt['id']:<8} {fmt['resolution']:<12} {fmt['codec']:<8} {fmt['size']:<10}")
    
    print("-"*70)
    print(f"{'A':<6} {'自动':<8} {'最佳画质':<12} {'自动':<8} {'自动':<10}")
    print("="*70)
    
    # 询问选择
    while True:
        choice = input("\n👉 请选择画质编号 (输入数字或A自动选择，默认A): ").strip().upper()
        
        if choice == '' or choice == 'A':
            return None
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(unique_formats):
                return unique_formats[idx]['id']
            else:
                print("❌ 无效的选择")
        except ValueError:
            print("❌ 请输入数字或A")

def get_output_filename(url, platform, ytdlp_path):
    """使用yt-dlp获取输出文件名（模拟）"""
    cmd = [ytdlp_path, "--print", "filename", "-o", "%(title)s [%(id)s].%(ext)s", "--no-download", url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def download_video(url, output_dir, format_id=None, platform='generic'):
    """下载视频"""
    config = PLATFORMS.get(platform, PLATFORMS['generic'])
    
    print(f"\n{config['emoji']} 开始下载 {config['name']} 视频")
    print(f"📁 输出目录: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    ytdlp_path = get_ytdlp_path()
    if not ytdlp_path:
        print("❌ yt-dlp 未找到")
        return None
    
    # 构建下载命令
    if format_id:
        format_spec = f"{format_id}+bestaudio/best"
    else:
        format_spec = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
    
    cmd = [
        ytdlp_path,
        "--no-playlist",
        "--merge-output-format", "mp4",
        "--remux-video", "mp4",
        "-f", format_spec,
        "-o", os.path.join(output_dir, "%(title)s [%(id)s].%(ext)s"),
        "--no-warnings",
        "--progress",
        "--newline",
        url
    ]
    
    print(f"\n🎯 下载格式: {format_spec}")
    print("⬇️  开始下载...\n")
    
    # 执行下载
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    last_progress = ""
    downloaded_file = None
    
    for line in process.stdout:
        line = line.strip()
        if not line:
            continue
        
        # 解析进度
        if '[download]' in line:
            if '%' in line:
                if line != last_progress:
                    print(f"\r  📥 {line}", end='', flush=True)
                    last_progress = line
            elif 'Destination:' in line:
                print(f"\n  📄 {line}")
                # 提取文件名
                match = re.search(r'Destination:\s*(.+)', line)
                if match:
                    downloaded_file = match.group(1).strip()
            elif 'has already been downloaded' in line:
                print(f"\n  ✅ {line}")
        elif 'Merger' in line or 'Merging' in line:
            print(f"\n  🔄 {line}")
        elif 'ERROR' in line:
            print(f"\n  ⚠️  {line}")
    
    print()  # 换行
    process.wait()
    
    if process.returncode != 0:
        print(f"\n❌ 下载失败")
        return None
    
    # 查找下载的文件
    if not downloaded_file:
        # 尝试在输出目录中查找最新文件
        files = sorted(
            [f for f in os.listdir(output_dir) if f.endswith(('.mp4', '.webm', '.mkv'))],
            key=lambda x: os.path.getmtime(os.path.join(output_dir, x)),
            reverse=True
        )
        if files:
            downloaded_file = os.path.join(output_dir, files[0])
    
    return downloaded_file

def print_help():
    """打印帮助信息"""
    print("""
📥 Video Download Tool - 多平台视频下载器

用法: python video_download.py <URL> [输出目录] [选项]

支持平台:
  📺 Bilibili   - bilibili.com, b23.tv
  ▶️  YouTube    - youtube.com, youtu.be
  🐦 Twitter/X  - twitter.com, x.com
  📷 Instagram  - instagram.com
  🎵 TikTok     - tiktok.com
  🎬 其他        - 任何 yt-dlp 支持的网站

选项:
  --auto, -y       自动选择最佳画质
  --best, -b       强制使用最佳质量
  --audio-only     仅下载音频
  --help, -h       显示帮助

示例:
  # 下载B站视频（交互选择画质）
  python video_download.py "https://www.bilibili.com/video/BV1xxxxx"

  # 下载YouTube视频到指定目录
  python video_download.py "https://youtube.com/watch?v=xxxxx" ~/Videos

  # 自动下载Twitter视频
  python video_download.py "https://twitter.com/..." --auto

  # 仅下载音频
  python video_download.py "https://youtube.com/watch?v=xxxxx" --audio-only
""")

def main():
    # 解析参数
    args = sys.argv[1:]
    
    # 检查帮助
    if not args or '--help' in args or '-h' in args:
        print_help()
        sys.exit(0)
    
    url = None
    output_dir = None
    auto_mode = '--auto' in args or '-y' in args
    best_mode = '--best' in args or '-b' in args
    audio_only = '--audio-only' in args
    
    # 提取URL和输出目录
    for arg in args:
        if arg.startswith('http'):
            url = arg
        elif arg.startswith('~/') or arg.startswith('/') or (len(arg) > 1 and not arg.startswith('--')):
            output_dir = arg
        elif not arg.startswith('-'):
            output_dir = arg
    
    if not url:
        print("❌ 请提供视频URL")
        print_help()
        sys.exit(1)
    
    if not validate_url(url):
        print("❌ 无效的URL")
        sys.exit(1)
    
    # 检测平台
    platform = detect_platform(url)
    config = PLATFORMS[platform]
    
    print(f"\n{config['emoji']} 检测到平台: {config['name']}")
    
    # 设置输出目录
    if not output_dir:
        output_dir = config['default_dir']
    output_dir = os.path.expanduser(output_dir)
    
    # 确保依赖
    print("🔧 检查依赖...")
    ensure_ytdlp()
    
    # 获取格式列表
    if not audio_only and not best_mode:
        format_output = list_formats(url)
        if format_output:
            formats = parse_video_formats(format_output)
            format_id = select_quality(formats, auto_select=auto_mode)
        else:
            format_id = None
    elif best_mode:
        format_id = None  # yt-dlp默认最佳
    else:
        format_id = "bestaudio" if audio_only else None
    
    # 下载
    result = download_video(url, output_dir, format_id, platform)
    
    if result:
        print("\n" + "="*70)
        print("✅ 下载完成!")
        print("="*70)
        print(f"📁 文件: {result}")
        if os.path.exists(result):
            size = os.path.getsize(result) / (1024 * 1024)
            print(f"📦 大小: {size:.1f} MB")
        print("="*70)
    else:
        print("\n❌ 下载失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
