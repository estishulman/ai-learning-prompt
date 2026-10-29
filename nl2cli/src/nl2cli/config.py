import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = ROOT / "prompts"
SCENARIOS_DIR = ROOT / "scenarios"
RESULTS_DIR = ROOT / "results"

MODEL = os.getenv("MODEL", "claude-sonnet-5-5")
TARGET_OS = os.getenv("TARGET_OS", "windows").lower()
DEFAULT_PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v4")

OS_INFO = {
    "windows": {"os_name": "Windows (cmd.exe)", "chain_op": "&&", "path_sep": "\\"},
    "linux": {"os_name": "Linux (bash)", "chain_op": "&&", "path_sep": "/"},
    "macos": {"os_name": "macOS (zsh)", "chain_op": "&&", "path_sep": "/"},
}
