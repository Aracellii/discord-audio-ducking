#!/usr/bin/env python3
"""Install Discord Duck as a user daemon with a terminal configuration command."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
HOME = Path.home()
INSTALL_DIR = HOME / ".local" / "share" / "discord-duck"
BIN_DIR = HOME / ".local" / "bin"
CONFIG_DIR = HOME / ".config" / "discord-duck"
SYSTEMD_DIR = HOME / ".config" / "systemd" / "user"
CONFIG_PATH = CONFIG_DIR / "config.json"
SERVICE_PATH = SYSTEMD_DIR / "discord-duck.service"
COMMAND_PATH = BIN_DIR / "discord-duck"
DEFAULT_CONFIG = {"enabled": True, "sensitivity": 30, "release_seconds": 2.0}


def run(*args, check=True):
    return subprocess.run(args, check=check)


def write_default_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8")


def install():
    if sys.platform != "linux":
        raise SystemExit("Discord Duck hanya mendukung Linux.")
    for command in ("pactl", "parec", "systemctl"):
        if shutil.which(command) is None:
            raise SystemExit(f"Perintah wajib tidak ditemukan: {command}")
    source = PROJECT / "discord_duck.py"
    service_source = PROJECT / "discord-duck.service"
    if not source.exists() or not service_source.exists():
        raise SystemExit("discord_duck.py dan discord-duck.service harus berada di folder yang sama dengan install.py.")

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    SYSTEMD_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, INSTALL_DIR / "discord_duck.py")
    shutil.copy2(service_source, SERVICE_PATH)
    COMMAND_PATH.unlink(missing_ok=True)
    COMMAND_PATH.symlink_to(INSTALL_DIR / "discord_duck.py")
    write_default_config()
    run("systemctl", "--user", "daemon-reload")
    run("systemctl", "--user", "enable", "--now", "discord-duck.service")
    print("Discord Duck berhasil di-install dan daemon sudah aktif.")
    print(f"Command: {COMMAND_PATH}")
    print("Jika ~/.local/bin belum ada di PATH, buka terminal baru atau jalankan:")
    print('export PATH="$HOME/.local/bin:$PATH"')


def uninstall():
    run("systemctl", "--user", "disable", "--now", "discord-duck.service", check=False)
    run("systemctl", "--user", "daemon-reload", check=False)
    SERVICE_PATH.unlink(missing_ok=True)
    COMMAND_PATH.unlink(missing_ok=True)
    shutil.rmtree(INSTALL_DIR, ignore_errors=True)
    print("Discord Duck daemon dan file instalasinya sudah dihapus.")
    print(f"Konfigurasi tetap disimpan di {CONFIG_PATH}.")


def main():
    parser = argparse.ArgumentParser(description="Install atau hapus Discord Duck.")
    parser.add_argument("--uninstall", action="store_true", help="Hapus daemon dan file instalasi")
    args = parser.parse_args()
    uninstall() if args.uninstall else install()


if __name__ == "__main__":
    main()
