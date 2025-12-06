# 🕵️‍♂️ AI Web Research Agent

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Ollama](https://img.shields.io/badge/Ollama-Local-white?style=for-the-badge&logo=ollama)
![OpenAI](https://img.shields.io/badge/OpenAI-API-green?style=for-the-badge&logo=openai)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

Автономный агент-исследователь, построенный на Python. Он умеет планировать стратегию поиска, собирать информацию из Интернета, фильтровать её с помощью векторного поиска (RAG) и составлять итоговые отчеты.

Проект спроектирован с упором на гибкость: вы можете использовать **локальные модели** (через Ollama или другие локальные платформы) для приватности, или подключить **облачные API** (OpenAI, DeepSeek, Groq) для максимального качества генерации.

## 📚 Содержание

- [✨ Особенности](#-особенности)
- [🛠 Технологический стек](#-технологический-стек)
- [🚀 Установка](#-установка)
- [⚙️ Настройка LLM (Локально vs API)](#️-настройка-llm-локально-vs-api)
- [🏃‍♂️ Запуск](#️-запуск)
- [📂 Структура проекта](#-структура-проекта)
- [👏 Благодарности и Авторство](#-благодарности-и-авторство)
- [📄 Лицензия](#-лицензия)

## ✨ Особенности

*   **Мульти-агентная архитектура**:
    *   🧠 **Planner Agent**: Анализирует запрос и разбивает его на несколько поисковых стратегий.
    *   🔍 **Search Agent**: Выполняет поиск, скачивает страницы и находит наиболее релевантные фрагменты текста.
    *   📝 **Synthesis Agent**: Собирает данные из всех источников и пишет связный, нейтральный отчет.
*   **Гибкость выбора моделей**: Поддержка любого провайдера, совместимого с OpenAI SDK. Работайте локально или через API.
*   **Умный поиск (RAG)**: Вместо чтения целых страниц, движок индексирует контент с помощью `FAISS` и `SentenceTransformers`, выбирая только те куски текста, которые отвечают на вопрос.
*   **Без API ключей для поиска**: Использует парсинг HTML выдачи DuckDuckGo.

## 🛠 Технологический стек

*   **Оркестрация**: [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
*   **LLM Бэкенд**: [OpenAI Python API](https://github.com/openai/openai-python) (Ollama / OpenAI / Custom endpoints)
*   **Поисковый движок**: Custom Scraper + FAISS Vector Store
*   **NLP**: Spacy, Sentence-Transformers

## 🚀 Установка

### 1. Предварительные требования

*   Установленный **Python 3.10** или выше.
*   Если планируете локальный запуск: **[Ollama](https://ollama.com/)**.

### 2. Клонирование и зависимости

```bash
# Клонируйте репозиторий
git clone https://github.com//antondanv/AI-Web-Research-Agent.git
cd AI-Web-Research-Agent
```
### (Опционально) Создайте виртуальное окружение
```bash
python -m venv venv
```
#### Windows:
```bash
venv\Scripts\activate
```
#### Mac/Linux:
```bash
source venv/bin/activate
```
#### Установите библиотеки
```bash
pip install -r requirements.txt
```
### 3. Загрузка NLP модели
Критически важный шаг для работы поискового движка (разбиение текста):
```bash
python -m spacy download en_core_web_sm
```

## ⚙️ Настройка LLM (Локально vs API)

Проект по умолчанию настроен на работу с Ollama. Вы можете легко изменить это в начале файла `WebResearchAgent.py`.

### Вариант 1: Локально (Ollama) - По умолчанию

1. Установите модель:
   ```bash
   ollama pull llama3.2
   ```
2. Убедитесь, что клиент настроен правильно в коде:
   ```python
   ollama_client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="not-required")
   ollama_model = OpenAIChatCompletionsModel(openai_client=ollama_client, model="llama3.2")
   ```

### Вариант 2: OpenAI (GPT-5.1 / GPT-5-mini / GPT-5-nano)

1. Получите API-ключ в [настройках OpenAI](https://platform.openai.com/account/api-keys).
2. Замените клиент в коде:
   ```python
   openai_client = AsyncOpenAI(api_key="sk-proj-...")  # Ваш API ключ
   model = OpenAIChatCompletionsModel(openai_client=openai_client, model="gpt-4o")
   ```

### Вариант 3: Сторонние API (DeepSeek, Groq, OpenRouter)

Любой провайдер, поддерживающий формат OpenAI, будет работать. Пример для DeepSeek:

```python
ds_client = AsyncOpenAI(base_url="https://api.deepseek.com", api_key="ваш-ключ")
model = OpenAIChatCompletionsModel(openai_client=ds_client, model="deepseek-chat")
```
## 🏃‍♂️ Запуск

1. Убедитесь, что Ollama запущена (если используете локальную модель):
   ```bash
   ollama serve
   ```
2. Запустите агента:
   ```bash
   python WebResearchAgent.py
   ```

> **Примечание**: Чтобы изменить тему исследования, отредактируйте переменную `query` в функции `main()` внутри файла `WebResearchAgent.py`.
## 📂 Структура проекта

```
.
├── WebResearchAgent.py        # Точка входа: логика агентов
├── WebSearch.py               # Обертка инструмента поиска
├── requirements.txt           # Список зависимостей
├── search_engine/             # Ядро поискового движка
│   ├── query.py               # Поиск DuckDuckGo
│   ├── scraper.py             # Загрузка HTML
│   ├── content_extraction.py  # Очистка контента
│   ├── indexer.py             # RAG: Векторизация и FAISS
│   └── retrieval.py           # Семантический поиск
└── README.md                  # Это руководство
```
## 👏 Благодарности и Авторство

Особая благодарность авторам, чьи наработки легли в основу компонентов этого проекта:

*   **Search Engine Module**: Модуль веб-скрапинга и контекстного поиска основан на репозитории [Web-Context-Retrieval-Engine-for-LLMs-and-AI-Agents](https://github.com/mominalix/Web-Context-Retrieval-Engine-for-LLMs-and-AI-Agents) от пользователя [mominalix](https://github.com/mominalix). Адаптирован для асинхронной работы агентов.
*   **OpenAI Agents SDK**: Архитектура построена на экспериментальной библиотеке агентов от [OpenAI](https://github.com/openai/openai-agents-python).
## 📄 Лицензия

Этот проект распространяется под лицензией [MIT License](LICENSE).