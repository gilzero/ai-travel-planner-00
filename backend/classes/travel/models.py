from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

class TravelStyle(str, Enum):
    LUXURY = "luxury"
    BUDGET = "budget"
    ADVENTURE = "adventure"
    FAMILY = "family"
    BUSINESS = "business"
    CULTURAL = "cultural"
    RELAXATION = "relaxation"

class ActivityType(str, Enum):
    SIGHTSEEING = "sightseeing"
    OUTDOOR = "outdoor"
    CULTURAL = "cultural"
    DINING = "dining"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    RELAXATION = "relaxation"

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

class Activity(BaseModel):
    name: str = Field(..., description="Name of the activity")
    type: ActivityType = Field(..., description="Type of activity")
    location: str = Field(..., description="Location of the activity")
    duration: float = Field(..., description="Duration in hours")
    cost: float = Field(..., description="Cost per person in USD")
    description: str = Field(..., description="Detailed description")
    booking_required: bool = Field(default=False, description="Whether booking is required")
    booking_url: Optional[str] = Field(None, description="URL for booking if required")
    recommended_time: Optional[str] = Field(None, description="Recommended time of day")
    indoor: bool = Field(default=True, description="Whether it's an indoor activity")

class Accommodation(BaseModel):
    name: str = Field(..., description="Name of the accommodation")
    type: str = Field(..., description="Type (hotel, hostel, apartment, etc.)")
    location: str = Field(..., description="Address/location")
    check_in: datetime = Field(..., description="Check-in time")
    check_out: datetime = Field(..., description="Check-out time")
    cost_per_night: float = Field(..., description="Cost per night in USD")
    booking_url: str = Field(..., description="Booking URL")
    amenities: List[str] = Field(default_factory=list, description="Available amenities")
    rating: Optional[float] = Field(None, description="Rating out of 5")

class Transportation(BaseModel):
    type: str = Field(..., description="Type of transportation")
    from_location: str = Field(..., description="Starting point")
    to_location: str = Field(..., description="Destination")
    departure_time: datetime = Field(..., description="Departure time")
    arrival_time: datetime = Field(..., description="Arrival time")
    cost: float = Field(..., description="Cost per person in USD")
    booking_url: Optional[str] = Field(None, description="Booking URL if applicable")

class DailyItinerary(BaseModel):
    date: date = Field(..., description="Date of the itinerary")
    accommodation: Optional[Accommodation] = Field(None, description="Accommodation for this day")
    activities: List[Activity] = Field(default_factory=list, description="List of activities")
    transportation: List[Transportation] = Field(default_factory=list, description="List of transportation segments")
    total_cost: float = Field(default=0, description="Total cost for the day")
    notes: Optional[str] = Field(None, description="Additional notes for the day")

class TravelQuery(BaseModel):
    query: str = Field(description="Travel-related search query")
    category: str = Field(description="Category of information (accommodation/activity/transport)")
    location: str = Field(description="Relevant location for the query")

class TravelSearchInput(BaseModel):
    sub_queries: List[TravelQuery] = Field(description="Set of travel-related sub-queries to be researched")