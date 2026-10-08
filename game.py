"""Deterministic game state and rules for ACE Adventures."""
import json
import random
from pathlib import Path

SAVE_PATH = Path("saves/game.json")
ELEMENTS = [("Fire", 30), ("Water", 24), ("Earth", 20), ("Air", 16), ("Time", 5), ("Gravity", 3), ("Creation", 1), ("Fate", 1)]
SHOP_ITEMS = [
    {"name": "Iron Sword", "price": 20, "effect": "A reliable weapon."},
    {"name": "Health Potion", "price": 12, "effect": "Restores 10 HP."},
    {"name": "Mana Potion", "price": 14, "effect": "Restores 8 mana."},
    {"name": "Ember Ring", "price": 55, "effect": "A warm, unusual relic."},
]

def new_game(name="Adventurer"):
    return {
        "name": name.strip()[:32] or "Adventurer", "hp": 30, "max_hp": 30,
        "mana": 20, "max_mana": 20, "gold": 60, "location": "Ironwood Forest",
        "inventory": ["Worn Sword"], "spells": [], "quests": [],
        "history": [], "enemy": None, "turn": 0
    }

def save(state):
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAVE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")

def load():
    if SAVE_PATH.exists():
        return json.loads(SAVE_PATH.read_text(encoding="utf-8"))
    return new_game()

def generate_spell():
    element = random.choices([e for e, _ in ELEMENTS], weights=[w for _, w in ELEMENTS])[0]
    potency = random.randint(3, 8) if element not in {"Time", "Creation", "Fate"} else random.randint(2, 5)
    return {"name": f"{element} Bolt", "element": element, "power": potency,
            "mana_cost": max(2, potency), "description": f"Deals {potency} {element.lower()} damage."}

def start_encounter(state):
    if state["enemy"]:
        return "An enemy is already present."
    state["enemy"] = {"name": random.choice(["Moss Goblin", "Forest Wisp", "Rootling"]), "hp": 16, "max_hp": 16}
    return f'A {state["enemy"]["name"]} appears with 16 HP.'

def attack(state):
    enemy = state.get("enemy")
    if not enemy:
        return "There is no enemy to attack."
    damage = random.randint(3, 8)
    enemy["hp"] = max(0, enemy["hp"] - damage)
    result = f'You hit {enemy["name"]} for {damage} damage.'
    if enemy["hp"] == 0:
        gold = random.randint(5, 14)
        state["gold"] += gold
        state["enemy"] = None
        return result + f" Victory! You gain {gold} gold."
    retaliation = random.randint(1, 5)
    state["hp"] = max(0, state["hp"] - retaliation)
    return result + f' The enemy strikes back for {retaliation} damage.'

def cast(state, index):
    if not state.get("enemy"):
        return "You need an enemy to cast an offensive spell."
    if not 0 <= index < len(state["spells"]):
        return "Unknown spell."
    spell = state["spells"][index]
    if state["mana"] < spell["mana_cost"]:
        return "Not enough mana."
    state["mana"] -= spell["mana_cost"]
    state["enemy"]["hp"] = max(0, state["enemy"]["hp"] - spell["power"])
    result = f'You cast {spell["name"]} for {spell["power"]} damage.'
    if state["enemy"]["hp"] == 0:
        reward = random.randint(5, 14)
        state["gold"] += reward
        state["enemy"] = None
        return result + f" Victory! You earn {reward} gold."
    retaliation = random.randint(1, 5)
    state["hp"] = max(0, state["hp"] - retaliation)
    return result + f" The enemy retaliates for {retaliation} damage."

def buy(state, item):
    if state["gold"] < item["price"]:
        return "Not enough gold."
    state["gold"] -= item["price"]
    state["inventory"].append(item["name"])
    return f'Bought {item["name"]} for {item["price"]} gold.'
