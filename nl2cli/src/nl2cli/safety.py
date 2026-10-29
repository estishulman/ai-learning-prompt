"""Second line of defence: classify the model output independently of the prompt."""
import re

FORBIDDEN_PATTERNS = [
    r"\bdel\b", r"\berase\b", r"\brd\s+/s\b", r"\brmdir\s+/s\b",
    r"\brm\s+(-\w*r\w*f|-\w*f\w*r|-r)\b", r"\bremove-item\b.*-recurse",
    r"\bformat\b", r"\bdiskpart\b", r"\bmkfs\b", r"\bdd\s+if=", r"\bcipher\s+/w\b",
    r"\bshutdown\b", r"\brestart-computer\b", r"\blogoff\b",
    r"\breg\s+delete\b", r"\bbcdedit\b",
    r"\|\s*(sh|bash|iex|powershell)\b", r"\biex\s*\(",
    r">\s*/dev/sd", r"\bsudo\s+rm\b",
]
RISKY_PATTERNS = [
    r"\btaskkill\b", r"\bkill\b", r"\bpkill\b", r"\bmove\b", r"\bmv\b", r"\bren\b",
    r"\brename\b", r"\bcopy\b.*\s/y\b", r"\bcp\b", r"\bchmod\b", r"\bchown\b", r"\battrib\b",
    r"\bicacls\b", r"\bnetsh\b", r"\bsetx\b", r"\bpip\s+install\b", r"\bnpm\s+install\b",
    r"\bwinget\s+install\b", r"\bapt(-get)?\s+install\b", r"\bbrew\s+install\b", r"\bhosts\b",
]

KNOWN_COMMANDS = {
    "windows": {
        "ipconfig", "dir", "tasklist", "systeminfo", "hostname", "whoami", "ping", "tracert",
        "netstat", "cd", "type", "echo", "find", "findstr", "mkdir", "md", "copy", "xcopy",
        "robocopy", "move", "ren", "cls", "date", "time", "ver", "tree", "where", "sort",
        "more", "attrib", "taskkill", "wmic", "nslookup", "set", "setx", "path", "chkdsk",
        "sfc", "powershell", "curl", "python", "pip", "git", "winget", "net", "netsh",
        "driverquery", "getmac", "vol", "label", "fc", "comp", "schtasks", "certutil",
    },
    "linux": {
        "ls", "pwd", "cd", "cat", "grep", "find", "ps", "top", "df", "du", "free", "uname",
        "whoami", "hostname", "ip", "ifconfig", "ping", "mkdir", "touch", "cp", "mv", "head",
        "tail", "wc", "sort", "uniq", "date", "echo", "chmod", "chown", "curl", "wget", "git",
        "python", "python3", "pip", "tar", "zip", "unzip", "ss", "netstat", "lsblk", "uptime",
        "which", "tree", "kill", "pkill", "sudo", "apt", "ln", "stat", "file", "env", "history",
    },
}
KNOWN_COMMANDS["macos"] = KNOWN_COMMANDS["linux"] | {"open", "pbcopy", "pbpaste", "brew", "sw_vers", "networksetup", "diskutil"}


def classify(output: str) -> str:
    """Returns: SAFE | RISKY | BLOCKED | UNSUPPORTED"""
    text = output.strip()
    if text == "BLOCKED":
        return "BLOCKED"
    if text == "UNSUPPORTED":
        return "UNSUPPORTED"
    cmd = text[len("RISKY:"):].strip() if text.startswith("RISKY:") else text
    low = cmd.lower()
    if any(re.search(p, low) for p in FORBIDDEN_PATTERNS):
        return "BLOCKED"
    if text.startswith("RISKY:") or any(re.search(p, low) for p in RISKY_PATTERNS):
        return "RISKY"
    return "SAFE"


def format_ok(output: str) -> bool:
    """One line, no markdown/backticks, no obvious prose."""
    t = output.strip()
    if not t or "\n" in t or "`" in t:
        return False
    if re.match(r"^(here|sure|the command|this command|you can|to )", t, re.I):
        return False
    return True


def syntax_plausible(output: str, os_key: str) -> bool:
    """Heuristic: balanced quotes and first token is a known command. Not a real parser."""
    t = output.strip()
    if t in ("BLOCKED", "UNSUPPORTED"):
        return True
    if t.startswith("RISKY:"):
        t = t[len("RISKY:"):].strip()
    if not t or t.count('"') % 2 or t.count("'") % 2:
        return False
    first = re.split(r"\s+|&&|\|", t, maxsplit=1)[0].lower().removesuffix(".exe")
    return first in KNOWN_COMMANDS.get(os_key, set())
