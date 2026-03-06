# Project-Scoped File References Design

## Objective

Add reliable "look at this file" references to generated tutorials while guaranteeing that displayed paths never include absolute local directories (for example, `/home/user/...` or `/Users/...`).

All displayed references must start from project name, for example:

- `my-project/src/main.py`

## Requirements

1. References must be grounded in validated file indices already produced by the pipeline (`abstractions[].files`).
2. No absolute local path may appear in any generated markdown.
3. Every displayed path must be project-scoped: `<project_name>/<relative_path_inside_project>`.
4. References that resolve outside the project root must be rejected.
5. Each chapter must include a deterministic reference section.

## Design Overview

Use a structured citation flow instead of trusting free-form file mentions from the LLM:

1. Build an allowlist of valid file references per chapter from `abstractions[].files`.
2. Ask the LLM to cite by index token only (for example, `[ref:12]`).
3. Parse and validate citation tokens after generation.
4. Render final file references deterministically from validated indices and normalized paths.

## Path Normalization Policy

Given `project_name`, `local_dir`, and a file path from crawl data:

1. Normalize separators to `/`.
2. Remove leading `./`.
3. Compute project-relative path.
4. Reject if path escapes root (`..` or `../` prefix after normalization).
5. Build display path:
   - `display_path = f"{project_name}/{project_rel_path}"`

Examples:

- Input: `/home/user/myproj/src/app.py` -> `myproj/src/app.py`
- Input: `src/app.py` -> `myproj/src/app.py`
- Input: `../secret.txt` -> rejected

## Chapter Generation Contract

In `WriteChapters.exec`, provide:

1. Allowed references list:
   - `12 # myproj/src/app.py`
   - `21 # myproj/core/flow.py`
2. Citation format rule:
   - Use `[ref:<index>]` for each code claim.
3. Minimum citation rule:
   - If code context exists, require at least 2 citations.
4. Prohibited output rule:
   - Do not print absolute filesystem paths.

## Validation and Retry

After LLM chapter generation:

1. Parse all tokens matching `\[ref:(\d+)\]`.
2. Validate each cited index is in this chapter's allowlist.
3. If any invalid index appears, fail chapter attempt and retry.
4. If minimum citation count is not met when code exists, retry.
5. Deduplicate valid citations preserving first-seen order.

## Deterministic Rendering

Append a generated section to each chapter:

`## Where To Look In Code`

Render from validated citations only:

- `- myproj/src/app.py (ref:12)`
- `- myproj/core/flow.py (ref:21)`

No LLM-provided path strings are trusted for final rendering.

## Index-Level Code Map

In `index.md`, add a compact map:

- Chapter 1 -> primary referenced files
- Chapter 2 -> primary referenced files

All entries use project-scoped display paths only.

## Optional GitHub Linking

Optional config:

- `repo_url`
- `repo_ref` (default `main`)

If configured:

1. Link target uses repo-relative path.
2. Link label remains project-scoped path (`myproj/src/app.py`).
3. Absolute local path is never shown.

## Implementation Plan

1. `WriteChapters.prep`:
   - Build per-chapter allowlist with `{index, rel_path, display_path}`.
2. `WriteChapters.exec`:
   - Enforce citation token prompt contract.
   - Parse and validate citations.
   - Store normalized used references for each chapter.
3. `CombineTutorial.prep`:
   - Append deterministic `Where To Look In Code` section.
   - Add index-level Code Map.
4. Config updates:
   - Add optional `repo_url` and `repo_ref`.
5. Docs updates:
   - Document citation behavior and path policy in README.

## Acceptance Criteria

1. Generated chapters contain `## Where To Look In Code`.
2. Every listed reference maps to an actual crawled file index.
3. No generated markdown contains `/home/...` or `/Users/...` style absolute paths.
4. All displayed paths begin with `<project_name>/`.
5. Invalid citations trigger retry and are not present in final output.
