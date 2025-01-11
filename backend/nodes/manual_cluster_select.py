# In your node file
from langchain_core.messages import AIMessage
from langgraph.errors import NodeInterrupt
from ..classes import ResearchState

class ManualSelectionNode:
    async def manual_cluster_selection(self, state: ResearchState, websocket):
        clusters = state['document_clusters']
        print(f"🔍 [DEBUG] Retrieved {len(clusters)} clusters for manual selection.")
        msg = "Multiple clusters were identified. Please review the options and select the correct cluster for the target company.\n\n"
        msg += "Enter '0' if none of these clusters match the target company.\n"

        if websocket:
            print("🌐 [DEBUG] WebSocket connection established. Sending cluster options to the frontend.")
            await websocket.send_text(msg)

            # Wait for user selection from WebSocket
            while True:
                try:
                    selection_text = await websocket.receive_text()
                    print(f"📨 [DEBUG] Received selection input: {selection_text}")
                    selected_cluster_index = int(selection_text) - 1

                    if selected_cluster_index == -1:
                        msg = "No suitable cluster found. Trying to cluster again.\n"
                        print("🔄 [DEBUG] No suitable cluster selected. Re-clustering initiated.")
                        await websocket.send_text(msg)
                        return {"messages": [AIMessage(content=msg, is_manual_selection=True)], "chosen_cluster": selected_cluster_index}
                    elif 0 <= selected_cluster_index < len(clusters):
                        chosen_cluster = clusters[selected_cluster_index]
                        msg = f"You selected cluster '{chosen_cluster.company_name}' as the correct cluster."
                        print(f"✅ [DEBUG] Cluster '{chosen_cluster.company_name}' selected as the correct cluster.")
                        await websocket.send_text(msg)
                        return {"messages": [AIMessage(content=msg, is_manual_selection=True)], "chosen_cluster": selected_cluster_index}
                    else:
                        print("⚠️ [WARNING] Invalid cluster selection. Prompting user for valid input.")
                        await websocket.send_text("Invalid choice. Please enter a number corresponding to the listed clusters or '0' to re-cluster.")
                except ValueError:
                    print("❌ [ERROR] Invalid input received. Prompting user for valid number.")
                    await websocket.send_text("Invalid input. Please enter a valid number.")
        else:
            print("🛠️ [DEBUG] No WebSocket connection. Manual selection needed in studio.")
            msg = "Manual selection needed, trying to cluster again.\n"
            return {"messages": [AIMessage(content=msg, is_manual_selection=True)], "chosen_cluster": -1}

    async def run(self, state: ResearchState, websocket=None):
        print("🚀 [DEBUG] Running manual cluster selection process.")
        return await self.manual_cluster_selection(state, websocket)
