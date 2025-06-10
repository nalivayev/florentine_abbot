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

- `run.py` — main entry point for launching batch workflows and calculations.
- `classes/batch.py` — batch and interactive DPI calculation logic.
- `classes/recorder.py` — logging utility.
- `classes/vuescan/workflow.py` — workflow automation for VueScan.
- `classes/exifer.py` — EXIF metadata extraction and parsing.

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

**Example:**

```
{digitization_year:8:>:0}
```

## Supported Template Variables

- `user_name` — operating system user name  
- `digitization_year` — year of digitization (from EXIF)  
- `digitization_month` — month of digitization (from EXIF)  
- `digitization_day` — day of digitization (from EXIF)  
- `digitization_hour` — hour of digitization (from EXIF)  
- `digitization_minute` — minute of digitization (from EXIF)  
- `digitization_second` — second of digitization (from EXIF)  
- ...plus any additional variables provided via command-line or batch templates

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

---

For more details, see the [README.ru.md](README.ru.md) (in Russian).
