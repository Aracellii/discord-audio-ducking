# Discord Duck

[English](README.md) · [Español](README.es.md) · [简体中文](README.zh-CN.md)

![Discord Duck](duck.jpeg)

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

### Quick install

The easiest method is to run the installer. It installs the daemon, creates the default configuration, enables automatic startup, and provides the `discord-duck` terminal command:

```bash
cd ~/Portofolio/Discord_Duck
python3 install.py
```

After installation, all settings can be controlled from the terminal:

```bash
discord-duck --status
discord-duck --toggle
discord-duck --enable
discord-duck --disable
discord-duck --sensitivity 50
discord-duck --release 3.0
```

To remove the daemon and installed files:

```bash
python3 install.py --uninstall
```

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

Copy the included service file into your user systemd directory:

```bash
mkdir -p ~/.config/systemd/user
cp discord-duck.service ~/.config/systemd/user/discord-duck.service
```

The included service file contains:

```ini
[Unit]
Description=Discord Duck audio ducking
After=pipewire-pulse.service

[Service]
ExecStart=/usr/bin/python3 %h/.local/share/discord-duck/discord_duck.py
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

## Toggle and settings

The daemon reads the configuration file continuously, so these commands can be used while the service is running:

```bash
python3 discord_duck.py --enable
python3 discord_duck.py --disable
python3 discord_duck.py --toggle
python3 discord_duck.py --status
python3 discord_duck.py --sensitivity 50
python3 discord_duck.py --release 3.0
```

`--enable`, `--disable`, and `--toggle` change the persistent on/off state. `--sensitivity` changes the voice detection sensitivity from 1 to 100. `--release` changes the release duration from 0.1 to 30 seconds.

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
--enable               Enable ducking and exit
--disable              Disable ducking and exit
--toggle               Toggle ducking and exit
--status               Print current settings and exit
--sensitivity 1-100    Save sensitivity and exit
--release SECONDS      Save release duration and exit
```

## License

MIT License. See [LICENSE](LICENSE).
