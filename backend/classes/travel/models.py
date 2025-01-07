from datetime import date, datetime
from typing import List, Optional, ForwardRef
from pydantic import BaseModel, Field
from .types.enums import ActivityType

# Forward references for circular dependencies
DayPlanRef = ForwardRef('DayPlan')
ActivityDetailsRef = ForwardRef('ActivityDetails')
AccommodationDetailsRef = ForwardRef('AccommodationDetails')
TransportationDetailsRef = ForwardRef('TransportationDetails')

class TransportationDetails(BaseModel):
    type: str = Field(..., description="Type of transportation")
    from_location: str = Field(..., description="Starting point")
    to_location: str = Field(..., description="Destination")
    departure_time: datetime = Field(..., description="Departure time")
    arrival_time: datetime = Field(..., description="Arrival time")
    cost: float = Field(..., description="Cost per person in USD")
    booking_url: Optional[str] = Field(None, description="Booking URL if applicable")

class ActivityDetails(BaseModel):
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

class AccommodationDetails(BaseModel):
    name: str = Field(..., description="Name of the accommodation")
    type: str = Field(..., description="Type (hotel, hostel, apartment, etc.)")
    location: str = Field(..., description="Address/location")
    check_in: datetime = Field(..., description="Check-in time")
    check_out: datetime = Field(..., description="Check-out time")
    cost_per_night: float = Field(..., description="Cost per night in USD")
    booking_url: str = Field(..., description="Booking URL")
    amenities: List[str] = Field(default_factory=list, description="Available amenities")
    rating: Optional[float] = Field(None, description="Rating out of 5")

class DayPlan(BaseModel):
    date: date = Field(..., description="Date of the itinerary")
    accommodation: Optional["AccommodationDetails"] = Field(None, description="Accommodation for this day")
    activities: List["ActivityDetails"] = Field(default_factory=list, description="List of activities")
    transportation: List["TransportationDetails"] = Field(default_factory=list, description="List of transportation segments")
    total_cost: float = Field(default=0, description="Total cost for the day")
    notes: Optional[str] = Field(None, description="Additional notes for the day")

# Update forward references
DayPlan.model_rebuild()
ActivityDetails.model_rebuild()
AccommodationDetails.model_rebuild()
TransportationDetails.model_rebuild()