from typing import Any

from config import (
    WORK_FOLDER_ID,
    REPORT_TEMPLATE_FILE_ID,
    REPORT_FILE_NAME,
    REPORT_SHEET_NAME,
    TOP_WORKS_COLUMN,
    TOP_WORKS_START_ROW,
    TOP_WORKS_END_ROW,
)

from drive_client import (
    get_drive_service,
    get_sheets_service,
    find_file_by_name,
    copy_file_to_folder,
)


def quote_sheet_name(sheet_name: str) -> str:
    escaped = sheet_name.replace("'", "''")
    return f"'{escaped}'"


def validate_report_config():
    if not REPORT_TEMPLATE_FILE_ID:
        raise ValueError("REPORT_TEMPLATE_FILE_ID is missing in .env")

    if not WORK_FOLDER_ID:
        raise ValueError("WORK_FOLDER_ID is missing in .env")


def ensure_work_report() -> str:
    """
    Finds report copy in work folder.
    If it does not exist, copies the template spreadsheet into work folder.

    Returns spreadsheet id.
    """
    validate_report_config()

    drive_service = get_drive_service()

    existing_report = find_file_by_name(
        service=drive_service,
        folder_id=WORK_FOLDER_ID,
        file_name=REPORT_FILE_NAME,
    )

    if existing_report:
        print(f"Report already exists: {REPORT_FILE_NAME}")
        return existing_report["id"]

    copied_report = copy_file_to_folder(
        service=drive_service,
        file_id=REPORT_TEMPLATE_FILE_ID,
        file_name=REPORT_FILE_NAME,
        target_folder_id=WORK_FOLDER_ID,
    )

    print(f"Report copied to work folder: {REPORT_FILE_NAME}")

    return copied_report["id"]


def get_sheet_id(spreadsheet_id: str, sheet_name: str) -> int:
    sheets_service = get_sheets_service()

    spreadsheet = (
        sheets_service.spreadsheets()
        .get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties(sheetId,title)",
        )
        .execute()
    )

    for sheet in spreadsheet.get("sheets", []):
        properties = sheet["properties"]

        if properties["title"] == sheet_name:
            return properties["sheetId"]

    raise ValueError(f"Sheet not found: {sheet_name}")


def read_top_works(spreadsheet_id: str) -> list[str]:
    sheets_service = get_sheets_service()

    sheet = quote_sheet_name(REPORT_SHEET_NAME)

    range_name = (
        f"{sheet}!{TOP_WORKS_COLUMN}{TOP_WORKS_START_ROW}:"
        f"{TOP_WORKS_COLUMN}{TOP_WORKS_END_ROW}"
    )

    response = (
        sheets_service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
        )
        .execute()
    )

    values = response.get("values", [])

    works = []

    for row in values:
        if not row:
            continue

        value = str(row[0]).strip()

        if value:
            works.append(value)

    return works


def insert_call_row_before_top_works(
    spreadsheet_id: str,
    row_values: list[Any],
    comment_is_bad: bool = False,
):
    """
    Inserts a new report row before the top works list.
    This is important because the template stores top works in column N at the bottom.
    If we simply append rows, we can break/overwrite that list.
    """
    sheets_service = get_sheets_service()

    sheet_id = get_sheet_id(
        spreadsheet_id=spreadsheet_id,
        sheet_name=REPORT_SHEET_NAME,
    )

    target_row = TOP_WORKS_START_ROW
    target_row_index = target_row - 1

    # Insert one row before top works list
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": target_row_index,
                            "endIndex": target_row_index + 1,
                        },
                        "inheritFromBefore": True,
                    }
                }
            ]
        },
    ).execute()

    # After insertion, write values into inserted row
    sheet = quote_sheet_name(REPORT_SHEET_NAME)
    range_name = f"{sheet}!A{target_row}:U{target_row}"

    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body={
            "values": [row_values],
        },
    ).execute()

    if comment_is_bad:
        mark_comment_cell_red(
            spreadsheet_id=spreadsheet_id,
            sheet_id=sheet_id,
            row_number=target_row,
        )

    print(f"Inserted report row: {target_row}")


def mark_comment_cell_red(
    spreadsheet_id: str,
    sheet_id: int,
    row_number: int,
):
    """
    Column T = comment column.
    T is column index 19 in zero-based Google Sheets API indexing.
    """
    sheets_service = get_sheets_service()

    row_index = row_number - 1

    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": row_index,
                            "endRowIndex": row_index + 1,
                            "startColumnIndex": 19,
                            "endColumnIndex": 20,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 1.0,
                                    "green": 0.8,
                                    "blue": 0.8,
                                },
                                "textFormat": {
                                    "foregroundColor": {
                                        "red": 0.65,
                                        "green": 0.0,
                                        "blue": 0.0,
                                    },
                                    "bold": True,
                                },
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat)",
                    }
                }
            ]
        },
    ).execute()