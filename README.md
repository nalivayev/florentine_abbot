[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/nalivayev/florentine_abbot/blob/master/README.md)
[![ru](https://img.shields.io/badge/lang-ru-yellow.svg)](https://github.com/nalivayev/florentine_abbot/blob/master/README.ru.md)

# Florentine Abbot

A utility designed to automate and optimize the scanning workflow using [VueScan](https://www.hamrick.com) by Ed Hamrick.

## Features

- **Automatic calculation of optimal scanning DPI** based on photo and output requirements.
- **Batch processing**: interactive, single calculation, or folder-based workflows.
- **Flexible template system** for file naming and metadata, including EXIF extraction.
- **Workflow automation**: run VueScan with generated settings, move and rename output files, extract EXIF metadata.
- **Comprehensive logging** for all workflow steps.
- **Command-line interface** with argument validation and help.

## Main Utilities

- `florentine_abbot/cli.py` — main CLI entry point (used for the `florentine-abbot` command).
- `florentine_abbot/batch.py` — batch and interactive DPI calculation logic.
- `florentine_abbot/calculator.py` — DPI calculation algorithms.
- `florentine_abbot/parser.py` — command-line argument parsing and validation.
- `florentine_abbot/recorder.py` — logging utility.
- `florentine_abbot/vuescan/workflow.py` — workflow automation for VueScan.
- `florentine_abbot/exifer.py` — EXIF metadata extraction and parsing.

## Template System

Templates are used in settings and file names to inject dynamic values.

**Template format:**

```
{<name>[:length[:align[:pad]]]}
```

- `name` — template variable name  
- `length` — total length (optional)  
- `align` — alignment (`<`, `>`, `^`; optional)  
- `pad` — padding character (optional)  

## Supported Template Variables

- `user_name` — operating system user name  
- `digitization_year` — year of digitization (from EXIF or file modification time)  
- `digitization_month` — month of digitization  
- `digitization_day` — day of digitization  
- `digitization_hour` — hour of digitization  
- `digitization_minute` — minute of digitization  
- `digitization_second` — second of digitization  
- `scan_dpi` — DPI value selected or calculated during the batch or interactive workflow  
- ...plus any additional variables provided via command-line (`--templates key=value`) or batch templates

**Note:**  
If EXIF metadata is missing, date/time variables are filled with the file's modification time.

**Example:**
```
{digitization_year:8:>:0}
```

## Usage

Run the main workflow:

```sh
python run.py --workflow <path_to_ini> --engine vuescan --batch scan --min-dpi 300 --max-dpi 4800 --dpis 600 1200 2400 4800
```

For full list of arguments and options, use:

```sh
python run.py --help
```

## Logging

All workflow steps and errors are logged to a file with the same name as the script and `.log` extension.

## Installation

To install the package locally from the source directory, use:

```sh
pip install .
```

This will install all required dependencies and make the `florentine-abbot` CLI command available in your system.

> **Note:**  
> It is recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html) for installation and development.

To upgrade an existing installation, use:

```sh
pip install --upgrade .
```

---

For more details, see the [README.ru.md](README.ru.md) (in Russian).
