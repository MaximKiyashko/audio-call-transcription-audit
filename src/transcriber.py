from pathlib import Path
from faster_whisper import WhisperModel

from config import (
    WHISPER_MODEL_SIZE,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    TRANSCRIPTION_LANGUAGE,
)


def format_time(seconds: float) -> str:
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def transcribe_audio(audio_path: Path) -> str:
    model = WhisperModel(
        WHISPER_MODEL_SIZE,
        device=WHISPER_DEVICE,
        compute_type=WHISPER_COMPUTE_TYPE,
    )

    segments, info = model.transcribe(
        str(audio_path),
        language=TRANSCRIPTION_LANGUAGE,
        vad_filter=True,
    )

    lines = [
        f"File: {audio_path.name}",
        f"Detected language: {info.language}",
        f"Language probability: {info.language_probability:.2f}",
        "",
        "Transcript:",
        "",
    ]

    for segment in segments:
        start = format_time(segment.start)
        end = format_time(segment.end)
        text = segment.text.strip()

        if text:
            lines.append(f"[{start} - {end}] {text}")

    return "\n".join(lines)