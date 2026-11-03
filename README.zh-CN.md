# Discord Duck

[English](README.md) · [Español](README.es.md) · [简体中文](README.zh-CN.md)

```text
       ___
   __ /   \ __
  /  | o o |  \
  \  |  ^  |  /
   \_|\___/|_/
     /|💬|\
    /_|___|_\
      /   \
     /_____\
```

Discord Duck 是一个 Linux 音频工具。当 Discord 语音频道中有人说话时，它会暂时降低所有非 Discord 音频的音量。Discord 音频本身不会被降低。

## 系统要求

- Linux
- PipeWire 和 `pipewire-pulse`，或 PulseAudio
- `pactl` 和 `parec`
- Python 3.9 或更高版本

## 安装步骤

### 1. 使用 Linux

Windows 和 macOS 目前不支持，因为本程序使用 Linux 的 PulseAudio/PipeWire 音频接口。

### 2. 安装依赖

Fedora：

```bash
sudo dnf install python3 pipewire-pulseaudio pulseaudio-utils
```

Ubuntu 或 Debian：

```bash
sudo apt install python3 pipewire-pulse pulseaudio-utils
```

Arch Linux：

```bash
sudo pacman -S python pipewire-pulse libpulse
```

确认音频命令可用：

```bash
command -v pactl
command -v parec
```

### 3. 进入项目目录

```bash
cd ~/Portofolio/Discord_Duck
```

### 4. 创建配置文件

```bash
mkdir -p ~/.config/discord-duck
cat > ~/.config/discord-duck/config.json <<'EOF'
{
  "enabled": true,
  "sensitivity": 30,
  "release_seconds": 2.0
}
EOF
```

`sensitivity` 的范围是 1 到 100，数值越高越容易检测到较小的声音。`release_seconds` 表示 Discord 停止说话后，其他音频保持降低的时间。

### 5. 手动运行

```bash
python3 discord_duck.py
```

保持终端打开，加入 Discord 语音频道，然后测试其他应用的音频。使用 `Ctrl+C` 停止程序。

### 6. 登录时自动运行

```bash
mkdir -p ~/.config/systemd/user
```

将以下内容保存为 `~/.config/systemd/user/discord-duck.service`：

```ini
[Unit]
Description=Discord Duck audio ducking
After=pipewire-pulse.service

[Service]
ExecStart=/usr/bin/python3 %h/Portofolio/Discord_Duck/discord_duck.py
Restart=on-failure
RestartSec=2

[Install]
WantedBy=default.target
```

启用服务：

```bash
systemctl --user daemon-reload
systemctl --user enable --now discord-duck.service
```

查看状态和日志：

```bash
systemctl --user status discord-duck.service
journalctl --user -u discord-duck.service -f
```

停止服务并取消自动启动：

```bash
systemctl --user disable --now discord-duck.service
```

## 命令行选项

```text
--config PATH          使用自定义配置文件
--sensitivity 1-100    覆盖灵敏度
--release SECONDS      覆盖恢复延迟
--disable              以禁用状态启动
```

## 许可证

MIT License。请参阅 [LICENSE](LICENSE)。
