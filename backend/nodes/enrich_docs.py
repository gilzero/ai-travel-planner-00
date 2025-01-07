from langchain_core.messages import AIMessage
from tavily import AsyncTavilyClient
import os
from typing import Dict, List, Optional
from ..classes import ResearchState


class EnrichDocsNode:
    def __init__(self):
        self.tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    async def curate(self, state: ResearchState):
        clusters = state['document_clusters']
        msg = "🔍 Enriching travel information...\n"
        enriched_docs = {}
        urls_to_extract = self._collect_and_validate_urls(clusters)

        # Log the collected URLs
        print(f"[DEBUG] Collected URLs for enrichment: {urls_to_extract}")

        if not urls_to_extract:
            msg += "❌ No valid URLs to enrich. Ensure clusters contain valid URLs.\n"
            print(f"[DEBUG] No valid URLs collected from clusters: {clusters}")
            return {
                "messages": [AIMessage(content=msg)],
                "documents": {}
            }

        try:
            # Enrich content using Tavily Extract
            print(f"[DEBUG] Sending {len(urls_to_extract)} URLs to Tavily Extract for enrichment...")
            extracted_content = await self.tavily_client.extract(urls=urls_to_extract)

            # Process extracted content
            enriched_docs = self._process_extracted_content(extracted_content, clusters)
            if enriched_docs:
                msg += f"✓ Successfully enriched {len(enriched_docs)} travel resources.\n"
                print(f"[DEBUG] Enriched documents: {enriched_docs}")
            else:
                msg += "❌ No valid content extracted from the provided URLs.\n"
                print(f"[DEBUG] Tavily Extract returned no valid content for URLs: {urls_to_extract}")

        except Exception as e:
            msg += f"❌ Error during content enrichment: {str(e)}\n"
            print(f"[ERROR] Exception during enrichment: {str(e)}")

        return {"messages": [AIMessage(content=msg)], "documents": enriched_docs}

    def _collect_and_validate_urls(self, clusters: List[Dict]) -> List[str]:
        """Collects and validates URLs from clusters."""
        urls = []
        for cluster in clusters:
            cluster_urls = cluster.get("urls", [])
            if not isinstance(cluster_urls, list):
                print(f"[WARNING] Cluster '{cluster.get('category', 'Unknown')}' contains invalid 'urls'.")
                continue  # Skip invalid clusters
            urls.extend(cluster_urls[:5])  # Limit to top 5 URLs per cluster

        # Remove duplicates while preserving order
        return list(dict.fromkeys(urls))

    def _process_extracted_content(self, extracted_content: Dict, clusters: List[Dict]) -> Dict:
        """Processes the extracted content and associates it with clusters."""
        enriched_docs = {}
        for item in extracted_content.get("results", []):
            url = item.get("url")
            if not url:
                print(f"[DEBUG] Skipping extracted item with no URL: {item}")
                continue

            # Identify the category for the URL
            category = self._identify_category(url, clusters)

            # Extract general content
            details = {
                "category": category,
                "url": url,
                "raw_content": item.get("raw_content", ""),
                "extracted_content": item.get("text", ""),
            }

            # Perform category-specific enrichment
            details.update(self._category_specific_enrichment(category, item))

            enriched_docs[url] = details

        return enriched_docs

    def _identify_category(self, url: str, clusters: List[Dict]) -> str:
        """Identifies the category for a given URL."""
        for cluster in clusters:
            if url in cluster.get("urls", []):
                return cluster.get("category", "Miscellaneous")
        return "Miscellaneous"

    def _category_specific_enrichment(self, category: str, item: Dict) -> Dict:
        """Performs category-specific enrichment."""
        if category == "Accommodations":
            return {
                "price_range": self.extract_price_range(item),
                "amenities": self.extract_amenities(item),
                "location": self.extract_location(item),
            }
        elif category == "Activities & Attractions":
            return {
                "duration": self.extract_duration(item),
                "best_time": self.extract_best_time(item),
                "booking_required": self.extract_booking_info(item),
            }
        elif category == "Transportation":
            return {
                "transport_type": self.extract_transport_type(item),
                "schedule": self.extract_schedule(item),
                "cost": self.extract_cost(item),
            }
        elif category == "Dining & Food":
            return {
                "cuisine": self.extract_cuisine(item),
                "price_level": self.extract_price_level(item),
                "opening_hours": self.extract_opening_hours(item),
            }
        return {}

    def extract_price_range(self, item):
        return "Price information not available"

    def extract_amenities(self, item):
        return []

    def extract_location(self, item):
        return "Location details not available"

    def extract_duration(self, item):
        return "Duration not specified"

    def extract_best_time(self, item):
        return "Time information not available"

    def extract_booking_info(self, item):
        return False

    def extract_transport_type(self, item):
        return "Transport type not specified"

    def extract_schedule(self, item):
        return "Schedule not available"

    def extract_cost(self, item):
        return "Cost information not available"

    def extract_cuisine(self, item):
        return "Cuisine type not specified"

    def extract_price_level(self, item):
        return "Price level not available"

    def extract_opening_hours(self, item):
        return "Opening hours not available"

    async def run(self, state: ResearchState):
        result = await self.curate(state)
        return result
