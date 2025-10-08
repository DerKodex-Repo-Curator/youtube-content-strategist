"""Trend Analyzer Agent - Discovers trending topics."""

import random
import logging
from typing import Dict, Any, List
from ..state import AgentState, TrendData
from ..llm import OllamaLLM

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """Analyzes trends for a given niche."""

    def __init__(self, llm: OllamaLLM):
        self.llm = llm
        # Simulated trending topics database
        self.trend_database = {
            "tech": [
                "AI productivity tools", "Open source alternatives", "Privacy-focused apps",
                "Coding tutorials", "Developer tools", "Tech reviews"
            ],
            "gaming": [
                "Game walkthroughs", "Speedrunning tips", "Indie game reviews",
                "Gaming hardware", "Competitive gaming", "Retro gaming"
            ],
            "education": [
                "Study techniques", "Learning apps", "Career advice",
                "Skill development", "Online courses", "Exam preparation"
            ],
            "lifestyle": [
                "Productivity hacks", "Minimalism", "Health and wellness",
                "Personal finance", "DIY projects", "Travel tips"
            ],
            "general": [
                "Top 10 lists", "How-to guides", "Product reviews",
                "Tutorials", "News and updates", "Behind the scenes"
            ]
        }

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Analyze trends for the given niche."""
        logger.info(f"🔍 Analyzing trends for niche: {state['niche']}")

        niche = state['niche'].lower()
        iteration = state['iteration_count']

        # Get relevant topics for the niche
        topics = self.trend_database.get(niche, self.trend_database["general"])

        # Simulate trend analysis with some randomness
        selected_topics = random.sample(topics, min(3, len(topics)))

        # Use LLM to enrich trend data
        trends = []
        for topic in selected_topics:
            trend_data = self._analyze_topic(topic, niche, iteration)
            trends.append(trend_data)

        # Sort by relevance score
        trends.sort(key=lambda x: x.relevance_score, reverse=True)

        logger.info(f"✅ Found {len(trends)} trending topics")
        for trend in trends:
            logger.info(f"  - {trend.topic} (score: {trend.relevance_score:.2f})")

        return {
            "trends": trends,
            "messages": [f"TrendAnalyzer: Found {len(trends)} trends for {niche}"],
            "current_stage": "trend_analysis"
        }

    def _analyze_topic(self, topic: str, niche: str, iteration: int) -> TrendData:
        """Analyze a single topic using LLM."""
        prompt = f"""Analyze this YouTube content topic for the {niche} niche:

Topic: {topic}

Provide a relevance score (0.0-1.0), estimated search volume, and competition level.
Consider this is iteration {iteration} of content creation."""

        system_prompt = """You are a YouTube trend analyst. Provide realistic assessments of content topics."""

        try:
            response = self.llm.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                schema={
                    "relevance_score": "float between 0.0 and 1.0",
                    "search_volume": "integer (estimated monthly searches)",
                    "competition": "string: low, medium, or high"
                }
            )

            return TrendData(
                topic=topic,
                relevance_score=min(1.0, max(0.0, float(response.get("relevance_score", 0.7)))),
                search_volume=int(response.get("search_volume", random.randint(1000, 50000))),
                competition=response.get("competition", "medium")
            )
        except Exception as e:
            logger.warning(f"LLM analysis failed, using defaults: {e}")
            # Fallback to simulated data
            return TrendData(
                topic=topic,
                relevance_score=random.uniform(0.6, 0.95),
                search_volume=random.randint(5000, 50000),
                competition=random.choice(["low", "medium", "high"])
            )
