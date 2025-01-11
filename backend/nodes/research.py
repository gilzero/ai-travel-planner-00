"""
@fileoverview This module defines the ResearcherNode class, which is responsible for conducting travel-specific research and storing results in the documents attribute.
@filepath backend/nodes/research.py
"""

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
        print("🔧 Initialized ResearcherNode with Tavily client.")

    async def tavily_search(self, sub_queries: List[TravelQuery]):
        """Perform searches for each travel-related sub-query using Tavily search concurrently."""
        print("🔍 Starting Tavily search for sub-queries...")

        async def perform_search(query: TravelQuery):
            try:
                print(f"🔎 Performing search for query: {query.query}")
                # Add date and location context to the query
                search_query = f"{query.query} {datetime.now().strftime('%Y')}"
                print(f"📅 Search query with date context: {search_query}")

                # Adjust search parameters based on query category
                search_params = {
                    "query": search_query,
                    "search_depth": "advanced",
                    "max_results": 5
                }

                # Add category-specific parameters
                if query.category == "accommodation":
                    search_params["include_domains"] = ["booking.com", "hotels.com", "airbnb.com", "tripadvisor.com"]
                    print("🏨 Accommodation search parameters set.")
                elif query.category == "activity":
                    search_params["include_domains"] = ["viator.com", "tripadvisor.com", "timeout.com",
                                                        "lonelyplanet.com"]
                    print("🎡 Activity search parameters set.")
                elif query.category == "transport":
                    search_params["include_domains"] = ["rome2rio.com", "skyscanner.com", "kayak.com"]
                    print("🚗 Transport search parameters set.")

                response = await self.tavily_client.search(**search_params)
                print(f"✅ Search completed for query: {query.query}")
                return response['results']
            except Exception as e:
                print(f"❌ Error searching for query '{query.query}': {str(e)}")
                return []

        # Run all search tasks in parallel
        search_tasks = [perform_search(query) for query in sub_queries]
        search_responses = await asyncio.gather(*search_tasks)
        print("🔄 All search tasks completed.")

        # Combine and deduplicate results
        seen_urls = set()
        search_results = []
        for response in search_responses:
            for result in response:
                url = result['url']
                if url not in seen_urls:
                    search_results.append(result)
                    seen_urls.add(url)
                    print(f"🌐 Added new result: {url}")

        print(f"📊 Total unique results found: {len(search_results)}")
        return search_results

    async def research(self, state: ResearchState):
        """
        Conducts travel-specific research and stores results in the documents attribute.
        """
        print("🔍 Starting research process...")
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
                    print(f"📄 Document added: {url}")

            msg += f"✓ Found {len(state['documents'])} relevant sources\n"
            print(f"✅ Research completed. {len(state['documents'])} documents added.")

        except Exception as e:
            msg += f"❌ Error during research: {str(e)}\n"
            print(f"❌ Error during research: {str(e)}")

        return {"messages": [AIMessage(content=msg)], "documents": state['documents']}

    async def run(self, state: ResearchState):
        print("🚀 Running research node...")
        result = await self.research(state)
        print("🏁 Research node execution completed.")
        return result