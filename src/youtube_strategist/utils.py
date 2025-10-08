"""Utility functions for YouTube Content Strategist."""

import logging
import colorlog
from typing import Dict, Any

def setup_logging(level: str = "INFO"):
    """Setup colored logging."""

    # Create color formatter
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    # Setup handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    root_logger.handlers = []
    root_logger.addHandler(handler)

    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("ollama").setLevel(logging.WARNING)

def print_summary(summary: Dict[str, Any]):
    """Print a formatted summary of pipeline execution."""

    print("\n" + "=" * 70)
    print("📊 PIPELINE EXECUTION SUMMARY")
    print("=" * 70)

    print(f"\n🎯 Niche: {summary.get('niche', 'N/A')}")
    print(f"🔄 Iterations: {summary.get('iterations', 0)}")

    if summary.get('final_video_title'):
        print(f"\n📹 Video Title: {summary['final_video_title']}")

    if summary.get('video_id'):
        print(f"🆔 Video ID: {summary['video_id']}")

    if summary.get('thumbnail_path'):
        print(f"🎨 Thumbnail: {summary['thumbnail_path']}")

    if summary.get('performance_score') is not None:
        score = summary['performance_score']
        status = "✅ GOOD" if score >= 0.6 else "⚠️ NEEDS IMPROVEMENT"
        print(f"\n📈 Performance Score: {score:.3f} {status}")

        if summary.get('views') is not None:
            print(f"   👁️  Views: {summary['views']:,}")
        if summary.get('ctr') is not None:
            print(f"   🎯 CTR: {summary['ctr']:.2%}")

    if summary.get('messages'):
        print(f"\n📝 Agent Activity Log:")
        for msg in summary['messages']:
            print(f"   • {msg}")

    print("\n" + "=" * 70)

def format_script(script) -> str:
    """Format script for display or export."""

    output = []
    output.append(f"Title: {script.title}")
    output.append(f"Duration: {script.estimated_length}s (~{script.estimated_length // 60}m {script.estimated_length % 60}s)")
    output.append(f"Keywords: {', '.join(script.keywords_used)}")
    output.append("\n" + "=" * 60)

    output.append("\n[INTRO]")
    output.append(script.intro)

    for i, section in enumerate(script.main_content, 1):
        output.append(f"\n[SECTION {i}]")
        output.append(section)

    output.append("\n[CALL TO ACTION]")
    output.append(script.call_to_action)

    output.append("\n[OUTRO]")
    output.append(script.outro)

    return "\n".join(output)

def export_script_to_file(script, filepath: str):
    """Export script to a text file."""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(format_script(script))

    logging.info(f"Script exported to {filepath}")
