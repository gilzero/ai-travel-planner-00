"""
@fileoverview This module defines the ClusterNode class, which is responsible for clustering travel information into meaningful categories.
@filepath backend/nodes/cluster.py
"""

from langchain_core.messages import AIMessage
from langchain_anthropic import ChatAnthropic
from typing import List, Dict, Any
import json
import re  # Import the regular expression module
from ..classes import ResearchState


class ClusterNode:
    def __init__(self):
        self.model = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            temperature=0
        )
        print("🛠️ [DEBUG] ClusterNode initialized.")

    async def cluster(self, state: ResearchState):
        print("🚀 [DEBUG] Starting cluster method.")
        preferences = state['preferences']
        documents = state.get('documents', {})

        print(f"⚙️ [DEBUG] Preferences: {preferences}")
        print(f"📚 [DEBUG] Documents passed to cluster (count: {len(documents)}):")
        for url, doc in documents.items():
            print(f"   🔗 [DEBUG] URL: {url}, Content: {doc.get('content', '')[:50]}...")

        unique_docs = []
        seen_urls = set()
        for url, doc in documents.items():
            if url not in seen_urls:
                unique_docs.append({'url': url, 'content': doc.get('content', '')})
                seen_urls.add(url)

        print(f"✅ [DEBUG] Unique documents extracted (count: {len(unique_docs)}):")
        for doc in unique_docs:
            print(f"   🔗 [DEBUG] URL: {doc['url']}, Content: {doc['content'][:50]}...")

        docs = unique_docs[:25]
        print(f"✂️ [DEBUG] Top 25 unique documents selected for clustering (count: {len(docs)}).")
        for doc in docs:
            print(f"   🔗 [DEBUG] URL: {doc['url']}, Content: {doc['content'][:50]}...")

        prompt = self._generate_prompt(preferences, docs)
        print(f"📝 [DEBUG] Generated Prompt:\n{prompt}")

        messages = [
            ("system", "You are a travel planning expert organizing research results."),
            ("human", prompt)
        ]

        msg = ""
        clusters = {"clusters": []}
        try:
            print("🤖 [DEBUG] Sending prompt to AI model...")
            response = await self.model.ainvoke(messages)
            print("✅ [DEBUG] Received response from AI model.")
            print(f"📦 [DEBUG] AI Response Content: {response.content}")

            # Remove any text before the JSON object
            json_start = response.content.find('{')
            if json_start != -1:
                json_string = response.content[json_start:]
                print(f"✂️ [DEBUG] Extracted JSON string (start): {json_string[:100]}...")
            else:
                print(f"🔥 [ERROR] No JSON object found in response: {response.content}")
                raise json.JSONDecodeError("No JSON object found in response", response.content, 0)

            # Remove any text after the JSON object
            json_end = self._find_json_end(json_string)
            if json_end != -1:
                json_string = json_string[:json_end + 1]
                print(f"✂️ [DEBUG] Extracted JSON string (end): {json_string[:100]}...")
            else:
                print(f"🔥 [ERROR] No valid JSON end found in response: {json_string}")
                raise json.JSONDecodeError("No valid JSON end found in response", json_string, 0)

            clusters = json.loads(json_string)
            print("✨ [DEBUG] JSON parsed successfully.")
            self._validate_clusters(clusters)
            print("✅ [DEBUG] Clusters validated successfully.")

            msg += "📂 Organized travel information into categories:\n"
            for cluster in clusters['clusters']:
                msg += f"   • {cluster['category']}: {len(cluster['urls'])} sources\n"
            print(f"💬 [DEBUG] Generated user message: {msg}")
        except json.JSONDecodeError as e:
            msg = f"🚨 Error: Failed to parse clustering results from the model. Error: {str(e)}"
            print(f"🔥 [ERROR] {msg}")
        except ValueError as e:
            msg = f"🚨 Error: {str(e)}"
            print(f"🔥 [ERROR] {msg}")
        except Exception as e:
            msg = f"🚨 Error during clustering: {str(e)}"
            print(f"🔥 [ERROR] {msg}")

        print(f"🗂️  [DEBUG] Final Clusters: {clusters.get('clusters', [])}")
        print("🚪 [DEBUG] Exiting cluster method.")
        return {"messages": [AIMessage(content=msg)], "document_clusters": clusters.get('clusters', [])}

    def _find_json_end(self, json_string):
        """Find the end of the JSON object, handling nested structures."""
        stack = []
        for i, char in enumerate(json_string):
            if char == '{':
                stack.append('{')
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack:
                        return i
                else:
                    return -1  # Invalid JSON
        return -1  # No valid JSON end found

    async def choose_cluster(self, state: ResearchState):
        print("🗂️ [DEBUG] Starting choose_cluster method.")
        clusters = state['document_clusters']
        print(f"🗂️ [DEBUG] Document clusters passed to choose_cluster: {clusters}")
        chosen_cluster = 0  # Default to first cluster
        msg = "✓ Organized travel information by category."

        print(f"🎯 [DEBUG] Chosen Cluster Index: {chosen_cluster}")
        print("🚪 [DEBUG] Exiting choose_cluster method.")
        return {"messages": [AIMessage(content=msg)], "chosen_cluster": chosen_cluster}

    async def run(self, state: ResearchState, websocket=None):
        print("🏃 [DEBUG] Starting run method.")
        if websocket:
            await websocket.send_text("🔄 Organizing travel information...")
            print("📡 [DEBUG] Sent websocket message.")

        cluster_result = await self.cluster(state)
        state['document_clusters'] = cluster_result['document_clusters']
        print(f"✅ [DEBUG] Cluster method completed with results: {cluster_result}")

        choose_result = await self.choose_cluster(state)
        print(f"✅ [DEBUG] choose_cluster method completed with results: {choose_result}")

        print("🚪 [DEBUG] Exiting run method.")
        return {
            'chosen_cluster': choose_result['chosen_cluster'],
            'document_clusters': state['document_clusters']
        }

    def _generate_prompt(self, preferences, docs):
        prompt = f"""
        We're planning a trip to {preferences.destination} and have gathered various travel-related documents.
        Your task is to categorize these documents into meaningful clusters for trip planning.

        ### Trip Details
        - Destination: {preferences.destination}
        - Style: {preferences.travel_style}
        - Activities: {', '.join(preferences.preferred_activities)}
        - Budget Range: ${preferences.budget_min} - ${preferences.budget_max}

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

        Format clusters as a valid JSON object:
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
        return prompt

    def _validate_clusters(self, clusters: Dict[str, Any]):
        print("🔎 [DEBUG] Starting cluster validation.")
        if "clusters" not in clusters:
            print(f"🔥 [ERROR] Validation Error: Missing 'clusters' key in response: {clusters}")
            raise ValueError("Invalid clustering result: Missing 'clusters' key.")
        if not isinstance(clusters["clusters"], list):
            print(f"🔥 [ERROR] Validation Error: 'clusters' is not a list: {clusters['clusters']}")
            raise ValueError("Invalid clustering result: 'clusters' must be a list.")
        for i, cluster in enumerate(clusters["clusters"]):
            print(f"🔍 [DEBUG] Validating cluster {i}: {cluster}")
            if not isinstance(cluster.get("category"), str):
                print(f"🔥 [ERROR] Validation Error: Invalid cluster format for cluster {i}: 'category' must be a string: {cluster}")
                raise ValueError(f"Invalid cluster format: 'category' must be a string in cluster {i}.")
            if not isinstance(cluster.get("urls"), list):
                print(f"🔥 [ERROR] Validation Error: Invalid cluster format for cluster {i}: 'urls' must be a list: {cluster}")
                raise ValueError(f"Invalid cluster format: 'urls' must be a list in cluster {i}.")
            if not all(isinstance(url, str) for url in cluster["urls"]):
                print(f"🔥 [ERROR] Validation Error: Invalid cluster format for cluster {i}: 'urls' must be a list of strings: {cluster['urls']}")
                raise ValueError(f"Invalid cluster format: 'urls' must be a list of strings in cluster {i}.")
            if len(cluster["urls"]) == 0:
                print(f"⚠️ [WARNING] Cluster '{cluster['category']}' has no valid URLs.")
        print("✅ [DEBUG] Cluster validation complete.")