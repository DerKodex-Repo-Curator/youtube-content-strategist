"""Thumbnail Generator Agent - Creates video thumbnails."""

import logging
import os
from datetime import datetime
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont
import random
from ..state import AgentState, ThumbnailData
from ..llm import OllamaLLM

logger = logging.getLogger(__name__)

class ThumbnailGenerator:
    """Generates video thumbnails."""

    def __init__(self, llm: OllamaLLM, output_dir: str = "output/thumbnails"):
        self.llm = llm
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Color palettes for different niches
        self.color_palettes = {
            "tech": ["#0066CC", "#00A8E8", "#FF6B35", "#00C9A7"],
            "gaming": ["#FF0050", "#7B2CBF", "#00D9FF", "#FFD60A"],
            "education": ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"],
            "lifestyle": ["#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9"],
            "general": ["#E63946", "#457B9D", "#F4A261", "#2A9D8F"]
        }

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Generate a thumbnail for the video."""
        logger.info("🎨 Generating thumbnail...")

        video_idea = state.get('video_idea')
        if not video_idea:
            logger.error("No video idea available for thumbnail")
            return {"messages": ["ThumbnailGenerator: No video idea to work with"]}

        # Design thumbnail concept using LLM
        design_concept = self._design_thumbnail_concept(video_idea, state['niche'])

        # Generate actual thumbnail image
        thumbnail_path = self._create_thumbnail_image(
            video_idea.title,
            design_concept,
            state['niche']
        )

        thumbnail_data = ThumbnailData(
            filepath=thumbnail_path,
            text_overlay=design_concept['text_overlay'],
            primary_color=design_concept['primary_color'],
            design_concept=design_concept['concept']
        )

        logger.info(f"✅ Thumbnail saved: {thumbnail_path}")
        logger.info(f"   Concept: {design_concept['concept']}")

        return {
            "thumbnail": thumbnail_data,
            "messages": [f"ThumbnailGenerator: Created thumbnail at {thumbnail_path}"],
            "current_stage": "thumbnail_generation"
        }

    def _design_thumbnail_concept(self, video_idea, niche: str) -> Dict[str, str]:
        """Design thumbnail concept using LLM."""

        prompt = f"""Design a compelling YouTube thumbnail for this video:

Title: {video_idea.title}
Niche: {niche}

Provide:

1. Primary text overlay (3-5 words, attention-grabbing)
2. Design concept description
3. Emotional tone (excited, curious, shocked, etc.)

Focus on high CTR (click-through rate) design principles."""

        system_prompt = """You are a YouTube thumbnail designer expert. Create designs that:

- Stand out in crowded feeds
- Are readable on mobile devices
- Create curiosity and urgency
- Use strong contrast and bold text"""
        try:
            response = self.llm.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                schema={
                    "text_overlay": "string (3-5 words)",
                    "concept": "string (design description)",
                    "emotional_tone": "string"
                }
            )

            # Select color based on niche
            colors = self.color_palettes.get(niche.lower(), self.color_palettes["general"])
            primary_color = random.choice(colors)

            return {
                "text_overlay": response.get("text_overlay", " ".join(video_idea.title.split()[0:3])),
                "concept": response.get("concept", "Bold text with high contrast background"),
                "emotional_tone": response.get("emotional_tone", "excited"),
                "primary_color": primary_color
            }

        except Exception as e:
            logger.warning(f"LLM thumbnail design failed, using defaults: {e}")
            colors = self.color_palettes.get(niche.lower(), self.color_palettes["general"])
            return {
                "text_overlay": " ".join(video_idea.title.split()[0:3]).upper(),
                "concept": "Bold text centered with gradient background",
                "emotional_tone": "excited",
                "primary_color": random.choice(colors)
            }

    def _create_thumbnail_image(
        self,
        title: str,
        design_concept: Dict[str, str],
        niche: str
    ) -> str:
        """Create actual thumbnail image using PIL."""
        # YouTube thumbnail dimensions
        width, height = 1280, 720

        # Create image with gradient background
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)

        # Create gradient background
        primary_color = self._hex_to_rgb(design_concept['primary_color'])
        for y in range(height):
            # Gradient from primary color to darker shade
            ratio = y / height
            color = tuple(int(c * (1 - ratio * 0.5)) for c in primary_color)
            draw.line([(0, y), (width, y)], fill=color)

        # Add text overlay
        text = design_concept['text_overlay']

        try:
            # Try to use a system font
            font_size = 120
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()

        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Draw text with outline for better visibility
        outline_color = (0, 0, 0)
        for offset_x in [-3, 0, 3]:
            for offset_y in [-3, 0, 3]:
                draw.text((x + offset_x, y + offset_y), text, font=font, fill=outline_color)

        draw.text((x, y), text, font=font, fill=(255, 255, 255))

        # Add border
        border_width = 10
        draw.rectangle(
            [(0, 0), (width-1, height-1)],
            outline=primary_color,
            width=border_width
        )

        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"thumbnail_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        image.save(filepath)

        return filepath

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
