#!/usr/bin/env python3
"""
Music Download Tool - 主流中文音乐平台下载器
支持: 网易云音乐, QQ音乐, 酷狗音乐, 酷我音乐等

⚠️ 免责声明：仅供个人学习研究使用，请支持正版音乐
"""

import subprocess
import sys
import os
import re
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

# 支持的平台配置
PLATFORMS = {
    'netease': {
        'name': '网易云音乐',
        'domains': ['music.163.com', '163.com'],
        'default_dir': '~/Music/NetEase',
        'emoji': '🎵'
    },
    'qq': {
        'name': 'QQ音乐',
        'domains': ['y.qq.com', 'qq.com'],
        'default_dir': '~/Music/QQMusic',
        'emoji': '🎶'
    },
    'kugou': {
        'name': '酷狗音乐',
        'domains': ['kugou.com'],
        'default_dir': '~/Music/Kugou',
        'emoji': '🎧'
    },
    'kuwo': {
        'name': '酷我音乐',
        'domains': ['kuwo.cn'],
        'default_dir': '~/Music/Kuwo',
        'emoji': '🎤'
    },
    'generic': {
        'name': '通用音频',
        'domains': [],
        'default_dir': '~/Music/Downloads',
        'emoji': '🎼'
    }
}

def detect_platform(url):
    """检测音乐平台"""
    # 移除URL中的hash部分
    url_clean = url.split('#')[0] if '#' in url else url
    domain = urlparse(url_clean).netloc.lower()
    
    for platform, config in PLATFORMS.items():
        if platform == 'generic':
            continue
        for pd in config['domains']:
            if pd in domain:
                return platform
    
    return 'generic'

def extract_netease_id(url):
    """提取网易云音乐ID和类型"""
    # 处理hash部分
    if '#' in url:
        hash_part = url.split('#')[1]
        url = 'https://music.163.com/' + hash_part
    
    # 解析URL
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    
    # 判断类型
    if '/playlist' in url or '/discover/playlist' in url:
        return 'playlist', query.get('id', [None])[0]
    elif '/song' in url:
        return 'song', query.get('id', [None])[0]
    elif '/album' in url:
        return 'album', query.get('id', [None])[0]
    
    # 尝试正则匹配
    match = re.search(r'id=(\d+)', url)
    if match:
        song_match = re.search(r'/song', url)
        playlist_match = re.search(r'/playlist', url)
        if song_match:
            return 'song', match.group(1)
        elif playlist_match:
            return 'playlist', match.group(1)
        return 'song', match.group(1)
    
    return None, None

def extract_qqmusic_id(url):
    """提取QQ音乐ID和类型"""
    # 解析URL
    parsed = urlparse(url)
    path = parsed.path
    query = parse_qs(parsed.query)
    
    # 判断类型
    if '/playlist' in path or '/ryqq/playlist' in path:
        # 尝试从路径提取
        match = re.search(r'playlist/(\d+)', path)
        if match:
            return 'playlist', match.group(1)
        return 'playlist', query.get('id', [None])[0]
    elif '/song' in path or '/ryqq/song' in path:
        match = re.search(r'song/(\d+)', path)
        if match:
            return 'song', match.group(1)
        return 'song', query.get('id', [None])[0]
    
    return None, None

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

def download_with_ytdlp(url, output_dir, quality='standard', audio_only=True):
    """使用yt-dlp下载音乐"""
    ytdlp_path = get_ytdlp_path()
    if not ytdlp_path:
        print("❌ yt-dlp 未找到")
        return None
    
    # 音质设置
    quality_map = {
        'standard': '128K',
        'high': '192K',
        'lossless': 'best'
    }
    audio_quality = quality_map.get(quality, '128K')
    
    # 构建下载命令
    cmd = [
        ytdlp_path,
        "-x",  # 仅提取音频
        "--audio-format", "mp3",
        "--audio-quality", audio_quality,
        "-o", os.path.join(output_dir, "%(title)s.%(ext)s"),
        "--no-warnings",
        "--progress",
        "--newline",
    ]
    
    # 如果是歌单，添加播放列表选项
    if 'playlist' in url.lower():
        cmd.extend(["--yes-playlist"])
    else:
        cmd.extend(["--no-playlist"])
    
    cmd.append(url)
    
    print(f"🎯 音质: {quality} ({audio_quality})")
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
    downloaded_files = []
    
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
                match = re.search(r'Destination:\s*(.+\.\w+)', line)
                if match:
                    downloaded_files.append(match.group(1).strip())
            elif 'has already been downloaded' in line:
                print(f"\n  ✅ {line}")
                match = re.search(r"'(.+?)' has already been downloaded", line)
                if match:
                    downloaded_files.append(match.group(1))
    
    print()  # 换行
    process.wait()
    
    if process.returncode != 0:
        print(f"\n⚠️ 下载可能未完成或部分失败")
        print("提示：部分歌曲可能受版权保护或需要VIP")
    
    return downloaded_files

