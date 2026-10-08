extends Control
# First native Godot interface prototype. Not the final rules engine.
const SAVE_PATH := "user://ace_adventures_godot.json"
const LIBRARY_PATH := "user://campaign_library.json"
const MIGRATION_MARKER := "user://legacy_campaign_imported.marker"
const CLASSES := ["Rogue", "Mage", "Fighter", "Vessel"]
const PATHS := {
	"Rogue": ["Thief", "Ranger", "Assassin", "Arcane Trickster"],
	"Mage": ["Elementalist", "Spellweaver", "Runesage", "Archon Apprentice"],
	"Fighter": ["Martial Artist", "Knight", "Swordsman", "Barbarian", "Paladin"],
	"Vessel": ["Monk", "Druid", "Spirit Fighter", "Warden", "Oracle Vessel"]
}
const AFFINITIES := ["Earth", "Water", "Fire", "Air", "Lightning", "Gravity", "Blood", "Illusion", "Light", "Dark", "Support", "Time", "Creation", "Chaos"]
const MOVES := {
	"Earth": ["Ground Tremble", "Pebble Shot", "Mud Slap"],
	"Water": ["Water Shot", "Ice Shard", "Splash"],
	"Air": ["Wind Gust", "Air Cutter", "Air Twist"],
	"Fire": ["Flame Flick", "Firewall", "Heat Wave"],
	"Lightning": ["Electric Whip", "Lightning Dash", "Static Shock"],
	"Gravity": ["Downfall", "Micro-Psychokinesis", "Gravitational Push"],
	"Blood": ["Blood Drain", "Hemorrhage", "Sanguine Strike"],
	"Illusion": ["Mirage", "Phantom Strike", "Shape Shift"],
	"Light": ["Blinding Light", "Heavenly Bullet", "Divine Shield"],
	"Dark": ["Shadow Step", "Nightmare", "Dark Pulse"],
	"Support": ["Healing Wave", "Protective Aura", "Mana Boost"],
	"Time": ["Slow Mo Bubble", "Temporal Shift", "Chrono Dash"],
	"Creation": ["Construct", "Materialize", "Form"],
	"Chaos": ["Mind Jumble", "Randomize", "Unpredictable Strike"]
}
const COLORS := {
	"background": Color("#25201c"), "panel": Color("#494137"),
	"border": Color("#b99864"), "ink": Color("#f2e4c6"),
	"highlight": Color("#806d53")
}
var rng := RandomNumberGenerator.new()
var state: Dictionary = {}
var library: Dictionary = {"campaigns": {}}
var active_campaign: String = ""
var campaign_title_input: LineEdit
var campaign_party_input: SpinBox
var name_input: LineEdit
var age_input: SpinBox
var selected_class: String = ""
var class_buttons: Dictionary = {}
var class_choice: OptionButton
var status: Label
var action_input: TextEdit
var scene_root: Control
var dice_dialog: AcceptDialog
var pending: Dictionary = {}
var log_text: RichTextLabel
var update_manager: Node
var update_status: Label

func _ready() -> void:
	rng.randomize()
	_load_state()
	_load_library()
	update_manager = preload("res://updater.gd").new()
	add_child(update_manager)
	_build()

func _load_state() -> void:
	if FileAccess.file_exists(SAVE_PATH):
		var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
		var parsed = JSON.parse_string(f.get_as_text())
		if parsed is Dictionary:
			state = parsed
	if state.is_empty():
		state = {"character": {}, "history": [], "location": "Ironwood Crossing", "enemy_hp": 0}

func _save_state() -> void:
	_store_campaign()

func _check_updates() -> void:
	update_status.text = "Checking GitHub Releases..."
	var response: Dictionary = await update_manager.check_update()
	update_status.text = str(response.get("message", response.get("error", "Unknown update status")))

func _install_updates() -> void:
	update_status.text = "Downloading verified update. Do not close the game..."
	var response: Dictionary = await update_manager.install_update()
	update_status.text = str(response.get("message", response.get("error", "Update failed")))

func _fresh_state() -> Dictionary:
	return {"character": {}, "history": [], "location": "Ironwood Crossing", "enemy_hp": 0}

