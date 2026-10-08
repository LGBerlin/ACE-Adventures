extends Node
# Native app updates for exported macOS builds; user:// saves are untouched.
const API := "https://api.github.com/repos/LGBerlin/ACE-Adventures/releases/latest"
const VERSION := "0.3.1"
var available: Dictionary = {}

func _newer(tag: String) -> bool:
	var a := tag.trim_prefix("v").split(".")
	var b := VERSION.split(".")
	for i in range(3):
		var x := int(a[i]) if i < a.size() else 0
		var y := int(b[i])
		if x > y: return true
		if x < y: return false
	return false

func _request(url: String, download: String = "") -> Array:
	var http := HTTPRequest.new()
	add_child(http)
	http.timeout = 180.0 if not download.is_empty() else 25.0
	if not download.is_empty(): http.download_file = download
	var error := http.request(url, ["User-Agent: ACE-Adventures", "Accept: application/vnd.github+json"])
	if error != OK:
		http.queue_free()
		return [false, PackedByteArray()]
	var response: Array = await http.request_completed
	http.queue_free()
	return [int(response[0]) == HTTPRequest.RESULT_SUCCESS and int(response[1]) == 200, response[3]]

func check_update() -> Dictionary:
	if not OS.has_feature("macos") or OS.has_feature("editor"):
		return {"error": "Updates require the installed macOS application."}
	var result := await _request(API)
	if not result[0]: return {"error": "GitHub release check failed."}
	var release = JSON.parse_string(result[1].get_string_from_utf8())
	if not release is Dictionary: return {"error": "Invalid GitHub response."}
	var tag := str(release.get("tag_name", ""))
	if not _newer(tag):
		available = {}
		return {"message": "Already up to date (v" + VERSION + ")."}
	for item in release.get("assets", []):
		if str(item.get("name", "")) == "ACE Adventures Mac.zip":
			var digest := str(item.get("digest", ""))
			if not digest.begins_with("sha256:") or digest.length() != 71:
				return {"error": "Release has no SHA-256 digest."}
			available = {"tag": tag, "url": str(item["browser_download_url"]), "hash": digest.substr(7)}
			return {"message": tag + " available. Click Install Update."}
	return {"error": "No Mac build in the latest release."}

func install_update() -> Dictionary:
	if available.is_empty(): return {"error": "Check for updates first."}
	var executable := OS.get_executable_path()
	var marker := "/Contents/MacOS/"
	var pos := executable.find(marker)
	if pos < 0: return {"error": "Installed app path not found."}
	var app := executable.substr(0, pos)
	if not app.ends_with(".app"): return {"error": "Invalid application path."}
	var zip := ProjectSettings.globalize_path("user://ACE Adventures update.zip")
	var result := await _request(str(available["url"]), zip)
	if not result[0]: return {"error": "Download failed."}
	if FileAccess.get_sha256(zip).to_lower() != str(available["hash"]).to_lower():
		DirAccess.remove_absolute(zip)
		return {"error": "Checksum mismatch. Update refused."}
	var installer := ProjectSettings.globalize_path("user://install update.sh")
	var lines := [
		"#!/bin/bash", "set -euo pipefail",
		"ZIP=\"$1\"", "TARGET=\"$2\"", "PID=\"$3\"",
		"for i in $(seq 1 80); do if ! kill -0 \"$PID\" 2>/dev/null; then break; fi; sleep 0.5; done",
		"if kill -0 \"$PID\" 2>/dev/null; then exit 1; fi",
		"WORK=$(mktemp -d)", "trap 'rm -rf \"$WORK\"' EXIT",
		"ditto -x -k \"$ZIP\" \"$WORK\"",
		"test -d \"$WORK/ACE Adventures.app/Contents/MacOS\"",
		"BACKUP=\"$TARGET.previous\"",
		"rm -rf \"$BACKUP\"", "mv \"$TARGET\" \"$BACKUP\"",
		"if ! mv \"$WORK/ACE Adventures.app\" \"$TARGET\"; then mv \"$BACKUP\" \"$TARGET\"; exit 1; fi",
		"open \"$TARGET\" || true"
	]
	var file := FileAccess.open(installer, FileAccess.WRITE)
	if file == null: return {"error": "Could not create installer."}
	file.store_string("\n".join(lines) + "\n")
	file.close()
	var pid := OS.create_process("/bin/bash", [installer, zip, app, str(OS.get_process_id())])
	if pid < 0: return {"error": "Could not start installer."}
	get_tree().quit()
	return {"message": "Installer started."}
