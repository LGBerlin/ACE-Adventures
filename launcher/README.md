# Permanent launcher — development branch design

**Not yet activated in the installed game.** These files are an initial bootstrap prototype, not an operational updater.

The goal is to keep a small Godot Mac application installed once. At startup it loads a versioned Godot resource pack (PCK) from Godot user data and only then launches the gameplay scene. This avoids replacing the Mac .app for routine game changes.

Planned release flow:
1. Import and validate Godot sources in CI.
2. Export the game's resource pack with the matching Godot export template.
3. Publish a versioned manifest with pack URL and SHA-256; don't republish identical versions.
4. Download to a staging file, verify digest, validate pack before activation, retain last-known-good pack.
5. Swap active pack atomically and restart using the fixed launcher.
6. Keep all saves, character sprites and generated imagery in user:// outside game packs.

Safety work remaining: verify Godot resource override behavior on macOS, packaging of bootstrap vs game pack, rollback after launch failure, exact pack checksum, cancellation/retry, and compatibility rules for engine updates. **Do not use this bootstrap to replace v0.4.0 yet.**