func _load_library() -> void:
	if FileAccess.file_exists(LIBRARY_PATH):
		var file := FileAccess.open(LIBRARY_PATH, FileAccess.READ)
		var parsed = JSON.parse_string(file.get_as_text())
		if parsed is Dictionary and parsed.has("campaigns") and parsed["campaigns"] is Dictionary:
			library = parsed
	if not FileAccess.file_exists(LIBRARY_PATH) and not FileAccess.file_exists(MIGRATION_MARKER) and FileAccess.file_exists(SAVE_PATH):
		var migrated_id := "legacy"
		library["campaigns"][migrated_id] = {
			"title": "Original Adventure", "players": 1,
			"state": state.duplicate(true)
		}
		_write_library()
		var marker := FileAccess.open(MIGRATION_MARKER, FileAccess.WRITE)
		if marker != null:
			marker.store_string("Legacy character imported; original file retained.")
	state = _fresh_state()

func _write_library() -> void:
	var tmp := LIBRARY_PATH + ".tmp"
	var file := FileAccess.open(tmp, FileAccess.WRITE)
	if file == null:
		push_error("Could not save campaign library")
		return
	file.store_string(JSON.stringify(library, "\t"))
	file.close()
	DirAccess.rename_absolute(ProjectSettings.globalize_path(tmp), ProjectSettings.globalize_path(LIBRARY_PATH))

func _store_campaign() -> void:
	if active_campaign.is_empty():
		return
	if library["campaigns"].has(active_campaign):
		library["campaigns"][active_campaign]["state"] = state.duplicate(true)
		_write_library()

func _create_campaign() -> void:
	var title := campaign_title_input.text.strip_edges()
	if title.is_empty() or title.length() > 60:
		status.text = "Enter a campaign name (1–60 characters)."
		return
	var id := str(Time.get_unix_time_from_system()).replace(".", "_") + "_" + str(rng.randi_range(10000, 99999))
	var players := int(campaign_party_input.value)
	library["campaigns"][id] = {"title": title, "players": players, "state": _fresh_state()}
	_write_library()
	_open_campaign(id)

func _open_campaign(id: String) -> void:
	if not library["campaigns"].has(id):
		return
	active_campaign = id
	state = library["campaigns"][id]["state"].duplicate(true)
	_build()

func _exit_campaign() -> void:
	_store_campaign()
	active_campaign = ""
	state = _fresh_state()
	_build()

func _build_library(root: VBoxContainer) -> void:
	var pane := _panel("Campaign Library")
	root.add_child(pane.get_parent())
	pane.add_child(_label("Choose a campaign, or begin a new adventure. Every campaign has its own character and save."))
	var campaigns: Dictionary = library["campaigns"]
	for id in campaigns:
		var campaign: Dictionary = campaigns[id]
		var saved: Dictionary = campaign.get("state", {})
		var char_data: Dictionary = saved.get("character", {})
		var description := str(campaign.get("title", "Untitled"))
		if not char_data.is_empty():
			description += "  ·  " + str(char_data.get("name", "Adventurer")) + " / Level " + str(char_data.get("level", 1))
		else:
			description += "  ·  Character not created"
		var campaign_id: String = str(id)
		pane.add_child(_button("CONTINUE  ·  " + description, func(): _open_campaign(campaign_id)))
	pane.add_child(_label("NEW CAMPAIGN", 18))
	campaign_title_input = LineEdit.new()
	campaign_title_input.placeholder_text = "Campaign name"
	pane.add_child(campaign_title_input)
	campaign_party_input = SpinBox.new()
	campaign_party_input.min_value = 1
	campaign_party_input.max_value = 8
	campaign_party_input.value = 1
	pane.add_child(_label("Number of players (future multiplayer planning)", 12))
	pane.add_child(campaign_party_input)
	status = _label("")
	pane.add_child(status)
	pane.add_child(_button("CREATE CAMPAIGN", _create_campaign))

func _label(t: String, sz: int = 16) -> Label:
	var l := Label.new()
	l.text = t
	l.add_theme_color_override("font_color", COLORS.ink)
	l.add_theme_font_size_override("font_size", sz)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return l

