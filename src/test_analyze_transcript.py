from pathlib import Path

from config import LOCAL_TRANSCRIPTS_DIR
from report_client import (
    ensure_work_report,
    read_top_works,
    find_next_report_row,
    write_report_row,
)
from call_analyzer import analyze_call
from report_mapper import build_report_row


TRANSCRIPT_FILE_NAME = "2025-07-14_17-18_0937828077_incoming.txt"
AUDIO_FILE_NAME = "2025-07-14_17-18_0937828077_incoming.mp3"


def main():
    transcript_path = LOCAL_TRANSCRIPTS_DIR / TRANSCRIPT_FILE_NAME

    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")

    transcript_text = transcript_path.read_text(encoding="utf-8")

    spreadsheet_id = ensure_work_report()
    top_works = read_top_works(spreadsheet_id)

    analysis = analyze_call(
        transcript_text=transcript_text,
        audio_file_name=AUDIO_FILE_NAME,
        top_works=top_works,
    )

    row_number = find_next_report_row(spreadsheet_id)
    row = build_report_row(analysis, row_number)

    write_report_row(
        spreadsheet_id=spreadsheet_id,
        row_values=row,
        comment_is_bad=analysis["comment_is_bad"],
    )

    print("Analysis result:")
    for key, value in analysis.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()