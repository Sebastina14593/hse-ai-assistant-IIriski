# Выгружаем итоговый датафрейм
from errors_defining import errors_def

# Задаем llm-модель GigaChat
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models.gigachat import GigaChat
from dotenv import load_dotenv
import os

# Задаем библиотеки для векторного представления
import torch
from transformers import BertModel, BertTokenizer

# Загрузка переменных окружения из файла .env
load_dotenv()
AUTH = os.getenv('GIGACHAT_AUTH')

def llm_model(number, task, script, description, error, error_type, is_injection):

    if error_type == 'logic error':
        template = """
            Описание задачи: '''{description}'''
            Ниже представлен неверный скрипт студента, нужно найти логическую ошибку.
            Неверный скрипт: '''{script}'''
            {error}
            Определи ошибку в коде и сформулируй сжатый ответ, который поможет студенту самостоятельно её найти. Подсказка должна быть одной строкой и не раскрывать детали исправления
            Используй следующую конструкцию ответа: "Вы совершили ошибку [...]"
            Твой короткий ответ:
            """
    else:
        template = """
            Ниже представлен правильный скрипт и скрипт студента, нужно найти ошибку.
            Правильный скрипт: '''{task}'''
            Неверный скрипт: '''{script}'''
            {error}
            Определи ошибку в коде и сформулируй сжатый ответ, который поможет студенту самостоятельно её найти. Подсказка должна быть одной строкой и не раскрывать детали исправления
            Используй следующую конструкцию ответа: "Вы совершили ошибку [...]"
            Твой короткий ответ:
            """

    giga = GigaChat(credentials=AUTH,
                    max_tokens=60,
                    temperature=0.001,
                    top_p = 0.9,
                    model='GigaChat:latest',
                    verify_ssl_certs=False)

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | giga
    response = chain.invoke({"task": task, "script": script, "description": description, "error": error})

    # Проверим скрипт студента на промпт-инъекцию
    if response.response_metadata["finish_reason"] == "blacklist" or is_injection == 1:
        return "Скрипт студента содержит промпт-инъекцию"
    else:
        response = response.content

    if error_type == 'logic error':
        response = "Ошибка в открытых и скрытых тестах. " + response
    print('\n')
    print(f'*** {error}')
    print('---')
    print(f"Решение {number}", response)
    return response


def get_sentence_embedding(sentence: str) -> torch.Tensor:
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].squeeze()
    return embedding


if __name__ == '__main__':

    model_name = "DeepPavlov/rubert-base-cased-sentence"
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertModel.from_pretrained(model_name)

    df_total = errors_def()[['id', 'student_solution', 'author_solution', 'description', 'error', 'error_type', 'is_injection']]
    df_total['author_comment'] = df_total.apply(lambda x: llm_model(x["id"], x['author_solution'], x['student_solution'], x['description'], x['error'],x['error_type'], x['is_injection']), axis=1)
    df_total["author_comment_embedding"] = df_total['author_comment'].apply(lambda x: " ".join(list(map(str, get_sentence_embedding(x).tolist()))))
    df_total = df_total[["id", "author_comment", "author_comment_embedding"]]
    df_total.rename(columns={"id": "solution_id"}, inplace=True)
    df_total.to_csv("data/complete/submit_solution_test.csv", index=False)