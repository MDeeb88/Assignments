# Homework 2 — Steam Dataset Loader

A Python script that loads a Steam games dataset and prints the first 10 rows using pandas.

## Setup

Clone the repository and create a virtual environment:

```bash
git clone -b Homework-2 https://github.com/MDeeb88/Assignments.git
cd Assignments
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Dataset

Download the [Steam Games Dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset) from Kaggle.

Place the CSV file at `datasets/games.csv`.

## Run

```bash
python data_loader.py
```

The script displays the first 10 rows of the dataset.

## Homework 3 — Data Type Conversion

The script converts Steam dataset columns to appropriate pandas data types and saves the processed DataFrame as `datasets/games.parquet`.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run:

```bash
python data_loader.py
```

The CSV and generated Parquet files are excluded from Git. Download the original dataset using the Kaggle link above.