from langchain_core.messages import AIMessage
from langchain_anthropic import ChatAnthropic
from typing import List, Dict, Any
import json

from ..classes import ResearchState


class ClusterNode:
    def __init__(self):
        self.model = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0
        )

    async def cluster(self, state: ResearchState):
        preferences = state['preferences']
        initial_data = state['initial_data']
        documents = state.get('documents', {})

        # Extract unique documents
        unique_docs = []
        seen_urls = set()
        for url, doc in documents.items():
            if url not in seen_urls:
                unique_docs.append({'url': url, 'content': doc.get('content', '')})
                seen_urls.add(url)

        # Limit to first 25 documents for processing
        docs = unique_docs[:25]

        # LLM prompt for travel-specific clustering
        prompt = self._generate_prompt(preferences, initial_data, docs)

        # Get clustering results from LLM
        messages = [
            ("system", "You are a travel planning expert organizing research results."),
            ("human", prompt)
        ]

        msg = ""
        clusters = {"clusters": []}
        try:
            response = await self.model.ainvoke(messages)
            clusters = json.loads(response.content)

            # Validate clusters
            self._validate_clusters(clusters)

            # Summarize the results
            msg += "📂 Organized travel information into categories:\n"
            for cluster in clusters['clusters']:
                msg += f"   • {cluster['category']}: {len(cluster['urls'])} sources\n"

        except json.JSONDecodeError:
            msg = "Error: Failed to parse clustering results from the model."
        except ValueError as e:
            msg = f"Error: {str(e)}"
        except Exception as e:
            msg = f"Error during clustering: {str(e)}"

        return {"messages": [AIMessage(content=msg)], "document_clusters": clusters.get('clusters', [])}

    async def choose_cluster(self, state: ResearchState):
        """Automatically select relevant clusters based on search criteria."""
        clusters = state['document_clusters']

        # Initialize result with all clusters included
        chosen_cluster = 0  # Default to first cluster
        msg = "✓ Organized travel information by category."

        return {"messages": [AIMessage(content=msg)], "chosen_cluster": chosen_cluster}

    async def run(self, state: ResearchState, websocket):
        if websocket:
            await websocket.send_text("🔄 Organizing travel information...")

        cluster_result = await self.cluster(state)
        state['document_clusters'] = cluster_result['document_clusters']
        choose_result = await self.choose_cluster(state)

        result = {
            'chosen_cluster': choose_result['chosen_cluster'],
            'document_clusters': state['document_clusters']
        }

        return result

    def _generate_prompt(self, preferences, initial_data, docs):
        """Generate the LLM prompt for clustering."""
        return f"""
        We're planning a trip to {preferences.destination} and have gathered various travel-related documents.
        Your task is to categorize these documents into meaningful clusters for trip planning.

        ### Trip Details
        - Destination: {preferences.destination}
        - Style: {preferences.travel_style}
        - Activities: {', '.join(preferences.preferred_activities)}
        - Budget Range: ${preferences.budget_min} - ${preferences.budget_max}

        ### Initial Context
        {json.dumps(initial_data, indent=2)}

        ### Retrieved Documents
        {[{'url': doc['url'], 'content': doc['content']} for doc in docs]}

        ### Clustering Instructions
        Group documents into these categories:
        1. Accommodations
        2. Activities & Attractions
        3. Transportation
        4. Dining & Food
        5. Practical Information
        6. Miscellaneous

        For each document, consider:
        - Relevance to trip dates and preferences
        - Price range alignment
        - Activity type match
        - Location relevance
        - Content freshness

        Format clusters as:
        {{
            "clusters": [
                {{
                    "category": "Category Name",
                    "description": "Brief description of this category",
                    "urls": ["url1", "url2"]
                }}
            ]
        }}
        """

    def _validate_clusters(self, clusters: Dict[str, Any]):
        """Validate the structure of the clusters."""
        if "clusters" not in clusters or not isinstance(clusters["clusters"], list):
            raise ValueError("Invalid clustering result: 'clusters' must be a list.")

        for cluster in clusters["clusters"]:
            if not isinstance(cluster.get("category"), str):
                raise ValueError("Invalid cluster format: 'category' must be a string.")
            if not isinstance(cluster.get("description"), str):
                raise ValueError("Invalid cluster format: 'description' must be a string.")
            if not isinstance(cluster.get("urls"), list) or not all(isinstance(url, str) for url in cluster["urls"]):
                raise ValueError("Invalid cluster format: 'urls' must be a list of strings.")
