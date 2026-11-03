# Discord Duck

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

## Instalasi langkah demi langkah

### 1. Pastikan sistem menggunakan Linux

Discord Duck menggunakan `pactl` dan `parec`, jadi Windows dan macOS belum didukung.

### 2. Pasang dependensi

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

Pastikan perintah audio tersedia:

```bash
command -v pactl
command -v parec
```

### 3. Masuk ke folder proyek

```bash
cd ~/Portofolio/Discord_Duck
```

### 4. Buat konfigurasi

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

### 5. Jalankan secara manual

```bash
python3 discord_duck.py
```

Biarkan terminal tetap terbuka, lalu masuk ke voice channel Discord dan uji audio dari aplikasi lain. Hentikan dengan `Ctrl+C`.

### 6. Jalankan otomatis saat login

Buat service user:

```bash
mkdir -p ~/.config/systemd/user
```

Simpan konfigurasi service berikut sebagai `~/.config/systemd/user/discord-duck.service`:

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

Aktifkan service:

```bash
systemctl --user daemon-reload
systemctl --user enable --now discord-duck.service
```

Periksa status dan log:

```bash
systemctl --user status discord-duck.service
journalctl --user -u discord-duck.service -f
```

Hentikan atau nonaktifkan otomatis:

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
