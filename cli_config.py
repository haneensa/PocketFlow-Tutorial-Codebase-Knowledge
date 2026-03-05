from typing import Any, Dict


DEFAULT_INCLUDE_PATTERNS = {
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "*Dockerfile",
    "*Makefile", "*.yaml", "*.yml",
}

DEFAULT_EXCLUDE_PATTERNS = {
    "assets/*", "data/*", "images/*", "public/*", "static/*", "temp/*",
    "*docs/*",
    "*venv/*",
    "*.venv/*",
    "*test*",
    "*tests/*",
    "*examples/*",
    "v1/*",
    "*dist/*",
    "*build/*",
    "*experimental/*",
    "*deprecated/*",
    "*misc/*",
    "*legacy/*",
    ".git/*", ".github/*", ".next/*", ".vscode/*",
    "*obj/*",
    "*bin/*",
    "*node_modules/*",
    "*.log",
}


def build_shared() -> Dict[str, Any]:
    include_patterns = set(DEFAULT_INCLUDE_PATTERNS)
    exclude_patterns = set(DEFAULT_EXCLUDE_PATTERNS)
    return {
        "config_path": "configure_args.yaml",
        "local_dir": None,
        "project_name": None,
        "output_dir": "output",
        "include_patterns": include_patterns,
        "exclude_patterns": exclude_patterns,
        "max_file_size": 100000,
        "language": "english",
        "use_cache": True,
        "max_abstraction_num": 10,
        "llm_require_consent": False,
        "llm_show_prompt": False,
        "log_dir": "workspace/logs",
        "llm_cache_file": "workspace/cache/llm_cache.json",
        "llm_manual_dir": "workspace/llm",
        "llm_manual_poll_interval_s": 2.0,
        "llm_manual_timeout_s": 0,
        "llm_redact_logs": True,
        "files": [],
        "abstractions": [],
        "relationships": {},
        "chapter_order": [],
        "chapters": [],
        "final_output_dir": None,
    }


def set_llm_runtime_config(config: Dict[str, Any]) -> None:
    if not isinstance(config, dict):
        return

    # Import lazily to avoid circular imports at module import time.
    from utils import call_llm as llm_runtime

    llm_runtime.cache_file = str(config.get("llm_cache_file", llm_runtime.cache_file))
    llm_runtime.MANUAL_DIR = str(config.get("llm_manual_dir", llm_runtime.MANUAL_DIR))
    llm_runtime.MANUAL_POLL_INTERVAL_S = float(
        config.get("llm_manual_poll_interval_s", llm_runtime.MANUAL_POLL_INTERVAL_S)
    )
    llm_runtime.MANUAL_TIMEOUT_S = int(
        config.get("llm_manual_timeout_s", llm_runtime.MANUAL_TIMEOUT_S)
    )
    llm_runtime.REDACT_LOGS = bool(config.get("llm_redact_logs", llm_runtime.REDACT_LOGS))
    llm_runtime.LOG_DIR = str(config.get("log_dir", llm_runtime.LOG_DIR))
    llm_runtime._ensure_logger_handler(llm_runtime.LOG_DIR)
