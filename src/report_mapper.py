from report_client import build_score_formula


def build_report_row(
    analysis: dict,
    row_number: int,
) -> list:
    return [
        analysis["call_date"],                  # A Дата
        analysis["request_type"],               # B Тип звернення
        analysis["phone"],                      # C Номер телефону
        analysis["branch"],                     # D Філія
        analysis["manager"],                    # E Менеджер

        analysis["opening_ok"],                 # F Початок розмови
        analysis["body_checked"],               # G Кузов
        analysis["year_checked"],               # H Рік
        analysis["mileage_checked"],            # I Пробіг
        analysis["diagnostics_offered"],        # J Комплексна діагностика
        analysis["previous_works_checked"],     # K Роботи раніше
        analysis["service_booking"],            # L Запис на сервіс
        analysis["closing_ok"],                 # M Завершення

        analysis["top_work"],                   # N Яка робота з топ 100
        analysis["instructions_followed"],      # O Дотримувався інструкцій
        analysis["missed_recommendations"],     # P Яких рекомендацій не дотримувався
        analysis["result"],                     # Q Результат
        analysis["manager_score"],              # R Оцінка
        analysis["parts"],                      # S Запчастини
        analysis["comment"],                    # T Коментар
        build_score_formula(row_number),        # U Підрахунок балів
    ]