extends Control
# Launcher logic remains bundled with the Mac application, outside game update packs.
const BASE_PACK := "res://base-game.pck"
const ACTIVE_PACK := "user://updates/active-game.pck"
const PREVIOUS_PACK := "user://updates/previous-game.pck"
const META := "user://updates/installed.json"
const OLD_META := "user://updates/previous-installed.json"
const GAME_SCENE := "res://main.tscn"

func _ready() -> void:
	# A base copy of the game is bundled; external content can override it.
	var base_path := ProjectSettings.globalize_path(BASE_PACK)
	if OS.has_feature("macos") and not OS.has_feature("editor"):
		base_path = OS.get_executable_path().get_base_dir().path_join("../Resources/base-game.pck").simplify_path()
	if not ProjectSettings.load_resource_pack(base_path, true):
		_show_problem("Bundled game content is missing.")
		return
	if FileAccess.file_exists(ACTIVE_PACK):
		if not ProjectSettings.load_resource_pack(ProjectSettings.globalize_path(ACTIVE_PACK), true):
			_rollback()
			_show_problem("Last update could not be loaded. Restored backup; restart the game.")
			return
	var scene = load(GAME_SCENE)
	if scene == null or not scene is PackedScene:
		_rollback()
		_show_problem("Game scene is invalid. Previous version restored. Restart to retry.")
		return
	var error := get_tree().change_scene_to_packed(scene)
	if error != OK:
		_rollback()
		_show_problem("Unable to start game. Previous version restored; restart.")

func _rollback() -> void:
	var active := ProjectSettings.globalize_path(ACTIVE_PACK)
	var prior := ProjectSettings.globalize_path(PREVIOUS_PACK)
	if FileAccess.file_exists(ACTIVE_PACK):
		DirAccess.remove_absolute(active)
	if FileAccess.file_exists(PREVIOUS_PACK):
		DirAccess.rename_absolute(prior, active)
	if FileAccess.file_exists(OLD_META):
		if FileAccess.file_exists(META):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(META))
		DirAccess.rename_absolute(ProjectSettings.globalize_path(OLD_META), ProjectSettings.globalize_path(META))


func _show_problem(message: String) -> void:
	var box := VBoxContainer.new()
	box.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	add_child(box)
	var label := Label.new()
	label.text = message
	box.add_child(label)
	var button := Button.new()
	button.text = "Close"
	button.pressed.connect(func(): get_tree().quit())
	box.add_child(button)
