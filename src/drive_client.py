import io
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

from config import CREDENTIALS_FILE, TOKEN_FILE, AUDIO_EXTENSIONS


SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_drive_service():
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    "credentials.json not found. Download OAuth Desktop credentials "
                    "from Google Cloud Console and put it into project root."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return build("drive", "v3", credentials=creds)


def list_files_in_folder(service, folder_id: str) -> list[dict]:
    files = []
    page_token = None

    query = f"'{folder_id}' in parents and trashed = false"

    while True:
        response = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)",
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )

        files.extend(response.get("files", []))
        page_token = response.get("nextPageToken")

        if not page_token:
            break

    return files


def list_audio_files(service, folder_id: str) -> list[dict]:
    files = list_files_in_folder(service, folder_id)

    result = []
    for file in files:
        name = file.get("name", "")
        mime_type = file.get("mimeType", "")
        suffix = Path(name).suffix.lower()

        if mime_type.startswith("audio/") or suffix in AUDIO_EXTENSIONS:
            result.append(file)

    return result


def escape_drive_query_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_file_by_name(service, folder_id: str, file_name: str) -> Optional[dict]:
    safe_name = escape_drive_query_value(file_name)
    query = f"'{folder_id}' in parents and name = '{safe_name}' and trashed = false"

    response = (
        service.files()
        .list(
            q=query,
            spaces="drive",
            fields="files(id, name, mimeType, modifiedTime)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            pageSize=1,
        )
        .execute()
    )

    files = response.get("files", [])
    return files[0] if files else None


def copy_file_to_folder(
    service,
    file_id: str,
    file_name: str,
    target_folder_id: str,
) -> dict:
    body = {
        "name": file_name,
        "parents": [target_folder_id],
    }

    return (
        service.files()
        .copy(
            fileId=file_id,
            body=body,
            fields="id, name, mimeType, modifiedTime",
            supportsAllDrives=True,
        )
        .execute()
    )


def download_file(service, file_id: str, target_path: Path) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)

    request = service.files().get_media(
        fileId=file_id,
        supportsAllDrives=True,
    )

    with io.FileIO(target_path, "wb") as file_handle:
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False

        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download progress: {int(status.progress() * 100)}%")

    return target_path


def upload_text_file(
    service,
    local_path: Path,
    folder_id: str,
    file_name: str,
) -> dict:
    media = MediaFileUpload(
        str(local_path),
        mimetype="text/plain",
        resumable=True,
    )

    body = {
        "name": file_name,
        "parents": [folder_id],
        "mimeType": "text/plain",
    }

    return (
        service.files()
        .create(
            body=body,
            media_body=media,
            fields="id, name, mimeType",
            supportsAllDrives=True,
        )
        .execute()
    )