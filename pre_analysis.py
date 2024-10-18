#Уберем предупреждения, чтобы они не загромождали вывод
import warnings
warnings.filterwarnings('ignore')

# Импортируем необходимые библиотеки
import pandas as pd
import numpy as np

import ast # модуль работы с абстрактными синтаксическими деревьями

import io
import sys
import multiprocessing
from collections import deque

import inspect

def data_loader(sample_type):
    # Считываем файлы, представленные в качестве обучающих данных
    tests = pd.read_excel(f"data/{sample_type}/tests.xlsx")
    tasks = pd.read_excel(f"data/{sample_type}/tasks.xlsx")
    solutions = pd.read_excel(f"data/{sample_type}/solutions.xlsx")

    return tests, tasks, solutions

def syntax_errors_search(script):
    # Добавляем тип ошибки (синтаксический/логический). Если тип ошибки - синтаксический, то указываем на место в скрипте, где возникает ошибка
    try:
        # Парсим скрипт
        ast.parse(script)
        return np.nan
    except SyntaxError as e:
        # Если возникает ошибка, сохраняем информацию о ней
        return f"В скрипте студента следующая синтаксическая ошибка: {str(e)}"

# Функция для выполнения скрипта в отдельном процессе (вынесена на уровень модуля)
def execute_script(script, input_queue, output_queue):
    # Перехват stdout
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    # Подмена функции input
    def mock_input(prompt=None):
        return input_queue.popleft() if input_queue else ''

    # Замена input на mock_input
    if isinstance(__builtins__, dict):
        original_input = __builtins__['input']
        __builtins__['input'] = mock_input
    else:
        original_input = __builtins__.input
        __builtins__.input = mock_input

    try:
        # Исполнение скрипта
        exec(script)
        # Сохранение результата исполнения
        result = sys.stdout.getvalue().strip()
    except Exception as e:
        result = f"В скрипте студента следующая синтаксическая ошибка: {str(e)}"
    finally:
        # Возврат стандартных функций и stdout
        if isinstance(__builtins__, dict):
            __builtins__['input'] = original_input
        else:
            __builtins__.input = original_input
        sys.stdout = old_stdout

    # Передача результата в очередь
    output_queue.put(result)


def input_script_check(script, tests_input_list, tests_output_list, timeout=2):
    # Проверка скрипта на тестах
    for i in range(len(tests_input_list)):
        input_value = tests_input_list[i]  # значение для input
        output_value = tests_output_list[i]  # ожидаемое значение output

        # Используем очередь для хранения всех вводов
        input_queue = deque(input_value)
        output_queue = multiprocessing.Queue()

        # Запускаем выполнение скрипта в отдельном процессе с таймаутом
        process = multiprocessing.Process(target=execute_script, args=(script, input_queue, output_queue))
        process.start()
        process.join(timeout)

        # Проверяем, завершился ли процесс
        if process.is_alive():
            # Если процесс все еще выполняется, значит скрипт зашел в бесконечный цикл
            process.terminate()
            process.join()
            results = "Скрипт студента содержит бесконечный цикл"
            return results

        # Получаем результат из очереди
        result = output_queue.get() if not output_queue.empty() else "Нет вывода"

        # Если ошибка:
        if 'В скрипте студента следующая синтаксическая ошибка' in result:
            return result

        # Проверяем результат выполнения
        if result != output_value:
            return f'''Студент не прошел проверку теста. Он ввел input: "{"; ".join(input_value)}", ожидалось получить output: "{output_value}", но студент получил output: "{result}".'''
    return 'Тесты пройдены'


def func_script_check(script, tests_input_list, tests_output_list):
    if "input" in script:
      return "Переменные для функции должны задаваться как ее параметры."
    for idx in range(len(tests_input_list)):
        try:
            # Исполнение строки с определением функции
            exec(script)

            # Подтягиваем самую последнюю функцию (т.е. ту, которая находится в текущей строке датафрейма)
            function = [obj for name, obj in locals().items() if inspect.isfunction(obj)][-1]

            # Получаем сигнатуру функции
            func_signature = inspect.signature(function)
            num_params = len(func_signature.parameters)

            # Подготовка аргументов для вызова функции
            args = []
            kwargs = {}

            # если параметр один
            if len(tests_input_list) == 1:
                # Обработка параметров функции
                for i, (name, param) in enumerate(func_signature.parameters.items()):
                    if param.default == inspect.Parameter.empty:
                        # Обязательный параметр
                        args.append(tests_input_list[idx])  # Пример значений для тестирования
                    else:
                        # Параметр с значением по умолчанию
                        kwargs[name] = param.default
            else:
                # Обработка параметров функции
                for i, (name, param) in enumerate(func_signature.parameters.items()):
                    if param.default == inspect.Parameter.empty:
                        # Обязательный параметр
                        args.append(tests_input_list[idx][i])  # Пример значений для тестирования
                    else:
                        # Параметр с значением по умолчанию
                        kwargs[name] = param.default

            # Выполнение функции с аргументами и ключевыми аргументами
            result = function(*args, **kwargs)

        except Exception as e:
            return f"В скрипте студента следующая синтаксическая ошибка: {str(e)}"

        if result != tests_output_list[idx]:
            if len(tests_input_list) == 1:
                return f'''Студент не прошел проверку теста. Он ввел input: "{tests_input_list}", ожидалось получить output: "{tests_output_list}", но студент получил output: "{result}"'''

            return f'''Студент не прошел проверку теста. Он ввел input: "{'; '.join(tests_input_list[idx])}", ожидалось получить output: "{'; '.join(tests_output_list[idx])}", но студент получил output: "{result}"'''

    return "Тесты пройдены"

