---
name: video_download
description: Downloads videos from major platforms (Bilibili, YouTube, Twitter/X, Instagram, TikTok, etc.) using yt-dlp. Supports quality selection, audio-only mode, and automatic platform detection.
---

# Video Download Tool

多平台视频下载工具，支持画质选择、平台自动识别、音频提取等功能。

## 支持平台

| 平台 | 域名 | 状态 |
|------|------|------|
| 📺 Bilibili | bilibili.com, b23.tv | ✅ 完全支持 |
| ▶️ YouTube | youtube.com, youtu.be | ✅ 完全支持 |
| 🐦 Twitter/X | twitter.com, x.com | ✅ 完全支持 |
| 📷 Instagram | instagram.com | ✅ 完全支持 |
| 🎵 TikTok | tiktok.com | ✅ 完全支持 |
| 🎬 其他 | 任何 yt-dlp 支持的网站 | ✅ 通用支持 |

## 功能特性

- ✅ **平台自动检测** - 根据URL自动识别视频平台
- ✅ **画质选择** - 交互式选择或自动选择最佳画质
- ✅ **音频提取** - 支持仅下载音频
- ✅ **默认目录** - 每个平台有独立的默认下载目录
- ✅ **统一输出** - 自动合并为 MP4 格式

## 使用方法

### 基础用法

```bash
# 下载视频（自动检测平台，交互选择画质）
python3 ~/.openclaw/workspace/skills/video_download/video_download.py "<URL>"

# 下载到指定目录
python3 ~/.openclaw/workspace/skills/video_download/video_download.py "<URL>" ~/Downloads
```

### 命令行选项

| 选项 | 说明 |
|------|------|
| `--auto`, `-y` | 自动选择最佳画质，跳过交互 |
| `--best`, `-b` | 强制使用最高质量 |
| `--audio-only` | 仅下载音频（MP3） |
| `--help`, `-h` | 显示帮助信息 |

### 示例

**下载B站视频：**
```bash
python3 ~/.openclaw/workspace/skills/video_download/video_download.py \
  "https://www.bilibili.com/video/BV1p6FrzTEHH"
```

**自动下载YouTube视频：**
```bash
python3 ~/.openclaw/workspace/skills/video_download/video_download.py \
  "https://youtube.com/watch?v=xxxxx" --auto
```

**下载Twitter视频到桌面：**
```bash
python3 ~/.openclaw/workspace/skills/video_download/video_download.py \
  "https://twitter.com/user/status/xxxxx" ~/Desktop
```

**仅提取音频：**
```bash
python3 ~/.openclaw/workspace/skills/video_download/video_download.py \
  "https://youtube.com/watch?v=xxxxx" --audio-only
```

## 默认下载目录

| 平台 | 默认目录 |
|------|----------|
| Bilibili | `~/Downloads/bilibili` |
| YouTube | `~/Downloads/youtube` |
| Twitter/X | `~/Downloads/twitter` |
| Instagram | `~/Downloads/instagram` |
| TikTok | `~/Downloads/tiktok` |
| 其他 | `~/Downloads/videos` |

## 依赖

- Python 3.7+
- yt-dlp (自动安装)

安装 yt-dlp：
```bash
pip3 install --user yt-dlp
```

## 注意事项

1. **会员内容** - B站1080P高码率及以上、YouTube Premium内容等需要登录/cookies
2. **地区限制** - 某些视频可能有地区限制
3. **尊重版权** - 请遵守各平台的服务条款和版权法规
4. **不要滥用** - 频繁下载可能触发平台限制

## 故障排除

**yt-dlp 未找到：**
```bash
pip3 install --user yt-dlp
# 或
python3 -m pip install --user yt-dlp
```

**需要登录/cookies：**
```bash
# 使用浏览器cookies
yt-dlp --cookies-from-browser chrome "<url>"
```

**下载失败：**
- 检查URL是否正确
- 确认视频未删除或设私密
- 尝试使用 `--auto` 跳过画质选择

## 进阶用法

直接使用 yt-dlp 的更多功能：

```bash
# 下载整个播放列表
yt-dlp -o "~/Downloads/%(playlist)s/%(title)s.%(ext)s" "<playlist_url>"

# 下载字幕
yt-dlp --write-subs --sub-langs zh-CN,en --convert-subs srt "<url>"

# 限制下载速度
yt-dlp -r 1M "<url>"

# 只下载元数据
yt-dlp --write-info-json --skip-download "<url>"
```
