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

Discord Duck reduce temporalmente el volumen de todo el audio que no pertenece a Discord cuando alguien habla en un canal de voz. El audio de Discord nunca se reduce.

## Requisitos

- Linux
- PipeWire con `pipewire-pulse`, o PulseAudio
- `pactl` y `parec`
- Python 3.9 o posterior

## Instalación paso a paso

### 1. Usa Linux

Windows y macOS no son compatibles actualmente porque el programa utiliza la interfaz de audio PulseAudio/PipeWire de Linux.

### 2. Instala las dependencias

Fedora:

```bash
sudo dnf install python3 pipewire-pulseaudio pulseaudio-utils
```

Ubuntu o Debian:

```bash
sudo apt install python3 pipewire-pulse pulseaudio-utils
```

Arch Linux:

```bash
sudo pacman -S python pipewire-pulse libpulse
```

Comprueba los comandos de audio:

```bash
command -v pactl
command -v parec
```

### 3. Entra en la carpeta del proyecto

```bash
cd ~/Portofolio/Discord_Duck
```

### 4. Crea la configuración

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

`sensitivity` acepta valores de 1 a 100. Los valores altos reaccionan a voces más silenciosas. `release_seconds` indica cuánto tiempo permanece reducido el audio después de que Discord queda en silencio.

### 5. Ejecuta el programa manualmente

```bash
python3 discord_duck.py
```

Deja la terminal abierta, entra en un canal de voz y prueba el audio de otra aplicación. Detén el programa con `Ctrl+C`.

### 6. Inícialo automáticamente

```bash
mkdir -p ~/.config/systemd/user
```

Guarda esto como `~/.config/systemd/user/discord-duck.service`:

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

Activa el servicio:

```bash
systemctl --user daemon-reload
systemctl --user enable --now discord-duck.service
```

Comprueba el estado y los registros:

```bash
systemctl --user status discord-duck.service
journalctl --user -u discord-duck.service -f
```

Para detenerlo y desactivar el inicio automático:

```bash
systemctl --user disable --now discord-duck.service
```

## Opciones

```text
--config PATH          Usa otro archivo de configuración
--sensitivity 1-100    Sobrescribe la sensibilidad
--release SECONDS      Sobrescribe la duración de liberación
--disable              Inicia desactivado
```

## Licencia

Licencia MIT. Consulta [LICENSE](LICENSE).
