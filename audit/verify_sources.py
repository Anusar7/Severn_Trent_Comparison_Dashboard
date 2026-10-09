"""Independently extract official PDF values and compare with dashboard CSVs.

Optional audit dependency: pip install pypdf==6.10.0 (tested release).
Run with paths to the four original documents; see README.md in the project root.
This script never overwrites dashboard inputs.
"""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
for name in ["ofwat", "apr2025", "apr2021", "apr2023"]:
    parser.add_argument("--" + name, type=Path, required=True)
args = parser.parse_args()
docs = {key: PdfReader(path) for key, path in vars(args).items()}


def read_csv(name):
    with (ROOT / "data" / name).open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def tokens(text, name):
    match = re.search(r"^" + re.escape(name) + r"(?:\d+(?:\s*,\s*\d+)*)?\s+(?=[0-9-])([^\n]*)", text, re.M)
    if not match:
        raise ValueError(name)
    segment = match[1]
    for line in text[match.end():].splitlines():
        if not line.strip():
            continue
        if re.search("[A-Za-z]", line):
            break
        segment += " " + line
    return re.findall(r"\d\d:\d\d:\d\d|[-+]?\d+(?:\.\d+)?", segment)


def seconds(value):
    return sum(int(v) * u for v, u in zip(value.split(":"), [3600, 60, 1]))


checks = []


def check(kind, key, source, page, extracted, stored, note=""):
    status = "MATCH" if abs(float(extracted) - float(stored)) < 1e-8 else "FAIL"
    if kind == "APR history" and key == "cmex/2024/25" and extracted == 74.42 and float(stored) == 74.43:
        status = "DOCUMENTED SOURCE DIFFERENCE"
        note = "App uses Ofwat 74.43, independently matched in peer/latest checks; APR is 74.42."
    checks.append(dict(kind=kind, key=key, source=source, pdf_page=page,
                       extracted=extracted, stored=stored, status=status, note=note))


metrics = read_csv("measures.csv")
history = read_csv("history.csv")
peers = read_csv("peers.csv")
name_map = {"South West Water – South West region": "South West region",
            "South West Water – Bristol region": "Bristol region",
            "Northumbrian – Northern": "Northumbrian Water",
            "Northumbrian – Essex & Suffolk": "Northumbrian Water",
            "South Staffs – Staffordshire": "South Staffs Water",
            "South Staffs – Cambridge": "South Staffs Water"}
for metric in metrics:
    mid = metric["id"]
    page = int(metric["page"])
    text = docs["ofwat"].pages[page - 1].extract_text()
    for peer in [p for p in peers if p["measure_id"] == mid]:
        company = name_map.get(peer["company"], peer["company"])
        if metric["domain"] == "Wastewater" and company == "South West region":
            company = "South West Water"
        values = tokens(text, company)
        if mid == "interruptions":
            actual = seconds(values[1])
        elif mid == "pcc" and company == "South Staffs Water":
            actual = float(values[3 if peer["company"].endswith("Cambridge") else 2])
        elif mid == "leakage":
            idx = 3 if peer["company"].endswith(("Suffolk", "Cambridge")) else 2
            actual = -float(values[idx if company in {"Northumbrian Water", "South Staffs Water"} else 1])
        else:
            actual = float(values[1])
        check("Peer", mid + "/" + peer["company"], "ofwat25", page, actual, peer["actual"])
        if peer["company"] == "Severn Trent Water":
            check("Latest ST actual", mid, "ofwat25", page, actual, metric["actual"])
    name = "Sector median" if metric["benchmark_type"] == "median" else "Sector" if mid == "leakage" else "Sector average"
    values = tokens(text, name)
    benchmark = -float(values[0]) if mid == "leakage" else seconds(values[1]) if mid == "interruptions" else float(values[1])
    check("Sector benchmark", mid, "ofwat25", page, benchmark, metric["benchmark"])
    st = tokens(text, "Severn Trent Water")
    if mid in {"cri", "treatment"}:
        check("Payment deadband", mid, "ofwat25", page, st[2], metric["deadband"])
    elif mid != "cmex":
        target = seconds(st[2]) if mid == "interruptions" else -float(st[2]) if mid == "leakage" else float(st[3 if mid == "pcc" else 2])
        check("Latest full target", mid, "ofwat25", page, target, metric["target"])

