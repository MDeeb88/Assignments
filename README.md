
# Домашнее задание 7 — Загрузка данных в PostgreSQL

## Цель

Подключиться к удалённой базе данных PostgreSQL и загрузить 100 записей из датасета Steam Games.

## Датасет

Используется датасет Steam Games из предыдущих заданий.

Источник: https://www.kaggle.com/datasets/fronkongames/steam-games-dataset

Скрипт использует следующие столбцы:

- AppID
- Name
- Price
- Positive
- Negative

## База данных

- База данных: `homeworks`
- Таблица: `deebm`
- Количество записей: 100

## Структура проекта

- `scripts/write_to_db.py` — скрипт для загрузки данных в PostgreSQL
- `notebooks/DB_exploration.ipynb` — проверка подключения и выполнение скрипта
- `requirements.txt` — зависимости Python

## Установка

```bash
pip install -r requirements.txt
```
