import os, subprocess, sys, json, shutil, textwrap
from pathlib import Path

PINOKIO_HOME = Path(os.getenv("PINOKIO_HOME", Path.cwd() / "pinokio_home")).expanduser()
CONDA_DIR    = PINOKIO_HOME / "conda"
BIN_DIR      = PINOKIO_HOME / "bin"

def ensure_dirs():
    for p in (PINOKIO_HOME, CONDA_DIR, BIN_DIR):
        p.mkdir(parents=True, exist_ok=True)

def shell(cmd, cwd=None, stream=None):
    "Run shell command and optionally yield stdout lines."
    proc = subprocess.Popen(
        cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, bufsize=1
    )
    for line in proc.stdout:
        if stream: stream(line.rstrip())
    proc.wait()
    return proc.returncode
