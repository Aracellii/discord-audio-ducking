# Discord Audio Ducking for Linux and Windows

![Discord Duck](duck.jpeg)

Discord Duck is an open-source Discord audio ducking utility for Linux and Windows. It automatically lowers other application audio while someone is speaking in Discord.

[Linux](linux/README.md) · [Windows](windows/README.md) · [Changelog](CHANGELOG.md) · [Live documentation](https://aracellii.github.io/Discord_Duck/)

![Before and after audio ducking](docs/demo.svg)

## Features

- Global ducking for every non-Discord audio session.
- Discord, Vesktop, and WebCord audio stays at normal volume.
- Persistent on/off toggle from the terminal.
- Adjustable voice sensitivity and release duration.
- Linux daemon with systemd user service.
- Windows daemon with Task Scheduler and Windows Audio Session API.
- Per-application volume restoration after ducking.
- MIT licensed and open source.

## Before and after

| Situation | Discord | Other applications |
| --- | ---: | ---: |
| No one is speaking | 100% | 100% |
| Someone is speaking | 100% | 20% |
| Voice stops after release duration | 100% | Restored |

## Platforms

- [Linux](linux/README.md) — PipeWire/PulseAudio daemon with systemd user service.
- [Windows](windows/README.md) — Windows Audio Session API daemon with Task Scheduler.

Both versions support persistent terminal controls for enable, disable, toggle, sensitivity, and release duration.

## Troubleshooting

### The command is not found

Linux:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Windows: open a new PowerShell window after running the installer so the updated user PATH is loaded.

### Discord is not detected

Make sure Discord is playing audio through the same output device as the other applications. For Linux, verify that `pactl list sink-inputs` shows a Discord stream. For Windows, verify that Discord appears in the Windows volume mixer.

### Other audio stays quiet

Use the toggle to disable and re-enable the daemon:

```bash
discord-duck --disable
discord-duck --enable
```

The daemon stores the original per-application volume and restores it after the release duration.

## GitHub Pages

The repository includes a ready-to-publish page in [`docs/index.html`](docs/index.html). To publish it:

1. Open the repository on GitHub.
2. Open **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select the default branch and the `/docs` folder.
5. Click **Save**.

The page title is `Discord Audio Ducking for Linux and Windows` and links back to this repository.

## Search visibility setup

1. Set the repository description to: `Discord audio ducking for Linux and Windows. Automatically lower other applications when someone speaks in Discord.`
2. Add these repository topics: `discord`, `audio-ducking`, `discord-ducking`, `audio-volume-control`, `pipewire`, `pulseaudio`, `windows-audio`, `pycaw`, `python`, `voice-activity-detection`.
3. Publish a GitHub Release with a version number and link it from the changelog.
4. Publish GitHub Pages using the steps above.
5. Add the GitHub Pages URL to Google Search Console and request indexing.

The repository can also be configured with GitHub CLI after authentication:

```bash
gh auth login
gh repo edit Aracellii/Discord_Duck \
  --description "Discord audio ducking for Linux and Windows. Automatically lower other applications when someone speaks in Discord."
gh repo edit Aracellii/Discord_Duck \
  --add-topic discord --add-topic audio-ducking --add-topic discord-ducking \
  --add-topic audio-volume-control --add-topic pipewire --add-topic pulseaudio \
  --add-topic windows-audio --add-topic pycaw --add-topic python \
  --add-topic voice-activity-detection
```

## License

MIT License. See [LICENSE](LICENSE).
