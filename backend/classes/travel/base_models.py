from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from .types.enums import TravelStyle, ActivityType


class TravelQuery(BaseModel):
    query: str = Field(..., description="Travel-related search query")
    category: str = Field(..., description="Category of information (accommodation/activity/transport)")
    location: str = Field(..., description="Relevant location for the query")


class TravelSearchInput(BaseModel):
    sub_queries: List[TravelQuery] = Field(..., description="Set of travel-related sub-queries to be researched")


class TravelPreferences(BaseModel):
    destination: str = Field(..., description="Primary destination city/country")
    additional_destinations: List[str] = Field(
        default_factory=list,
        description="Additional destinations if multi-city trip"
    )
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    budget_min: float = Field(..., ge=0, description="Minimum budget in USD (must be non-negative)")
    budget_max: float = Field(..., ge=0, description="Maximum budget in USD (must be non-negative)")
    travel_style: TravelStyle = Field(..., description="Preferred travel style")
    preferred_activities: List[ActivityType] = Field(..., description="List of preferred activity types")
    accessibility_requirements: Optional[str] = Field(None, description="Any accessibility requirements")
    dietary_restrictions: Optional[List[str]] = Field(
        default_factory=list,
        description="List of dietary restrictions"
    )
    number_of_travelers: int = Field(default=1, ge=1, description="Number of travelers (minimum 1)")
    preferred_languages: List[str] = Field(
        default_factory=lambda: ["English"],
        description="Preferred languages for activities"
    )

    @model_validator(mode="after")
    def validate_dates_and_budget(self):
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be earlier than the end date.")
        if self.budget_min > self.budget_max:
            raise ValueError("Minimum budget must not exceed maximum budget.")
        return self

    def summary(self) -> str:
        """Returns a brief summary of the travel preferences."""
        return (
            f"Destination: {self.destination}\n"
            f"Dates: {self.start_date} to {self.end_date}\n"
            f"Budget: ${self.budget_min} - ${self.budget_max}\n"
            f"Style: {self.travel_style}\n"
            f"Activities: {', '.join([activity.value for activity in self.preferred_activities])}\n"
            f"Travelers: {self.number_of_travelers}\n"
            f"Languages: {', '.join(self.preferred_languages)}"
        )
