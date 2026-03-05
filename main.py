from cli_config import build_shared, set_llm_runtime_config

# --- Main Function ---
def main():
    shared = build_shared()
    set_llm_runtime_config(shared)

    # Display startup message. Actual values are loaded from YAML in RunConfig.
    print("Starting tutorial generation.")
    print(f"Configuration file: {shared['config_path']}")
    print(f"Log directory: {shared['log_dir']}")
    print(f"LLM cache file: {shared['llm_cache_file']}")
    print(f"Manual LLM directory: {shared['llm_manual_dir']}")
    print("RunConfig will load YAML and ask for explicit approval.")

    # Create the flow instance
    from flow import create_tutorial_flow

    tutorial_flow = create_tutorial_flow()

    # Run the flow
    tutorial_flow.run(shared)


if __name__ == "__main__":
    main()
