# Discord Audio Ducking untuk Linux dan Windows

[English](README.md) · [Bahasa Indonesia](README.id.md) · [Español](README.es.md) · [简体中文](README.zh-CN.md)

![Discord Duck](../duck.jpeg)

Discord Duck adalah utilitas open-source untuk menurunkan volume aplikasi lain saat seseorang berbicara di Discord.

## Clone dan instalasi cepat

```bash
git clone https://github.com/Aracellii/Discord_Duck.git
cd Discord_Duck/linux
python3 install.py
```

## Pengaturan terminal

```bash
discord-duck --status
discord-duck --enable
discord-duck --disable
discord-duck --toggle
discord-duck --sensitivity 50
discord-duck --release 3.0
```

## Dependensi

- Linux dengan PipeWire/PulseAudio
- Python 3.9 atau lebih baru
- `pactl` dan `parec`

## Lisensi

MIT License. Lihat [LICENSE](../LICENSE).
