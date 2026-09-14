#!/usr/bin/env python3
"""Generic teacher-guide projection regression tests."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import teacher_guide_runtime_projection as projection


class GenericTeacherGuideProjectionTests(unittest.TestCase):
    def _source(self, root: Path, *, relation_target: str = "ACT_FORCE_01") -> None:
        (root / "teacher_guide" / "force").mkdir(parents=True)
        (root / "curriculum_map.json").write_text(
            json.dumps({"course_id": "FIZIK_10", "grade": 10}) + "\n",
            encoding="utf-8",
        )
        manifest = {
            "schema_version": "1.0.0",
            "document_type": "TYMM_TEACHER_GUIDE_MANIFEST",
            "course_id": "FIZIK_10",
            "grade": 10,
            "scope_type": "theme",
            "scope_id": "THEME_FORCE",
            "title": "Kuvvet ve Hareket Öğretmen Rehberi",
            "status": "REVIEW_REQUIRED",
            "provenance": {
                "source_ids": ["physics_textbook"],
                "source_locators": ["p42"],
                "content_class": "OFFICIAL_TEXTBOOK",
            },
            "sections": [
                {
                    "section_id": "FORCE_EXPERIMENTS",
                    "title": "Deneyler",
                    "section_type": "EXPERIMENT",
                    "content_status": "REVIEW_REQUIRED",
                    "content_ref": "teacher_guide/force/experiments.json",
                }
            ],
            "validation_contract": {"current_status": "PASS_WITH_WARNINGS"},
        }
        section = {
            "schema_version": "1.0.0",
            "document_type": "TYMM_TEACHER_GUIDE_SECTION",
            "course_id": "FIZIK_10",
            "section_id": "FORCE_EXPERIMENTS",
            "title": "Deneyler",
            "section_type": "EXPERIMENT",
            "content_status": "REVIEW_REQUIRED",
            "guide_units": [
                {
                    "unit_id": "FORCE_CART_UNIT",
                    "title": "Arabalı deney",
                    "content_status": "REVIEW_REQUIRED",
                    "purpose": {"steps": ["Kur", "Gözle", "Yorumla"]},
                    "items": [
                        {
                            "item_id": "FORCE_OBSERVATION_01",
                            "label": "Gözlem kaydı",
                            "item_type": "OBSERVATION",
                            "page_locator": {"page": 42, "figure": "A"},
                            "expected_response": {
                                "observations": ["hız değişimi"],
                                "claim": None,
                            },
                            "acceptance_criteria": ["Veri kaydı bulunur."],
                            "teacher_guidance": "Değişkenleri sabit tut.",
                            "common_misconceptions": {"force": "speed"},
                            "assessment_evidence": None,
                            "differentiation": {
                                "support": ["Hazır tablo ver."],
                                "enrichment": {"prompt": "Grafik çiz."},
                            },
                            "provenance": {
                                "source_ids": ["physics_textbook"],
                                "source_locators": ["p42"],
                                "content_class": "OFFICIAL_TEXTBOOK",
                            },
                            "relations": [
                                {
                                    "target_type": "activity",
                                    "target_id": relation_target,
                                    "relation_type": "references",
                                },
                                {
                                    "target_type": "outcome",
                                    "target_id": "FIZ10.FORCE.1",
                                    "relation_type": "references",
                                },
                            ],
                        }
                    ],
                    "provenance": {
                        "source_ids": ["physics_textbook"],
                        "source_locators": ["p42"],
                        "content_class": "OFFICIAL_TEXTBOOK",
                    },
                }
            ],
            "provenance": {
                "source_ids": ["physics_textbook"],
                "source_locators": ["p42"],
                "content_class": "OFFICIAL_TEXTBOOK",
            },
        }
        (root / "teacher_guide" / "force" / "teacher_guide.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (root / "teacher_guide" / "force" / "experiments.json").write_text(
            json.dumps(section, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def _database(self, *, relation_target: str = "ACT_FORCE_01") -> sqlite3.Connection:
        db = sqlite3.connect(":memory:")
        db.execute("PRAGMA foreign_keys=ON")
        db.executescript(
            """
            CREATE TABLE courses (course_id TEXT PRIMARY KEY);
            CREATE TABLE themes (theme_id TEXT PRIMARY KEY);
            CREATE TABLE blocks (block_id TEXT PRIMARY KEY);
            CREATE TABLE outcomes (
              outcome_id TEXT PRIMARY KEY, theme_id TEXT, outcome_code TEXT
            );
            CREATE TABLE activities (activity_id TEXT PRIMARY KEY);
            CREATE TABLE textbook_sections (section_id TEXT PRIMARY KEY);
            CREATE TABLE forms (form_id TEXT PRIMARY KEY);
            CREATE TABLE assessment_artifacts (artifact_id TEXT PRIMARY KEY);
            CREATE TABLE lesson_plan_packages (package_id TEXT PRIMARY KEY, source_path TEXT);
            """
        )
        db.execute("INSERT INTO courses VALUES ('FIZIK_10')")
        db.execute("INSERT INTO themes VALUES ('THEME_FORCE')")
        db.execute("INSERT INTO blocks VALUES ('BLOCK_FORCE')")
        db.execute(
            "INSERT INTO outcomes VALUES ('OUT_FORCE_01','THEME_FORCE','FIZ10.FORCE.1')"
        )
        if relation_target != "MISSING_ACTIVITY":
            db.execute("INSERT INTO activities VALUES (?)", (relation_target,))
        db.executescript(projection.TEACHER_GUIDE_SCHEMA)
        return db

    def _project(self, root: Path, *, relation_target: str = "ACT_FORCE_01"):
        db = self._database(relation_target=relation_target)
        try:
            result = projection.project_teacher_guides(
                root,
                db,
                {"canonical_content_fingerprint": "sha256:physics"},
            )
            rows = db.execute(
                "SELECT section_type, item_type, expected_response_json, "
                "canonical_payload_sha256 FROM teacher_guide_sections "
                "JOIN teacher_guide_units USING(section_id) "
                "JOIN teacher_guide_items USING(unit_id)"
            ).fetchall()
            relations = db.execute(
                "SELECT target_type, target_id, relation_type "
                "FROM teacher_guide_item_relations ORDER BY relation_order"
            ).fetchall()
            return result, rows, relations
        finally:
            db.close()

    def test_non_tde_scope_and_structured_response_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._source(root)
            result, rows, relations = self._project(root)
            self.assertTrue(result["capability"]["available"])
            self.assertEqual(rows[0][0:2], ("EXPERIMENT", "OBSERVATION"))
            self.assertEqual(
                json.loads(rows[0][2]),
                {"claim": None, "observations": ["hız değişimi"]},
            )
            self.assertRegex(rows[0][3], r"^[0-9a-f]{64}$")
            self.assertIn(("activity", "ACT_FORCE_01", "references"), relations)
            self.assertIn(("outcome", "OUT_FORCE_01", "references"), relations)

    def test_same_source_has_deterministic_item_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._source(root)
            first = self._project(root)
            second = self._project(root)
            self.assertEqual(first[0]["validation"], second[0]["validation"])
            self.assertEqual(first[1], second[1])

    def test_dangling_relation_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._source(root, relation_target="MISSING_ACTIVITY")
            with self.assertRaises(projection.TeacherGuideProjectionError):
                self._project(root, relation_target="MISSING_ACTIVITY")


if __name__ == "__main__":
    unittest.main()
