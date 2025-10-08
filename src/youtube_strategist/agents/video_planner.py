"""Video Planner Agent - Creates video concepts from trends."""

import logging
from typing import Dict, Any
from ..state import AgentState, VideoIdea
from ..llm import OllamaLLM

logger = logging.getLogger(__name__)

class VideoPlanner:
    """Plans video content based on trending topics."""

    def __init__(self, llm: OllamaLLM):
        self.llm = llm

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Generate a video idea from trends."""
        logger.info("📋 Planning video content...")

        if not state.get('trends'):
            logger.error("No trends available for planning")
            return {"messages": ["VideoPlanner: No trends to work with"]}

        # Use the top trend
        top_trend = state['trends'][0]
        niche = state['niche']

        # Generate video idea using LLM
        video_idea = self._generate_video_idea(top_trend.topic, niche, state)

        logger.info(f"✅ Video idea created: {video_idea.title}")
        logger.info(f"   Target: {video_idea.target_audience}")
        logger.info(f"   Duration: {video_idea.estimated_duration}")

        return {
            "video_idea": video_idea,
            "messages": [f"VideoPlanner: Created video idea '{video_idea.title}'"],
            "current_stage": "video_planning"
        }

    def _generate_video_idea(
        self,
        topic: str,
        niche: str,
        state: AgentState
    ) -> VideoIdea:
        """Generate a detailed video idea using LLM."""

        prompt = f"""Create a compelling YouTube video idea for the {niche} niche.

Topic: {topic}
Iteration: {state['iteration_count']}

Generate:

1. An attention-grabbing title (50-70 characters)
2. A detailed description (2-3 sentences)
3. Target audience definition
4. Estimated video duration (e.g., "8-10 minutes")
5. 5-7 relevant keywords
6. A strong hook for the first 10 seconds

Make it engaging, unique, and optimized for YouTube's algorithm."""

        system_prompt = """You are an expert YouTube content strategist. Create video ideas that maximize viewer engagement and retention."""

        try:
            response = self.llm.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                schema={
                    "title": "string",
                    "description": "string",
                    "target_audience": "string",
                    "estimated_duration": "string",
                    "keywords": ["list", "of", "strings"],
                    "hook": "string"
                }
            )

            return VideoIdea(
                title=response.get("title", f"Everything You Need to Know About {topic}"),
                description=response.get("description", f"A comprehensive guide to {topic}"),
                target_audience=response.get("target_audience", f"{niche} enthusiasts"),
                estimated_duration=response.get("estimated_duration", "10-12 minutes"),
                keywords=response.get("keywords", [topic, niche, "tutorial"]),
                hook=response.get("hook", f"Are you struggling with {topic}? Watch this!")
            )

        except Exception as e:
            logger.warning(f"LLM generation failed, using fallback: {e}")
            # Fallback idea
            return VideoIdea(
                title=f"The Ultimate {topic} Guide for {niche}",
                description=f"Learn everything about {topic} in this comprehensive guide tailored for {niche} enthusiasts.",
                target_audience=f"{niche} content creators and enthusiasts",
                estimated_duration="10-12 minutes",
                keywords=[topic, niche, "guide", "tutorial", "tips"],
                hook=f"Want to master {topic}? This video has everything you need!"
            )
