"""ACE Adventures local Streamlit prototype."""
import requests
import streamlit as st
from game import new_game, load, save, generate_spell, SHOP_ITEMS, start_encounter, attack, cast

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3.5:4b"

st.set_page_config(page_title="ACE Adventures", page_icon="⚔️", layout="wide")
st.title("⚔️ ACE Adventures")
st.caption("Local AI Dungeon Master · Early playable prototype")

if "game" not in st.session_state:
    st.session_state.game = load()
game = st.session_state.game

def narrate(action):
    system = (
        "You are the game master of a free-choice fantasy adventure. "
        "Write only the game narration, in second person, 60-140 words. "
        "Be vivid, surprising and consistent. No internal analysis or reasoning. "
        "Never invent or change hit points, gold, inventory, dice rolls, spell effects, "
        "or other state. Those are decided by the rules engine. "
        "Ask what the player does next. The player may attempt any plausible action."
    )
    recent = game["history"][-8:]
    context = f'GAME STATE: { {k:v for k,v in game.items() if k != "history"} }\\nRECENT EVENTS: {recent}\\nPLAYER ACTION OR EVENT: {action}'
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL, "stream": False, "think": False,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": context}],
            "options": {"temperature": 0.8, "num_predict": 250}
        }, timeout=120)
        response.raise_for_status()
        payload = response.json()
        return payload.get("message", {}).get("content", "").strip() or "(No narration returned.)"
    except requests.RequestException as exc:
        return f"Ollama unavailable: {exc}. Make sure Ollama is running."

def record(action, result):
    game["turn"] += 1
    game["history"].append({"action": action, "result": result})
    save(game)

with st.sidebar:
    st.subheader("Character")
    st.write(f'**{game["name"]}** · {game["location"]}')
    st.metric("HP", f'{game["hp"]}/{game["max_hp"]}')
    st.metric("Mana", f'{game["mana"]}/{game["max_mana"]}')
    st.metric("Gold", game["gold"])
    st.write("**Inventory:**", ", ".join(game["inventory"]) or "Empty")
    st.write("**Spells:**", ", ".join(s["name"] for s in game["spells"]) or "None")
    st.divider()
    if st.button("New game", type="secondary"):
        st.session_state.game = new_game()
        save(st.session_state.game)
        st.rerun()

left, right = st.columns([2, 1])
with right:
    st.subheader("Rules engine")
    if game["enemy"]:
        st.error(f'{game["enemy"]["name"]}: {game["enemy"]["hp"]} HP')
    if st.button("Find enemy"):
        msg = start_encounter(game)
        record("Find enemy", msg)
        st.session_state.last_result = msg
        st.rerun()
    if st.button("Attack"):
        msg = attack(game)
        record("Attack", msg)
        st.session_state.last_result = msg
        st.rerun()
    if st.button("Discover spell"):
        spell = generate_spell()
        game["spells"].append(spell)
        msg = f'Discovered {spell["name"]} ({spell["power"]} damage, {spell["mana_cost"]} mana).'
        record("Discover spell", msg)
        st.session_state.last_result = msg
        st.rerun()
    for i, spell in enumerate(game["spells"]):
        if st.button(f'Cast {spell["name"]}', key=f"spell_{i}"):
            msg = cast(game, i)
            record(f'Cast {spell["name"]}', msg)
            st.session_state.last_result = msg
            st.rerun()
    with st.expander("Village shop"):
        for item in SHOP_ITEMS:
            if st.button(f'{item["name"]} — {item["price"]}g', key=item["name"]):
                from game import buy
                msg = buy(game, item)
                record("Buy item", msg)
                st.session_state.last_result = msg
                st.rerun()

with left:
    st.subheader("Adventure")
    if "last_result" in st.session_state:
        st.info(st.session_state.last_result)
    for entry in game["history"][-8:]:
        st.markdown(f'**You:** {entry["action"]}')
        st.write(entry["result"])
    with st.form("turn_form", clear_on_submit=True):
        action = st.text_area("What do you do?", placeholder="I examine the glowing stones beneath the arch...")
        submitted = st.form_submit_button("Take action")
    if submitted and action.strip():
        with st.spinner("The Dungeon Master is thinking..."):
            story = narrate(action.strip())
        record(action.strip(), story)
        st.rerun()
    if st.button("Begin / Describe the scene"):
        with st.spinner("Generating opening scene..."):
            story = narrate("Introduce the Ironwood Forest and a mysterious plot hook.")
        record("Begin adventure", story)
        st.rerun()
