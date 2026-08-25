#!/usr/bin/env python3
"""Regression tests for P6 differentiation, accessibility, and media fallback contracts."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import apply_classroom_adaptations
import validate_classroom_adaptations

ROOT = Path(__file__).parents[3] / "courses" / "TDE_9"


class ClassroomAdaptationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "TDE_9"
        shutil.copytree(ROOT, self.tmp, ignore=shutil.ignore_patterns("runtime", "*.sqlite"))
        result = apply_classroom_adaptations.apply(self.tmp, write=True)
        self.assertEqual(result["status"], "PASS")
        self.assertGreater(result["target_packages"], 0)

    def tearDown(self):
        shutil.rmtree(self.tmp.parent, ignore_errors=True)

    def _read_manifest(self):
        path = self.tmp / "production" / "classroom_adaptation_manifest.json"
        return path, json.loads(path.read_text(encoding="utf-8"))

    def _plan_path(self, package):
        return self.tmp / package["path"]

    def test_materialized_contract_passes(self):
        result = validate_classroom_adaptations.validate_course(self.tmp)
        self.assertEqual(result["status"], "PASS", result)
        self.assertGreater(result["media_dependent_packages"], 0)
        self.assertGreater(result["live_performance_packages"], 0)

    def test_target_package_cannot_drop_adaptation(self):
        _, manifest = self._read_manifest()
        package = manifest["packages"][0]
        path = self._plan_path(package)
        plan = json.loads(path.read_text(encoding="utf-8"))
        plan.pop("classroom_adaptations", None)
        path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

        result = validate_classroom_adaptations.validate_course(self.tmp)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("CLASSROOM_ADAPTATIONS_REQUIRED" in item for item in result["errors"]))

    def test_media_transcript_cannot_replace_listening_by_default(self):
        _, manifest = self._read_manifest()
        package = next(item for item in manifest["packages"] if "MEDIA_DEPENDENT" in item["trigger_categories"])
        path = self._plan_path(package)
        plan = json.loads(path.read_text(encoding="utf-8"))
        plan["classroom_adaptations"]["media_fallback"]["transcript_is_support_not_default_substitute"] = False
        path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

        result = validate_classroom_adaptations.validate_course(self.tmp)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("TRANSCRIPT_IS_SUPPORT_NOT_DEFAULT_SUBSTITUTE" in item for item in result["errors"]))

    def test_speaking_cannot_become_written_only_substitution(self):
        _, manifest = self._read_manifest()
        package = next(item for item in manifest["packages"] if "LIVE_PERFORMANCE" in item["trigger_categories"])
        path = self._plan_path(package)
        plan = json.loads(path.read_text(encoding="utf-8"))
        plan["classroom_adaptations"]["live_performance_access"]["written_only_substitution_allowed"] = True
        path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

        result = validate_classroom_adaptations.validate_course(self.tmp)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("WRITTEN_ONLY_SPEAKING_SUBSTITUTION_FORBIDDEN" in item for item in result["errors"]))

    def test_manifest_cannot_omit_discovered_target(self):
        manifest_path, manifest = self._read_manifest()
        manifest["packages"] = manifest["packages"][1:]
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

        result = validate_classroom_adaptations.validate_course(self.tmp)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("ADAPTATION_PACKAGE_SET_MISMATCH" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
