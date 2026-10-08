import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from updater import activate, load_active, rollback

URL="https://raw.githubusercontent.com/LGBerlin/ACE-Adventures/main/v2/updates/1.0.0/core.py"
def manifest(v,base,content,url=URL):
    return {"version":v,"base":base,"files":[{"path":"core.py","url":url,"sha256":hashlib.sha256(content).hexdigest()}]}

class UpdaterTests(unittest.TestCase):
    def test_new_install_and_patch_and_rollback(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            a=b"VERSION='1.0.0'\n"
            b=b"VERSION='1.0.1'\n"
            activate(root,manifest("1.0.0","0.0.0",a),lambda _:a)
            self.assertEqual(load_active(root)["version"],"1.0.0")
            activate(root,manifest("1.0.1","1.0.0",b),lambda _:b)
            self.assertEqual(load_active(root)["version"],"1.0.1")
            rollback(root)
            self.assertEqual(load_active(root)["version"],"1.0.0")
    def test_bad_hash_does_not_change_active(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            a=b"a"
            activate(root,manifest("1.0.0","0.0.0",a),lambda _:a)
            with self.assertRaises(ValueError):
                activate(root,manifest("1.0.1","1.0.0",b"expected"),lambda _:b"wrong")
            self.assertEqual(load_active(root)["version"],"1.0.0")
    def test_wrong_base_rejected(self):
        with TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                activate(Path(td),manifest("1.0.0","9.9.9",b"x"),lambda _:b"x")
    def test_traversal_rejected(self):
        with TemporaryDirectory() as td:
            m=manifest("1.0.0","0.0.0",b"x")
            m["files"][0]["path"]="../bad.py"
            with self.assertRaises(ValueError):activate(Path(td),m,lambda _:b"x")
    def test_wrong_host_rejected(self):
        with TemporaryDirectory() as td:
            m=manifest("1.0.0","0.0.0",b"x","https://example.com/evil.py")
            with self.assertRaises(ValueError):activate(Path(td),m,lambda _:b"x")
    def test_campaign_save_is_untouched(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            saves=root/"campaigns"
            saves.mkdir()
            (saves/"character.json").write_text('{"name":"Ranger"}')
            activate(root,manifest("1.0.0","0.0.0",b"x"),lambda _:b"x")
            self.assertEqual((saves/"character.json").read_text(),'{"name":"Ranger"}')

if __name__=="__main__": unittest.main()
