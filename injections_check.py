import re

# Функции, проверяющие скрипты студента на промпт-инъекцию

def detect_prompt_injection_combined(script):
    # Шаблоны для явных запросов к ассистенту
    patterns = [
        r"(скажи|дай|выведи|реши|помоги).*ответ",
        r"(ассистент|помощник).*дай.*ответ",
        r"(реши|помоги|выведи|скажи).*задач[ауы]",
        r"(ассистент|помощник).*реши.*задач[ауы]",
        r"(ассистент|помощник).*помоги.*(решить|ответить)"
    ]

    # Проверка на явные запросы к ассистенту
    def detect_prompt_injection(script):
        for pattern in patterns:
            if re.search(pattern, script, re.IGNORECASE):
                return True
        return False

    # Поиск скрытых инъекций в переменных
    def detect_hidden_prompts(script):
        pattern = r"(\w+)\s*=\s*[\"'].*(ассистент|помощник|реши|ответ).*"
        return bool(re.search(pattern, script, re.IGNORECASE))

    # Поиск подозрительных комментариев
    def detect_comment_injections(script):
        pattern = r"#.*(ассистент|помощник|реши|ответ).*"
        return bool(re.search(pattern, script, re.IGNORECASE))

    # Проверка на длинные строки внутри кода
    def detect_long_strings_in_code(script):
        pattern = r"([\"']).{200,}\1"
        return bool(re.search(pattern, script))

    # Проверка на длинные комментарии
    def detect_long_comments_in_code(script):
        pattern = r"#.{200,}"
        return bool(re.search(pattern, script))

    # Общий алгоритм, объединяющий все проверки
    return (
            detect_prompt_injection(script) or
            detect_hidden_prompts(script) or
            detect_comment_injections(script) or
            detect_long_strings_in_code(script) or
            detect_long_comments_in_code(script)
    )