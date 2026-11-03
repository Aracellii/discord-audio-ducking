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

Discord Duck is a small Linux utility that lowers every non-Discord audio stream while someone is speaking in a Discord voice channel. Discord audio itself is never lowered.

It uses the PulseAudio compatibility interface provided by PipeWire:

- `pactl` lists and changes sink-input volume.
- `parec` monitors Discord audio for voice activity.
- Discord, Vesktop, and WebCord streams are excluded from ducking.
- Other audio is restored to its previous volume after the release duration.

## Requirements

- Linux
- PipeWire with `pipewire-pulse`, or PulseAudio
- `pactl` and `parec`
- Python 3.9 or newer

## Step-by-step installation

### 1. Use Linux

Discord Duck uses `pactl` and `parec`, so Windows and macOS are not currently supported.

### 2. Install dependencies

Fedora:

```bash
sudo dnf install python3 pipewire-pulseaudio pulseaudio-utils
```

Ubuntu atau Debian:

```bash
sudo apt install python3 pipewire-pulse pulseaudio-utils
```

Arch Linux:

```bash
sudo pacman -S python pipewire-pulse libpulse
```

Make sure the audio commands are available:

```bash
command -v pactl
command -v parec
```

### 3. Enter the project directory

```bash
cd ~/Portofolio/Discord_Duck
```

### 4. Create the configuration

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

### 5. Run manually

```bash
python3 discord_duck.py
```

Keep the terminal open, join a Discord voice channel, and test audio from another application. Stop with `Ctrl+C`.

### 6. Start automatically at login

Create the user service directory:

```bash
mkdir -p ~/.config/systemd/user
```

Save the following service as `~/.config/systemd/user/discord-duck.service`:

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

Enable the service:

```bash
systemctl --user daemon-reload
systemctl --user enable --now discord-duck.service
```

Check the status and logs:

```bash
systemctl --user status discord-duck.service
journalctl --user -u discord-duck.service -f
```

Stop or disable automatic startup:

```bash
systemctl --user disable --now discord-duck.service
```

## Usage

```bash
python3 discord_duck.py
```

The default configuration file is `~/.config/discord-duck/config.json`:

```json
{
  "enabled": true,
  "sensitivity": 30,
  "release_seconds": 2.0
}
```

`sensitivity` accepts values from 1 to 100. Higher values react to quieter speech. `release_seconds` controls how long other audio stays lowered after Discord becomes quiet.

Command-line options:

```text
--config PATH          Use a custom configuration file
--sensitivity 1-100    Override sensitivity
--release SECONDS      Override release duration
--disable              Start disabled
```

## License

MIT License. See [LICENSE](LICENSE).
