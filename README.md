# Audio Call Transcription Audit

This project copies audio files from a Google Drive source folder to a working folder, transcribes them locally, and uploads `.txt` transcript files back to the working folder.

## Requirements

- Python 3.10+
- Google account with access to Google Drive
- Google Cloud project with Google Drive API enabled
- OAuth Desktop credentials saved as `credentials.json`

## Setup

```bash
python -m venv .venv