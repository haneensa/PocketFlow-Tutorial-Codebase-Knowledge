from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict

# =========================
# Logging
# =========================

logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False
LOG_DIR = "workspace/logs"


def _ensure_logger_handler(log_directory: str):
    os.makedirs(log_directory, exist_ok=True)
    log_file = os.path.join(log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log")
    log_file_abs = os.path.abspath(log_file)
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == log_file_abs:
            return

    for h in list(logger.handlers):
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
            h.close()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)


_ensure_logger_handler(LOG_DIR)

# =========================
# Config / constants
# =========================

cache_file = "workspace/cache/llm_cache.json"
MANUAL_DIR = "workspace/llm"
MANUAL_POLL_INTERVAL_S = 2.0
MANUAL_TIMEOUT_S = 0  # 0 means no timeout
REDACT_LOGS = True
_CONSENT_APPROVED_FOR_RUN = False


def _status(message: str):
    print(f"[LLM] {message}")
    logger.info(message)


def _error(message: str):
    print(f"[LLM][ERROR] {message}")
    logger.error(message)


def _estimate_tokens(text: str) -> int:
    # Lightweight approximation: ~4 chars/token for English-heavy prompts.
    return max(1, (len(text) + 3) // 4)


def _request_llm_consent_with_flags(
    prompt: str,
    require_consent: bool,
    show_prompt_by_default: bool,
    prompt_file_path: str | None = None,
):
    global _CONSENT_APPROVED_FOR_RUN

    if not require_consent:
        return
    if _CONSENT_APPROVED_FOR_RUN:
        return

    estimated_prompt_tokens = _estimate_tokens(prompt)

    print(f"\nLLM consent required. Estimated prompt tokens: ~{estimated_prompt_tokens}.")
    if prompt_file_path:
        print(f"Prompt file for review: {prompt_file_path}")

    if show_prompt_by_default:
        print("\n--- Prompt Start ---")
        print(prompt)
        print("--- Prompt End ---\n")

    while True:
        try:
            reply = input("Approve this manual LLM call? [y]es/[n]o/[p]rompt: ").strip().lower()
        except EOFError as exc:
            raise RuntimeError("LLM consent is enabled but no interactive stdin is available.") from exc

        if reply in {"y", "yes"}:
            _CONSENT_APPROVED_FOR_RUN = True
            _status("Consent approved for manual LLM call.")
            return
        if reply in {"n", "no", ""}:
            _error("LLM call cancelled by user.")
            raise RuntimeError("LLM call cancelled by user.")
        if reply in {"p", "prompt"}:
            print("\n--- Prompt Start ---")
            print(prompt)
            print("--- Prompt End ---\n")
            continue
        print("Please answer with 'y', 'n', or 'p'.")


def _get_project_cache_file(project_name: str | None) -> str:
    base_dir = os.path.dirname(cache_file) or "."
    base_name = os.path.basename(cache_file)
    stem, ext = os.path.splitext(base_name)
    ext = ext or ".json"
    project_dir = os.path.join(base_dir, _sanitize_project_name(project_name))
    return os.path.join(project_dir, f"{stem}{ext}")


def load_cache(cache_path: str) -> Dict[str, str]:
    cache_parent = os.path.dirname(cache_path)
    if cache_parent:
        os.makedirs(cache_parent, exist_ok=True)
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.warning("Failed to load cache.")
    return {}


def save_cache(cache: Dict[str, str], cache_path: str) -> None:
    cache_parent = os.path.dirname(cache_path)
    if cache_parent:
        os.makedirs(cache_parent, exist_ok=True)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
    except Exception:
        logger.warning("Failed to save cache")


def _cache_key(prompt: str) -> str:
    h = hashlib.sha256()
    h.update(prompt.encode("utf-8"))
    return f"MANUAL|prompt_sha256={h.hexdigest()}"


def _sanitize_tag(tag: str) -> str:
    sanitized = "".join(c if c.isalnum() or c in {"-", "_"} else "_" for c in tag.strip().lower())
    return sanitized or "manual_request"


def _sanitize_project_name(project_name: str | None) -> str:
    if not project_name:
        return "default_project"
    return _sanitize_tag(project_name)


def _write_consent_prompt_file(prompt: str, project_name: str | None) -> str:
    project_dir = os.path.join("workspace", _sanitize_project_name(project_name), "llm")
    os.makedirs(project_dir, exist_ok=True)
    prompt_path = os.path.join(project_dir, "prompt")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    return prompt_path


def _call_manual(
    prompt: str,
    request_tag: str | None = None,
    project_name: str | None = None,
) -> str:
    project_dir = os.path.join(MANUAL_DIR, _sanitize_project_name(project_name))
    os.makedirs(project_dir, exist_ok=True)
    prompts_dir = os.path.join(project_dir, "prompts")
    responses_dir = os.path.join(project_dir, "responses")
    os.makedirs(prompts_dir, exist_ok=True)
    os.makedirs(responses_dir, exist_ok=True)

    if request_tag:
        prompt_id = _sanitize_tag(request_tag)
    else:
        prompt_id = f"{int(time.time())}_{hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:10]}"
    prompt_path = os.path.join(prompts_dir, f"{prompt_id}.txt")
    response_path = os.path.join(responses_dir, f"{prompt_id}.txt")

    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    _status(f"Manual prompt saved: {prompt_path}")
    signal = {
        "type": "llm_manual_request",
        "prompt_path": prompt_path,
        "response_path": response_path,
    }
    print(f"[LLM_SIGNAL]{json.dumps(signal, ensure_ascii=False)}")

    # Auto-skip if the response file already exists and is non-empty.
    if os.path.exists(response_path):
        with open(response_path, "r", encoding="utf-8") as f:
            existing_response = f.read().strip()
        if existing_response:
            _status(f"Found existing response file, skipping prompt wait: {response_path}")
            return existing_response

    # File-only workflow: poll until the response file exists and is non-empty.
    start_ts = time.time()
    while True:
        if not os.path.exists(response_path):
            if MANUAL_TIMEOUT_S > 0 and (time.time() - start_ts) > MANUAL_TIMEOUT_S:
                raise RuntimeError(f"Timed out waiting for response file: {response_path}")
            time.sleep(MANUAL_POLL_INTERVAL_S)
            continue

        with open(response_path, "r", encoding="utf-8") as f:
            response_text = f.read().strip()
        if not response_text:
            if MANUAL_TIMEOUT_S > 0 and (time.time() - start_ts) > MANUAL_TIMEOUT_S:
                raise RuntimeError(f"Timed out waiting for non-empty response file: {response_path}")
            time.sleep(MANUAL_POLL_INTERVAL_S)
            continue

        _status(f"Loaded manual response from file: {response_path}")
        return response_text


def call_llm(
    prompt: str,
    use_cache: bool = True,
    request_tag: str | None = None,
    project_name: str | None = None,
    llm_require_consent: bool = False,
    llm_show_prompt: bool = False,
) -> str:
    ck = _cache_key(prompt)
    project_cache_file = _get_project_cache_file(project_name)

    if use_cache:
        cache = load_cache(project_cache_file)
        if ck in cache:
            _status("Cache hit. Reusing previous manual LLM response.")
            return cache[ck]

    consent_prompt_path = None
    if llm_require_consent:
        consent_prompt_path = _write_consent_prompt_file(prompt, project_name)
        _status(f"Wrote prompt for consent review: {consent_prompt_path}")

    _request_llm_consent_with_flags(
        prompt,
        require_consent=llm_require_consent,
        show_prompt_by_default=llm_show_prompt,
        prompt_file_path=consent_prompt_path,
    )
    _status("Preparing manual LLM call.")

    if not REDACT_LOGS:
        logger.info("PROMPT:\n%s", prompt)
    else:
        logger.info("PROMPT: [redacted] (len=%d chars)", len(prompt))

    response_text = _call_manual(
        prompt,
        request_tag=request_tag,
        project_name=project_name,
    )

    if not REDACT_LOGS:
        logger.info("RESPONSE:\n%s", response_text)
    else:
        logger.info("RESPONSE: [redacted] (len=%d chars)", len(response_text))

    if use_cache:
        cache = load_cache(project_cache_file)
        cache[ck] = response_text
        save_cache(cache, project_cache_file)

    return response_text


if __name__ == "__main__":
    test_prompt = "Hello, how are you?"
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")
