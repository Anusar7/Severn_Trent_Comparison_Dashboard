# Severn Trent — five years of performance

A focused interview dashboard by Anusar Jadon, built with Python, Streamlit,
pandas and Plotly. Official published data only; no synthetic observations,
live API or prediction model.

## Run on Windows

Install Python 3.12 from https://www.python.org/downloads/ if needed. Extract
the ZIP first. Open the extracted `Severn-Trent-Streamlit` folder in VS Code,
then choose **Terminal → New Terminal**. Run these commands, one at a time:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

The browser opens at http://localhost:8501. Keep the terminal open while using
the app. Press Ctrl+C in that terminal to stop it. On subsequent runs, only
the third command is needed. There is no PowerShell activation step.

Alternatively, double-click `run_windows.bat`. It detects an installed 64-bit
Python 3.10, 3.11, 3.12 or 3.13, preferring the tested Python 3.12 version.
It creates an isolated environment and installs the pinned packages on the
first run. Internet access is needed for installation, not to view the bundled
data or charts afterward. External source links still need internet access.

If you see **No suitable Python runtime found** with the original launcher,
that means its specific request for Python 3.12 was not satisfied; it does not
necessarily mean you have no Python installation. The updated launcher detects
the compatible versions above. Python 3.14+ is excluded because this project's
pinned packages were not selected for that runtime.

If the updated launcher finds no compatible runtime, open Microsoft Store,
search for **Python 3.12**, and install the free package published by **Python
Software Foundation**. Close the old command window and run the launcher again.
To list detected installations manually, run `py --list` in Command Prompt.

If Windows cannot find `py`, the automatic launcher also checks `python` on
PATH. For the manual commands, replace `py -3.12` with the full path to a
compatible Python executable, or install Python with its launcher enabled.

## Run on macOS / Linux

From the extracted project folder, using Python 3.12:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## What is in the dashboard?

1. **Overview:** 12 measures, with eight meeting the “target missed or behind
   sector” screen. Filters let you focus on wastewater, water or customer outcomes.
2. **Measure explorer:** actuals, targets, peer ranks, five-year trends, target
   achievement and source notes. Pollution is the initial selection.
3. **Recommendations:** three investigation priorities supported by the evidence.

The dataset is a historical AMP7 review: 2020/21–2024/25. The latest comparison
uses the fixed October 2025 Ofwat report. It is not the latest regulatory position.

## Understand the project

Read `LEARNING_GUIDE.md`, then follow these files in this order:

| File | Responsibility |
|---|---|
| `data/measures.csv` | 12 latest results, targets, units and benchmarks |
| `data/history.csv` | 60 historical results with source references |
| `data/peers.csv` | 183 company/region observations |
| `data/sources.csv` | Official source URLs and editions |
| `analysis.py` | Loading tables and calculating gaps, status, ranks and scores |
| `charts.py` | Two reusable Plotly chart functions |
| `app.py` | Streamlit page layout, controls and evidence-based commentary |
| `branding.py` | Name, author, logo path and chart colours |
| `.streamlit/config.toml` | Streamlit widget colours and page theme |
| `test_project.py` | Calculation and app-interaction checks |
| `AUDIT.md` | Source checks, differences and verification limits |

The interface has no tutorial panels, code dumps, AI assistant, invented
risk score or extra company-specific measures. Learning and audit material
stays in the project files.

## Customise

- Change the author, title, logo path and chart colours in `branding.py`.
- Set `LOGO = ""` to remove the logo, or point it to another local image.
- Change widget colours in `.streamlit/config.toml`; restart after changing it.
- Edit CSVs to update inputs, preserving column names, units and source references.
- Calculated results update automatically when the script reruns.
- The introduction and recommendations are editorial text in `app.py` for this
  fixed snapshot. Review them whenever you change the dataset; they are not
  automatically generated explanations.
- Do not overwrite a historical value with a new edition without checking the
  full series and updating its source notes. Re-run the audit and tests after edits.

The logo is a crop rendered from the official 2024/25 APR cover, not a recreated
mark. See `assets/ATTRIBUTION.md`. This remains clearly labelled independent work.

## Verify

```powershell
.venv\Scripts\python.exe -m unittest -v test_project.py
```

For a fresh source audit, download the four PDFs listed in `data/sources.csv`.
The PDFs are not bundled. Install the optional audit dependency:

```powershell
.venv\Scripts\python.exe -m pip install pypdf==6.10.0
.venv\Scripts\python.exe audit/verify_sources.py --ofwat "path/to/WCPR-24-25.pdf" --apr2025 "path/to/stw-apr-2025.pdf" --apr2021 "path/to/apr-2021.pdf" --apr2023 "path/to/stw-apr-2023.pdf"
```

Use the retained editions, not a different document with a similar filename.
The script writes a check-by-check CSV and document hashes into `audit/`.
Its parsing is intentionally specific to these PDF editions; a changed PDF
layout should prompt review, not a silent update.

## Present or share

Run locally before the interview and leave the app open. Start with the overview,
then explore pollution, internal flooding and CRI, and finish with recommendations.

The ZIP contains the working application; it is not itself a public website.
A hosted version requires a Python-capable service. GitHub stores the code;
GitHub Pages alone cannot run this Streamlit application. Never include your
`.venv` directory or private credentials when sharing the project.

Tested with Python 3.12, Streamlit 1.65.0, pandas 2.2.3 and Plotly 7.1.0.
