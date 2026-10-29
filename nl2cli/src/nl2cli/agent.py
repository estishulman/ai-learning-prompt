import anthropic
from . import config
from .safety import classify


def load_prompt(version: str, os_key: str | None = None) -> str:
    os_key = os_key or config.TARGET_OS
    raw = (config.PROMPTS_DIR / f"{version}.txt").read_text(encoding="utf-8")
    return raw.format(**config.OS_INFO[os_key]).strip()


_client = None


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    return _client


def to_command(instruction: str, version: str | None = None, os_key: str | None = None) -> dict:
    """Returns {'raw': model text, 'status': SAFE|RISKY|BLOCKED|UNSUPPORTED, 'command': str|None}"""
    version = version or config.DEFAULT_PROMPT_VERSION
    resp = _get_client().messages.create(
        model=config.MODEL,
        max_tokens=300,
        temperature=0,
        system=load_prompt(version, os_key),
        messages=[{"role": "user", "content": instruction}],
    )
    raw = "".join(b.text for b in resp.content if b.type == "text").strip()
    status = classify(raw)
    command = None
    if status in ("SAFE", "RISKY"):
        command = raw.removeprefix("RISKY:").strip()
    return {"raw": raw, "status": status, "command": command}
