from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
from typing import TypedDict, List, Annotated, Dict, Union
from datetime import date

from .travel.models import (
    TravelPreferences,
    DayPlan,
    TravelSearchInput
)

class ResearchState(TypedDict):
    preferences: TravelPreferences
    initial_data: Dict[str, Dict[Union[str, int], Union[str, float]]]
    sub_queries: TravelSearchInput
    documents: Dict[str, Dict[Union[str, int], Union[str, float]]]
    document_clusters: List[Dict[str, Union[str, List[str]]]]
    chosen_cluster: int
    itinerary: List[DayPlan]
    eval: Dict[str, Union[int, List[str]]]
    output_format: str
    messages: Annotated[list[AnyMessage], add_messages]

class InputState(TypedDict):
    preferences: TravelPreferences

class OutputState(TypedDict):
    itinerary: List[DayPlan]