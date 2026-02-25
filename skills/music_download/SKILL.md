---
name: music_download
description: Downloads music from major Chinese music platforms (NetEase Cloud Music 网易云音乐, QQ Music, etc.) using yt-dlp and alternative methods. Supports playlists and individual tracks.
---

# Music Download Tool

主流中文音乐平台下载工具，支持网易云音乐、QQ音乐等。

## ⚠️ 免责声明

本工具仅供**个人学习研究**使用：
- 下载的音乐受版权保护
- 请遵守各平台的服务条款
- 请勿传播或用于商业用途
- 支持正版音乐，尊重创作者权益
- 部分歌曲需要VIP会员才能完整下载

## 支持平台

| 平台 | 状态 | 说明 |
|------|------|------|
| 🎵 网易云音乐 | ⚠️ 部分支持 | 取决于版权保护程度 |
| 🎶 QQ音乐 | ⚠️ 部分支持 | VIP歌曲可能无法下载 |
| 🎧 酷狗音乐 | ⚠️ 实验性 | 支持有限 |
| 🎤 酷我音乐 | ⚠️ 实验性 | 支持有限 |
| 🎼 Bilibili音频 | ✅ 支持较好 | 不受版权限制的内容 |
| 🎬 YouTube Music | ✅ 支持 | 需科学上网 |

## 使用方法

### 基础用法

```bash
# 下载网易云歌单
python3 ~/.openclaw/workspace/skills/music_download/music_download.py \
  "https://music.163.com/#/playlist?id=12999186542"

# 下载单曲
python3 ~/.openclaw/workspace/skills/music_download/music_download.py \
  "https://music.163.com/#/song?id=123456789"

# 下载QQ音乐
python3 ~/.openclaw/workspace/skills/music_download/music_download.py \
  "https://y.qq.com/n/ryqq/playlist/1234567890"

# 指定输出目录
python3 ~/.openclaw/workspace/skills/music_download/music_download.py \
  "<URL>" ~/Music/Downloads
```

### 命令行选项

| 选项 | 说明 |
|------|------|
| `--audio-only`, `-a` | 仅下载音频（默认） |
| `--quality`, `-q` | 音质选择：standard(128k), high(192k), lossless(无损) |
| `--metadata`, `-m` | 添加元数据（封面、歌词等） |
| `--lyrics`, `-l` | 下载歌词 |
| `--help`, `-h` | 显示帮助 |

### 示例

**下载网易云歌单（标准音质）：**
```bash
python3 ~/.openclaw/workspace/skills/music_download/music_download.py \
  "https://music.163.com/#/playlist?id=12999186542" \
  --quality standard
```

**下载高品质音频并添加元数据：**
```bash
python3 ~/.openclaw/workspace/skills/music_download/music_download.py \
  "https://music.163.com/#/song?id=123456789" \
  --quality high --metadata --lyrics
```

## 默认下载目录

| 平台 | 默认目录 |
|------|----------|
| 网易云音乐 | `~/Music/NetEase` |
| QQ音乐 | `~/Music/QQMusic` |
| 其他 | `~/Music/Downloads` |

## 依赖

- Python 3.7+
- yt-dlp
- requests (用于API调用)
- mutagen (用于元数据编辑)

安装依赖：
```bash
pip3 install --user yt-dlp requests mutagen
```

## 注意事项

1. **版权问题**：部分歌曲受版权保护，无法下载完整版
2. **VIP歌曲**：需要登录cookies才能下载高品质音频
3. **地区限制**：部分歌曲可能有地区限制
4. **稳定性**：音乐平台API经常变化，工具可能随时失效

## 故障排除

**下载失败或只有片段：**
- 歌曲可能受版权保护
- 尝试添加 `--cookies-from-browser chrome`（需登录网易云）

**音质不理想：**
- 免费用户通常只能下载128k
- VIP歌曲需要登录cookies

**yt-dlp 未找到：**
```bash
pip3 install --user yt-dlp
```

## 进阶用法

使用 cookies 下载VIP歌曲：
```bash
# 从浏览器获取cookies
yt-dlp --cookies-from-browser chrome \
  -x --audio-format mp3 \
  -o "~/Music/%(title)s.%(ext)s" \
  "https://music.163.com/#/song?id=123456789"
```

## 更新日志

- v1.0.0: 初始版本，支持网易云、QQ音乐基础下载

---

**再次提醒：请支持正版音乐，本工具仅供学习研究使用。**
