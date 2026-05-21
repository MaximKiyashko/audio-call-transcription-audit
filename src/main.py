from pathlib import Path

from config import (
    SOURCE_FOLDER_ID,
    WORK_FOLDER_ID,
    LOCAL_AUDIO_DIR,
    LOCAL_TRANSCRIPTS_DIR,
)
from drive_client import (
    get_drive_service,
    list_audio_files,
    find_file_by_name,
    copy_file_to_folder,
    download_file,
    upload_text_file,
)
from transcriber import transcribe_audio


def validate_config():
    if not SOURCE_FOLDER_ID:
        raise ValueError("SOURCE_FOLDER_ID is missing in .env")

    if not WORK_FOLDER_ID:
        raise ValueError("WORK_FOLDER_ID is missing in .env")


def main():
    validate_config()

    LOCAL_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    service = get_drive_service()

    source_audio_files = list_audio_files(service, SOURCE_FOLDER_ID)

    if not source_audio_files:
        print("No audio files found in source folder.")
        return

    print(f"Found audio files: {len(source_audio_files)}")

    for index, source_file in enumerate(source_audio_files, start=1):
        source_file_id = source_file["id"]
        audio_name = source_file["name"]

        print("")
        print(f"[{index}/{len(source_audio_files)}] Processing: {audio_name}")

        existing_audio = find_file_by_name(
            service=service,
            folder_id=WORK_FOLDER_ID,
            file_name=audio_name,
        )

        if existing_audio:
            work_audio = existing_audio
            print("Audio already exists in work folder. Using existing file.")
        else:
            work_audio = copy_file_to_folder(
                service=service,
                file_id=source_file_id,
                file_name=audio_name,
                target_folder_id=WORK_FOLDER_ID,
            )
            print("Audio copied to work folder.")

        transcript_name = f"{Path(audio_name).stem}.txt"

        existing_transcript = find_file_by_name(
            service=service,
            folder_id=WORK_FOLDER_ID,
            file_name=transcript_name,
        )

        if existing_transcript:
            print(f"Transcript already exists: {transcript_name}. Skipping.")
            continue

        local_audio_path = LOCAL_AUDIO_DIR / audio_name
        local_transcript_path = LOCAL_TRANSCRIPTS_DIR / transcript_name

        download_file(
            service=service,
            file_id=work_audio["id"],
            target_path=local_audio_path,
        )

        print("Transcribing...")
        transcript_text = transcribe_audio(local_audio_path)

        local_transcript_path.write_text(transcript_text, encoding="utf-8")

        upload_text_file(
            service=service,
            local_path=local_transcript_path,
            folder_id=WORK_FOLDER_ID,
            file_name=transcript_name,
        )

        print(f"Transcript uploaded: {transcript_name}")

    print("")
    print("Done.")


if __name__ == "__main__":
    main()