"""
@fileoverview This module defines data structures used for enhancing web search capabilities, 
              clustering documents, and evaluating reports.
              This module contains the classes for the TavilyQuery and TavilySearchInput models.
              It also contains the classes for the DocumentCluster and DocumentClusters models.
              Finally, it contains the class for the ReportEvaluation model.
              
@filepath backend/classes/classes.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class TavilyQuery(BaseModel):
    """
    Represents a single web search query for Tavily's search tool.
    """
    query: str = Field(description="web search query")

class TavilySearchInput(BaseModel):
    """
    Defines the input schema for the Tavily search tool using a multi-query approach.
    """
    sub_queries: List[TavilyQuery] = Field(description="set of sub-queries that can be answered in isolation")

class DocumentCluster(BaseModel):
    """
    Represents a cluster of documents associated with a specific company.
    """
    company_name: str = Field(
        ...,
        description="The name or identifier of the company these documents belong to."
    )
    cluster: List[str] = Field(
        ...,
        description="A list of URLs relevant to the identified company."
    )

class DocumentClusters(BaseModel):
    """
    Contains a list of document clusters.
    """
    clusters: List[DocumentCluster] = Field(default_factory=list, description="List of document clusters")

class ReportEvaluation(BaseModel):
    """
    Represents the evaluation of a report, including a grade and any critical gaps.
    """
    grade: int = Field(
        ..., 
        description="Overall grade of the report on a scale from 1 to 3 (1 = needs improvement, 3 = complete and thorough)."
    )
    critical_gaps: Optional[List[str]] = Field(
        None, 
        description="List of critical gaps to address if the grade is 1."
    )