apr = docs["apr2025"].pages[24].extract_text()
labels = {"cmex": "Customer measure of experience", "psr": "circumstances - PSR reach",
          "leakage": "Leakage", "pcc": "Per capita consumption", "interruptions": "Water supply interruptions",
          "cri": "Good to drink Water quality compliance", "outage": "Unplanned outage", "mains": "Mains Repairs",
          "internal": "Wastewater taken safely away Internal sewer flooding", "pollution": "Pollution incidents",
          "treatment": "Treatment works compliance", "collapses": "Sewer collapses"}
for metric in metrics:
    mid = metric["id"]
    line = next(line for line in apr.splitlines() if labels[mid] in line)
    if mid == "cmex":
        actuals = [float(v) for v in re.findall(r"(\d+\.\d+) / \d+\w+ N/A", line)]
    elif mid == "interruptions":
        actuals = [seconds(v) for v in re.findall(r"\d\d:\d\d:\d\d", line)]
    else:
        actuals = [float(v) for v in re.findall(r"([-+]?\d+(?:\.\d+)?)\s+(?:Yes|No)", line)]
    rows = [h for h in history if h["measure_id"] == mid]
    assert len(actuals) == len(rows) == 5
    for actual, row in zip(actuals, rows):
        check("APR history", mid + "/" + row["year"], "apr25", 25, actual, row["actual"])

# APR2021 is a two-page table: named rows on p50, numeric rows on p51.
# Unique first-target/actual pairs identify each row independently of CSV values.
schedule = docs["apr2021"].pages[50].extract_text()
prefixes = {"cri": "0.00  1.53", "psr": "2.1  2.6", "mains": "123.5  122.0",
            "outage": "2.34  1.05", "internal": "1.68  1.86", "pollution": "24.51  20.60",
            "treatment": "100.00  99.60", "collapses": "8.00  7.74"}
schedule_targets = {}
for mid, prefix in prefixes.items():
    line = next(line for line in schedule.splitlines() if line.strip().startswith(prefix))
    numbers = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", line)]
    schedule_targets[mid] = [numbers[0]] + numbers[-4:]
line = next(line for line in schedule.splitlines() if line.startswith("06m 30s"))
durations = [int(m) * 60 + int(s) for m, s in re.findall(r"(\d+)m (\d+)s", line)]
schedule_targets["interruptions"] = [durations[0]] + durations[-4:]
revised = docs["apr2023"].pages[31].extract_text()
leakage = revised.split("AMP7 Targets", 1)[1].split("Restated", 1)[0]
pcc = revised.split("G03", 1)[1].split("AMP7 Targets", 1)[1].split("Restated", 1)[0]
for mid, text in [("leakage", leakage), ("pcc", pcc)]:
    schedule_targets[mid] = [float(v) for v in re.findall(r"(\d+\.\d+)%", text)]
for mid, targets in schedule_targets.items():
    rows = [h for h in history if h["measure_id"] == mid]
    assert len(targets) == len(rows) == 5
    source, page = ("apr23", 32) if mid in {"pcc", "leakage"} else ("apr21", 51)
    for target, row in zip(targets, rows):
        check("Historical target", mid + "/" + row["year"], source, page, target, row["target"])
    if mid in {"cri", "treatment"}:
        metric = next(m for m in metrics if m["id"] == mid)
        check("Latest full target", mid, source, page, targets[-1], metric["target"])

with (ROOT / "audit/source-checks.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(checks[0]))
    writer.writeheader()
    writer.writerows(checks)
manifest = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}" for path in vars(args).values()]
(ROOT / "audit/source-sha256.txt").write_text("\n".join(manifest) + "\n")
input_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted((ROOT / "data").glob("*.csv"))}
(ROOT / "audit/input-sha256.json").write_text(json.dumps(input_hashes, indent=2) + "\n")
failures = [row for row in checks if row["status"] == "FAIL"]
print(f"{len(checks)} checks; {len(failures)} failures; 1 documented APR/Ofwat C-MeX difference.")
for row in failures:
    print(row)
raise SystemExit(bool(failures))