func _panel(title: String) -> VBoxContainer:
	var style := StyleBoxFlat.new()
	style.bg_color = COLORS.panel
	style.border_color = COLORS.border
	style.set_border_width_all(4)
	style.set_content_margin_all(12)
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", style)
	var content := VBoxContainer.new()
	content.add_theme_constant_override("separation", 9)
	p.add_child(content)
	content.add_child(_label(title.to_upper(), 19))
	return content

func _button(t: String, callback: Callable) -> Button:
	var b := Button.new()
	b.text = t
	b.custom_minimum_size.y = 41
	b.pressed.connect(callback)
	return b

func _clear_screen() -> void:
	for child in get_children():
		if child == update_manager:
			continue
		remove_child(child)
		child.queue_free()

func _build() -> void:
	_clear_screen()
	var bg := ColorRect.new()
	bg.color = COLORS.background
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	scene_root = MarginContainer.new()
	scene_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene_root.add_theme_constant_override("margin_left", 18)
	scene_root.add_theme_constant_override("margin_right", 18)
	scene_root.add_theme_constant_override("margin_top", 16)
	scene_root.add_theme_constant_override("margin_bottom", 16)
	add_child(scene_root)
	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 12)
	scene_root.add_child(root)
	root.add_child(_label("⚔  ACE ADVENTURES  ·  THE D20 CHRONICLES", 26))
	var toolbar := HBoxContainer.new()
	root.add_child(toolbar)
	toolbar.add_child(_button("CHECK FOR UPDATES", _check_updates))
	toolbar.add_child(_button("INSTALL UPDATE", _install_updates))
	update_status = _label("Game v0.3.0 · Campaigns are saved separately from app updates.", 12)
	toolbar.add_child(update_status)
	if active_campaign.is_empty():
		_build_library(root)
	elif state.character.is_empty():
		_build_creation(root)
	else:
		_build_game(root)

func _build_creation(root: VBoxContainer) -> void:
	root.add_child(_button("← SAVE & RETURN TO CAMPAIGNS", _exit_campaign))
	var pane := _panel("Character Roulette — One permanent roll")
	root.add_child(pane.get_parent())
	pane.add_child(_label("Choose your name, age, and class. All other character traits are random. No rerolls."))
	name_input = LineEdit.new()
	name_input.placeholder_text = "Character name"
	pane.add_child(name_input)
	age_input = SpinBox.new()
	age_input.min_value = 10
	age_input.max_value = 120
	age_input.value = 20
	pane.add_child(age_input)
	pane.add_child(_label("SELECT YOUR CLASS", 18))
	var class_row := HBoxContainer.new()
	pane.add_child(class_row)
	selected_class = ""
	class_buttons.clear()
	for cl in CLASSES:
		var class_id: String = str(cl)
		var b := _button(class_id, func(): _select_class(class_id))
		b.toggle_mode = true
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		class_row.add_child(b)
		class_buttons[class_id] = b
	status = _label("")
	pane.add_child(status)
	pane.add_child(_button("ROLL MY CHARACTER — PERMANENT", _roll_character))

func _select_class(cl: String) -> void:
	selected_class = cl
	for key in class_buttons:
		class_buttons[key].button_pressed = (key == cl)
	status.text = "SELECTED CLASS: " + cl

func _weighted(options: Array, weights: Array) -> String:
	var total := 0
	for w in weights:
		total += int(w)
	var n := rng.randi_range(1, total)
	for i in options.size():
		n -= int(weights[i])
		if n <= 0:
			return str(options[i])
	return str(options.back())

