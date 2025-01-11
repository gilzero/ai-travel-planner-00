"""
@fileoverview This module defines the state structures used in the research
process, including input, output, and intermediate states.

@filepath backend/classes/research_state.py
"""

from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
from typing import TypedDict, List, Annotated, Dict, Union
from datetime import date
from pydantic import TypeAdapter

from .travel.base_models import TravelPreferences
from .travel.models import DayPlan

class ResearchState(TypedDict):
    """
    Represents the complete state of the research process, including
    preferences, data, and evaluation results.
    """
    preferences: TravelPreferences
    initial_data: Dict[str, Dict[Union[str, int], Union[str, float]]]
    sub_queries: Dict[str, List[str]]
    documents: Dict[str, Dict[Union[str, int], Union[str, float]]]
    document_clusters: List[Dict[str, Union[str, List[str]]]]
    chosen_cluster: int
    itinerary: List[DayPlan]
    eval: Dict[str, Union[int, List[str]]]
    output_format: str
    messages: Annotated[list[AnyMessage], add_messages]

class InputState(TypedDict):
    """
    Represents the initial input state containing user preferences.
    """
    preferences: TravelPreferences

class OutputState(TypedDict):
    """
    Represents the output state containing the generated itinerary.
    """
    itinerary: List[DayPlan]