"""
@fileoverview This module defines the Graph class for managing the workflow
              of the research process, including node initialization and
              workflow execution.
@filepath backend/graph.py
"""

from langchain_core.messages import SystemMessage, AIMessage
from functools import partial
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from backend.classes.research_state import ResearchState, InputState, OutputState
from backend.nodes import (
    InitialGroundingNode, SubQuestionsNode, ResearcherNode, ClusterNode,
    ManualSelectionNode, EnrichDocsNode, GenerateNode, EvaluationNode,
    PublishNode
)
from backend.utils.routing_helper import (
    route_based_on_cluster, route_after_manual_selection,
    should_continue_research, route_based_on_evaluation
)

class Graph:
    """
    Manages the workflow of the research process, including node
    initialization and workflow execution.
    """
    def __init__(self, output_format="pdf", websocket=None):
        """
        Initialize the Graph with output format and optional WebSocket.

        Args:
            output_format (str): The format for output, default is "pdf".
            websocket: Optional WebSocket for real-time communication.
        """
        self.websocket = websocket
        self.output_format = output_format
        self.memory = MemorySaver()
        self.messages = [
            SystemMessage(content="You are an expert researcher ready to begin "
                                  "the information gathering process.")
        ]
        self.state = None  # State will be set dynamically with preferences

        print(f"🔧 [INIT] Graph initialized with output format: {self.output_format}")

        # Initialize nodes
        self._initialize_nodes()

        # Setup workflow
        self._setup_workflow()

    def _initialize_nodes(self):
        """Initialize all the graph nodes."""
        self.initial_search_node = InitialGroundingNode()
        self.sub_questions_node = SubQuestionsNode()
        self.researcher_node = ResearcherNode()
        self.cluster_node = ClusterNode()
        self.manual_selection_node = ManualSelectionNode()
        self.curate_node = EnrichDocsNode()
        self.generate_node = GenerateNode()
        self.evaluation_node = EvaluationNode()
        self.publish_node = PublishNode()

        print("🔄 [NODES] All graph nodes initialized.")

    def _setup_workflow(self):
        """Setup the workflow graph."""
        self.workflow = StateGraph(ResearchState, input=InputState,
                                   output=OutputState)

        # Add nodes to workflow
        self.workflow.add_node("initial_grounding", self.initial_search_node.run)
        self.workflow.add_node("sub_questions_gen", self.sub_questions_node.run)
        self.workflow.add_node("research", self.researcher_node.run)
        self.workflow.add_node("cluster", self.curried_node(self.cluster_node.run))
        self.workflow.add_node("manual_cluster_selection",
                               self.curried_node(self.manual_selection_node.run))
        self.workflow.add_node("enrich_docs", self.curate_node.run)
        self.workflow.add_node("generate_report",
                               self.curried_node(self.generate_node.run))
        self.workflow.add_node("eval_report", self.evaluation_node.run)
        self.workflow.add_node("publish", self.publish_node.run)

        print("🔗 [WORKFLOW] Nodes added to workflow.")

        # Add edges to workflow
        self.workflow.add_edge("initial_grounding", "sub_questions_gen")
        self.workflow.add_edge("sub_questions_gen", "research")
        self.workflow.add_edge("research", "cluster")
        self.workflow.add_conditional_edges("cluster", route_based_on_cluster)
        self.workflow.add_conditional_edges("manual_cluster_selection",
                                            route_after_manual_selection)
        self.workflow.add_conditional_edges("enrich_docs", should_continue_research)
        self.workflow.add_edge("generate_report", "eval_report")
        self.workflow.add_conditional_edges("eval_report", route_based_on_evaluation)

        print("🔗 [WORKFLOW] Edges added to workflow.")

        # Define entry and exit points
        self.workflow.set_entry_point("initial_grounding")
        self.workflow.set_finish_point("publish")

        print("🚀 [WORKFLOW] Workflow setup complete with entry and exit points defined.")

    def initialize_state(self, preferences):
        """
        Initialize the ResearchState with given preferences.

        Args:
            preferences: User preferences for the research process.
        """
        self.state = ResearchState(
            preferences=preferences,
            output_format=self.output_format,
            messages=self.messages
        )
        print(f"🗺️ [STATE] ResearchState initialized with preferences: {preferences}")

    async def run(self, progress_callback=None):
        """
        Run the workflow asynchronously.

        Args:
            progress_callback: Optional callback for progress updates.
        """
        if not self.state:
            raise ValueError("State has not been initialized. Call "
                             "`initialize_state` with preferences first.")

        print("🏃 [RUN] Starting workflow execution.")

        # Compile the workflow
        graph = self.workflow.compile(checkpointer=self.memory)
        thread = {"configurable": {"thread_id": "2"}}

        print("🔧 [COMPILE] Workflow compiled.")

        # Execute the graph and send progress updates
        async for s in graph.astream(self.state, thread, stream_mode="values"):
            if "messages" in s and s["messages"]:
                message = s["messages"][-1]
                output_message = message.content if hasattr(message, "content") else str(message)
                print(f"📩 [MESSAGE] New message: {output_message}")
                if progress_callback and not getattr(message, "is_manual_selection", False):
                    await progress_callback(output_message)

        print("✅ [RUN] Workflow execution completed.")

    def curried_node(self, node_run_method):
        """
        Wrapper for node methods to include WebSocket.

        Args:
            node_run_method: The method to run for the node.
        """
        async def wrapper(state):
            print(f"🔄 [NODE] Running node with state: {state}")
            return await node_run_method(state, self.websocket)
        return wrapper

    def compile(self):
        """Compile the graph for LangGraph Studio."""
        thread = {"configurable": {"thread_id": "2"}}
        print("🔧 [COMPILE] Compiling graph for LangGraph Studio.")
        return self.workflow.compile(checkpointer=self.memory)
