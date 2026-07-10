from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from crew import research_crew
from logger import logger

load_dotenv()

# Create outputs folder if it doesn't exist
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def save_report(report: str):

    # Create a unique filename every time
    filename = datetime.now().strftime(
        "research_%Y-%m-%d_%H-%M-%S.md"
    )

    report_path = OUTPUT_DIR / filename

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(report)

    logger.info(f"Report saved to {report_path}")

    return report_path


def main():

    topic = input("Enter research topic: ").strip()

    if not topic:
        print("Topic cannot be empty.")
        return

    logger.info("=" * 50)
    logger.info(f"Research Started : {topic}")

    try:

        result = research_crew.kickoff(
            inputs={
                "topic": topic
            }
        )

        report = result.raw

        report_path = save_report(report)

        print("\nResearch completed successfully!")
        print(f"\nReport saved at:\n{report_path}")

        logger.info("Research completed successfully")

    except Exception as e:

        logger.exception("Crew execution failed")
        print("Something went wrong!")
        print(e)


if __name__ == "__main__":
    main()
