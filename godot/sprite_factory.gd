extends RefCounted
# Deterministic 48x64 sprite art. No API, random reroll, or network needed.
# The identical saved character attributes/seed produce the identical sprite.
const W := 48
const H := 64

static func generate(c: Dictionary) -> Texture2D:
	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	img.fill(Color.TRANSPARENT)
	var seed_value := int(c.get("sprite_seed", 1))
	var r := RandomNumberGenerator.new()
	r.seed = seed_value if seed_value >= 0 else -seed_value
	var class_id := str(c.get("class", "Rogue"))
	var race := str(c.get("race", "Human"))
	var path := str(c.get("path", ""))
	var magic := str(c.get("magic", "None"))
	var skin := Color("#d2a079")
	match race:
		"Elf": skin = Color("#e0b999")
		"Dwarf": skin = Color("#c38f75")
		"Orc": skin = Color("#83aa78")
		"Tiefling": skin = Color("#aa778e")
		"Gnome": skin = Color("#e8bc8e")
		"Halfling": skin = Color("#cb9b78")
	var fabric := Color("#466c59")
	match class_id:
		"Mage": fabric = Color("#63518d")
		"Fighter": fabric = Color("#687c8b")
		"Vessel": fabric = Color("#977a59")
	if path == "Assassin": fabric = Color("#45435d")
	if path == "Paladin": fabric = Color("#c9b07a")
	if path == "Druid": fabric = Color("#4f8859")
	var hair_palette := [Color("#372a25"), Color("#bd8a4f"), Color("#a5a09a"), Color("#5c4441")]
	var hair: Color = hair_palette[r.randi_range(0, hair_palette.size()-1)]
	var boots := Color("#302b31")
	# Shadow and boots
	_rect(img, 10, 58, 29, 3, Color("#4b463d"))
	_rect(img, 16, 52, 7, 7, boots)
	_rect(img, 26, 52, 7, 7, boots)
	# Legs and cloak.
	_rect(img, 16, 39, 17, 15, Color("#33323b"))
	_rect(img, 12, 28, 25, 19, Color("#292d31"))
	_rect(img, 14, 30, 21, 18, fabric)
	_rect(img, 19, 32, 10, 13, fabric.lightened(0.1))
	# Arms and hands.
	_rect(img, 9, 30, 5, 17, fabric.darkened(0.25))
	_rect(img, 36, 30, 5, 17, fabric.darkened(0.25))
	_rect(img, 10, 45, 4, 4, skin)
	_rect(img, 36, 45, 4, 4, skin)
	# Head and hair
	_rect(img, 16, 13, 17, 17, Color("#362e2d"))
	_rect(img, 18, 15, 13, 14, skin)
	_rect(img, 17, 11, 15, 7, hair)
	_rect(img, 16, 14, 3, 7, hair)
	if race == "Elf" or race == "Tiefling":
		_rect(img, 12, 19, 5, 4, skin)
		_rect(img, 33, 19, 5, 4, skin)
	if race == "Tiefling":
		_rect(img, 19, 7, 3, 6, Color("#473642"))
		_rect(img, 28, 7, 3, 6, Color("#473642"))
	_rect(img, 21, 23, 2, 2, Color("#263039"))
	_rect(img, 28, 23, 2, 2, Color("#263039"))
	# Equipment changes silhouette.
	if class_id == "Mage":
		_rect(img, 6, 19, 2, 35, Color("#78604b"))
		_rect(img, 4, 16, 6, 7, Color("#8badd5") if magic != "Fire" else Color("#e58c4b"))
	elif class_id == "Fighter":
		_rect(img, 39, 27, 3, 29, Color("#d2d2ce"))
		_rect(img, 36, 44, 9, 3, Color("#967951"))
	elif class_id == "Rogue":
		_rect(img, 40, 39, 2, 13, Color("#c0c7c8"))
		_rect(img, 7, 39, 2, 13, Color("#c0c7c8"))
	else:
		_rect(img, 7, 19, 3, 35, Color("#9c8664"))
		_rect(img, 5, 16, 7, 5, Color("#83b999"))
	# Permanent small rune keyed by affinity.
	if magic != "None":
		var glow := Color("#78badb")
		if magic == "Fire": glow = Color("#f1a65c")
		if magic == "Nature": glow = Color("#7cce80")
		_rect(img, 22, 36, 4, 4, glow)
	return ImageTexture.create_from_image(img)

static func _rect(img: Image, x: int, y: int, w: int, h: int, color: Color) -> void:
	for xx in range(maxi(0, x), mini(W, x + w)):
		for yy in range(maxi(0, y), mini(H, y + h)):
			img.set_pixel(xx, yy, color)
