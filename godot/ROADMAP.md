# ACE Adventures development roadmap (October 2026)

## Non-negotiable gameplay rules
- Four classes: Rogue, Mage, Fighter, Vessel.
- Player chooses only class, name, age at character creation.
- One permanent generation per campaign character; each campaign has separate state.
- Path, affinity, race, abilities, equipment, initial gold, and starting stats determined by weighted generation.
- Each meaningful uncertain action prompts a d20; player types intentions, including creative uses of learned techniques.
- The engine validates and resolves actions; Ollama narrates resolved state but never invents dice results.
- One saved visual identity for each character, enemy, place, and campaign.
- The entire app shares a retro pixel RPG presentation.

## Stage 0 — reliability (in progress)
- No automatic public release on every push.
- Explicit version and manual publishing approval.
- Existing release tags never overwritten.
- Headless Godot parser/startup checks run before publishing.
- Verified SHA-256 manifest and isolated campaign saves.
- Remaining: actual updater end-to-end install and rollback test on user Mac; Apple code signing/notarization.

## Stage 1 — character graphics (started v0.4.0)
- Deterministic, race/class/path-based pixel sprite used in the character sheet.
- Upgrade to layered equipment system and four-directional frames.
- Support cosmetic-only edits and save revised asset, never reroll game attributes.
- Optional Draw Things local service for unique portraits/scene art (not yet integrated).

## Stage 2 — real combat
- Validation against abilities, physical position and environment.
- D20 check overlay, animation and transparent success thresholds.
- Damage rolls, initiative, movement, terrain, enemy turns and reactions.
- Creative tactics like lighting dry leaves to make cover when conditions permit.

## Stage 3 — persistent world and storyline
- AI Director, quest memory, named NPCs with consistent appearances.
- Procedural tile maps kept stable and stateful upon revisits.
- Inventory, shops, faction relationships and level progression.

## Stage 4 — multiplayer foundation
- Campaign party size already stored; actual multiple players and characters remain unimplemented.

## Local software requirements
- Godot 4.7.2 for source editing/test; released Mac app is standalone.
- Ollama qwen3.5:4b already installed for narrative work.
- Draw Things installed but needs a pixel-art-capable model and API integration.
- LibreSprite is optional for editing asset sprites; not required while playing.
- No further downloads required for the current procedural-sprite stage.
