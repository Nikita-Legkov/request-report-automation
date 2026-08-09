# Request Report Automation

Скрипт превращает выгрузку заявок из Excel/ELMA/CRM в наглядный HTML-отчёт и сводную CSV-таблицу. Находит просрочку, считает статусы, приоритеты и нагрузку по исполнителям.

## Быстрый запуск

Нужен Python 3.9 или новее. Сторонние библиотеки не требуются.

```bash
python3 report.py data/demo_requests.csv --output output --today 2026-08-09
```

Откройте `output/report.html` в браузере, а `output/summary.csv` — в Excel. Готовый результат для демоданных уже лежит в `demo_output/`.

Проверка:

```bash
python3 -m unittest -v
```

## Формат входного файла

CSV должен содержать колонки:

```text
id, created_at, due_date, status, priority, assignee, title
```

Даты — в формате `ГГГГ-ММ-ДД`. Excel умеет открывать и сохранять CSV. Скрипт читает также CSV с BOM, который часто создаёт русская версия Excel.

## Структура

```text
.
├── report.py
├── data/demo_requests.csv
├── demo_output/report.html
├── demo_output/summary.csv
├── test_report.py
└── PORTFOLIO.md
```

## Адаптация под клиента

Под реальную выгрузку меняются названия колонок, статусы, правила SLA и блоки отчёта. По согласованию можно добавить `.xlsx`, отправку по почте, расписание или загрузку данных через API.
