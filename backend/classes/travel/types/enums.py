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