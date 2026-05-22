from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent

SOURCE_FOLDER_ID = os.getenv("SOURCE_FOLDER_ID")
WORK_FOLDER_ID = os.getenv("WORK_FOLDER_ID")

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "small")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
TRANSCRIPTION_LANGUAGE = os.getenv("TRANSCRIPTION_LANGUAGE") or "uk"

LOCAL_AUDIO_DIR = ROOT_DIR / "data" / "audio"
LOCAL_TRANSCRIPTS_DIR = ROOT_DIR / "data" / "transcripts"

CREDENTIALS_FILE = ROOT_DIR / "credentials.json"
TOKEN_FILE = ROOT_DIR / "token.json"

REPORT_TEMPLATE_FILE_ID = os.getenv("REPORT_TEMPLATE_FILE_ID")
REPORT_FILE_NAME = os.getenv("REPORT_FILE_NAME", "Звіт прослуханих розмов - auto")
REPORT_SHEET_NAME = os.getenv("REPORT_SHEET_NAME", "Лист1")

TOP_WORKS_COLUMN = "N"
TOP_WORKS_START_ROW = int(os.getenv("TOP_WORKS_START_ROW", "2980"))
TOP_WORKS_END_ROW = int(os.getenv("TOP_WORKS_END_ROW", "3064"))

AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".ogg",
    ".flac",
    ".webm",
    ".mp4",
}