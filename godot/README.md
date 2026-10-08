# ACE Adventures — Godot macOS game

## Current development build: v0.3.0

### Campaign Library
- Opens to the Campaign Library when launched.
- Create a campaign with a name and planned player count (1–8).
- Continue any saved campaign, or start a new one with an independent character.
- Save & Return to the library from character creation or gameplay.
- Character creation is permanent per campaign: name, age, class chosen; path, affinity, race, stats and equipment randomised.
- Previous single-character Godot saves are copied into **Original Adventure** on first launch. Original legacy save remains in place.

Campaigns are saved in Godot user data under `user://campaign_library.json`, not inside the application bundle.

### macOS in-app updates
- Buttons on the main screen: **CHECK FOR UPDATES** and **INSTALL UPDATE**.
- The app queries the latest release from the repository's GitHub Releases.
- It downloads `ACE Adventures Mac.zip`, checks the release asset SHA-256 digest, and launches an external installer that waits for the app to exit.
- The previous app is retained beside the new version as `ACE Adventures.app.previous` for rollback.
- Campaign files in `user://` are not replaced.

### First-time installation
GitHub Actions **Build ACE Adventures macOS App** publishes version `v0.3.0` as a GitHub Release after successfully building. Download the Mac ZIP from that release, unzip, and move ACE Adventures.app into Applications. The original Python app is **not** the Godot game.

**Important:** This build is not Apple-notarized and may be blocked by Gatekeeper. The workflow must pass and the app/updater must be tested on macOS before the release can be considered validated.

## Remaining work
The image AI, real playable tile map, sprite animation, sophisticated action interpretation, and multiplayer are not connected yet. The player-count selector is groundwork, not active multiplayer.
