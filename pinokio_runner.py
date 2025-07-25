import json, subprocess, os, re
from pathlib import Path
from env_helpers import PINOKIO_HOME, shell, ensure_dirs

ensure_dirs()

def parse_script(script_path):
    with open(script_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_pinokio_actions(actions, app_path, log):
    for step in actions:
        method = step["method"]
        params = step.get("params", {})
        if method == "shell.run":
            msg   = params["message"]
            path  = params.get("path", ".")
            code  = shell(msg, cwd=app_path / path, stream=log)
            if code != 0:
                raise RuntimeError(f"Command failed: {msg}")
        elif method == "fs.download":
            url   = params["url"]
            dest  = app_path / params["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shell(f"curl -L {url} -o {dest}", stream=log)
        elif method == "notify":
            log(f"[notify] {params.get('html','')}")
        elif method == "process.wait":
            log("[wait] ✨ Done")
        # Extend with other Pinokio RPCs as needed [42][50]
    log("✅ All steps finished.")

def install_app(app_root, log):
    script = parse_script(app_root / "install.json")
    run_pinokio_actions(script["run"], app_root, log)

def start_app(app_root, log):
    script = parse_script(app_root / "start.json")
    run_pinokio_actions(script["run"], app_root, log)

def list_apps(base="pinokio_apps"):
    return {
        p.name: p
        for p in Path(base).iterdir()
        if p.is_dir() and (p / "install.json").exists()
    }
