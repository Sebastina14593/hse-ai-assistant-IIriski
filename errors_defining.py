# Импортируем pandas
import numpy as np
from pre_analysis import data_preparation
import datetime

template1 = """
Ниже представлен правильный скрипт и скрипт студента, нужно найти ошибку в скрипте студента. 
Правильный скрипт: '''{task}'''
Неверный скрипт: '''{script}'''
{error}
Сформулируй в одно предложение подсказку студенту не раскрывая название переменных, синтаксиса и конструкций кода.
Используй следующую конструкцию ответа: "Вы совершили ошибку, вам следует проверить..."
Твой короткий ответ в одно предложение:
"""

template2 = """
Ниже представлен правильный скрипт и скрипт студента, нужно найти ошибку или некорректность в скрипте студента. 
Правильный скрипт: '''{task}'''
Неверный скрипт: '''{script}'''
Сформулируй в одно предложение не раскрывая название переменных, синтаксиса и конструкций, где нужно искать ошибку студенту.
Используй следующую конструкцию ответа: "В вашем коде можно изменить ..."
Твой короткий ответ в одно предложение:
"""

template3 = """
Ниже представлен скрипт преподавателя и скрипт студента, нужно найти логическую ошибку в скрипте студента.
Правильный скрипт: '''{task}'''
Неверный скрипт: '''{script}''' 
Сформулируй короткую подсказку студенту, и укажи условие задачи, которое студент выполнил некорректно. 
Запрещено присылать готовый скрипт.
Используй следующую конструкцию ответа: "Вы совершили ошибку, вам следует проверить... "
Твой короткий ответ в одно предложение:
"""

def errors_def():
    dt1 = datetime.datetime.today()
    print(dt1)
    # Загружаем данные
    df = data_preparation(sample_type="test")

    # Зададим поле с типом ошибки
    df['error_type'] = df.apply(lambda x: "считывание файла" if x["task_type"] == 2 else
                                          "sytax error" if x["syntax_error"] is not np.nan and x["syntax_error"] is not None and x["syntax_error"] != '' else
                                          "logic error" if x["logic_error"] is not np.nan and x["logic_error"] is not None and x["logic_error"] != "" else "ХЗ", axis=1
                                                                                  )

    # # Далее создадим соответствующие templates для LLM-моделей
    # # df["syntax_error_template"] = df.apply(
    # df["template"] = df.apply(
    #     lambda x: template1.format(task=x["author_solution"], script=x["student_solution"], error=x["error"]) if x["error_type"] == "sytax error" or x["error_type"]  == 'считывание файла' and x["error"] != 'Тесты пройдены' else "",
    #     axis=1)
    # # df["logic_error_template"] = df.apply(
    # df["template"] = df.apply(
    #     lambda x: template2.format(task=x["author_solution"], script=x["student_solution"]) if (x["error_type"] == "sytax error" or x["error_type"]  == 'считывание файла') and x["error"] == 'Тесты пройдены' else "",
    #     axis=1)
    #
    # # df["template"] = df["syntax_error_template"] + df["logic_error_template"]
    # # На случай, если не выяснилось, какая именно ошибка
    # df["template"] = df.apply(
    #     lambda x: template3.format(task=x["author_solution"], script=x["student_solution"]) if x["template"] == "" else
    #     np.nan, axis=1)
    #
    # # Сохраняем результат в файл
    # # df.to_excel("data/complete/SuperResultVersionTest.xlsx", index=False)
    dt2 = datetime.datetime.today()
    print("Время исполнения программы:", (dt2 - dt1).total_seconds())
    return df
