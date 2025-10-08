"""State models for the YouTube Content Strategist pipeline."""

from typing import List, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field
import operator

class TrendData(BaseModel):
    """Trending topic data."""
    topic: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    search_volume: int
    competition: str # "low", "medium", "high"

class VideoIdea(BaseModel):
    """Video idea with metadata."""
    title: str
    description: str
    target_audience: str
    estimated_duration: str
    keywords: List[str]
    hook: str

class Script(BaseModel):
    """Video script with sections."""
    title: str
    intro: str
    main_content: List[str]
    call_to_action: str
    outro: str
    estimated_length: int # in seconds
    keywords_used: List[str]

class ThumbnailData(BaseModel):
    """Thumbnail generation data."""
    filepath: str
    text_overlay: str
    primary_color: str
    design_concept: str

class UploadResult(BaseModel):
    """Upload simulation result."""
    video_id: str
    title: str
    status: str
    upload_timestamp: str

class AnalyticsData(BaseModel):
    """Video analytics data."""
    video_id: str
    views: int
    ctr: float = Field(ge=0.0, le=1.0) # Click-through rate
    watch_time_avg: float
    likes: int
    comments: int
    performance_score: float = Field(ge=0.0, le=1.0)

class AgentState(TypedDict):
    """State shared across all agents in the pipeline."""
    # Input
    niche: str
    iteration_count: int
    # Agent outputs
    trends: List[TrendData]
    video_idea: Optional[VideoIdea]
    script: Optional[Script]
    thumbnail: Optional[ThumbnailData]
    upload_result: Optional[UploadResult]
    analytics: Optional[AnalyticsData]
    # Control flow
    feedback_needed: bool
    messages: Annotated[List[str], operator.add]  # For logging
    max_iterations: int
    current_stage: str
