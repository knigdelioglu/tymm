#!/usr/bin/env python3
"""TDE10 regression coverage for calendar-neutral block-hour projection."""
import json, shutil, sqlite3, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import build_runtime_course_package as compiler

ROOT = Path(__file__).parents[3] / "courses" / "TDE_10"

class TDE10BlockHourTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "TDE_10"
        shutil.copytree(ROOT, self.tmp, ignore=shutil.ignore_patterns("runtime", "*.sqlite"))
    def tearDown(self): shutil.rmtree(self.tmp.parent, ignore_errors=True)

    def test_tde10_block_hours_project_with_43_hour_theme_totals(self):
        result=compiler.build(self.tmp)
        self.assertEqual(result["status"], "PASS")
        db=sqlite3.connect(self.tmp/"runtime/course_runtime.sqlite")
        self.assertEqual(db.execute("SELECT COUNT(*) FROM timeline_blocks WHERE planned_hours IS NOT NULL").fetchone()[0],16)
        self.assertEqual(dict(db.execute("SELECT theme_id,SUM(planned_hours) FROM timeline_blocks GROUP BY theme_id")),{"TEMA_01":43,"TEMA_02":43,"TEMA_03":43,"TEMA_04":43})
        expected={
            "BLOCK_T1_01_OKUMA":15,"BLOCK_T1_02_KONUSMA":10,"BLOCK_T1_03_DINLEME":8,"BLOCK_T1_04_YAZMA":10,
            "BLOCK_T2_01_OKUMA":15,"BLOCK_T2_02_YAZMA":10,"BLOCK_T2_03_DINLEME":8,"BLOCK_T2_04_KONUSMA":10,
            "BLOCK_T4_01_OKUMA":15,"BLOCK_T4_02_KONUSMA":10,"BLOCK_T4_03_DINLEME":8,"BLOCK_T4_04_YAZMA":10,
        }
        self.assertEqual(dict(db.execute("SELECT block_id,planned_hours FROM timeline_blocks WHERE block_id IN (%s)" % ",".join("?"*len(expected)),tuple(expected))),expected)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM blocks WHERE time_status='OFFICIAL_ANNUAL_PLAN_DERIVED'").fetchone()[0],16)
        manifest=json.loads((self.tmp/"runtime/runtime_manifest.json").read_text())
        self.assertEqual(manifest["timeline_resolution"],"BLOCK_TIME_RESOLVED")
        self.assertIsNone(manifest["timeline_unresolved_fields"]["block_hours"])
        self.assertEqual(manifest["timeline_unresolved_fields"]["calendar_binding"],"UNRESOLVED")

if __name__ == "__main__": unittest.main()
