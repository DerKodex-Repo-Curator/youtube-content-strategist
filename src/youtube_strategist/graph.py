"""LangGraph workflow for YouTube Content Strategist."""

import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from .state import AgentState
from .agents.trend_analyzer import TrendAnalyzer
from .agents.video_planner import VideoPlanner
from .agents.script_writer import ScriptWriter
from .agents.thumbnail_gen import ThumbnailGenerator
from .agents.uploader import Uploader
from .agents.analytics_monitor import AnalyticsMonitor
from .llm import OllamaLLM

logger = logging.getLogger(__name__)

class YouTubeContentGraph:
    """LangGraph-based workflow for YouTube content creation."""

    def __init__(
        self,
        model: str = "mistral:7b",
        max_iterations: int = 3,
        performance_threshold: float = 0.6
    ):
        self.llm = OllamaLLM(model=model)
        self.max_iterations = max_iterations
        self.performance_threshold = performance_threshold

        # Initialize agents
        self.trend_analyzer = TrendAnalyzer(self.llm)
        self.video_planner = VideoPlanner(self.llm)
        self.script_writer = ScriptWriter(self.llm)
        self.thumbnail_gen = ThumbnailGenerator(self.llm)
        self.uploader = Uploader()
        self.analytics_monitor = AnalyticsMonitor(
            performance_threshold=performance_threshold
        )

        # Build graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes (agents)
        workflow.add_node("trend_analyzer", self.trend_analyzer)
        workflow.add_node("video_planner", self.video_planner)
        workflow.add_node("script_writer", self.script_writer)
        workflow.add_node("thumbnail_gen", self.thumbnail_gen)
        workflow.add_node("uploader", self.uploader)
        workflow.add_node("analytics_monitor", self.analytics_monitor)

        # Set entry point
        workflow.set_entry_point("trend_analyzer")

        # Add edges (workflow)
        workflow.add_edge("trend_analyzer", "video_planner")
        workflow.add_edge("video_planner", "script_writer")
        workflow.add_edge("script_writer", "thumbnail_gen")
        workflow.add_edge("thumbnail_gen", "uploader")
        workflow.add_edge("uploader", "analytics_monitor")

        # Add conditional edge for feedback loop
        workflow.add_conditional_edges(
            "analytics_monitor",
            self._should_continue,
            {
                "continue": "trend_analyzer",  # Feedback loop
                "end": END
            }
        )

        return workflow.compile()

    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """Determine if feedback loop should continue."""

        feedback_needed = state.get('feedback_needed', False)
        iteration_count = state.get('iteration_count', 0)
        max_iterations = state.get('max_iterations', self.max_iterations)

        if feedback_needed and iteration_count < max_iterations:
            logger.info(f"🔄 Feedback loop: Iteration {iteration_count + 1}/{max_iterations}")
            return "continue"
        else:
            if iteration_count >= max_iterations:
                logger.info(f"⏹️  Max iterations ({max_iterations}) reached")
            else:
                logger.info("✅ Performance acceptable, pipeline complete")
            return "end"

    def run(self, niche: str, max_iterations: int = None) -> AgentState:
        """Run the complete workflow."""

        if max_iterations is None:
            max_iterations = self.max_iterations

        logger.info("=" * 60)
        logger.info("🚀 Starting YouTube Content Strategist Pipeline")
        logger.info(f"   Niche: {niche}")
        logger.info(f"   Max Iterations: {max_iterations}")
        logger.info("=" * 60)

        # Initialize state
        initial_state: AgentState = {
            "niche": niche,
            "iteration_count": 0,
            "trends": [],
            "video_idea": None,
            "script": None,
            "thumbnail": None,
            "upload_result": None,
            "analytics": None,
            "feedback_needed": False,
            "messages": [],
            "max_iterations": max_iterations,
            "current_stage": "initialized"
        }

        # Run the graph
        final_state = None
        for state in self.graph.stream(initial_state):
            # Update iteration count when we loop back
            if "trend_analyzer" in state and final_state is not None:
                state["trend_analyzer"]["iteration_count"] = \
                    final_state.get("iteration_count", 0) + 1

            final_state = next(iter(state.values()))

            # Log progress
            stage = final_state.get("current_stage", "unknown")
            logger.debug(f"Stage: {stage}")

        logger.info("=" * 60)
        logger.info("✅ Pipeline execution complete!")
        logger.info("=" * 60)

        return final_state

    def get_summary(self, state: AgentState) -> dict:
        """Get a summary of the pipeline execution."""

        return {
            "niche": state.get("niche"),
            "iterations": state.get("iteration_count", 0),
            "final_video_title": state.get("video_idea").title if state.get("video_idea") else None,
            "video_id": state.get("upload_result").video_id if state.get("upload_result") else None,
            "performance_score": state.get("analytics").performance_score if state.get("analytics") else None,
            "views": state.get("analytics").views if state.get("analytics") else None,
            "ctr": state.get("analytics").ctr if state.get("analytics") else None,
            "thumbnail_path": state.get("thumbnail").filepath if state.get("thumbnail") else None,
            "messages": state.get("messages", [])
        }
