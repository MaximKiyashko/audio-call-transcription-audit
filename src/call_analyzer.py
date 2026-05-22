import re
from difflib import SequenceMatcher


def normalize_text(text: str) -> str:
    return text.lower().replace("ʼ", "'").replace("’", "'")


def contains_any(text: str, phrases: list[str]) -> bool:
    normalized = normalize_text(text)
    return any(phrase.lower() in normalized for phrase in phrases)


def extract_phone(text: str, fallback: str = "") -> str:
    candidates = re.findall(r"(?:\+?38)?0\d{9}", text)

    if candidates:
        phone = candidates[0]
        if phone.startswith("380"):
            return phone
        if phone.startswith("0"):
            return "38" + phone
        return phone

    candidates = re.findall(r"\+?380\d{9}", text)
    if candidates:
        return candidates[0].replace("+", "")

    return fallback


def extract_phone_from_filename(file_name: str) -> str:
    match = re.search(r"(?:\+?38)?0\d{9}", file_name)

    if not match:
        return ""

    phone = match.group(0).replace("+", "")

    if phone.startswith("380"):
        return phone

    if phone.startswith("0"):
        return "38" + phone

    return phone


def extract_date_from_filename(file_name: str) -> str:
    """
    Supports names like:
    2025-07-14_13-07_0661194054_incoming.mp3
    2025.07.14_13-07_call.mp3
    """
    match = re.search(r"(\d{4})[-_.](\d{2})[-_.](\d{2})", file_name)

    if not match:
        return file_name

    year, month, day = match.groups()
    return f"{day}.{month}.{year}"


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def detect_top_work(transcript_text: str, top_works: list[str]) -> str:
    text = normalize_text(transcript_text)

    # 1. Exact / partial phrase match
    for work in top_works:
        work_normalized = normalize_text(work)

        if len(work_normalized) >= 5 and work_normalized in text:
            return work

    # 2. Keyword fallback
    keyword_map = {
        "Компʼютерна діагностика": [
            "комп'ютерна діагностика",
            "компютерна діагностика",
            "діагностика комп'ютерна",
            "підключити комп'ютер",
            "підключимо сканер",
        ],
        "Комплексна діагностика": [
            "комплексна діагностика",
            "повна діагностика",
            "продіагностувати авто",
            "діагностика всього авто",
        ],
        "Заміна Оливи ДВЗ": [
            "заміна оливи",
            "поміняти масло",
            "замінити масло",
            "олива двигуна",
            "масло двигуна",
        ],
        "Заміна повітряного фільтра ДВЗ": [
            "повітряний фільтр",
            "фільтр двигуна",
        ],
        "Заміна фільтру салону": [
            "салонний фільтр",
            "фільтр салону",
        ],
        "Заміна масла в АКПП": [
            "масло в коробці",
            "олива в коробці",
            "акпп",
            "автоматична коробка",
        ],
        "Заміна гальмівних дисків та колодок": [
            "гальмівні диски",
            "гальмівні колодки",
            "колодки",
            "диски",
        ],
        "Ендоскопія двигуна": [
            "ендоскопія",
            "ендоскопом",
        ],
    }

    for target_work, keywords in keyword_map.items():
        if target_work in top_works and contains_any(text, keywords):
            return target_work

    # 3. Similarity fallback against top works
    best_work = ""
    best_score = 0.0

    for work in top_works:
        score = similarity(text[:800], work)

        if score > best_score:
            best_score = score
            best_work = work

    if best_score >= 0.35:
        return best_work

    return "інший варіант"


def analyze_call(
    transcript_text: str,
    audio_file_name: str,
    top_works: list[str],
) -> dict:
    text = normalize_text(transcript_text)

    phone_from_filename = extract_phone_from_filename(audio_file_name)
    phone = extract_phone(transcript_text, fallback=phone_from_filename)

    opening_ok = int(
        contains_any(
            text,
            [
                "добрий день",
                "доброго дня",
                "вітаю",
                "автосервіс",
                "слухаю вас",
            ],
        )
    )

    body_checked = int(
        contains_any(
            text,
            [
                "кузов",
                "седан",
                "універсал",
                "хетчбек",
                "позашляховик",
                "кросовер",
            ],
        )
    )

    year_checked = int(
        contains_any(
            text,
            [
                "який рік",
                "рік авто",
                "рік випуску",
                "якого року",
            ],
        )
    )

    mileage_checked = int(
        contains_any(
            text,
            [
                "пробіг",
                "скільки пробіг",
                "який пробіг",
                "кілометраж",
            ],
        )
    )

    diagnostics_offered = int(
        contains_any(
            text,
            [
                "комплексна діагностика",
                "діагностика",
                "продіагностувати",
                "перевірити авто",
            ],
        )
    )

    previous_works_checked = int(
        contains_any(
            text,
            [
                "що вже робили",
                "раніше робили",
                "до цього міняли",
                "вже міняли",
                "обслуговували раніше",
            ],
        )
    )

    service_booking = int(
        contains_any(
            text,
            [
                "записати",
                "запишу",
                "запис на сервіс",
                "на яку дату",
                "можемо вас записати",
                "під'їжджайте",
                "приїжджайте",
            ],
        )
    )

    closing_ok = int(
        contains_any(
            text,
            [
                "дякую",
                "гарного дня",
                "до побачення",
                "чекаємо вас",
                "будемо раді",
            ],
        )
    )

    top_work = detect_top_work(transcript_text, top_works)

    missed = []

    if not opening_ok:
        missed.append("Не було коректного привітання")

    if not body_checked:
        missed.append("Не уточнив кузов автомобіля")

    if not year_checked:
        missed.append("Не уточнив рік автомобіля")

    if not mileage_checked:
        missed.append("Не уточнив пробіг автомобіля")

    if not diagnostics_offered:
        missed.append("Не запропонував діагностику / перевірку")

    if not previous_works_checked:
        missed.append("Не уточнив, які роботи виконувалися раніше")

    if not service_booking:
        missed.append("Не довів клієнта до запису на сервіс")

    if not closing_ok:
        missed.append("Не було коректного завершення розмови")

    binary_score = (
        opening_ok
        + body_checked
        + year_checked
        + mileage_checked
        + diagnostics_offered
        + previous_works_checked
        + service_booking
        + closing_ok
    )

    instructions_followed = int(binary_score >= 6 and service_booking == 1)

    comment_is_bad = int(binary_score < 6 or service_booking == 0)

    if comment_is_bad:
        comment = "НЕ ОК: " + "; ".join(missed[:5])
    else:
        comment = "ОК: менеджер в цілому коректно провів розмову з клієнтом."

    if service_booking:
        result = "Є запис"
    else:
        result = "Без запису"

    manager_score = round((binary_score + instructions_followed) / 9 * 10, 1)

    return {
        "call_date": extract_date_from_filename(audio_file_name),
        "request_type": "Консультація",
        "phone": phone,
        "branch": "",
        "manager": "",

        "opening_ok": opening_ok,
        "body_checked": body_checked,
        "year_checked": year_checked,
        "mileage_checked": mileage_checked,
        "diagnostics_offered": diagnostics_offered,
        "previous_works_checked": previous_works_checked,
        "service_booking": service_booking,
        "closing_ok": closing_ok,

        "top_work": top_work,
        "instructions_followed": instructions_followed,
        "missed_recommendations": "; ".join(missed),
        "result": result,
        "manager_score": manager_score,
        "parts": "",

        "comment": comment,
        "comment_is_bad": bool(comment_is_bad),
    }