def download_netease(url, output_dir, quality='standard'):
    """下载网易云音乐"""
    content_type, content_id = extract_netease_id(url)
    
    if not content_id:
        print("❌ 无法解析网易云音乐链接")
        return None
    
    print(f"🎵 检测到网易云音乐 {content_type}，ID: {content_id}")
    
    # 构造标准URL供yt-dlp使用
    if content_type == 'playlist':
        standard_url = f"https://music.163.com/#/playlist?id={content_id}"
    elif content_type == 'song':
        standard_url = f"https://music.163.com/#/song?id={content_id}"
    else:
        standard_url = url
    
    return download_with_ytdlp(standard_url, output_dir, quality)

def download_qqmusic(url, output_dir, quality='standard'):
    """下载QQ音乐"""
    content_type, content_id = extract_qqmusic_id(url)
    
    if not content_id:
        print("❌ 无法解析QQ音乐链接")
        return None
    
    print(f"🎶 检测到QQ音乐 {content_type}，ID: {content_id}")
    print("⚠️  QQ音乐支持有限，部分歌曲可能无法下载")
    
    return download_with_ytdlp(url, output_dir, quality)

def print_help():
    """打印帮助信息"""
    print("""
🎵 Music Download Tool - 中文音乐平台下载器

⚠️  免责声明：仅供个人学习研究使用，请支持正版音乐

用法: python music_download.py <URL> [输出目录] [选项]

支持平台:
  🎵 网易云音乐   - music.163.com
  🎶 QQ音乐       - y.qq.com
  🎧 酷狗音乐     - kugou.com (实验性)
  🎤 酷我音乐     - kuwo.cn (实验性)

选项:
  --quality, -q    音质选择: standard(128k), high(192k), lossless(无损)
  --metadata, -m   添加元数据（封面、歌词等）
  --lyrics, -l     下载歌词
  --help, -h       显示帮助

示例:
  # 下载网易云歌单
  python music_download.py "https://music.163.com/#/playlist?id=12999186542"

  # 下载高品质音频
  python music_download.py "https://music.163.com/#/song?id=123456789" --quality high

  # 指定输出目录
  python music_download.py "<URL>" ~/Music/Downloads

注意:
  - 部分歌曲受版权保护，无法下载
  - VIP歌曲需要登录cookies才能下载完整版
  - 支持正版音乐，尊重创作者权益
""")

def main():
    print("="*70)
    print("🎵 Music Download Tool")
    print("⚠️  仅供学习研究使用，请支持正版音乐")
    print("="*70)
    
    # 解析参数
    args = sys.argv[1:]
    
    # 检查帮助
    if not args or '--help' in args or '-h' in args:
        print_help()
        sys.exit(0)
    
    url = None
    output_dir = None
    quality = 'standard'
    
    # 提取参数
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('http'):
            url = arg
        elif arg in ['--quality', '-q'] and i + 1 < len(args):
            quality = args[i + 1]
            i += 1
        elif arg.startswith('~/') or arg.startswith('/') or (len(arg) > 1 and not arg.startswith('--')):
            output_dir = arg
        i += 1
    
    if not url:
        print("❌ 请提供音乐链接")
        print_help()
        sys.exit(1)
    
    # 检测平台
    platform = detect_platform(url)
    config = PLATFORMS[platform]
    
    print(f"\n{config['emoji']} 检测到平台: {config['name']}")
    
    # 设置输出目录
    if not output_dir:
        output_dir = config['default_dir']
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 输出目录: {output_dir}")
    
    # 确保依赖
    print("🔧 检查依赖...")
    ensure_ytdlp()
    
    # 根据平台下载
    if platform == 'netease':
        result = download_netease(url, output_dir, quality)
    elif platform == 'qq':
        result = download_qqmusic(url, output_dir, quality)
    else:
        print(f"⚠️  尝试通用下载方式...")
        result = download_with_ytdlp(url, output_dir, quality)
    
    # 输出结果
    print("\n" + "="*70)
    if result:
        print("✅ 下载完成!")
        print("="*70)
        if isinstance(result, list) and result:
            print(f"📦 共下载 {len(result)} 个文件")
            for f in result[:5]:  # 最多显示5个
                print(f"   📄 {f}")
            if len(result) > 5:
                print(f"   ... 还有 {len(result) - 5} 个文件")
    else:
        print("⚠️ 下载可能失败或未找到可下载内容")
        print("="*70)
        print("可能原因：")
        print("  • 歌曲受版权保护")
        print("  • 需要VIP会员权限")
        print("  • 链接格式不支持")
        print("  • 平台API变更")
        print("\n建议：")
        print("  • 检查链接是否正确")
        print("  • 尝试使用 cookies-from-browser 选项登录")
        print("  • 使用官方客户端下载")
    print("="*70)

if __name__ == "__main__":
    main()
