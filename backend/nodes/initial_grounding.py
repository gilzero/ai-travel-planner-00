"""
@fileoverview This module defines the InitialGroundingNode class, which is responsible for generating initial search queries based on user preferences.
@filepath backend/nodes/initial_grounding.py
"""

from langchain_core.messages import AIMessage
from tavily import AsyncTavilyClient
import os
from datetime import datetime
from ..classes import ResearchState

class InitialGroundingNode:
    def __init__(self) -> None:
        self.tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        print("🛠️ [DEBUG] InitialGroundingNode initialized with Tavily client.")

    async def generate_search_queries(self, preferences):
        print(f"🔍 [DEBUG] Generating search queries for destination: {preferences.destination}")
        base_queries = [
            f"tourist guide {preferences.destination}",
            f"best time to visit {preferences.destination}",
            f"{preferences.travel_style} activities {preferences.destination}",
            f"weather {preferences.destination} {preferences.start_date.strftime('%B')}",
            f"local transportation {preferences.destination}"
        ]

        if preferences.accessibility_requirements:
            base_queries.append(f"accessibility {preferences.accessibility_requirements} {preferences.destination}")
            print(f"♿ [DEBUG] Added accessibility query for: {preferences.accessibility_requirements}")

        if preferences.dietary_restrictions:
            dietary_str = " ".join(preferences.dietary_restrictions)
            base_queries.append(f"restaurants {dietary_str} {preferences.destination}")
            print(f"🍽️ [DEBUG] Added dietary restrictions query for: {dietary_str}")

        for dest in preferences.additional_destinations:
            base_queries.extend([
                f"tourist guide {dest}",
                f"transportation from {preferences.destination} to {dest}"
            ])
            print(f"🗺️ [DEBUG] Added queries for additional destination: {dest}")

        print(f"✅ [DEBUG] Generated search queries: {base_queries}")
        return base_queries

    async def initial_search(self, state: ResearchState):
        preferences = state['preferences']
        print(f"🔎 [DEBUG] Starting initial search for: {preferences.destination}")
        msg = f"🔎 Starting initial research for {preferences.destination}...\n"

        state['initial_data'] = {}
        search_queries = await self.generate_search_queries(preferences)
        print(f"📋 [DEBUG] Search queries to be executed: {search_queries}")

        try:
            for query in search_queries:
                print(f"🔍 [DEBUG] Executing search query: {query}")
                search_results = await self.tavily_client.search(query=query, max_results=3)
                print(f"📊 [DEBUG] Search results for query '{query}': {search_results}")

                for result in search_results['results']:
                    url = result['url']
                    if url not in state['initial_data']:
                        state['initial_data'][url] = {
                            'url': url,
                            'content': result.get('content', ''),
                            'score': result.get('score', 0),
                            'query': query
                        }
                        print(f"🌐 [DEBUG] Added result for URL: {url}")

            msg += f"✔️ Gathered initial information about {preferences.destination}\n"
            if preferences.additional_destinations:
                msg += f"✔️ Including information about additional destinations: {', '.join(preferences.additional_destinations)}\n"
                print(f"🗺️ [DEBUG] Additional destinations included: {preferences.additional_destinations}")

        except Exception as e:
            error_msg = f"Error during initial research: {str(e)}"
            print(f"🔥 [ERROR] {error_msg}")
            msg += f"❌ {error_msg}\n"

        print("🏁 [DEBUG] Initial search completed.")
        return {
            "messages": [AIMessage(content=msg)],
            "initial_data": state['initial_data']
        }

    async def run(self, state: ResearchState):
        print("🚀 [DEBUG] Running initial grounding process.")
        result = await self.initial_search(state)
        print("✅ [DEBUG] Initial grounding process completed.")
        return result
