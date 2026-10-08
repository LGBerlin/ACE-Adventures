extends Node
# Stable launcher pack updater. Saves never reside in this directory.
const MANIFEST_URL := "https://raw.githubusercontent.com/LGBerlin/ACE-Adventures/main/game-update.json"
const UPDATE_DIR := "user://updates/"
const ACTIVE := UPDATE_DIR + "active-game.pck"
const BACKUP := UPDATE_DIR + "previous-game.pck"
const STAGING := UPDATE_DIR + "staging-game.pck"
const METADATA := UPDATE_DIR + "installed.json"
var remote: Dictionary = {}

func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(UPDATE_DIR))

func _is_newer(candidate: String, current: String) -> bool:
	var c := candidate.split(".")
	var v := current.split(".")
	if c.size() != 3 or v.size() != 3:
		return false
	for i in range(3):
		if not c[i].is_valid_int() or not v[i].is_valid_int():
			return false
		if int(c[i]) > int(v[i]):
			return true
		if int(c[i]) < int(v[i]):
			return false
	return false

func current_version() -> String:
	if FileAccess.file_exists(METADATA):
		var obj = JSON.parse_string(FileAccess.get_file_as_string(METADATA))
		if obj is Dictionary:
			return str(obj.get("version", "0.4.0"))
	return "0.4.0"

func check() -> Dictionary:
	var req := HTTPRequest.new()
	add_child(req)
	req.timeout = 30
	var err := req.request(MANIFEST_URL, ["User-Agent: ACE-Adventures"])
	if err != OK:
		req.queue_free()
		return {"error": "Cannot start update check (" + str(err) + ")"}
	var response: Array = await req.request_completed
	req.queue_free()
	if response[0] != HTTPRequest.RESULT_SUCCESS or response[1] != 200:
		return {"error": "Update check failed (HTTP %s, network %s)" % [response[1], response[0]]}
	var m = JSON.parse_string(response[3].get_string_from_utf8())
	if not m is Dictionary:
		return {"error": "Invalid update manifest"}
	var version := str(m.get("version", ""))
	if not _is_newer(version, current_version()):
		remote = {}
		return {"message": "Game is current: " + current_version()}
	var url := str(m.get("url", ""))
	var digest := str(m.get("sha256", "")).to_lower()
	if not url.begins_with("https://github.com/LGBerlin/ACE-Adventures/releases/download/"):
		return {"error": "Untrusted download URL"}
	if digest.length() != 64:
		return {"error": "Missing SHA-256"}
	for letter in digest:
		if not "0123456789abcdef".contains(letter):
			return {"error": "Invalid SHA-256"}
	remote = {"version": version, "url": url, "sha256": digest}
	return {"message": "Game update " + version + " is available"}

func download_and_stage() -> Dictionary:
	if remote.is_empty():
		return {"error": "Check for updates first"}
	var req := HTTPRequest.new()
	add_child(req)
	req.timeout = 180
	req.download_file = ProjectSettings.globalize_path(STAGING)
	var err := req.request(str(remote["url"]), ["User-Agent: ACE-Adventures"])
	if err != OK:
		req.queue_free()
		return {"error": "Could not start download"}
	var result: Array = await req.request_completed
	req.queue_free()
	if result[0] != HTTPRequest.RESULT_SUCCESS or result[1] != 200:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(STAGING))
		return {"error": "Download failed: HTTP %s network %s" % [result[1], result[0]]}
	var actual := FileAccess.get_sha256(STAGING).to_lower()
	if actual != remote["sha256"]:
		DirAccess.remove_absolute(ProjectSettings.globalize_path(STAGING))
		return {"error": "SHA-256 verification failed; original game is unchanged"}
	var active := ProjectSettings.globalize_path(ACTIVE)
	var backup := ProjectSettings.globalize_path(BACKUP)
	var staged := ProjectSettings.globalize_path(STAGING)
	if FileAccess.file_exists(BACKUP):
		DirAccess.remove_absolute(backup)
	if FileAccess.file_exists(ACTIVE):
		if DirAccess.rename_absolute(active, backup) != OK:
			return {"error": "Could not create rollback backup"}
	if DirAccess.rename_absolute(staged, active) != OK:
		if FileAccess.file_exists(BACKUP):
			DirAccess.rename_absolute(backup, active)
		return {"error": "Failed to activate update; previous game restored"}
	var tmp := ProjectSettings.globalize_path(METADATA + ".tmp")
	var file := FileAccess.open(tmp, FileAccess.WRITE)
	if file == null:
		return {"error": "Update installed but metadata could not be saved"}
	file.store_string(JSON.stringify({"version": remote["version"], "sha256": remote["sha256"]}))
	file.close()
	DirAccess.rename_absolute(tmp, ProjectSettings.globalize_path(METADATA))
	remote = {}
	return {"message": "Update installed. Restart ACE Adventures to activate it."}