func _roll_character() -> void:
	if not state.character.is_empty():
		return
	var nm := name_input.text.strip_edges()
	if nm.length() < 1 or nm.length() > 32:
		status.text = "Enter a name (1–32 characters)."
		return
	if selected_class.is_empty():
		status.text = "Select Rogue, Mage, Fighter, or Vessel first."
		return
	var cl: String = selected_class
	var paths: Array = PATHS[cl]
	var weights := []
	match cl:
		"Rogue": weights = [35, 25, 30, 10]
		"Mage": weights = [45, 30, 18, 7]
		"Fighter": weights = [25, 25, 24, 18, 8]
		"Vessel": weights = [28, 25, 23, 18, 6]
	var path: String = _weighted(paths, weights)
	var magic := "None"
	if cl == "Mage" or path == "Arcane Trickster":
		magic = _weighted(AFFINITIES, [9, 9, 9, 8, 8, 7, 7, 7, 7, 7, 7, 5, 5, 5])
	elif path in ["Druid", "Warden"]:
		magic = "Nature"
	elif path in ["Monk", "Spirit Fighter", "Oracle Vessel"]:
		magic = "Spirit"
	elif path == "Paladin":
		magic = "Light"
	var race := _weighted(["Human", "Elf", "Dwarf", "Halfling", "Orc", "Tiefling", "Gnome"], [30, 16, 15, 12, 11, 9, 7])
	var abilities := {}
	for attribute in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
		abilities[attribute] = rng.randi_range(8, 16)
	var hp := rng.randi_range(15, 23)
	var mana := rng.randi_range(10, 18)
	match cl:
		"Mage": hp -= 5; mana += 12
		"Fighter": hp += 9; mana -= 7
		"Vessel": hp += 3; mana += 3
	var moves: Array = MOVES.get(magic, [])
	if moves.is_empty():
		moves = [path + " Strike", "Guard", "Quick Step"]
	state.character = {
		"name": nm, "age": int(age_input.value), "class": cl, "path": path,
		"magic": magic, "race": race, "level": 1, "xp": 0,
		"hp": hp, "max_hp": hp, "mana": mana, "max_mana": mana,
		"abilities": abilities, "skills": ["Perception", "Survival", "Athletics"],
		"moves": moves, "passives": [path + " Training"],
		"items": ["Travel Rations", "Worn Weapon"], "gold": rng.randi_range(7, 35),
		"sprite_seed": rng.randi()
	}
	state.history.append("Your adventure begins at Ironwood Crossing.")
	_save_state()
	_build()

func _build_game(root: VBoxContainer) -> void:
	root.add_child(_button("← SAVE & RETURN TO CAMPAIGNS", _exit_campaign))
	var columns := HBoxContainer.new()
	columns.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(columns)
	var left := VBoxContainer.new()
	left.custom_minimum_size.x = 280
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	columns.add_child(left)
	var mid := VBoxContainer.new()
	mid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	columns.add_child(mid)
	var right := VBoxContainer.new()
	right.custom_minimum_size.x = 270
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	columns.add_child(right)
	var c: Dictionary = state.character
	var identity := _panel("Character sheet")
	left.add_child(identity.get_parent())
	var identity_grid := GridContainer.new()
	identity_grid.columns = 2
	identity.add_child(identity_grid)
	for pair in [
		["NAME", c.name], ["AGE", c.age], ["CLASS", c["class"]],
		["RACE", c.race], ["LEVEL", c.level], ["PATH", c.path],
		["MAGIC / AFFINITY", c.magic], ["EXPERIENCE", c.xp]
	]:
		var value_box := VBoxContainer.new()
		value_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		value_box.custom_minimum_size.x = 118
		value_box.add_child(_label(str(pair[0]), 12))
		value_box.add_child(_label(str(pair[1]), 16))
		identity_grid.add_child(value_box)
	identity.add_child(_label("HP %s/%s   ·   MANA %s/%s" % [c.hp, c.max_hp, c.mana, c.max_mana]))
	for attribute in c.abilities:
		identity.add_child(_label("%s  %s" % [attribute, c.abilities[attribute]]))
	var skills := _panel("Skills — checks")
	left.add_child(skills.get_parent())
	for skill in c.skills:
		skills.add_child(_label("• " + str(skill)))
	if OS.has_feature("editor"):
		var test_panel := _panel("Development tools")
		left.add_child(test_panel.get_parent())
		test_panel.add_child(_label("Testing only — not a gameplay reroll.", 12))
		test_panel.add_child(_button("RESET TEST CHARACTER", _reset_test_character))
	var encounter := _panel("Exploration & battle")
	mid.add_child(encounter.get_parent())
	encounter.add_child(_label("IRONWOOD CROSSING"))
	encounter.add_child(_label("The forest road passes a ruined stone gate. Describe what you do, in your own words."))
	encounter.add_child(_label("Enemy HP: %d" % state.enemy_hp if state.enemy_hp > 0 else "No enemy currently present"))
	encounter.add_child(_button("Find an encounter", _spawn_enemy))
	var adventure := _panel("Adventure log & free-form actions")
	mid.add_child(adventure.get_parent())
	log_text = RichTextLabel.new()
	log_text.custom_minimum_size.y = 180
	log_text.size_flags_vertical = Control.SIZE_EXPAND_FILL
	for e in state.history:
		log_text.add_text(str(e) + "\n\n")
	adventure.add_child(log_text)
	action_input = TextEdit.new()
	action_input.custom_minimum_size.y = 90
	action_input.placeholder_text = "I ignite the dry leaves with Flame Flick to create smoke and escape..."
	adventure.add_child(action_input)
	adventure.add_child(_button("ATTEMPT ACTION → ROLL D20", _attempt_action))
	var sprite := _panel("Pixel sprite")
	right.add_child(sprite.get_parent())
	var picture := ColorRect.new()
	picture.color = Color("#b8af99")
	picture.custom_minimum_size = Vector2(210, 190)
	sprite.add_child(picture)
	sprite.add_child(_label("Sprite system: graphical asset pipeline pending", 11))
	var identity2 := _panel("Path & affinity")
	right.add_child(identity2.get_parent())
	identity2.add_child(_label(str(c.path)))
	identity2.add_child(_label("Magic: " + str(c.magic)))
	var abilities := _panel("Moveset — active")
	right.add_child(abilities.get_parent())
	for move in c.moves:
		abilities.add_child(_label("• " + str(move)))
	var inventory := _panel("Equipment & passives")
	right.add_child(inventory.get_parent())
	for item in c.items:
		inventory.add_child(_label("• " + str(item)))
	inventory.add_child(_label("Gold: " + str(c.gold)))
	for passive in c.passives:
		inventory.add_child(_label("Passive: " + str(passive)))

