# GigaVibeMiptCode

Консольный AI-чат на базе Google Gemini.

## Возможности

* чат с AI;
* хранение истории сообщений;
* лимиты на размер контекста;
* поддержка файлов;
* обработка больших файлов по частям;
* настройка через `.env` или `config.yaml`.

---

# Установка

```bash
git clone <repo>
cd final_project

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

# Настройка

Создайте `config.yaml`:

```yaml
api_key: YOUR_API_KEY
model: gemini-2.5-flash
temperature: 0.7

limit_message: 20
limit_chars: 2000

system_prompt: |
  Ты senior Python developer.
  Отвечай кратко и по делу.
```

---

# Запуск

```bash
python main.py
```

---

# Команды

| Команда      | Описание                  |
| ------------ | ------------------------- |
| `\q`         | выход                     |
| `/reset`     | очистить чат              |
| `/filechunk` | обработка файла по частям |

---

# Файлы

Можно прикреплять файлы прямо в сообщении:

```text
@::./main.py::
```

Пример:

```text
Объясни ошибку @::./main.py::
```

---

# Обработка больших файлов

```text
/filechunk
```

Дополнительно:

```text
/filechunk paragraph=3
/filechunk len=300
/filechunk -y
```

---

# Проверка кода

```bash
ruff check .
mypy .
```

---

# Структура проекта

| Файл                 | Назначение        |
| -------------------- | ----------------- |
| `main.py`            | основной цикл     |
| `request_to_llm.py`  | запросы к Gemini  |
| `chat_context.py`    | история сообщений |
| `files_utils.py`     | работа с файлами  |
| `config.py`          | настройки         |
| `file_chunk_mode.py` | режим чанков      |

---

# Пример

```text
>>> Привет
Привет! Чем могу помочь?

>>> Объясни этот код @::./main.py::

>>> /reset

>>> \q
```
