"""Script Writer Agent - Generates video scripts."""

import logging
from typing import Dict, Any, List
from ..state import AgentState, Script
from ..llm import OllamaLLM

logger = logging.getLogger(__name__)

class ScriptWriter:
    """Writes detailed video scripts."""

    def __init__(self, llm: OllamaLLM):
        self.llm = llm

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        """Generate a video script from the video idea."""
        logger.info("✍️  Writing video script...")

        video_idea = state.get('video_idea')
        if not video_idea:
            logger.error("No video idea available for script writing")
            return {"messages": ["ScriptWriter: No video idea to work with"]}

        # Generate script using LLM
        script = self._generate_script(video_idea, state)

        logger.info(f"✅ Script completed: {script.estimated_length}s total")
        logger.info(f"   Sections: Intro + {len(script.main_content)} main + CTA + Outro")

        return {
            "script": script,
            "messages": [f"ScriptWriter: Created script for '{video_idea.title}'"],
            "current_stage": "script_writing"
        }

    def _generate_script(self, video_idea, state: AgentState) -> Script:
        """Generate detailed script using LLM."""

        prompt = f"""Write a complete YouTube video script.

Title: {video_idea.title}
Description: {video_idea.description}
Target Audience: {video_idea.target_audience}
Duration: {video_idea.estimated_duration}
Hook: {video_idea.hook}
Keywords: {', '.join(video_idea.keywords)}

Create a structured script with:

1. Intro (15-20 seconds) - Use the hook, introduce yourself, preview value
2. Main Content (3-5 sections) - Each section should be detailed and valuable
3. Call to Action (10 seconds) - Ask for likes, comments, subscriptions
4. Outro (10 seconds) - Thank viewers, preview next video

Make it conversational, engaging, and natural. Include specific examples and actionable insights."""

        system_prompt = """You are an expert YouTube scriptwriter. Write scripts that:

- Keep viewers engaged throughout
- Deliver clear value
- Use conversational language
- Include pattern interrupts
- Optimize for watch time and retention"""
        try:
            response = self.llm.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                schema={
                    "intro": "string (15-20 seconds of content)",
                    "main_content": ["list", "of", "section", "strings"],
                    "call_to_action": "string (10 seconds)",
                    "outro": "string (10 seconds)"
                }
            )

            main_content = response.get("main_content", [])
            if isinstance(main_content, str):
                main_content = [main_content]

            # Calculate estimated length (rough approximation)
            total_words = (
                len(response.get("intro", "").split()) +
                sum(len(section.split()) for section in main_content) +
                len(response.get("call_to_action", "").split()) +
                len(response.get("outro", "").split())
            )
            estimated_seconds = int(total_words * 0.4)  # ~150 words per minute

            return Script(
                title=video_idea.title,
                intro=response.get("intro", f"Hey everyone! Today we're diving into {video_idea.title}. {video_idea.hook}"),
                main_content=main_content if main_content else self._generate_fallback_content(video_idea),
                call_to_action=response.get("call_to_action", "If you found this helpful, smash that like button and subscribe for more content!"),
                outro=response.get("outro", "Thanks for watching! See you in the next video!"),
                estimated_length=estimated_seconds,
                keywords_used=video_idea.keywords
            )

        except Exception as e:
            logger.warning(f"LLM script generation failed, using template: {e}")
            return self._generate_template_script(video_idea)

    def _generate_fallback_content(self, video_idea) -> List[str]:
        """Generate fallback content sections."""
        return [
            f"Let's start with the basics of {video_idea.keywords[0]}. This is crucial for understanding everything else.",
            f"Now, here's the key insight that most people miss about {video_idea.title}.",
            f"Let me show you a practical example of how to apply this in real life.",
            "Here are the top mistakes to avoid when getting started.",
            "Finally, let's look at some advanced tips for taking this to the next level."
        ]

    def _generate_template_script(self, video_idea) -> Script:
        """Generate a template-based script as fallback."""
        return Script(
            title=video_idea.title,
            intro=f"Welcome back! {video_idea.hook} In this video, I'll show you everything you need to know about {video_idea.keywords[0]}",
            main_content=self._generate_fallback_content(video_idea),
            call_to_action="If you enjoyed this video, please like and subscribe. It really helps the channel grow!",
            outro="Thanks so much for watching! Drop a comment if you have questions, and I'll see you in the next one!",
            estimated_length=600, # 10 minutes
            keywords_used=video_idea.keywords
        )
