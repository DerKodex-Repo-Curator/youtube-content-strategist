"""Main CLI entry point for YouTube Content Strategist."""

import argparse
import logging
import sys
import json
from pathlib import Path
from .graph import YouTubeContentGraph
from .utils import setup_logging, print_summary

def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="YouTube Content Strategist - Multi-Agent Content Pipeline"
    )
    parser.add_argument(
        "niche",
        type=str,
        help="Content niche (e.g., tech, gaming, education, lifestyle)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="mistral:7b",
        help="Ollama model to use (default: mistral:7b)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum feedback loop iterations (default: 3)"
    )
    parser.add_argument(
        "--performance-threshold",
        type=float,
        default=0.6,
        help="Performance threshold for feedback loop (default: 0.6)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory for results (default: output)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--save-state",
        action="store_true",
        help="Save final state to JSON file"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Create output directory
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)

        # Initialize and run the graph
        logger.info("Initializing YouTube Content Strategist...")
        graph = YouTubeContentGraph(
            model=args.model,
            max_iterations=args.max_iterations,
            performance_threshold=args.performance_threshold
        )

        # Run the pipeline
        final_state = graph.run(niche=args.niche)

        # Get and print summary
        summary = graph.get_summary(final_state)
        print_summary(summary)

        # Save state if requested
        if args.save_state:
            state_file = Path(args.output_dir) / "final_state.json"
            with open(state_file, 'w') as f:
                # Convert Pydantic models to dicts
                serializable_state = {
                    "niche": final_state.get("niche"),
                    "iteration_count": final_state.get("iteration_count"),
                    "video_idea": final_state.get("video_idea").dict() if final_state.get("video_idea") else None,
                    "script": final_state.get("script").dict() if final_state.get("script") else None,
                    "thumbnail": final_state.get("thumbnail").dict() if final_state.get("thumbnail") else None,
                    "upload_result": final_state.get("upload_result").dict() if final_state.get("upload_result") else None,
                    "analytics": final_state.get("analytics").dict() if final_state.get("analytics") else None,
                    "messages": final_state.get("messages", [])
                }
                json.dump(serializable_state, f, indent=2)
            logger.info(f"State saved to {state_file}")

        logger.info("✅ Pipeline completed successfully!")
        return 0

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Pipeline interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
