# Импортируем pandas
import numpy as np
from pre_analysis import data_preparation
import datetime

syntax_error_template_value = """
Ты помощник на специальной обучающей платформе, на которой студент учится программировать, отправляя на проверку свой код. Твоя задача зная синтаксическую ошибку, дать студенту короткую подсказку, которая поможет ему понять на что он должен обратить внимание, чтобы ее исправить.
Твой ответ должен быть в 1 предложение 5-10 слов без примеров кода. Начни предложение с "Вам нужно проверить то-то". Обращайся к студенту на "Вы"
Скрипт студента: {script}
{error}
Твой ответ студенту: 
"""

logic_error_template_value = """
Ты помощник на специальной обучающей платформе, на которой студент учится программировать, отправляя на проверку свой код. Твоя задача сравнить код преподавателя и студента, чтобы указать студенту логическую ошибку, которая была им допущена и дать короткую подсказку, которая поможет понять ему, на что он должен обратить внимание, чтобы ее исправить.
Твой ответ должен быть в 1 предложение 5-10 слов без примеров кода. Начни предложение с "Вам нужно проверить". Обращайся к студенту на "Вы" 
Скрипт преподавателя: {task}
Скрипт студента: {script}
{error}
Твой ответ студенту:
"""

neutral_error_template_value = """
Ниже представлен правильный скрипт и скрипт студента, нужно найти ошибку в скрипте студента. Представь, что ты требовательный преподаватель, который хочет, чтобы студент думал своей головой, поэтому давай минимальное описание ошибки. Минимальные рекомендации.
Правильный скрипт: '''{task}'''
Неверный скрипт: '''{script}'''
Сформулируй в одно предложение не раскрывая название переменных, синтаксиса и конструкций, где нужно искать ошибку студенту.
Начинать предложение можно: "Ошибку можно искать в..."
Твой ответ:
"""

if __name__ == '__main__':
    dt1 = datetime.datetime.today()
    # Загружаем данные
    df = data_preparation(sample_type="test")

    # Зададим поле с типом ошибки
    df['error_type'] = df.apply(lambda x: "считывание файла" if x["task_type"] == 2 else
                                          "sytax error" if x["syntax_error"] is not np.nan and x["syntax_error"] is not None and x["syntax_error"] != '' else
                                          "logic error" if x["logic_error"] is not np.nan and x["logic_error"] is not None and x["logic_error"] != "" else "ХЗ", axis=1
                                                                                  )

    # Далее создадим соответствующие templates для LLM-моделей
    df["syntax_error_template"] = df.apply(
        lambda x: syntax_error_template_value.format(script=x["student_solution"], error=x["syntax_error"]) if x["error_type"] == "sytax error" else "",
        axis=1)
    df["logic_error_template"] = df.apply(
        lambda x: logic_error_template_value.format(task=x["author_solution"], script=x["student_solution"],
                                                    error=x["logic_error"]) if x["error_type"] == "logic error" else "",
        axis=1)

    df["template"] = df["syntax_error_template"] + df["logic_error_template"]
    # На случай, если не выяснилось, какая именно ошибка
    df["template"] = df.apply(
        lambda x: neutral_error_template_value.format(task=x["author_solution"], script=x["student_solution"]) if x["template"] == "" else
        x["template"], axis=1)

    # Сохраняем результат в файл
    df.to_excel("data/complete/SuperResultVersionTest.xlsx", index=False)
    dt2 = datetime.datetime.today()
    print("Время исполнения программы:", (dt2 - dt1).total_seconds())
