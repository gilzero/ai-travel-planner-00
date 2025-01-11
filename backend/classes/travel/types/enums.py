"""
@fileoverview This module defines enumerations for travel styles and activity
              types used in travel-related models.
@filepath backend/classes/travel/types/enums.py
"""

from enum import Enum

class TravelStyle(str, Enum):
    """
    Enumeration for different travel styles.
    """
    LUXURY = "luxury"
    BUDGET = "budget"
    ADVENTURE = "adventure"
    FAMILY = "family"
    BUSINESS = "business"
    CULTURAL = "cultural"
    RELAXATION = "relaxation"

    def __new__(cls, *args, **kwargs):
        obj = str.__new__(cls, *args, **kwargs)
        obj._value_ = args[0]
        print(f"🌟 TravelStyle created: {obj}")
        return obj

class ActivityType(str, Enum):
    """
    Enumeration for different types of activities.
    """
    SIGHTSEEING = "sightseeing"
    OUTDOOR = "outdoor"
    CULTURAL = "cultural"
    DINING = "dining"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    RELAXATION = "relaxation"

    def __new__(cls, *args, **kwargs):
        obj = str.__new__(cls, *args, **kwargs)
        obj._value_ = args[0]
        print(f"🎯 ActivityType created: {obj}")
        return obj