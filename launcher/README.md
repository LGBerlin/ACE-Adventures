# ACE Adventures permanent launcher — validation build

The stable launcher is now isolated from the gameplay source in `launcher/`. The GitHub workflow `permanent-launcher.yml` attempts to build and smoke-test a standalone Mac application containing a baseline `base-game.pck`.

## Current status

**Not yet validated on macOS, not a public release.** Source changes trigger an automatic GitHub validation build. If it passes, the workflow provides a **Permanent Launcher Test Build** artifact. Do not replace a working installation until this test build starts correctly and saves are checked.

## Architecture

- The launcher exports as a fixed Mac application, with the bundled game pack at `Contents/Resources/base-game.pck`.
- A game update pack can be downloaded to `user://updates/active-game.pck`.
- `launcher/pack_updater.gd` checks `game-update.json` (not yet published), validates SHA-256 and retains `previous-game.pck`.
- `launcher/bootstrap.gd` loads bundled content, then an active update if present, and opens the game.
- The game UI uses the autoloaded updater where available, and its legacy updater when launched from the old standalone build.
- Saved campaigns and generated art remain in `user://` and are not included in the game pack.

## Remaining acceptance tests

1. GitHub automated Godot parser/import and real packaged startup validation pass.
2. Download a new pack using a valid published manifest and verify activation after restart.
3. Corrupt/mismatch checksum and ensure rejection without changing installed game.
4. Simulate pack startup failure and confirm previous game AND version metadata restored.
5. Confirm multiple campaign saves persist after update and failed update.
6. Verify there is no requirement to reinstall the .app for a normal game-data release.

A successful source commit is **not** proof that these tests have passed.
