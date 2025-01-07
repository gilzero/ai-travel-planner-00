from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from .types.enums import TravelStyle, ActivityType

class TravelQuery(BaseModel):
    query: str = Field(description="Travel-related search query")
    category: str = Field(description="Category of information (accommodation/activity/transport)")
    location: str = Field(description="Relevant location for the query")

class TravelSearchInput(BaseModel):
    sub_queries: List[TravelQuery] = Field(description="Set of travel-related sub-queries to be researched")

class TravelPreferences(BaseModel):
    destination: str = Field(..., description="Primary destination city/country")
    additional_destinations: List[str] = Field(default_factory=list, description="Additional destinations if multi-city trip")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    budget_min: float = Field(..., description="Minimum budget in USD")
    budget_max: float = Field(..., description="Maximum budget in USD")
    travel_style: TravelStyle = Field(..., description="Preferred travel style")
    preferred_activities: List[ActivityType] = Field(..., description="List of preferred activity types")
    accessibility_requirements: Optional[str] = Field(None, description="Any accessibility requirements")
    dietary_restrictions: Optional[List[str]] = Field(None, description="Any dietary restrictions")
    number_of_travelers: int = Field(default=1, description="Number of travelers")
    preferred_languages: List[str] = Field(default_factory=lambda: ["English"], description="Preferred languages for activities")