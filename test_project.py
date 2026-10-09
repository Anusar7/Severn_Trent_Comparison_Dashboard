"""Run with: python -m unittest -v test_project.py"""
import unittest
import hashlib
import json
from pathlib import Path
import pandas as pd
from streamlit.testing.v1 import AppTest
from analysis import load_data, meets_target, adverse_gap, history_results, achievement, peer_rank
from charts import trend_chart, peer_chart

ROOT = Path(__file__).resolve().parent


class DataTests(unittest.TestCase):
    def setUp(self):
        self.m, self.h, self.p, self.s = load_data()

    def test_source_audit_has_no_unexplained_difference(self):
        audit = pd.read_csv(ROOT / "audit/source-checks.csv")
        self.assertEqual(len(audit), 335)
        self.assertEqual((audit.status == "FAIL").sum(), 0)
        self.assertEqual((audit.status == "DOCUMENTED SOURCE DIFFERENCE").sum(), 1)
        hashes = json.loads((ROOT / "audit/input-sha256.json").read_text())
        for name, expected in hashes.items():
            self.assertEqual(hashlib.sha256((ROOT / "data" / name).read_bytes()).hexdigest(), expected,
                             "Inputs changed: repeat the official-source audit.")

    def test_data_integrity_and_denominators(self):
        self.assertEqual((len(self.m), len(self.h), len(self.p)), (12, 60, 183))
        self.assertFalse(self.m.id.duplicated().any())
        self.assertFalse(self.h.duplicated(["measure_id", "year"]).any())
        self.assertFalse(self.p.duplicated(["measure_id", "company"]).any())
        self.assertEqual(set(self.h.measure_id), set(self.m.id))
        self.assertEqual((self.m.target_met == False).sum(), 5)
        self.assertEqual(self.m.target.notna().sum(), 11)
        self.assertEqual(self.m.behind_sector.sum(), 4)
        self.assertEqual(self.m.attention.sum(), 8)
        for _, m in self.m.iterrows():
            self.assertEqual(self.p[(self.p.measure_id == m.id) & (self.p.company == "Severn Trent Water")].actual.iloc[0], m.actual)
            self.assertEqual(len(self.h[self.h.measure_id == m.id]), 5)

    def test_equality_zero_and_higher_is_better(self):
        self.assertTrue(meets_target(1.63, 1.63, "lower"))
        self.assertFalse(meets_target(99.46, 100, "higher"))
        self.assertTrue(meets_target(99.46, 99, "higher"))
        self.assertEqual(adverse_gap(99.46, 100, "higher"), .54)
        self.assertIsNone(meets_target(74.43, float("nan"), "higher"))
        self.assertTrue(pd.isna(self.m[self.m.id == "cri"].gap_pct.iloc[0]))

    def test_conflicting_sources_are_not_combined(self):
        m = self.m[self.m.id == "internal"].iloc[0]
        h = history_results(m, self.h)
        self.assertEqual(m.actual, 1.52)
        self.assertEqual(h.actual.iloc[-1], 1.33)
        self.assertIsNone(achievement(m, h))
        self.assertFalse(m.target_met)
        self.assertTrue(h.met.iloc[-1])

    def test_calendar_year_units_ties_and_charts(self):
        pcc = self.m[self.m.id == "pcc"].iloc[0]
        ranks = peer_rank(pcc, self.p)
        self.assertEqual(ranks[ranks.actual == 133.1]["rank"].nunique(), 1)
        self.assertEqual(pcc.direction, "lower")
        self.assertEqual(pcc.history_direction, "higher")
        for _, m in self.m.iterrows():
            h = history_results(m, self.h)
            if m.id in {"cri", "pollution", "treatment"}:
                self.assertEqual(str(h.period.iloc[-1]), "2024")
            fig = trend_chart(m, h)
            self.assertEqual(list(fig.data[0].y), list(h.actual))
            if m.id == "internal":
                self.assertEqual(list(fig.data[-1].y), [1.52])
            fig.to_json()
            peer_chart(m, peer_rank(m, self.p)).to_json()


class AppTests(unittest.TestCase):
    def test_all_filters_and_measure_views(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "5 / 11")
        for scope in ["Target missed or behind sector", "All 12 measures", "Full target missed", "Behind sector"]:
            for domain in ["All services", "Wastewater", "Water", "Customer"]:
                app.selectbox[0].set_value(scope)
                app.selectbox[1].set_value(domain).run()
                self.assertFalse(app.exception, (scope, domain))
        app.radio[0].set_value("Measure explorer").run()
        measures, _, _, _ = load_data()
        for mid in measures.id:
            app.selectbox[0].set_value(mid).run()
            self.assertFalse(app.exception, mid)
            self.assertEqual(len(app.get("plotly_chart")), 2)
            if mid == "internal":
                self.assertTrue(app.warning)
                self.assertEqual(app.metric[4].value, "Not scored")
        app.radio[0].set_value("Recommendations").run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.success), 1)


if __name__ == "__main__":
    unittest.main()
