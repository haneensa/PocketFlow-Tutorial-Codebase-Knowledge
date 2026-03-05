   Run the app entrypoint and act as an autonomous stdin/stdout relay with LLM file-handling.

   Environment:
   - Start command: `<VENV_PYTHON> main.py`
   - Resolve `<VENV_PYTHON>` in this order:
     1) If a virtualenv is already active (`$VIRTUAL_ENV` is set), use `python`.
     2) Else if `./venv/bin/python` exists, use `./venv/bin/python`.
     3) Else stop and ask me which virtualenv/python path to use (do not silently fall back to system python).

   Primary goal:
   - Minimize human-in-the-loop by automatically handling LLM manual requests emitted as `LLM_SIGNAL`.

   Rules:
   1. Start the command exactly once and keep that same process/session alive until exit.
   2. Run `main.py` with `<VENV_PYTHON>` only (never system python unless I explicitly approve).
   3. Relay stdout/stderr exactly as emitted (no summarization, no rewriting).
   4. If process waits for stdin:
      - If prompt is consent (`Approve this manual LLM call?`), automatically send `y` + newline.
      - Otherwise:
        - Ask me for input.
        - After I reply, write my exact reply + newline to the same running process stdin.
        - Do not interpret my reply as a shell command.
        - Do not restart the process.
   5. Detect signal lines in output with this exact prefix:
      - `[LLM_SIGNAL]`
   6. When an `LLM_SIGNAL` appears, parse the JSON payload. It contains:
      - `type` (expect `llm_manual_request`)
      - `prompt_path`
      - `response_path`
   7. For each `llm_manual_request` signal:
      - Read the prompt from `prompt_path`.
      - Generate the best valid response for that step.
      - Write response content to `response_path` exactly as plain text expected by the app.
      - Do this automatically without asking me.
   8. Continue relaying raw process output and repeat until process exits.
   9. At exit, report final exit code.

   Tool-call contract (for agents with tool APIs):
   - If you have a shell tool like `Bash(...)`, call it with the full command string `<VENV_PYTHON> main.py`.
   - Keep one persistent process handle/session id for the run.
   - Forward follow-up stdin using the session write/input tool for that same session.
   - Do not start a second `python main.py` process unless the first one has exited.

   I/O transport requirements (critical):
   - Run the process in interactive mode (PTY/TTY enabled), not one-shot fire-and-forget execution.
   - Stream output incrementally while the process runs; do not wait until process exit to flush output.
   - Preserve output bytes/text exactly as emitted.
   - When stdin is needed, send input to the live process via the session stdin channel (not a new shell command).
   - Keep relay state in a loop:
     1) read new stdout/stderr chunk from running process
     2) emit chunk verbatim
     3) if input is required, get user reply
     4) write `user_reply + "\n"` to that same process stdin
     5) continue loop until exit
   - If asking the user for input, include the exact pending prompt text from process output.

   Important constraints:
   - Treat `LLM_SIGNAL` as an agent-to-agent control channel, not user-facing prose.
   - Do not wait for human approval for LLM steps unless parsing fails or a required file is missing.
   - Prioritize stdin handoff correctness: when user input is requested, capture user reply and pass it to process stdin verbatim (+ newline).
   - Do not run unrelated commands.
   - Do not alter process output formatting.