func _reset_test_character() -> void:
	if not OS.has_feature("editor"):
		return
	state = {"character": {}, "history": [], "location": "Ironwood Crossing", "enemy_hp": 0}
	_save_state()
	_build()

func _spawn_enemy() -> void:
	if state.enemy_hp <= 0:
		state.enemy_hp = 16
		state.history.append("A moss goblin steps out of the undergrowth.")
		_save_state()
		_build()

func _attempt_action() -> void:
	var action := action_input.text.strip_edges()
	if action.is_empty():
		return
	var c: Dictionary = state.character
	var lower := action.to_lower()
	var check := "WIS"
	if "persuad" in lower or "convinc" in lower or "talk" in lower:
		check = "CHA"
	elif "sneak" in lower or "hide" in lower or "escape" in lower:
		check = "DEX"
	elif "strike" in lower or "attack" in lower or "push" in lower:
		check = "STR"
	elif "spell" in lower or "cast" in lower or "magic" in lower:
		check = "INT"
	var modifier := int(floor((float(c.abilities[check]) - 10.0) / 2.0))
	pending = {"action": action, "check": check, "modifier": modifier, "dc": 13}
	_open_die()

func _open_die() -> void:
	dice_dialog = AcceptDialog.new()
	dice_dialog.title = "D20 — Action Check"
	dice_dialog.dialog_text = "Roll for %s. Modifier %+d. Difficulty %d.\nClick ROLL to reveal your fate." % [pending.check, pending.modifier, pending.dc]
	add_child(dice_dialog)
	dice_dialog.get_ok_button().text = "ROLL D20"
	dice_dialog.confirmed.connect(_resolve_roll)
	dice_dialog.popup_centered(Vector2i(470, 220))

func _resolve_roll() -> void:
	var die := rng.randi_range(1, 20)
	var result := die + int(pending.modifier)
	var outcome := "Success" if result >= int(pending.dc) else "Failure"
	if die == 20:
		outcome = "Critical Success"
	elif die == 1:
		outcome = "Critical Failure"
	elif result >= int(pending.dc) + 5:
		outcome = "Exceptional Success"
	elif result >= int(pending.dc) - 3 and result < int(pending.dc):
		outcome = "Partial Success"
	var message := "%s\nD20 %d %+d = %d vs DC %d — %s." % [pending.action, die, pending.modifier, result, pending.dc, outcome]
	state.history.append(message)
	_save_state()
	_build()
