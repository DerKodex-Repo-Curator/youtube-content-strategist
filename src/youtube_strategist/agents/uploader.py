"""Uploader Agent - Simulates video upload process."""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Any
import uuid
from ..state import AgentState, UploadResult

logger = logging.getLogger(__name__)

class Uploader:
    """Simulates uploading video to YouTube."""

    def __init__(self, output_dir: str = "output/uploads"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Simulate video upload."""
        logger.info("📤 Uploading video...")

        video_idea = state.get('video_idea')
        script = state.get('script')
        thumbnail = state.get('thumbnail')

        if not all([video_idea, script, thumbnail]):
            logger.error("Missing required components for upload")
            return {"messages": ["Uploader: Missing video components"]}

        # Simulate upload process
        upload_result = self._simulate_upload(video_idea, script, thumbnail)

        logger.info(f"✅ Video uploaded successfully!")
        logger.info(f"   Video ID: {upload_result.video_id}")
        logger.info(f"   Status: {upload_result.status}")

        return {
            "upload_result": upload_result,
            "messages": [f"Uploader: Video '{video_idea.title}' uploaded (ID: {upload_result.video_id})"],
            "current_stage": "upload_complete"
        }

    def _simulate_upload(self, video_idea, script, thumbnail) -> UploadResult:
        """Simulate the upload process and save metadata."""

        # Generate unique video ID
        video_id = f"VID_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now().isoformat()

        # Create upload metadata
        metadata = {
            "video_id": video_id,
            "title": video_idea.title,
            "description": video_idea.description,
            "keywords": video_idea.keywords,
            "duration": script.estimated_length,
            "thumbnail_path": thumbnail.filepath,
            "upload_timestamp": timestamp,
            "status": "published",
            "script_sections": len(script.main_content),
            "target_audience": video_idea.target_audience
        }

        # Save metadata to file
        filename = f"upload_{video_id}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.debug(f"Upload metadata saved to {filepath}")

        return UploadResult(
            video_id=video_id,
            title=video_idea.title,
            status="published",
            upload_timestamp=timestamp
        )
