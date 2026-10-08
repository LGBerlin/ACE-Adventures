extends Control
# Stable Godot launcher prototype. This script is intended to be bundled
# inside the permanent application, and must not be overridden by game packs.
const PACK_PATH := "user://updates/active-game.pck"
const GAME_SCENE := "res://main.tscn"

func _ready() -> void:
	var active_path := ProjectSettings.globalize_path(PACK_PATH)
	if FileAccess.file_exists(PACK_PATH):
		if not ProjectSettings.load_resource_pack(active_path, true):
			push_warning("Unable to load installed game content; using bundled fallback")
	var error := get_tree().change_scene_to_file(GAME_SCENE)
	if error != OK:
		push_error("Unable to launch ACE Adventures game scene")
