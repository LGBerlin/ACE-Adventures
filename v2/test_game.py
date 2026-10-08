import unittest
from game import create_character, new_campaign, roll_d20, PATHS, SPELLS, MOVES
from pixel_art import COLORS

class GameTests(unittest.TestCase):
    def test_all_classes_create_valid_character(self):
        for cls in PATHS:
            for _ in range(25):
                c=create_character("Tester",20,cls)
                self.assertEqual(c["class"],cls)
                self.assertIn(c["path"],[name for name,_ in PATHS[cls]])
                self.assertEqual(c["level"],1)
                self.assertTrue(c["moves"])
                self.assertGreater(c["hp"],0)
                self.assertIn("sprite_seed",c)
    def test_character_name_age_chosen(self):
        c=create_character("Liam",22,"Mage")
        self.assertEqual((c["name"],c["age"]),("Liam",22))
    def test_character_rejects_bad_class(self):
        with self.assertRaises(ValueError):create_character("Test",20,"Wizard")
    def test_campaign_party_validation(self):
        self.assertEqual(new_campaign("Quest",1)["players"],1)
        with self.assertRaises(ValueError):new_campaign("Quest",9)
    def test_d20_bounds(self):
        for _ in range(200):
            x=roll_d20(2,13)
            self.assertTrue(1<=x["roll"]<=20)
            self.assertEqual(x["total"],x["roll"]+2)
    def test_sprite_palette_for_each_class(self):
        for cls in PATHS:
            self.assertIn(cls,COLORS)

if __name__=="__main__":unittest.main()
