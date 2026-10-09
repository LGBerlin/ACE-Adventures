"""Validate the staged playable-campaign payload without opening Tkinter."""
from pathlib import Path
import ast
import importlib.util
import unittest
class ReleaseTests(unittest.TestCase):
    def test_release_compiles(self):
        root=Path(__file__).parent/"updates"/"1.3.0"
        for name in ("app.py","game.py","pixel_art.py"):
            ast.parse((root/name).read_text(encoding="utf-8"),filename=str(root/name))
    def test_required_screens_and_background_ai(self):
        source=(Path(__file__).parent/"updates"/"1.3.0"/"app.py").read_text()
        for marker in ("def character_creation", "def character_sheet", "def start_campaign",
                       'tab("Inventory")', 'tab("Moves")', 'def _poll_ai', 'self.ai_queue.put(("story"',
                       'def _check_ollama_async', 'attempt_action(self.data,text)'):
            self.assertIn(marker,source)
    def test_party_and_campaign_state(self):
        root=Path(__file__).parent/"updates"/"1.3.0"
        spec=importlib.util.spec_from_file_location("ace_release_130_game",root/"game.py")
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        new_campaign=module.new_campaign
        add_party_character=module.add_party_character
        party=module.party
        begin_story=module.begin_story
            d=new_campaign("Test",2)
            add_party_character(d,"Alpha",22,"Rogue")
            self.assertEqual(len(party(d)),1)
            with self.assertRaises(ValueError):begin_story(d)
            add_party_character(d,"Beta",25,"Vessel")
            self.assertTrue(begin_story(d))
            self.assertFalse(begin_story(d))
            self.assertEqual(len(party(d)),2)
if __name__=="__main__":unittest.main()
