"""Readable, independent calculations. No Streamlit code in this file."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent


def meets_target(actual, target, direction):
    """Equality counts as met. Missing targets remain unassessed."""
    if pd.isna(target):
        return None
    if direction == "lower":
        return actual <= target + 1e-9
    return actual >= target - 1e-9


def adverse_gap(actual, target, direction):
    """A positive gap always means worse than the comparison."""
    if pd.isna(target):
        return None
    return round(actual - target if direction == "lower" else target - actual, 10)


def load_data():
    measures = pd.read_csv(ROOT / "data/measures.csv").fillna({"note": ""})
    history = pd.read_csv(ROOT / "data/history.csv")
    peers = pd.read_csv(ROOT / "data/peers.csv")
    sources = pd.read_csv(ROOT / "data/sources.csv").set_index("id")
    measures["target_met"] = measures.apply(
        lambda r: meets_target(r.actual, r.target, r.direction), axis=1)
    measures["behind_sector"] = measures.apply(
        lambda r: not meets_target(r.actual, r.benchmark, r.direction), axis=1)
    measures["gap"] = measures.apply(
        lambda r: adverse_gap(r.actual, r.target, r.direction), axis=1)
    # Percentage gap is undefined when the target is zero (e.g. CRI).
    measures["gap_pct"] = measures.gap / measures.target.abs().replace(0, float("nan")) * 100
    measures["attention"] = (measures.target_met == False) | measures.behind_sector
    return measures, history, peers, sources


def history_results(measure, history):
    rows = history[history.measure_id == measure.id].copy().sort_values("year")
    rows["met"] = rows.apply(
        lambda r: meets_target(r.actual, r.target, measure.history_direction), axis=1)
    rows["gap"] = rows.apply(
        lambda r: adverse_gap(r.actual, r.target, measure.history_direction), axis=1)
    rows["change"] = rows.actual.diff()
    return rows


def achievement(measure, rows):
    """Never mix conflicting flooding versions or score C-MeX as a fixed target."""
    if measure.id in {"internal", "cmex"}:
        return None
    valid = rows[rows.target.notna()]
    return int(valid.met.sum()), len(valid)


def peer_rank(measure, peers):
    rows = peers[peers.measure_id == measure.id].copy()
    rows["rank"] = rows.actual.rank(method="min", ascending=measure.direction == "lower").astype(int)
    return rows.sort_values(["rank", "company"])


def format_value(value, measure, history=False):
    if pd.isna(value):
        return "—"
    unit = measure.history_unit if history else measure.unit
    if measure.id == "interruptions":
        minutes, seconds = divmod(round(value), 60)
        return f"{minutes}m {seconds:02d}s"
    if unit.startswith("%"):
        return f"{value:.2f}%"
    return f"{value:.2f}"


def change_description(measure, rows):
    if measure.id == "internal":
        return "Withheld", "Full history needs reconciliation with Ofwat."
    first, last = rows.actual.iloc[0], rows.actual.iloc[-1]
    change = last - first
    if measure.history_unit.startswith("%"):
        return f"{change:+.2f} pp", "Change in percentage points, first to last year."
    if measure.id in {"cmex", "cri"}:
        return f"{change:+.2f} points", "Change in score, first to last year."
    return f"{change / abs(first) * 100:+.1f}%", "Relative change, first to last year."

