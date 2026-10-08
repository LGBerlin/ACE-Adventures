# ACE Adventures 2 — clean rebuild (development only)

**DO NOT INSTALL YET.** This is a fresh architecture isolated from all v0.x Godot, Python, and Mac app release paths. No old updater, release tag, or manifest is reused.

## Update contract (modelled on original A.C.E.)

1. A fixed launcher resides in the Mac application; normal updates do **not** rewrite the app bundle.
2. The launcher loads a versioned application payload from the user's Application Support directory.
3. `v2/latest.json` is the one source of update truth: a semver, base version, list of files, relative paths and SHA-256 digests.
4. Updates download into an isolated staging directory, verify **all** hashes, then atomically switch to the staged version; never partially update the active payload.
5. Last-known-good remains available for recovery. No downgrade/rollback without a verified retained version.
6. Per-campaign saves, generated sprites, artwork and settings live outside both app and update directory.
7. CI tests fresh install, update, missing files, mismatched hashes, interruption, rollback, preserve-save behaviour, startup, and UI screenshot on a macOS runner before release.
8. Public releases are explicitly gated; no release is considered finished until the exported .app is exercised on macOS.

## Not a complete application yet

This directory starts a verified, dependency-free Python payload/update core. A separate native-window launcher and graphics runtime will be selected and added with integration tests. The previous Godot version will not be overwritten or relied upon.

## No action required from the user

Do not download any new installer until the fresh exported application, updater, and rollback have passed CI and macOS testing.
