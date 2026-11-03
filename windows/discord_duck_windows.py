#!/usr/bin/env python3
"""Discord Duck for Windows using Windows Audio Session API through pycaw."""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
except ImportError:
    AudioUtilities = None
    IAudioMeterInformation = None

CONFIG_PATH = Path(os.environ.get("APPDATA", Path.home())) / "Discord Duck" / "config.json"
INSTALL_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Discord Duck"
COMMAND_DIR = INSTALL_DIR / "bin"
INSTALLED_SCRIPT = INSTALL_DIR / "discord_duck_windows.py"
COMMAND_FILE = COMMAND_DIR / "discord-duck.cmd"
DEFAULT_CONFIG = {"enabled": True, "sensitivity": 30, "release_seconds": 2.0}
DUCK_FACTOR = 0.20
POLL_SECONDS = 0.10
DISCORD_PROCESSES = {"discord.exe", "vesktop.exe", "webcord.exe"}


def load_config():
    config = DEFAULT_CONFIG.copy()
    try:
        value = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            config.update(value)
    except (OSError, ValueError, TypeError):
        pass
    config["enabled"] = bool(config.get("enabled", True))
    try:
        config["sensitivity"] = max(1, min(100, int(config.get("sensitivity", 30))))
    except (TypeError, ValueError):
        config["sensitivity"] = 30
    try:
        config["release_seconds"] = max(0.1, min(30.0, float(config.get("release_seconds", 2.0))))
    except (TypeError, ValueError):
        config["release_seconds"] = 2.0
    return config


def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def process_name(session):
    return (session.Process.name().lower() if session.Process else "")


def is_discord(session):
    return process_name(session) in DISCORD_PROCESSES


def session_key(session):
    return getattr(session, "Identifier", None) or str(session.ProcessId)


def threshold(sensitivity):
    return max(0.002, 0.03 - (sensitivity - 1) * 0.00025)


def peak(session):
    if IAudioMeterInformation is None:
        return 0.0
    meter = session._ctl.QueryInterface(IAudioMeterInformation)
    return meter.GetPeakValue()


def duck_sessions(sessions, originals):
    for session in sessions:
        if is_discord(session):
            continue
        key = session_key(session)
        volume = session.SimpleAudioVolume
        if key not in originals:
            originals[key] = volume.GetMasterVolume()
        volume.SetMasterVolume(max(0.0, originals[key] * DUCK_FACTOR), None)


def restore_sessions(sessions, originals):
    for session in sessions:
        key = session_key(session)
        if key in originals:
            session.SimpleAudioVolume.SetMasterVolume(originals[key], None)
    originals.clear()


def daemon():
    if AudioUtilities is None:
        raise SystemExit("Install dependencies first: py -m pip install pycaw comtypes")
    originals = {}
    last_voice = 0.0
    ducked = False
    try:
        while True:
            config = load_config()
            sessions = AudioUtilities.GetAllSessions()
            discord = [session for session in sessions if is_discord(session)]
            if config["enabled"]:
                speaking = any(peak(session) >= threshold(config["sensitivity"]) for session in discord)
                if speaking:
                    last_voice = time.monotonic()
                    duck_sessions(sessions, originals)
                    ducked = True
                elif ducked and time.monotonic() - last_voice >= config["release_seconds"]:
                    restore_sessions(sessions, originals)
                    ducked = False
            elif ducked:
                restore_sessions(sessions, originals)
                ducked = False
            time.sleep(POLL_SECONDS)
    finally:
        restore_sessions(AudioUtilities.GetAllSessions(), originals)


def install_task():
    if sys.platform != "win32":
        raise SystemExit("The Windows installer must be run on Windows.")
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    COMMAND_DIR.mkdir(parents=True, exist_ok=True)
    INSTALLED_SCRIPT.write_bytes(Path(__file__).resolve().read_bytes())
    COMMAND_FILE.write_text(
        f'@echo off\n"{sys.executable}" "{INSTALLED_SCRIPT}" %*\n',
        encoding="utf-8",
    )
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
        try:
            current_path = winreg.QueryValueEx(key, "Path")[0]
        except FileNotFoundError:
            current_path = ""
        path_parts = [part for part in current_path.split(";") if part]
        if str(COMMAND_DIR) not in path_parts:
            path_parts.append(str(COMMAND_DIR))
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, ";".join(path_parts))
    script = str(INSTALLED_SCRIPT)
    command = f'"{sys.executable}" "{script}"'
    subprocess.run(["schtasks", "/Create", "/TN", "Discord Duck", "/SC", "ONLOGON", "/TR", command, "/F"], check=True)
    print("Discord Duck Windows daemon installed.")
    print(f"Command: {COMMAND_FILE}")
    print("Open a new terminal before using: discord-duck --status")


def uninstall_task():
    subprocess.run(["schtasks", "/Delete", "/TN", "Discord Duck", "/F"], check=False)
    if COMMAND_DIR.exists():
        for path in COMMAND_DIR.iterdir():
            path.unlink(missing_ok=True)
        COMMAND_DIR.rmdir()
    if INSTALL_DIR.exists():
        INSTALLED_SCRIPT.unlink(missing_ok=True)
        try:
            INSTALL_DIR.rmdir()
        except OSError:
            pass
    print("Discord Duck Windows daemon removed.")


def main():
    parser = argparse.ArgumentParser(description="Discord Duck")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--enable", action="store_true")
    actions.add_argument("--disable", action="store_true")
    actions.add_argument("--toggle", action="store_true")
    actions.add_argument("--status", action="store_true")
    actions.add_argument("--install", action="store_true")
    actions.add_argument("--uninstall", action="store_true")
    parser.add_argument("--sensitivity", type=int, choices=range(1, 101), metavar="1-100")
    parser.add_argument("--release", type=float, metavar="SECONDS")
    args = parser.parse_args()
    if args.install:
        install_task()
        return
    if args.uninstall:
        uninstall_task()
        return
    config = load_config()
    action = any((args.enable, args.disable, args.toggle, args.status,
                  args.sensitivity is not None, args.release is not None))
    if args.sensitivity is not None:
        config["sensitivity"] = args.sensitivity
    if args.release is not None:
        if not 0.1 <= args.release <= 30.0:
            parser.error("--release must be between 0.1 and 30 seconds")
        config["release_seconds"] = args.release
    if args.enable:
        config["enabled"] = True
    if args.disable:
        config["enabled"] = False
    if args.toggle:
        config["enabled"] = not config["enabled"]
    if action:
        save_config(config)
        if args.enable or args.disable or args.toggle:
            print(f"discord-duck {'on' if config['enabled'] else 'off'}")
        else:
            print(json.dumps(config, indent=2))
        return
    daemon()


if __name__ == "__main__":
    main()
