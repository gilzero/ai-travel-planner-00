from langchain_core.messages import AIMessage
from tavily import AsyncTavilyClient
import os
from ..classes import ResearchState


class EnrichDocsNode:
    def __init__(self):
        self.tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    async def curate(self, state: ResearchState):
        clusters = state['document_clusters']
        msg = "🔍 Enriching travel information...\n"

        enriched_docs = {}
        urls_to_extract = []

        # Collect URLs from all clusters
        for cluster in clusters:
            urls_to_extract.extend(cluster['urls'][:5])  # Limit to top 5 URLs per category

        # Remove duplicates while preserving order
        urls_to_extract = list(dict.fromkeys(urls_to_extract))

        try:
            # Enrich content using Tavily Extract
            extracted_content = await self.tavily_client.extract(urls=urls_to_extract)

            # Process extracted content by category
            for item in extracted_content["results"]:
                url = item['url']

                # Find which cluster this URL belongs to
                for cluster in clusters:
                    if url in cluster['urls']:
                        category = cluster['category']
                        break
                else:
                    category = "Miscellaneous"

                # Extract and structure relevant information based on category
                details = {
                    'category': category,
                    'url': url,
                    'raw_content': item.get('raw_content', ''),
                    'extracted_content': item.get('text', ''),
                }

                # Add category-specific extraction
                if category == "Accommodations":
                    details.update({
                        'price_range': self.extract_price_range(item),
                        'amenities': self.extract_amenities(item),
                        'location': self.extract_location(item)
                    })
                elif category == "Activities & Attractions":
                    details.update({
                        'duration': self.extract_duration(item),
                        'best_time': self.extract_best_time(item),
                        'booking_required': self.extract_booking_info(item)
                    })
                elif category == "Transportation":
                    details.update({
                        'transport_type': self.extract_transport_type(item),
                        'schedule': self.extract_schedule(item),
                        'cost': self.extract_cost(item)
                    })
                elif category == "Dining & Food":
                    details.update({
                        'cuisine': self.extract_cuisine(item),
                        'price_level': self.extract_price_level(item),
                        'opening_hours': self.extract_opening_hours(item)
                    })

                enriched_docs[url] = details

            msg += f"✓ Enriched {len(enriched_docs)} travel resources\n"

        except Exception as e:
            msg += f"Error during content enrichment: {str(e)}\n"

        return {"messages": [AIMessage(content=msg)], "documents": enriched_docs}

    def extract_price_range(self, item):
        # Implementation for price range extraction
        return "Price information not available"

    def extract_amenities(self, item):
        # Implementation for amenities extraction
        return []

    def extract_location(self, item):
        # Implementation for location extraction
        return "Location details not available"

    def extract_duration(self, item):
        # Implementation for duration extraction
        return "Duration not specified"

    def extract_best_time(self, item):
        # Implementation for best time extraction
        return "Time information not available"

    def extract_booking_info(self, item):
        # Implementation for booking information extraction
        return False

    def extract_transport_type(self, item):
        # Implementation for transport type extraction
        return "Transport type not specified"

    def extract_schedule(self, item):
        # Implementation for schedule extraction
        return "Schedule not available"

    def extract_cost(self, item):
        # Implementation for cost extraction
        return "Cost information not available"

    def extract_cuisine(self, item):
        # Implementation for cuisine extraction
        return "Cuisine type not specified"

    def extract_price_level(self, item):
        # Implementation for price level extraction
        return "Price level not available"

    def extract_opening_hours(self, item):
        # Implementation for opening hours extraction
        return "Opening hours not available"

    async def run(self, state: ResearchState):
        result = await self.curate(state)
        return result