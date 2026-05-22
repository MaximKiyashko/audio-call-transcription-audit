from report_client import ensure_work_report, read_top_works


def main():
    spreadsheet_id = ensure_work_report()

    print(f"Work report spreadsheet id: {spreadsheet_id}")

    top_works = read_top_works(spreadsheet_id)

    print(f"Top works found: {len(top_works)}")

    for work in top_works[:20]:
        print(f"- {work}")


if __name__ == "__main__":
    main()