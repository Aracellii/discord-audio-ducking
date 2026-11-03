#!/usr/bin/env python3
"""Discord Duck: global audio ducking for Discord voice activity."""

import argparse
import json
import math
import os
import select
import signal
import subprocess
import time
from array import array
from pathlib import Path

DEFAULT_CONFIG = {
    "enabled": True,
    "sensitivity": 30,
    "release_seconds": 2.0,
}
DUCK_FACTOR = 0.20
SAMPLE_RATE = 16000
CHUNK_SAMPLES = 1600
POLL_SECONDS = 0.10


class DiscordDuck:
    def __init__(self, config_path, enabled=True, sensitivity=30, release_seconds=2.0):
        self.config_path = Path(config_path).expanduser()
        self.config = {
            "enabled": enabled,
            "sensitivity": sensitivity,
            "release_seconds": release_seconds,
        }
        self.overrides = {}
        self.original_volumes = {}
        self.monitors = {}
        self.ducked = False

    @staticmethod
    def command(*args):
        return subprocess.run(args, capture_output=True, text=True)

    def load_config(self):
        try:
            value = json.loads(self.config_path.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                self.config.update(value)
        except (OSError, ValueError, TypeError):
            pass
        self.config["enabled"] = bool(self.config.get("enabled", True))
        try:
            self.config["sensitivity"] = max(1, min(100, int(self.config.get("sensitivity", 30))))
        except (TypeError, ValueError):
            self.config["sensitivity"] = 30
        try:
            self.config["release_seconds"] = max(0.1, min(30.0, float(self.config.get("release_seconds", 2.0))))
        except (TypeError, ValueError):
            self.config["release_seconds"] = 2.0
        self.config.update(self.overrides)

    def sink_inputs(self):
        result = self.command("pactl", "-f", "json", "list", "sink-inputs")
        if result.returncode != 0:
            return []
        try:
            return json.loads(result.stdout)
        except ValueError:
            return []

    @staticmethod
    def property_value(item, key):
        return str(item.get("properties", {}).get(key, "")).lower()

    def is_discord(self, item):
        identity = " ".join(self.property_value(item, key) for key in (
            "application.name", "application.process.binary", "application.id",
            "media.name", "node.name", "node.description",
        ))
        return any(name in identity for name in ("discord", "vesktop", "webcord"))

    @staticmethod
    def volume_values(item):
        return [channel["value"] for channel in item.get("volume", {}).values()
                if isinstance(channel, dict) and isinstance(channel.get("value"), (int, float))]

    def set_volume(self, index, value):
        value = max(0, min(100, int(round(value))))
        return self.command("pactl", "set-sink-input-volume", str(index), f"{value}%").returncode == 0

    def threshold(self):
        # Higher sensitivity means a lower RMS threshold.
        return 220 - (self.config["sensitivity"] - 1) * 1.9

    def duck_other_audio(self, items):
        changed = False
        present = set()
        for item in items:
            if self.is_discord(item):
                continue
            index = item["index"]
            present.add(index)
            if index not in self.original_volumes:
                values = self.volume_values(item)
                if values:
                    self.original_volumes[index] = sum(values) / len(values) / 655.36
            if index in self.original_volumes:
                changed = self.set_volume(index, self.original_volumes[index] * DUCK_FACTOR) or changed
        for index in list(self.original_volumes):
            if index not in present:
                del self.original_volumes[index]
        self.ducked = self.ducked or changed

    def restore(self):
        for index, volume in list(self.original_volumes.items()):
            self.set_volume(index, volume)
        self.original_volumes.clear()
        self.ducked = False

    def stop_monitors(self):
        for process in self.monitors.values():
            process.terminate()
        for process in self.monitors.values():
            try:
                process.wait(timeout=0.4)
            except subprocess.TimeoutExpired:
                process.kill()
        self.monitors.clear()

    @staticmethod
    def start_monitor(index):
        return subprocess.Popen(
            ["parec", "--monitor-stream", str(index), "--format=s16le",
             "--rate", str(SAMPLE_RATE), "--channels=1", "--raw"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0,
        )

    def run(self):
        last_config = None
        last_voice = 0.0
        try:
            while True:
                self.load_config()
                current_config = tuple(self.config.items())
                if current_config != last_config and not self.config["enabled"]:
                    self.stop_monitors()
                    self.restore()
                last_config = current_config

                items = self.sink_inputs()
                discord = [item for item in items if self.is_discord(item)]
                discord_ids = {item["index"] for item in discord}
                for index in list(self.monitors):
                    if index not in discord_ids or self.monitors[index].poll() is not None:
                        self.monitors[index].terminate()
                        del self.monitors[index]

                if self.config["enabled"]:
                    for index in discord_ids - self.monitors.keys():
                        self.monitors[index] = self.start_monitor(index)
                    if self.ducked:
                        self.duck_other_audio(items)
                    streams = [process.stdout for process in self.monitors.values() if process.stdout]
                    if streams:
                        readable, _, _ = select.select(streams, [], [], POLL_SECONDS)
                        for stream in readable:
                            data = os.read(stream.fileno(), CHUNK_SAMPLES * 2)
                            samples = array("h")
                            samples.frombytes(data[:len(data) // 2 * 2])
                            rms = math.sqrt(sum(x * x for x in samples) / len(samples)) if samples else 0
                            if rms >= self.threshold():
                                last_voice = time.monotonic()
                                if not self.ducked:
                                    self.duck_other_audio(items)

                if self.ducked and time.monotonic() - last_voice >= self.config["release_seconds"]:
                    self.restore()
                if not self.monitors:
                    time.sleep(POLL_SECONDS)
        finally:
            self.stop_monitors()
            self.restore()


def main():
    parser = argparse.ArgumentParser(description="Duck non-Discord audio while someone speaks in Discord.")
    parser.add_argument("--config", default="~/.config/discord-duck/config.json")
    parser.add_argument("--enable", action="store_true", help="Enable ducking and exit")
    parser.add_argument("--disable", action="store_true", help="Disable ducking and exit")
    parser.add_argument("--toggle", action="store_true", help="Toggle ducking and exit")
    parser.add_argument("--status", action="store_true", help="Print the current configuration and exit")
    parser.add_argument("--sensitivity", type=int, choices=range(1, 101), metavar="1-100", help="Persist sensitivity and exit")
    parser.add_argument("--release", type=float, metavar="SECONDS", help="Persist release duration and exit")
    args = parser.parse_args()
    config_path = Path(args.config).expanduser()
    defaults = DEFAULT_CONFIG.copy()
    try:
        stored = json.loads(config_path.read_text(encoding="utf-8"))
        if isinstance(stored, dict):
            defaults.update(stored)
    except (OSError, ValueError, TypeError):
        pass

    control_action = any((args.enable, args.disable, args.toggle, args.status,
                          args.sensitivity is not None, args.release is not None))
    if args.enable and args.disable or args.enable and args.toggle or args.disable and args.toggle:
        parser.error("--enable, --disable, and --toggle cannot be combined")
    if args.sensitivity is not None:
        defaults["sensitivity"] = args.sensitivity
    if args.release is not None:
        if not 0.1 <= args.release <= 30.0:
            parser.error("--release must be between 0.1 and 30 seconds")
        defaults["release_seconds"] = args.release
    if args.enable:
        defaults["enabled"] = True
    if args.disable:
        defaults["enabled"] = False
    if args.toggle:
        defaults["enabled"] = not bool(defaults.get("enabled", True))
    if control_action:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(defaults, indent=2) + "\n", encoding="utf-8")
        if args.status or args.enable or args.disable or args.toggle or args.sensitivity is not None or args.release is not None:
            print(json.dumps(defaults, indent=2))
        if args.status:
            return
        if args.enable or args.disable or args.toggle or args.sensitivity is not None or args.release is not None:
            return
    duck = DiscordDuck(
        config_path,
        enabled=defaults.get("enabled", True),
        sensitivity=defaults.get("sensitivity", 30),
        release_seconds=defaults.get("release_seconds", 2.0),
    )
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(SystemExit(0)))
    signal.signal(signal.SIGINT, lambda *_: (_ for _ in ()).throw(SystemExit(0)))
    duck.run()


if __name__ == "__main__":
    main()
