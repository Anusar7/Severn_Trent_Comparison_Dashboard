# Rebuild it and understand each decision

## 1. Start with the question

“Where did Severn Trent miss its commitments, how does it compare with its
peers, and which gaps warrant further investigation?”

These are separate questions. A company can beat its peers and still miss its
own target. Pollution illustrates this: 29.30 is better than the published
sector average of 45.91, but worse than the 19.50 target. Lower is better.

The dashboard is descriptive analysis. We do not have the local incident,
rainfall, groundwater or asset records needed to predict infiltration or
establish why failures occurred.

## 2. Understand the four tables

Open the CSVs in a text editor or Excel. One row represents one observation
at the table's intended level:

- `measures.csv`: one measure in the latest comparison period.
- `history.csv`: one measure in one reporting year.
- `peers.csv`: one measure for one company or operating region.
- `sources.csv`: one published source edition.

`measure_id` links history and peers to the relevant measure. Using the same
IDs avoids joining on names that might be spelled differently. Source IDs and
page references make each number traceable. Nothing is simulated.

Why CSV? You can inspect the data without running Python. The dataset is
small enough that a database would add unnecessary work.

## 3. Load one table yourself

Create a temporary `practice.py` in the project folder:

```python
import pandas as pd

data = pd.read_csv("data/measures.csv")
print(data[["name", "actual", "target", "direction"]])
```

Run it with your virtual environment's Python. pandas turns a CSV into a
DataFrame: a table whose rows you can filter and whose columns you can calculate.

Next try:

```python
wastewater = data[data["domain"] == "Wastewater"]
print(wastewater)
```

This is the same kind of filtering used by the dashboard's service selector.

## 4. Calculate status and gap before making charts

For a lower-is-better measure:

```python
actual = 29.30
target = 19.50
met = actual <= target
gap = actual - target
gap_pct = gap / target * 100
print(met, gap, gap_pct)
```

Result: target missed, adverse gap 9.80 incidents per 10,000 km, approximately
50.26% above target. That is not 9.80 extra incidents across the entire company:
the unit is a normalised rate.

For higher-is-better measures, use `actual >= target`, and define the adverse
gap as `target - actual`. This makes positive gaps consistently mean shortfalls.

Read `meets_target()` and `adverse_gap()` in `analysis.py`. These functions
centralise the rules so the app does not calculate the same thing differently
in several places. Equality counts as meeting a target.

Never calculate a percentage gap against a zero target. CRI's target is zero,
so show its score and absolute gap instead. A blank target is different from zero:
C-MeX has no fixed numeric company target in this analysis.

## 5. Calculate a five-year achievement score

For pollution, the first three years meet their respective targets; the final
two do not. The result is 3/5 = 60%. Compare each year against that year's target,
not against the final-year target.

This is a simple descriptive score. It does not weight severity, calculate
penalties, represent every regulatory obligation or reproduce Ofwat's overall
company categorisation.

Internal flooding cannot be given one harmonised score here: the original APR
and Ofwat disagree on the final result. Keep the original series visible,
identify the separate Ofwat point and withhold the combined score.

## 6. Understand change and ranking

Relative change is `(last - first) / abs(first) * 100`.
Pollution increased by about 42.2% from 20.60 to 29.30.

For a percentage measure, use percentage points. Leakage reduction moved from
3.6% to 16.8%, a rise of 13.2 percentage points. For CRI and C-MeX, show score
points. Never label every change as a percentage.

Ranking orders each measure in its preferred direction, with 1 best. Ties
share a rank. Some companies have separately reported regions, so the denominator
is “peer observations”, not always a count of distinct companies.

The sector benchmark comes from Ofwat. Do not replace a published sector
average with the simple mean of company rates: weighting may differ.

## 7. Draw the evidence

`trend_chart()` draws actuals and targets against time. The target line is dashed.
The payment deadband is a separate dotted line when relevant.

`peer_chart()` sorts the observations, highlights Severn Trent and draws the
published benchmark. Plotly handles hover labels and browser interaction;
you do not write JavaScript.

Read chart titles, units and periods before interpreting a line. Consumption
peers are in litres/person/day, but its historical trend is the percentage
reduction from baseline. CRI, pollution and treatment use calendar years.

## 8. Add Streamlit last

Start a separate practice app with:

```python
import pandas as pd
import streamlit as st

st.title("Severn Trent performance")
data = pd.read_csv("data/measures.csv")
service = st.selectbox("Service", data["domain"].unique())
st.dataframe(data[data["domain"] == service])
```

Run `python -m streamlit run practice_app.py` using your virtual environment's
Python. Changing the selector causes Streamlit to rerun the script from the
top. The selected value controls which rows are displayed. That is the core
interaction model of the final app.

Then add one metric card, one chart, and finally the page selector. Use the
finished `app.py` as a reference, rather than trying to reproduce it all at once.

## 9. Explain the method in an interview

Explain the business question first. Then explain that you used official
published reports, retained their editions and units, calculated target status
separately from peer standing, and checked the figures back to the PDFs.

Use internal flooding to demonstrate data-quality judgement: you identified a
source conflict and withheld an unsupported combined score. Use pollution to
demonstrate analytical judgement: it beats the sector average yet misses its
target and deteriorates over time.

Be accurate about your role: this version was built with assistance. After
working through the code, describe the calculations and choices you understand,
and explain which parts you have personally rebuilt and tested.

