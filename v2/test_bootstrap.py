import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
import bootstrap

class BootstrapTests(unittest.TestCase):
    def test_versioned_directory_validation(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            with patch.object(bootstrap,"UPDATES",root):
                self.assertIsNone(bootstrap._verified_dir("../malicious"))
                folder=root/"versions"/"1.0.0"
                folder.mkdir(parents=True)
                self.assertIsNone(bootstrap._verified_dir("1.0.0"))
                for name in bootstrap.MODULES:(folder/(name+".py")).write_text("x=1\n")
                self.assertEqual(bootstrap._verified_dir("1.0.0"),folder)
    def test_dynamic_loader_uses_updated_app(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            (root/"game.py").write_text("VALUE=17\n")
            (root/"pixel_art.py").write_text("COLOR='gold'\n")
            (root/"app.py").write_text("from game import VALUE\nfrom pixel_art import COLOR\nclass App:\n  def identity(self): return (VALUE,COLOR)\n")
            with patch.dict("sys.modules",{},clear=False):
                cls=bootstrap._load_path(root)
                self.assertEqual(cls().identity(),(17,"gold"))
    def test_missing_module_does_not_load(self):
        with TemporaryDirectory() as td:
            with self.assertRaises(Exception):bootstrap._load_path(Path(td))

if __name__=="__main__":unittest.main()
