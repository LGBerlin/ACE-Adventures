# ACE Adventures — Mac app build and installation

The Godot source is now the app to distribute. The older Python ACE Adventures.app remains separate and is not the graphical game.

## Get an app build

1. In this GitHub repository open **Actions → Build ACE Adventures macOS App**.
2. Select **Run workflow**.
3. When it finishes successfully, open the run's **Artifacts** section and download **ACE Adventures Mac Build**.
4. Extract its artifact ZIP, then extract **ACE Adventures Mac.zip** inside it.
5. Move **ACE Adventures.app** to Applications.

This version is an unsigned developer build. Gatekeeper may require **Open Anyway** under macOS Privacy & Security. Do not bypass security for binaries from unknown sources.

## Important current limitations

- This GitHub Action has not yet been run and may need export template adjustments for the Godot version that Homebrew installs.
- A Godot-native one-click updater is not complete. Do not use the old Python app's Update button for the Godot game.
- Saves are in Godot's `user://` directory and should remain separate from the app bundle.
- The game currently lacks actual AI-generated sprites, full combat rules, and Draw Things integration.
- Before publishing public auto-updates we must implement integrity validation and rollback for application replacements.
