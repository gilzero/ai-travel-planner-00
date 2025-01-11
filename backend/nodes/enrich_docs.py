"""
@fileoverview This module defines the EnrichDocsNode class, which is responsible for enriching travel information by curating and processing document clusters.
@filepath backend/nodes/enrich_docs.py
"""

from langchain_core.messages import AIMessage
from tavily import AsyncTavilyClient
import os
from typing import Dict, List, Optional
from ..classes import ResearchState
import re


class EnrichDocsNode:
    def __init__(self):
        self.tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        print("🛠️ [DEBUG] EnrichDocsNode initialized.")

    async def curate(self, state: ResearchState):
        """
        Curate and enrich documents from provided clusters.
        """
        print("🚀 [DEBUG] Starting curate method.")

        # Initialize variables
        MAX_BATCH_SIZE = 20
        clusters = state['document_clusters']
        msg = "🔍 Enriching travel information...\n"
        enriched_docs = {}

        print(f"🗂️ [DEBUG] Document clusters received: {clusters}")

        # Collect URLs to process
        urls_to_extract = self._collect_and_validate_urls(clusters)
        print(f"🔗 [DEBUG] Collected URLs for enrichment: {urls_to_extract}")

        # Handle case when no valid URLs found
        if not urls_to_extract:
            msg += "❌ No valid URLs to enrich. Ensure clusters contain valid URLs.\n"
            print(f"⚠️ [DEBUG] No valid URLs collected from clusters: {clusters}")
            return {
                "messages": [AIMessage(content=msg)],
                "documents": {}
            }

        # Process URLs and enrich documents
        try:
            print(f"📡 [DEBUG] Sending URLs to Tavily Extract for enrichment...")

            for i in range(0, len(urls_to_extract), MAX_BATCH_SIZE):
                batch_urls = urls_to_extract[i:i + MAX_BATCH_SIZE]
                print(f"📡 [DEBUG] Sending batch of {len(batch_urls)} URLs to Tavily Extract for enrichment...")

                extracted_content = await self.tavily_client.extract(urls=batch_urls)
                print(f"✅ [DEBUG] Received content from Tavily API.")

                batch_enriched_docs = self._process_extracted_content(extracted_content, clusters)
                enriched_docs.update(batch_enriched_docs)

            # Create appropriate success message
            if enriched_docs:
                msg += f"✓ Successfully enriched {len(enriched_docs)} travel resources.\n"
                print(f"✨ [DEBUG] Enriched documents: {enriched_docs}")
            else:
                msg += "❌ No valid content extracted from the provided URLs.\n"
                print(f"⚠️ [DEBUG] Tavily Extract returned no valid content for URLs: {urls_to_extract}")

        except Exception as e:
            msg += f"🚨 Error during content enrichment: {str(e)}\n"
            print(f"🔥 [ERROR] Exception during enrichment: {str(e)}")

        print("🚪 [DEBUG] Exiting curate method.")
        return {
            "messages": [AIMessage(content=msg)],
            "documents": enriched_docs
        }

    def _collect_and_validate_urls(self, clusters: List[Dict]) -> List[str]:
        """
        Collect and validate URLs from clusters, applying limits and deduplication.

        Args:
            clusters: List of dictionaries containing cluster data with URLs

        Returns:
            List of validated, deduplicated URLs, limited to max 20 total
        """
        MAX_URLS_PER_CLUSTER = 5
        MAX_TOTAL_URLS = 20

        def is_valid_url(url: str) -> bool:
            """Validate URL format using regex pattern."""
            url_pattern = re.compile(r'^(https?://)[\w.-]+(:\d+)?(/[\w./-]*)?$')
            return isinstance(url, str) and bool(url_pattern.match(url))

        def process_cluster(cluster: Dict) -> List[str]:
            """Extract and validate URLs from a single cluster."""
            category = cluster.get('category', 'Unknown')
            cluster_urls = cluster.get('urls', [])

            if not isinstance(cluster_urls, list):
                print(f"   ⚠️ [WARNING] Cluster '{category}' has invalid 'urls' format. Skipping cluster.")
                return []

            valid_urls = [url for url in cluster_urls if is_valid_url(url)]

            if not valid_urls:
                print(f"   ⚠️ [WARNING] Cluster '{category}' has no valid URLs after filtering. Skipping cluster.")
                return []

            selected_urls = valid_urls[:MAX_URLS_PER_CLUSTER]
            print(f"   ✅ [DEBUG] Added {len(selected_urls)} valid URLs from cluster '{category}': {selected_urls}")
            return selected_urls

        # Main processing
        print("🔎 [DEBUG] Starting URL collection and validation.")
        collected_urls = []

        for cluster in clusters:
            cluster_urls = process_cluster(cluster)
            collected_urls.extend(cluster_urls)

            if len(collected_urls) >= MAX_TOTAL_URLS:
                print(f"   ✂️ [DEBUG] Reached max URL limit of {MAX_TOTAL_URLS}. Stopping collection.")
                break

        print(f"🔗 [DEBUG] Final collected URLs for enrichment (before deduplication): {collected_urls}")

        # Deduplicate while preserving order
        deduplicated_urls = list(dict.fromkeys(collected_urls[:MAX_TOTAL_URLS]))

        print(f"🔗 [DEBUG] Final collected URLs for enrichment (after deduplication): {deduplicated_urls}")
        print("✅ [DEBUG] URL collection and validation complete.")
        return deduplicated_urls

    def _process_extracted_content(self, extracted_content: Dict, clusters: List[Dict]) -> Dict:
        print("⚙️ [DEBUG] Starting processing of extracted content.")
        enriched_docs = {}
        for item in extracted_content.get("results", []):
            url = item.get("url")
            if not url:
                print(f"   ⚠️ [DEBUG] Skipping extracted item with no URL: {item}")
                continue

            category = self._identify_category(url, clusters)
            print(f"   🏷️ [DEBUG] URL '{url}' categorized as '{category}'.")

            details = {
                "category": category,
                "url": url,
                "raw_content": item.get("raw_content", "")[:100] + "...",
                "extracted_content": item.get("text", "")[:100] + "...",
            }

            details.update(self._category_specific_enrichment(category, item))
            print(f"   ➕ [DEBUG] Enriched details for URL '{url}': {details}")
            enriched_docs[url] = details

        print("✅ [DEBUG] Processing of extracted content complete.")
        return enriched_docs

    def _identify_category(self, url: str, clusters: List[Dict]) -> str:
        print(f"🏷️ [DEBUG] Identifying category for URL '{url}'.")
        for cluster in clusters:
            if url in cluster.get("urls", []):
                print(f"  ✅ [DEBUG] URL '{url}' found in cluster '{cluster.get('category', 'Miscellaneous')}'")
                return cluster.get("category", "Miscellaneous")
        print(f"  ⚠️ [DEBUG] URL '{url}' not found in any cluster. Defaulting to 'Miscellaneous'.")
        return "Miscellaneous"

    def _category_specific_enrichment(self, category: str, item: Dict) -> Dict:
        print(f"✨ [DEBUG] Starting category-specific enrichment for category '{category}'.")
        if category == "Accommodations":
            print(f"  🏨 [DEBUG] Applying enrichment for 'Accommodations' category.")
            return {
                "price_range": self.extract_price_range(item),
                "amenities": self.extract_amenities(item),
                "location": self.extract_location(item),
            }
        elif category == "Activities & Attractions":
            print(f"  🏞️ [DEBUG] Applying enrichment for 'Activities & Attractions' category.")
            return {
                "duration": self.extract_duration(item),
                "best_time": self.extract_best_time(item),
                "booking_required": self.extract_booking_info(item),
            }
        elif category == "Transportation":
            print(f" 🚌 [DEBUG] Applying enrichment for 'Transportation' category.")
            return {
                "transport_type": self.extract_transport_type(item),
                "schedule": self.extract_schedule(item),
                "cost": self.extract_cost(item),
            }
        elif category == "Dining & Food":
            print(f"  🍽️ [DEBUG] Applying enrichment for 'Dining & Food' category.")
            return {
                "cuisine": self.extract_cuisine(item),
                "price_level": self.extract_price_level(item),
                "opening_hours": self.extract_opening_hours(item),
            }
        print(f"  ℹ️ [DEBUG] No specific enrichment for category '{category}'.")
        return {}

    # Dummy enrichment methods to avoid failures
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
        print("🏃 [DEBUG] Starting run method.")
        result = await self.curate(state)
        print("✅ [DEBUG] Completed run method.")
        return result