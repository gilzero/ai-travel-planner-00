# backend/nodes/pass_through.py
from ..classes import ResearchState

class PassThroughNode:
    async def run(self, state: ResearchState):
        print("🔄 [DEBUG] PassThroughNode: Passing state along.")
        return state