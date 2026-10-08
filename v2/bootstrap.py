"""ACE Adventures 2 stable launch entrypoint.

Normal updates live in ~/Library/Application Support/ACE Adventures 2/updates.
This loader stays bundled with the Mac app. It loads the verified active
payload, or rolls back to the previous payload if imports fail.
"""
import importlib.util
import json
import sys
import traceback
from pathlib import Path

APP_DATA=Path.home()/"Library"/"Application Support"/"ACE Adventures 2"
UPDATES=APP_DATA/"updates"
MODULES=("game","pixel_art","app")

def _verified_dir(name):
    if not isinstance(name,str) or not name.replace(".","").isdigit():
        return None
    candidate=UPDATES/"versions"/name
    if not candidate.is_dir():
        return None
    if not all((candidate/(module+".py")).is_file() for module in MODULES):
        return None
    return candidate

def _load_path(path):
    # Explicit names ensure PyInstaller's bundled import hooks cannot silently
    # select the stale app instead of the updated payload.
    for module in MODULES:
        sys.modules.pop(module,None)
    try:
        for name in MODULES:
            source=path/(name+".py")
            spec=importlib.util.spec_from_file_location(name,source)
            if spec is None or spec.loader is None:raise ImportError(str(source))
            loaded=importlib.util.module_from_spec(spec)
            sys.modules[name]=loaded
            spec.loader.exec_module(loaded)
        return sys.modules["app"].App
    except BaseException:
        for name in MODULES:sys.modules.pop(name,None)
        raise

def launch():
    # The imported copy is the bootstrap's fallback; the normal app stays
    # operational even if the new update cannot be imported.
    from app import App as bundled_app
    marker=UPDATES/"active.json"
    if marker.is_file():
        try:
            state=json.loads(marker.read_text())
            active=_verified_dir(state.get("directory"))
            if active:
                try:
                    return _load_path(active)().mainloop()
                except Exception:
                    traceback.print_exc()
                    previous=_verified_dir(state.get("previous"))
                    if previous:
                        try:
                            app=_load_path(previous)
                            marker.write_text(json.dumps({"version":state["previous"],"directory":state["previous"],"previous":None}))
                            return app().mainloop()
                        except Exception:traceback.print_exc()
        except Exception:traceback.print_exc()
    return bundled_app().mainloop()

if __name__=="__main__":
    launch()
