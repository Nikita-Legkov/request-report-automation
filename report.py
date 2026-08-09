"""Строит CSV-сводку и HTML-отчёт по выгрузке заявок."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import date, datetime
from html import escape
from pathlib import Path


REQUIRED_COLUMNS = {"id", "created_at", "due_date", "status", "priority", "assignee", "title"}
CLOSED_STATUSES = {"Выполнена", "Закрыта"}


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"В файле нет колонок: {', '.join(sorted(missing))}")
        rows = list(reader)
    if not rows:
        raise ValueError("В выгрузке нет заявок")
    return rows


def is_overdue(row: dict[str, str], today: date) -> bool:
    due = datetime.strptime(row["due_date"], "%Y-%m-%d").date()
    return row["status"] not in CLOSED_STATUSES and due < today


def build_metrics(rows: list[dict[str, str]], today: date) -> dict:
    return {
        "total": len(rows),
        "overdue": sum(is_overdue(row, today) for row in rows),
        "statuses": Counter(row["status"] for row in rows),
        "priorities": Counter(row["priority"] for row in rows),
        "assignees": Counter(row["assignee"] for row in rows),
    }


def write_summary(metrics: dict, path: Path) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(["Раздел", "Значение", "Количество"])
        writer.writerow(["Итого", "Все заявки", metrics["total"]])
        writer.writerow(["Итого", "Просрочено", metrics["overdue"]])
        for section, title in (("statuses", "Статус"), ("priorities", "Приоритет"), ("assignees", "Исполнитель")):
            for value, count in sorted(metrics[section].items()):
                writer.writerow([title, value, count])


def write_html(rows: list[dict[str, str]], metrics: dict, today: date, path: Path) -> None:
    overdue = [row for row in rows if is_overdue(row, today)]
    table_rows = "".join(
        f"<tr><td>{escape(row['id'])}</td><td>{escape(row['title'])}</td>"
        f"<td>{escape(row['assignee'])}</td><td>{escape(row['due_date'])}</td></tr>"
        for row in overdue
    ) or '<tr><td colspan="4">Просроченных заявок нет</td></tr>'
    status_rows = "".join(
        f"<li><span>{escape(name)}</span><strong>{count}</strong></li>"
        for name, count in metrics["statuses"].most_common()
    )
    document = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Отчёт по заявкам</title><style>
body{{font:16px system-ui;margin:0;background:#f4f6fa;color:#1e293b}}main{{max-width:960px;margin:40px auto;padding:0 20px}}
.cards{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}}.card,section{{background:white;border-radius:16px;padding:22px;margin-bottom:20px}}
.number{{font-size:42px;font-weight:800}}ul{{padding:0;list-style:none}}li{{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #eef2f7}}
table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #e5e7eb}}small{{color:#64748b}}
@media(max-width:600px){{.cards{{grid-template-columns:1fr}}table{{font-size:13px}}}}
</style></head><body><main><h1>Отчёт по заявкам</h1><p><small>Срез на {today.isoformat()}</small></p>
<div class="cards"><div class="card"><div class="number">{metrics['total']}</div>Всего заявок</div>
<div class="card"><div class="number">{metrics['overdue']}</div>Просрочено</div></div>
<section><h2>По статусам</h2><ul>{status_rows}</ul></section>
<section><h2>Просроченные заявки</h2><table><thead><tr><th>ID</th><th>Заявка</th><th>Исполнитель</th><th>Срок</th></tr></thead><tbody>{table_rows}</tbody></table></section>
</main></body></html>"""
    path.write_text(document, encoding="utf-8")


def generate(source: Path, output: Path, today: date) -> None:
    output.mkdir(parents=True, exist_ok=True)
    rows = load_rows(source)
    metrics = build_metrics(rows, today)
    write_summary(metrics, output / "summary.csv")
    write_html(rows, metrics, today, output / "report.html")
    print(f"Готово: {output / 'report.html'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="CSV-выгрузка заявок")
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    generate(args.source, args.output, args.today)
