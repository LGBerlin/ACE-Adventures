# ACE Adventures — first local launch

Requirements: macOS, Python 3.10+, Ollama installed, model qwen3.5:4b already downloaded.

1. Clone the repository: `git clone https://github.com/LGBerlin/ACE-Adventures.git`
2. Enter it: `cd ACE-Adventures`
3. Create a virtual environment: `python3 -m venv .venv`
4. Activate it: `source .venv/bin/activate`
5. Install Python packages: `pip install -r requirements.txt`
6. Make sure Ollama is running: `ollama list`
7. Start: `streamlit run app.py`

This is an early prototype, not a complete game. The current buttons implement deterministic combat, weighted elemental spells, and a basic shop. The free-text story channel narrates actions but does not yet convert them into authoritative changes in the rules engine. Character sprites, map generation, image generation, richer mechanics, and story planning are future stages.

All save data is written locally to `saves/game.json`; the folder is excluded from Git.
