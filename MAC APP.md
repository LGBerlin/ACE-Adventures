# ACE Adventures — standalone Mac app

The first distribution is **ACE Adventures Mac App.zip**, containing **ACE Adventures.app**.

## Install
1. Download the ZIP and double-click it to extract.
2. Drag **ACE Adventures.app** into Applications.
3. Open it. Because this starter package is not Apple Developer-signed, macOS may block it. Open System Settings → Privacy & Security and choose **Open Anyway** after trying to open the app.
4. The game will open in your default browser. Ollama must be running locally, with `qwen3.5:4b` installed, to narrate open-ended actions.
5. From that point onward, use **Check for Updates** or **Install Update** inside the app. On successful installation, quit and reopen the app.

## Permanent updater

The app fetches `latest.json` from this repository's main branch via GitHub raw content. Future versions must set `version` to a higher three-part semantic version and specify downloadable files in `files`. Each file entry is:

```json
{"path":"adventures.py","url":"https://raw.githubusercontent.com/LGBerlin/ACE-Adventures/main/updates/0.2.0/adventures.py","sha256":"64-character lowercase SHA-256"}
```

The updater only accepts `adventures.py` files hosted under the repository's `updates/` directory, downloads the contents, verifies SHA-256, and atomically installs it at `~/Library/Application Support/ACE Adventures/adventures.py`. The immutable original app launcher then loads the updated game file on the next launch. Saves reside in the same user data directory. App files in Applications are never modified by updates.

Important: version 0.1.0 is the starting version and intentionally has an empty update file list. Subsequent releases must publish the update file before updating latest.json.

Current prototype limitations: no native macOS gameplay window (uses a local browser), no graphical map or sprites yet; English-language basic rules; no full D&D rule implementation. Free-text narrative does not yet execute arbitrary mechanical actions. The Mac package must be tested on an actual Mac.
