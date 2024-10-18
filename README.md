# Проект HSE Hack

## Структура проекта

Структура проекта выглядит следующим образом:

```

hse_hack/ ├── .ipynb_checkpoints/ # Автоматически создаваемые контрольные точки Jupyter Notebook
          ├── .venv/ # Виртуальное окружение для Python-зависимостей
          ├── data/ # Папка с данными
          ├── .env # Файл конфигурации окружения
          ├   └── complete # Папка с итоговым файлом
          ├   ├── test # Папка test
          ├   └── train # Папка train
          ├
          ├── .env.docker # Файл конфигурации окружения для Docker
          ├── docker-compose.yaml # Конфигурация Docker Compose
          ├── Dockerfile # Настройки для создания Docker-образа
          ├── errors_defining.py # Скрипт для определения ошибок
          ├── injections_check.py # Скрипт для проверки инъекций
          ├── main.py # Основной скрипт для запуска
          ├── main_jupyter.ipynb # Jupyter Notebook для интерактивного анализа
          ├── pre_analysis.py # Скрипт для предварительного анализа
          ├── README.md # Документация проекта
          └── requirements.txt # Список зависимостей Python
```


## Требования

Перед запуском проекта убедитесь, что у вас установлены следующие компоненты:
- Python 3.10 или выше
- Docker (если вы предпочитаете запускать проект с его помощью)
- Jupyter Notebook (опционально, для запуска `main_jupyter.ipynb`)

## Запуск проекта

### Способ 1: Локальный запуск

1. **Клонирование репозитория**

   Клонируйте этот репозиторий на локальную машину:
   ```bash
   git clone https://github.com/Sebastina14593/hse-ai-assistant-IIriski.git
   cd hse_hack

### Способ 2: Запуск с помощью Docker
#### 1.Создание Docker-образа
```commandline
docker build . --tag hse_hack
```
#### 2. Запуск контейнера Docker
```commandline
docker-compose run
```
### Способ 3: Запуск в Jupyter Notebook
Если возникают проблемы с запуском Docker, можно воспользоваться Jupyter Notebook, открыв файл `main_jupyter.ipynb`
