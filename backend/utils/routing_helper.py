"""
@fileoverview This module provides routing logic for research state transitions
              based on various conditions such as cluster selection and
              evaluation results.
@filepath backend/utils/routing_helper.py
"""

from typing import Literal
from ..classes import ResearchState
from langchain_core.messages import AIMessage

def route_based_on_cluster(state: ResearchState) -> Literal["enrich_docs", "manual_cluster_selection"]:
    """
    Determines the next step based on the presence of a chosen cluster.
    
    Args:
        state (ResearchState): The current research state.
    
    Returns:
        Literal: "enrich_docs" if a cluster is chosen, otherwise "manual_cluster_selection".
    """
    chosen_cluster = state.get('chosen_cluster')
    print(f"🔍 Checking chosen cluster: {chosen_cluster}")
    if chosen_cluster is not None:
        print("📂 Route: enrich_docs")
        return "enrich_docs"
    print("🗂️ Route: manual_cluster_selection")
    return "manual_cluster_selection"

def route_after_manual_selection(state: ResearchState) -> Literal["enrich_docs", "cluster"]:
    """
    Routes the flow after manual cluster selection.
    
    Args:
        state (ResearchState): The current research state.
    
    Returns:
        Literal: "enrich_docs" if a valid cluster is chosen, otherwise "cluster".
    """
    chosen_cluster = state.get('chosen_cluster')
    print(f"🔍 Checking chosen cluster after manual selection: {chosen_cluster}")
    if chosen_cluster >= 0:
        print("📂 Route: enrich_docs")
        return "enrich_docs"
    print("🔄 Route: cluster")
    return "cluster"

def should_continue_research(state: ResearchState) -> Literal["research", "generate_report"]:
    """
    Decides whether to continue research or generate a report based on document count.
    
    Args:
        state (ResearchState): The current research state.
    
    Returns:
        Literal: "research" if document count is below threshold, otherwise "generate_report".
    """
    min_doc_count = 2
    doc_count = len(state["documents"])
    print(f"📄 Document count: {doc_count}, Minimum required: {min_doc_count}")
    if doc_count < min_doc_count:
        print("🔍 Route: research")
        return "research"
    print("📝 Route: generate_report")
    return "generate_report"

def route_based_on_evaluation(state: ResearchState) -> Literal["research", "publish"]:
    """
    Routes based on the evaluation grade of the report.
    
    Args:
        state (ResearchState): The current research state.
    
    Returns:
        Literal: "research" if the report grade is critical, otherwise "publish".
    """
    evaluation = state.get("eval")
    grade = evaluation.grade
    print(f"📊 Evaluation grade: {grade}")
    if grade == 1:
        print("🔍 Route: research")
        return "research"
    print("🚀 Route: publish")
    return "publish"
