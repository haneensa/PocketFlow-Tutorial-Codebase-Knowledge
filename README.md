<h1 align="center">Turns Codebase into Easy Tutorial with AI</h1>

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
 <a href="https://discord.gg/hUHHE9Sa6T">
    <img src="https://img.shields.io/discord/1346833819172601907?logo=discord&style=flat">
</a>
> *Ever stared at a new codebase written by others feeling completely lost? This tutorial shows you how to build an AI agent that analyzes local codebases and creates beginner-friendly tutorials explaining exactly how the code works.*

<p align="center">
  <img
    src="./assets/banner.png" width="800"
  />
</p>

This is a tutorial project of [Pocket Flow](https://github.com/The-Pocket/PocketFlow), a 100-line LLM framework. It crawls local directories and builds a knowledge base from the code. It analyzes entire codebases to identify core abstractions and how they interact, and transforms complex code into beginner-friendly tutorials with clear visualizations.

- Check out the [YouTube Development Tutorial](https://youtu.be/AFY67zOpbSo) for more!

- Check out the [Substack Post Tutorial](https://zacharyhuang.substack.com/p/ai-codebase-knowledge-builder-full) for more!

&nbsp;&nbsp;**🔸 🎉 Reached Hacker News Front Page** (April 2025) with >900 up‑votes:  [Discussion »](https://news.ycombinator.com/item?id=43739456)

&nbsp;&nbsp;**🔸 🎊 Online Service Now Live!** (May&nbsp;2025) Try our new online version at [https://code2tutorial.com/](https://code2tutorial.com/) – just paste a GitHub link, no installation needed!

## ⭐ Example Results for Popular GitHub Repositories!

<p align="center">
    <img
      src="./assets/example.png" width="600"
    />
</p>

🤯 All these tutorials are generated **entirely by AI** by crawling the GitHub repo!

- [AutoGen Core](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/AutoGen%20Core) - Build AI teams that talk, think, and solve problems together like coworkers!

- [Browser Use](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/Browser%20Use) - Let AI surf the web for you, clicking buttons and filling forms like a digital assistant!

- [Celery](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/Celery) - Supercharge your app with background tasks that run while you sleep!

- [Click](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/Click) - Turn Python functions into slick command-line tools with just a decorator!

- [Codex](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/Codex) - Turn plain English into working code with this AI terminal wizard!

- [Crawl4AI](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/Crawl4AI) - Train your AI to extract exactly what matters from any website!

- [CrewAI](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/CrewAI) - Assemble a dream team of AI specialists to tackle impossible problems!

- [DSPy](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/DSPy) - Build LLM apps like Lego blocks that optimize themselves!

- [FastAPI](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/FastAPI) - Create APIs at lightning speed with automatic docs that clients will love!

- [Flask](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/Flask) - Craft web apps with minimal code that scales from prototype to production!

- [Google A2A](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/Google%20A2A) - The universal language that lets AI agents collaborate across borders!

- [LangGraph](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/LangGraph) - Design AI agents as flowcharts where each step remembers what happened before!

- [LevelDB](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/LevelDB) - Store data at warp speed with Google's engine that powers blockchains!

- [MCP Python SDK](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/MCP%20Python%20SDK) - Build powerful apps that communicate through an elegant protocol without sweating the details!

- [NumPy Core](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/NumPy%20Core) - Master the engine behind data science that makes Python as fast as C!

- [OpenManus](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/OpenManus) - Build AI agents with digital brains that think, learn, and use tools just like humans do!

- [PocketFlow](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/PocketFlow) - 100-line LLM framework. Let Agents build Agents!

- [Pydantic Core](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/Pydantic%20Core) - Validate data at rocket speed with just Python type hints!

- [Requests](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/Requests) - Talk to the internet in Python with code so simple it feels like cheating!

- [SmolaAgents](https://the-pocket.github.io/PocketFlow-Tutorial-Codebase-Knowledge/SmolaAgents) - Build tiny AI agents that punch way above their weight class!

- Showcase Your AI-Generated Tutorials in [Discussions](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge/discussions)!

## 🚀 Getting Started

1. Clone this repository
   ```bash
   git clone https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. LLM mode is file-based by default in [`utils/call_llm.py`](./utils/call_llm.py):
   - For each step, prompt/response files are generated under `workspace/llm/<project_name>/prompts/` and `workspace/llm/<project_name>/responses/`.
   - The process emits a machine-readable signal line:
     - `[LLM_SIGNAL]{"type":"llm_manual_request","prompt_path":"...","response_path":"..."}`
   - An agent should read `prompt_path`, write a response to `response_path`, and the runner automatically continues once the file is non-empty.
   - Consent is asked once per run (when enabled), then subsequent steps proceed automatically.
   - Prompt/response files use stable step names (for example `identify_abstractions.txt`, `write_chapter_01.txt`) so reruns can auto-skip steps when response files already exist.
   You can verify manual mode by running:
   ```bash
   python utils/call_llm.py
   ```

5. Configure run settings in YAML:
    ```yaml
    # configure_args.yaml
    local_dir: /path/to/your/codebase
    project_name: my-project
    include_patterns:
      - "*.py"
    exclude_patterns:
      - "tests/*"
    output_dir: output
    language: english
    max_file_size: 100000
    use_cache: true
    max_abstraction_num: 10
    llm_require_consent: false
    llm_show_prompt: false
    log_dir: workspace/logs
    llm_cache_file: workspace/cache/llm_cache.json
    llm_manual_dir: workspace/llm
    llm_manual_poll_interval_s: 2.0
    llm_manual_timeout_s: 0
    llm_redact_logs: true
    ```
   - Edit this YAML file directly before running.

6. Run the full pipeline:
    ```bash
    python main.py
    ```
   - `RunConfig` loads and shows the effective YAML config, then asks for final approval before crawling starts.

7. Manual mode behavior:
   - No terminal paste is required.
   - The app writes prompt files and automatically waits/polls for matching response files.
   - `LLM_SIGNAL` lines provide exact prompt/response paths for agent automation.
   - LLM cache is project-scoped under `workspace/cache/<project_name>/` (derived from `llm_cache_file` base name).
   - Polling can be configured in YAML with `llm_manual_poll_interval_s` and `llm_manual_timeout_s`.

8. Prompt for your terminal agent:
   - See [`PROMPT_INIT.md`](./PROMPT_INIT.md).

The application reads project settings from YAML, crawls the configured local directory, analyzes the codebase structure, generates tutorial content, and saves output to the configured output directory.


<details>
 
<summary> 🐳 <b>Running with Docker</b> </summary>

To run this project in a Docker container, manual mode is the default and no API key is required.

1. Build the Docker image
   ```bash
   docker build -t pocketflow-app .
   ```

2. Run the container

   This project uses manual mode. Prompts are written to files, then you write model responses to matching response files.
   
   Mount a local directory to `/app/output` inside the container to access the generated tutorials on your host machine.
   
   **Example for analyzing a local directory:**
   
   ```bash
   docker run -it --rm \
     -v "/path/to/your/local_codebase":/app/code_to_analyze \
     -v "$(pwd)/workspace":/app/workspace \
     -v "$(pwd)/output_tutorials":/app/output \
     pocketflow-app
   ```
</details>

## 💡 Development Tutorial

- I built using [**Agentic Coding**](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to), the fastest development paradigm, where humans simply [design](docs/design.md) and agents [code](flow.py).

- The secret weapon is [Pocket Flow](https://github.com/The-Pocket/PocketFlow), a 100-line LLM framework that lets Agents (e.g., Cursor AI) build for you

- Check out the Step-by-step YouTube development tutorial:

<br>
<div align="center">
  <a href="https://youtu.be/AFY67zOpbSo" target="_blank">
    <img src="./assets/youtube_thumbnail.png" width="500" alt="Pocket Flow Codebase Tutorial" style="cursor: pointer;">
  </a>
</div>
<br>