def data_correction(tasks, tests, solutions):
    # Задачи условно можно поделить на 3 группы: 1 - задачи с вводом (input) и без считывания файлов (with open)
    #                                            2 - задачи со считыванием файлов
    #                                            3 - задачи с реализацией функции
    #                                            np.nan - если задачи с указанными типами выше вообще не встречаются
    # Таким образом, создадим дополнительное поле, с указыванием того, к какой группе задач относится данная задача
    tasks["task_type"] = tasks["author_solution"].apply(lambda x: 1 if "input" in x and "with open" not in x else
                                                                  2 if "with open" in x else
                                                                  3 if "def" in x else np.nan
                                                        )

    # В дальнейшем нам понадобится информация о входных и выходных примеров данных для каждого из заданий
    # Поэтому приджойним к датафрейму df_test датафрейм df_tests
    tasks = (tasks.merge(tests.groupby("task_id", as_index=False)[["input", "output"]].agg(list)
                               , left_on="id"
                               , right_on="task_id"
                               )
                  .drop("task_id", axis=1)
             )

    # Далее сделаем еще одно преобразование входных данных для последующей проверки
    # Для задач 1ой группы предполагается, что если в программе задействуется сразу несколько input,
    # то они переносятся символом \n
    # Т.е. сделаем следующее
    tasks["input"] = tasks.apply(lambda x: [el.split("\n") if "\n" in el else el.split(";") for el in x["input"]] if x["task_type"] == 1 else x["input"], axis = 1)

    # Если же это 3я группа задач, то предполагается, что это функции, принимающие на вход какие-либо значения (структуры)
    # Используем метод literal_eval из модуля ast для преобразования структур данных
    tasks["input"] = tasks.apply(lambda x: ast.literal_eval(f"[{x['input'][0]}]") if x["task_type"] == 3 else x["input"], axis=1)

    # Добавляем к решениям студентов описания заданий
    df_total = (solutions.merge(tasks, left_on="task_id", right_on="id")
                         .drop("id_y", axis=1)
                         .rename(columns={"id_x": "id"})
                )

    # Добавляем тип ошибки (синтаксический/логический). Если тип ошибки - синтаксический, то указываем на место в скрипте, где возникает ошибка
    df_total["student_solution_syntaxis_error_step_1"] = df_total["student_solution"].apply(lambda x: syntax_errors_search(x))

    # Далее осуществим проверку скриптов, отправленных студентами
    df_total["student_solution_syntaxis_error_step_2"] = df_total.apply(
        lambda x: input_script_check(x["student_solution"], x["input"], x["output"]) if (x["task_type"] == 1) and (
                    x["student_solution_syntaxis_error_step_1"] is np.nan) else np.nan, axis=1)

    # Далее осуществим проверку скриптов, отправленных студентами по задачам 3ей группы
    df_total["student_solution_syntaxis_error_step_3"] = df_total.apply(
        lambda x: func_script_check(x["student_solution"], x["input"], x["output"]) if (x["task_type"] == 3) and (
                    x["student_solution_syntaxis_error_step_1"] is np.nan) else np.nan, axis=1)

    # После того, как задали всевозможные синтаксические ошибки, а также для некоторых кейсов и логические, объединим всю информацию

    df_total["error"] = df_total["student_solution_syntaxis_error_step_1"].fillna("") + \
                        df_total["student_solution_syntaxis_error_step_2"].fillna("") + \
                        df_total["student_solution_syntaxis_error_step_3"].fillna("")

    df_total["syntax_error"] = df_total["error"].apply(lambda x: "" if "Он ввел" in x else x)
    df_total["logic_error"] = df_total["error"].apply(lambda x: "" if "Он ввел" not in x else x)

    df_total = df_total.drop(["student_solution_syntaxis_error_step_1", "student_solution_syntaxis_error_step_2",
                              "student_solution_syntaxis_error_step_3"], axis=1)


    return df_total

def data_preparation(sample_type="train"):
    # Загружаем данные
    print("Загружаем данные")
    df_tests, df_tasks, df_solutions = data_loader(sample_type)
    # Корректируем их и добавляем дополнительные поля
    print("Корректируем их и добавляем дополнительные поля")
    df_result = data_correction(df_tasks, df_tests, df_solutions)
    return df_result