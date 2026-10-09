"""ACE Adventures 2 stable launch entrypoint.

Normal updates live in ~/Library/Application Support/ACE Adventures 2/updates.
This loader stays bundled with the Mac app. It loads the verified active
payload, or rolls back to the previous payload if imports fail.
"""
import importlib.util
import json
import sys
import traceback
import datetime
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

def _log_failure(stage):
    APP_DATA.mkdir(parents=True,exist_ok=True)
    with (APP_DATA/"startup-errors.log").open("a",encoding="utf-8") as log:
        log.write("\n"+datetime.datetime.now().isoformat()+" "+stage+"\n")
        traceback.print_exc(file=log)

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
                    app_class=_load_path(active)
                    return app_class().mainloop()
                except Exception:
                    _log_failure("Active update failed: "+str(state.get("version")))
                    previous=_verified_dir(state.get("previous"))
                    if previous:
                        try:
                            app=_load_path(previous)
                            marker.write_text(json.dumps({"version":state["previous"],"directory":state["previous"],"previous":None}))
                            return app().mainloop()
                        except Exception:_log_failure("Previous update also failed")
        except Exception:_log_failure("Launcher state failed")
    return bundled_app().mainloop()

if __name__=="__main__":
    launch()
