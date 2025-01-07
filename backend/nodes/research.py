from langchain_core.messages import AIMessage
from tavily import AsyncTavilyClient
import os
import asyncio
from datetime import datetime
from typing import List

from ..classes import ResearchState, TravelQuery


class ResearcherNode():
    def __init__(self):
        self.tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    async def tavily_search(self, sub_queries: List[TravelQuery]):
        """Perform searches for each travel-related sub-query using Tavily search concurrently."""

        async def perform_search(query: TravelQuery):
            try:
                # Add date and location context to the query
                search_query = f"{query.query} {datetime.now().strftime('%Y')}"

                # Adjust search parameters based on query category
                search_params = {
                    "query": search_query,
                    "search_depth": "advanced",
                    "max_results": 5
                }

                # Add category-specific parameters
                if query.category == "accommodation":
                    search_params["include_domains"] = ["booking.com", "hotels.com", "airbnb.com", "tripadvisor.com"]
                elif query.category == "activity":
                    search_params["include_domains"] = ["viator.com", "tripadvisor.com", "timeout.com",
                                                        "lonelyplanet.com"]
                elif query.category == "transport":
                    search_params["include_domains"] = ["rome2rio.com", "skyscanner.com", "kayak.com"]

                response = await self.tavily_client.search(**search_params)
                return response['results']
            except Exception as e:
                print(f"Error searching for query '{query.query}': {str(e)}")
                return []

        # Run all search tasks in parallel
        search_tasks = [perform_search(query) for query in sub_queries]
        search_responses = await asyncio.gather(*search_tasks)

        # Combine and deduplicate results
        seen_urls = set()
        search_results = []
        for response in search_responses:
            for result in response:
                url = result['url']
                if url not in seen_urls:
                    search_results.append(result)
                    seen_urls.add(url)

        return search_results

    async def research(self, state: ResearchState):
        """
        Conducts travel-specific research and stores results in the documents attribute.
        """
        msg = "🔍 Researching travel options and details...\n"
        state['documents'] = {}  # Initialize documents if not present

        try:
            # Perform the search and gather results
            response = await self.tavily_search(state['sub_queries'].sub_queries)

            # Process search results
            for doc in response:
                url = doc.get('url')
                if url and url not in state['documents']:
                    # Add metadata about the result
                    state['documents'][url] = {
                        'url': url,
                        'content': doc.get('content', ''),
                        'title': doc.get('title', ''),
                        'score': doc.get('score', 0),
                        'published_date': doc.get('published_date'),
                    }

            msg += f"✓ Found {len(state['documents'])} relevant sources\n"

        except Exception as e:
            msg += f"❌ Error during research: {str(e)}\n"

        return {"messages": [AIMessage(content=msg)], "documents": state['documents']}

    async def run(self, state: ResearchState):
        result = await self.research(state)
        return result