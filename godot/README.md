# ACE Adventures — Godot graphical prototype

This folder is an **independent Godot project** intended for Godot 4.x, including the user's installed 4.7.2.

## Opening it
1. Launch **Godot**.
2. Click **Import**.
3. Select the `godot/project.godot` file.
4. Click **Import & Edit**, then **Run Project** (F6 or F5 as appropriate).

No extra assets or downloaded AI models are required to open this first project.

## Implemented in this first Godot source version
- Native game-engine window with retro panel colours and a character sheet structure.
- Name, age, and class are the only user-selected character generation inputs.
- One-time character roll persisted in `user://ace_adventures_godot.json`.
- Class paths, rarities, magic affinities, stats, starting items, moves and skills.
- Separate skills and moves panels.
- Free-text action input and a D20 popup with modifiers, DCs and outcome grades.

## Not implemented yet
- This is a source project, **not an in-app update for the existing Mac .app**. The existing updater only accepts a Python payload; native Godot bundles need a new signed/versioned distribution path.
- Ollama, Draw Things, and LibreSprite aren't connected yet.
- The sprite panel is deliberately marked as a placeholder.
- Combat and action interpretation use simple heuristics; damage, tactical positioning, world persistence and quests will follow after core UI review.
- Custom fonts and production sprite sheets are not bundled.

Character data from the old Python version does not automatically migrate here. Do not delete the old Mac app or its saves.
