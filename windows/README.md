# Discord Duck for Windows

[Linux](../linux/README.md) · Windows

![Discord Duck](../duck.jpeg)

This Windows version lowers every non-Discord audio session while someone is speaking in Discord. Discord audio remains unchanged.

## Requirements

- Windows 10 or newer
- Python 3.9 or newer
- Discord desktop app, Vesktop, or WebCord

## Install

Open PowerShell in this folder and install the audio libraries:

```powershell
py -m pip install pycaw comtypes
```

Install the automatic logon daemon:

```powershell
py discord_duck_windows.py --install
```

Start the daemon manually for a test:

```powershell
py discord_duck_windows.py
```

The daemon uses Windows Audio Session API peak meters and per-application session volume. It does not change the Windows master volume.

## Terminal controls

```powershell
py discord_duck_windows.py --status
py discord_duck_windows.py --enable
py discord_duck_windows.py --disable
py discord_duck_windows.py --toggle
py discord_duck_windows.py --sensitivity 50
py discord_duck_windows.py --release 3.0
```

Settings are stored in `%APPDATA%\Discord Duck\config.json`.

Remove the automatic task with:

```powershell
py discord_duck_windows.py --uninstall
```

## Notes

Discord must be playing audio through the same Windows output device as the other applications. The first time Discord creates or changes an audio session, restart the daemon if it does not appear in the session list.

## License

MIT License. See [LICENSE](../LICENSE).
