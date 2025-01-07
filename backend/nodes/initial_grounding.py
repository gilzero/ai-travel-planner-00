from langchain_core.messages import AIMessage
from tavily import AsyncTavilyClient
import os
from datetime import datetime, timedelta

from ..classes import ResearchState


class InitialGroundingNode:
    def __init__(self) -> None:
        self.tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    async def generate_search_queries(self, preferences):
        """Generate initial search queries based on travel preferences."""
        base_queries = [
            f"tourist guide {preferences.destination}",
            f"best time to visit {preferences.destination}",
            f"{preferences.travel_style} activities {preferences.destination}",
            f"weather {preferences.destination} {preferences.start_date.strftime('%B')}",
            f"local transportation {preferences.destination}"
        ]

        # Add queries based on specific preferences
        if preferences.accessibility_requirements:
            base_queries.append(f"accessibility {preferences.accessibility_requirements} {preferences.destination}")

        if preferences.dietary_restrictions:
            dietary_str = " ".join(preferences.dietary_restrictions)
            base_queries.append(f"restaurants {dietary_str} {preferences.destination}")

        # Add queries for additional destinations
        for dest in preferences.additional_destinations:
            base_queries.extend([
                f"tourist guide {dest}",
                f"transportation from {preferences.destination} to {dest}"
            ])

        return base_queries

    async def initial_search(self, state: ResearchState):
        """Perform initial destination research using Tavily search."""
        preferences = state['preferences']
        msg = f"🔎 Starting initial research for {preferences.destination}...\n"

        state['initial_data'] = {}
        search_queries = await self.generate_search_queries(preferences)

        try:
            # Search for each query
            for query in search_queries:
                search_results = await self.tavily_client.search(query=query, max_results=3)

                # Store results
                for result in search_results['results']:
                    url = result['url']
                    if url not in state['initial_data']:
                        state['initial_data'][url] = {
                            'url': url,
                            'content': result['content'],
                            'score': result.get('score', 0),
                            'query': query
                        }

            msg += f"✔️ Gathered initial information about {preferences.destination}\n"
            if preferences.additional_destinations:
                msg += f"✔️ Including information about additional destinations: {', '.join(preferences.additional_destinations)}\n"

        except Exception as e:
            error_msg = f"Error during initial research: {str(e)}"
            print(error_msg)
            msg += f"❌ {error_msg}\n"

        return {
            "messages": [AIMessage(content=msg)],
            "initial_data": state['initial_data']
        }

    async def run(self, state: ResearchState):
        result = await self.initial_search(state)
        return result