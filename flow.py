from pocketflow import Flow
# Import all node classes from nodes.py
from nodes import (
    RunConfig,
    FetchRepo,
    IdentifyAbstractions,
    AnalyzeRelationships,
    OrderChapters,
    WriteChapters,
    CombineTutorial
)

def create_tutorial_inner_flow():
    """Create the inner tutorial flow from fetching files to final assembly."""
    # Instantiate nodes
    fetch_repo = FetchRepo()
    identify_abstractions = IdentifyAbstractions(max_retries=5, wait=20)
    analyze_relationships = AnalyzeRelationships(max_retries=5, wait=20)
    order_chapters = OrderChapters(max_retries=5, wait=20)
    write_chapters = WriteChapters(max_retries=5, wait=20) # This is a BatchNode
    combine_tutorial = CombineTutorial()

    # Inner sequence
    fetch_repo >> identify_abstractions
    identify_abstractions >> analyze_relationships
    analyze_relationships >> order_chapters
    order_chapters >> write_chapters
    write_chapters >> combine_tutorial

    return Flow(start=fetch_repo)


def create_tutorial_flow():
    """
    Create outer flow where run configuration is confirmed and the entire tutorial
    generation pipeline is modeled as an inner Flow node.
    """
    run_config = RunConfig()
    tutorial_inner_flow = create_tutorial_inner_flow()

    run_config >> tutorial_inner_flow
    return Flow(start=run_config)
