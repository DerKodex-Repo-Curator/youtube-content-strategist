"""Analytics Monitor Agent - Tracks performance and provides feedback."""

import logging
import random
from typing import Dict, Any
from ..state import AgentState, AnalyticsData

logger = logging.getLogger(__name__)

class AnalyticsMonitor:
    """Monitors video analytics and triggers feedback loop."""

    def __init__(
        self,
        performance_threshold: float = 0.6,
        min_ctr: float = 0.03,
        min_watch_time: float = 0.5
    ):
        self.performance_threshold = performance_threshold
        self.min_ctr = min_ctr
        self.min_watch_time = min_watch_time

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Monitor analytics and determine if feedback is needed."""
        logger.info("📊 Analyzing video performance...")

        upload_result = state.get('upload_result')
        if not upload_result:
            logger.error("No upload result available for analytics")
            return {"messages": ["AnalyticsMonitor: No video to analyze"]}

        # Simulate analytics data
        analytics = self._simulate_analytics(
            upload_result.video_id,
            state['iteration_count']
        )

        # Calculate performance score
        performance_score = self._calculate_performance_score(analytics)
        analytics.performance_score = performance_score

        # Determine if feedback loop is needed
        feedback_needed = performance_score < self.performance_threshold

        logger.info(f"✅ Analytics complete for {upload_result.video_id}")
        logger.info(f"   Views: {analytics.views:,}")
        logger.info(f"   CTR: {analytics.ctr:.2%}")
        logger.info(f"   Avg Watch Time: {analytics.watch_time_avg:.1f}%")
        logger.info(f"   Performance Score: {performance_score:.2f}")

        if feedback_needed:
            logger.warning(f"⚠️  Performance below threshold ({self.performance_threshold})")
            logger.info("🔄 Triggering feedback loop...")
        else:
            logger.info("✨ Performance meets expectations!")

        return {
            "analytics": analytics,
            "feedback_needed": feedback_needed,
            "messages": [
                f"AnalyticsMonitor: Performance score {performance_score:.2f} "
                f"({'NEEDS IMPROVEMENT' if feedback_needed else 'GOOD'})"
            ],
            "current_stage": "analytics_complete"
        }

    def _simulate_analytics(self, video_id: str, iteration: int) -> AnalyticsData:
        """Simulate realistic analytics data."""

        # Simulate improvement over iterations
        base_performance = 0.5 + (iteration * 0.1)
        variance = 0.2

        # Generate metrics with some randomness
        views = random.randint(1000, 50000)
        ctr = max(0.01, min(0.15, random.gauss(base_performance * 0.08, 0.02)))
        watch_time = max(0.2, min(0.9, random.gauss(base_performance * 0.7, 0.15)))

        likes = int(views * random.uniform(0.02, 0.08))
        comments = int(views * random.uniform(0.001, 0.01))

        return AnalyticsData(
            video_id=video_id,
            views=views,
            ctr=round(ctr, 4),
            watch_time_avg=round(watch_time * 100, 2),  # Convert to percentage
            likes=likes,
            comments=comments,
            performance_score=0.0  # Will be calculated
        )

    def _calculate_performance_score(self, analytics: AnalyticsData) -> float:
        """Calculate overall performance score (0-1)."""

        # Weighted scoring
        weights = {
            'ctr': 0.3,
            'watch_time': 0.4,
            'engagement': 0.3
        }

        # Normalize CTR (target: 5%)
        ctr_score = min(1.0, analytics.ctr / 0.05)

        # Normalize watch time (target: 60%)
        watch_time_score = min(1.0, (analytics.watch_time_avg / 100) / 0.6)

        # Normalize engagement (likes + comments relative to views)
        engagement_rate = (analytics.likes + analytics.comments * 5) / analytics.views
        engagement_score = min(1.0, engagement_rate / 0.05)

        # Calculate weighted score
        performance_score = (
            weights['ctr'] * ctr_score +
            weights['watch_time'] * watch_time_score +
            weights['engagement'] * engagement_score
        )

        return round(performance_score, 3)
