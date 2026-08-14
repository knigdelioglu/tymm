#!/usr/bin/env python3
"""
TYMM Assessment Generation Standards & Annual Stability Regression Test Suite
(test_assessment_generation_standards.py)

Verifies global assessment generation standards (v1.1.0), annual stability policies,
cross-theme consolidation, and contract policies (v1.4.0):
- PREVIOUS 7 DIMENSIONS:
  1. Source-bound parameters: No ungrounded duration ("3-5 dakika") or tolerances.
  2. No invented score bands: Mathematical conversion does not permit qualitative cutoffs (70=başarılı).
  3. Shared level semantics: Generic level model remains strictly criterion-neutral (no "özgünlük").
  4. Criterion scope purity: No construct contamination (e.g. no "zengin edebî söz varlığı" on grammar).
  5. Observable descriptor standards: Absolutist ("kusursuz", "hiçbir") and mind-reading ("özgüvensizdir") flagged.
  6. Teacher vs. student level semantics consistency: Divergence or added burdens detected.
  7. Evidence-based feedback: Bare praise without OBSERVED EVIDENCE -> EFFECT -> NEXT STEP flagged.
- ANNUAL STABILITY REGRESSION CASES:
  - CASE 1: Same grade + same speaking construct + 3 different themes -> Single annual core artifact (no 3 separate rubrics).
  - CASE 2: Theme name changes but criterion signature same -> REUSE_ANNUAL_CORE.
  - CASE 3: Task title changes -> Task binding changes; core rubric remains unchanged.
  - CASE 4: Official extra criterion in a theme -> REUSE_WITH_CRITERION_EXTENSION evaluated first.
  - CASE 5: Genuinely distinct official construct -> Separate artifact allowed with mandatory source locator + rationale.
  - CASE 6: 7 gap instances resolve into lower unique artifact count (7 gaps -> 3 unique artifacts).
  - CASE 7: Accidental duplicate gap mapping to multiple artifacts -> FAIL.
  - CASE 8: Unmapped REQUIRED gap -> FAIL.
  - CASE 9: Teacher vs. student core criterion set divergence in annual artifact -> FAIL.
- CONTRACT & SPEC AUDIT: Validates contract version 1.4.0, global standard 1.1.0, registry, and QA gates.
"""

import json
import os
import re
import sys
import unittest
from typing import Any, Dict, List, Set, Tuple

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(TESTS_DIR)


def _resolve_contract_path() -> str:
    candidates = [
        os.path.join(SKILL_DIR, "..", "..", "..", "courses", "TDE_9", "production", "assessment_design_contract.json"),
        os.path.abspath(os.path.join(os.getcwd(), "courses", "TDE_9", "production", "assessment_design_contract.json")),
        "/Users/kadir/Desktop/tymm/courses/TDE_9/production/assessment_design_contract.json"
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return candidates[-1]


def _resolve_registry_path() -> str:
    candidates = [
        os.path.join(SKILL_DIR, "..", "..", "..", "courses", "TDE_9", "production", "assessment_artifact_registry.json"),
        os.path.abspath(os.path.join(os.getcwd(), "courses", "TDE_9", "production", "assessment_artifact_registry.json")),
        "/Users/kadir/Desktop/tymm/courses/TDE_9/production/assessment_artifact_registry.json"
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return candidates[-1]


def _resolve_manifest_path() -> str:
    candidates = [
        os.path.join(SKILL_DIR, "..", "..", "..", "courses", "TDE_9", "production", "production_manifest.json"),
        os.path.abspath(os.path.join(os.getcwd(), "courses", "TDE_9", "production", "production_manifest.json")),
        "/Users/kadir/Desktop/tymm/courses/TDE_9/production/production_manifest.json"
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return candidates[-1]


class AssessmentStandardValidator:
    """Helper validator implementing the 12 QA gate checks and pre-generation assertions."""

    ABSOLUTIST_PATTERNS = [
        r"\bkusursuz\b", r"\bmükemmel\b", r"\btamamen\b", r"\bhiçbir\b", r"\bhiç\b",
        r"\bdaima\b", r"\basla\b", r"\btüm sınıf\b", r"\bsınıfın ilgisini tamamen kaybeder\b",
        r"\bhiçbir olumlu etki oluşturamaz\b"
    ]
    MIND_READING_PATTERNS = [
        r"\bözgüvensizdir\b", r"\bisteksizdir\b", r"\bilgisizdir\b", r"\bdikkatsizdir\b",
        r"\bheyecanına yenik düşer\b", r"\bumursamazdır\b"
    ]
    UNGROUNDED_DURATION_PATTERNS = [
        r"\b\d+\s*[-–]\s*\d+\s*(?:dakika|dk|saniye|sn)\b",
        r"\b\d+\s*(?:dakika|dk|saniye|sn)\s*içinde\b",
        r"[±+-]\s*\d+\s*(?:saniye|sn|dakika|kelime)\b"
    ]
    INVENTED_SCORE_BAND_PATTERNS = [
        r"\b\d+\s*=\s*(?:başarılı|geçer|yeterli|ileri|yetkin|orta|zayıf)\b",
        r"\b\d+\s*(?:ve\s*üzeri|üstü)\s*(?:alan|puan)?\s*(?:başarılı|geçer)\b",
        r"\b(?:başarı\s*eşiği|geçme\s*barajı)\s*:\s*\d+\b"
    ]

    @classmethod
    def check_unsupported_parameters(cls, text: str, canonical_has_duration: bool = False) -> Tuple[bool, List[str]]:
        violations = []
        if not canonical_has_duration:
            for pat in cls.UNGROUNDED_DURATION_PATTERNS:
                matches = re.findall(pat, text, re.IGNORECASE)
                if matches:
                    violations.extend([f"Invented duration/tolerance parameter: '{m}'" for m in matches])
        return (len(violations) == 0, violations)

    @classmethod
    def check_score_band_purity(cls, text: str, contract_defines_qualitative_bands: bool = False) -> Tuple[bool, List[str]]:
        violations = []
        if not contract_defines_qualitative_bands:
            for pat in cls.INVENTED_SCORE_BAND_PATTERNS:
                matches = re.findall(pat, text, re.IGNORECASE)
                if matches:
                    violations.extend([f"Invented score band/cutoff: '{m}'" for m in matches])
        return (len(violations) == 0, violations)

    @classmethod
    def check_shared_level_neutrality(cls, level_definitions: Dict[str, str]) -> Tuple[bool, List[str]]:
        forbidden_construct_stems = [
            "özgün", "estetik", "yaratıcı", "yaratıcılık", "etkileyici", "etkileyicilik",
            "akıcı", "akıcılık", "hız", "hızlı", "zengin", "zenginlik"
        ]
        violations = []
        for lvl_id, desc in level_definitions.items():
            for stem in forbidden_construct_stems:
                if stem in desc.lower():
                    violations.append(f"Level definition '{lvl_id}' contains criterion-specific construct: '{stem}'")
        return (len(violations) == 0, violations)

    @classmethod
    def check_criterion_scope_purity(cls, criterion_name: str, descriptor_text: str, allowed_constructs: List[str]) -> Tuple[bool, List[str]]:
        violations = []
        if "türkçenin doğru kullanımı" in criterion_name.lower() or "dil bilgisi" in criterion_name.lower():
            if "zengin edebî söz varlığı" in descriptor_text.lower() or "edebî sanatlar" in descriptor_text.lower():
                violations.append("Construct contamination: Grammar criterion requires literary device enrichment not in construct scope.")
        if "kurgusallık" in criterion_name.lower() or "olay örgüsü" in criterion_name.lower():
            if "estetik anlatım" in descriptor_text.lower() or "özgün benzetmeler" in descriptor_text.lower():
                violations.append("Construct contamination: Plot structure criterion requires aesthetic narrative style.")
        return (len(violations) == 0, violations)

    @classmethod
    def check_descriptor_language(cls, text: str) -> Tuple[bool, List[str]]:
        violations = []
        for pat in cls.ABSOLUTIST_PATTERNS:
            matches = re.findall(pat, text, re.IGNORECASE)
            if matches:
                violations.extend([f"Absolutist descriptor language: '{m}'" for m in matches])
        for pat in cls.MIND_READING_PATTERNS:
            matches = re.findall(pat, text, re.IGNORECASE)
            if matches:
                violations.extend([f"Mental state attribution / mind-reading: '{m}'" for m in matches])
        return (len(violations) == 0, violations)

    @classmethod
    def check_student_teacher_consistency(cls, teacher_descriptor: str, student_descriptor: str) -> Tuple[bool, List[str]]:
        violations = []
        if "bağımsız" in teacher_descriptor.lower() and "öğretmen yardımıyla" in student_descriptor.lower():
            violations.append("Student descriptor diluted cognitive requirement (independent -> with help).")
        if "en az 3 kaynak" in student_descriptor.lower() and "kaynak" not in teacher_descriptor.lower():
            violations.append("Student descriptor introduces additional obligation not present in teacher rubric.")
        return (len(violations) == 0, violations)

    @classmethod
    def check_feedback_structure(cls, feedback_text: str) -> Tuple[bool, str, List[str]]:
        bare_praise_patterns = [
            r"^çok başarılı(?:sın| bir (?:sunum|performans|metin))?[.!]?$",
            r"^harika(?:sın)?[.!]?$",
            r"^tebrikler[.!]?$",
            r"^yetersiz(?:sin)?[.!]?$"
        ]
        for pat in bare_praise_patterns:
            if re.match(pat, feedback_text.strip(), re.IGNORECASE):
                return (False, "FAIL", ["Feedback consists solely of ungrounded bare praise or labeling."])

        has_evidence = any(kw in feedback_text.lower() for kw in ["yansıttın", "kullandın", "belirttin", "gözlendi", "uyguladın", "yer verdin"])
        has_effect = any(kw in feedback_text.lower() for kw in ["kolaylaştırdı", "sağladı", "destekledi", "anlaşılmasını", "akışını"])
        has_next_step = any(kw in feedback_text.lower() for kw in ["bir sonraki", "önerilir", "geliştirmek için", "daha dengeli", "odaklan"])

        if has_evidence and has_effect and has_next_step:
            return (True, "PASS", [])
        elif has_evidence and (has_effect or has_next_step):
            return (True, "REVIEW_REQUIRED", ["Feedback partially structured; full 3-part chain recommended."])
        else:
            return (False, "FAIL", ["Feedback missing OBSERVED EVIDENCE -> EFFECT -> NEXT STEP structure."])


class AnnualAssessmentStabilityValidator:
    """Helper validator implementing Annual Assessment Stability & Cross-Theme Consolidation QA."""

    @classmethod
    def evaluate_reuse_decision(cls, grade: int, skill_domain: str, construct: str,
                                 theme_change_only: bool, has_distinct_construct: bool = False,
                                 has_official_extension: bool = False) -> str:
        """Determines reuse decision according to the 4-tier hierarchy."""
        if has_distinct_construct:
            return "GENERATE_NEW_ASSESSMENT"
        if has_official_extension:
            return "REUSE_WITH_CRITERION_EXTENSION"
        if theme_change_only:
            return "REUSE_WITH_TASK_BINDING"
        return "REUSE_ANNUAL_CORE"

    @classmethod
    def validate_registry_mappings(cls, registry_data: Dict[str, Any],
                                   expected_required_gap_count: int = 7) -> Tuple[bool, List[str]]:
        violations = []
        annual_artifacts = registry_data.get("annual_artifacts", [])
        if not annual_artifacts:
            return (False, ["Registry contains 0 annual_artifacts."])

        seen_gap_instances: Dict[str, str] = {}
        all_covered_gaps: Set[str] = set()

        for art in annual_artifacts:
            art_id = art.get("artifact_id")
            if not art_id:
                violations.append("Annual artifact missing artifact_id.")
                continue

            gaps = art.get("covered_gap_instances", [])
            if not gaps:
                violations.append(f"Annual artifact '{art_id}' covers 0 gap instances.")

            for g in gaps:
                if g in seen_gap_instances:
                    violations.append(f"Duplicate gap mapping: '{g}' mapped to both '{seen_gap_instances[g]}' and '{art_id}'.")
                seen_gap_instances[g] = art_id
                all_covered_gaps.add(g)

            # Check core criteria presence
            if art.get("assessment_family") == "ANALYTIC_RUBRIC":
                core_crits = art.get("core_criteria", [])
                if len(core_crits) < 3:
                    violations.append(f"Rubric '{art_id}' has fewer than 3 core criteria ({len(core_crits)}).")

            # Check task bindings
            task_bindings = art.get("task_bindings", [])
            if len(task_bindings) != len(gaps):
                violations.append(f"Artifact '{art_id}' has {len(task_bindings)} task bindings for {len(gaps)} covered gaps.")

        if len(all_covered_gaps) < expected_required_gap_count:
            violations.append(f"Incomplete gap coverage: expected {expected_required_gap_count}, got {len(all_covered_gaps)}.")

        return (len(violations) == 0, violations)

    @classmethod
    def validate_student_teacher_criteria_identity(cls, teacher_criteria: List[Dict[str, Any]],
                                                   student_criteria: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        violations = []
        t_ids = [c.get("criterion_id") for c in teacher_criteria]
        s_ids = [c.get("criterion_id") for c in student_criteria]
        if t_ids != s_ids:
            violations.append(f"Criteria IDs mismatch: Teacher={t_ids}, Student={s_ids}")

        t_names = [c.get("criterion_name") for c in teacher_criteria]
        s_names = [c.get("criterion_name") for c in student_criteria]
        if t_names != s_names:
            violations.append(f"Criteria names mismatch: Teacher={t_names}, Student={s_names}")

        return (len(violations) == 0, violations)


class TestAssessmentGenerationStandards(unittest.TestCase):
    """Test suite covering the 7 baseline regression cases and 9 annual stability cases."""

    @classmethod
    def setUpClass(cls):
        contract_path = _resolve_contract_path()
        cls.contract_path = contract_path
        if os.path.exists(contract_path):
            with open(contract_path, "r", encoding="utf-8") as f:
                cls.contract_data = json.load(f)
        else:
            cls.contract_data = {}

        registry_path = _resolve_registry_path()
        cls.registry_path = registry_path
        if os.path.exists(registry_path):
            with open(registry_path, "r", encoding="utf-8") as f:
                cls.registry_data = json.load(f)
        else:
            cls.registry_data = {}

        manifest_path = _resolve_manifest_path()
        cls.manifest_path = manifest_path
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                cls.manifest_data = json.load(f)
        else:
            cls.manifest_data = {}

        global_ref_path = os.path.join(SKILL_DIR, "references", "assessment-generation.md")
        cls.global_ref_path = global_ref_path
        if os.path.exists(global_ref_path):
            with open(global_ref_path, "r", encoding="utf-8") as f:
                cls.global_ref_content = f.read()
        else:
            cls.global_ref_content = ""

    # =========================================================================
    # BASELINE TEST CASES (1 to 7)
    # =========================================================================

    def test_case_1_source_bound_no_invented_durations_or_parameters(self):
        """CASE 1: When source has no duration, model must not invent '3-5 dakika' or '±30 saniye'."""
        invented_text = "Öğrenci konuşmasını 3–5 dakika içinde tamamlar ve ±30 saniye süre toleransına uyar."
        is_valid, violations = AssessmentStandardValidator.check_unsupported_parameters(invented_text, canonical_has_duration=False)
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)
        self.assertTrue(any("3–5 dakika" in v or "±30 saniye" in v for v in violations))

        safe_text = "Öğrenci konuşmasını etkinlik için belirlenen süre içinde tamamlar ve süreyi dengeli kullanır."
        is_valid, violations = AssessmentStandardValidator.check_unsupported_parameters(safe_text, canonical_has_duration=False)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_case_2_no_invented_score_bands(self):
        """CASE 2: Optional 100 conversion does not permit deriving cutoffs like 70=başarılı."""
        invented_cutoffs = "Puanlama Sonucu: 70=başarılı, 50=geçer, 89=ileri düzey kabul edilir."
        is_valid, violations = AssessmentStandardValidator.check_score_band_purity(invented_cutoffs, contract_defines_qualitative_bands=False)
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)

        pure_math_table = "Ham Puan 16 = 100, Ham Puan 12 = 75, Ham Puan 8 = 50, Ham Puan 4 = 25 (İsteğe bağlı gösterim)."
        is_valid, violations = AssessmentStandardValidator.check_score_band_purity(pure_math_table, contract_defines_qualitative_bands=False)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_case_3_shared_level_semantics_neutrality(self):
        """CASE 3: Generic shared level model must not contain criterion-specific constructs like 'özgünlük'."""
        contaminated_levels = {
            "LEVEL_4": "Hedeflenen ölçütü eksiksiz, özgün ve yaratıcı biçimde bağımsız sergiler.",
            "LEVEL_3": "Hedeflenen ölçütü büyük ölçüde doğru sergiler."
        }
        is_valid, violations = AssessmentStandardValidator.check_shared_level_neutrality(contaminated_levels)
        self.assertFalse(is_valid)
        self.assertTrue(any("özgünlük" in v or "yaratıcı" in v for v in violations))

        contract_levels = self.contract_data.get("shared_rubric_level_model", {}).get("levels", [])
        self.assertTrue(len(contract_levels) >= 4)
        level_map = {lvl["level_id"]: lvl["general_meaning"] for lvl in contract_levels}
        is_valid, violations = AssessmentStandardValidator.check_shared_level_neutrality(level_map)
        self.assertTrue(is_valid, f"Contract shared levels contained violations: {violations}")

    def test_case_4_criterion_scope_purity(self):
        """CASE 4: 'Türkçenin Doğru Kullanımı' cannot be burdened with ungrounded 'zengin edebî söz varlığı'."""
        contaminated_desc = "Cümle yapısını doğru kurar, imla kurallarına uyar ve zengin edebî söz varlığı ile mecazlar kullanır."
        is_valid, violations = AssessmentStandardValidator.check_criterion_scope_purity(
            criterion_name="Türkçenin Doğru Kullanımı",
            descriptor_text=contaminated_desc,
            allowed_constructs=["dil_bilgisi", "imla", "bagdasiklik", "sozcuk_uyumu"]
        )
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)

        pure_desc = "Cümle yapısını ve bağdaşıklık ögelerini kurallara uygun kullanır; yazım ve noktalama hataları yapmaz."
        is_valid, violations = AssessmentStandardValidator.check_criterion_scope_purity(
            criterion_name="Türkçenin Doğru Kullanımı",
            descriptor_text=pure_desc,
            allowed_constructs=["dil_bilgisi", "imla", "bagdasiklik", "sozcuk_uyumu"]
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_case_5_descriptor_absolutism_and_mental_state_detection(self):
        """CASE 5: Descriptors with 'kusursuz / hiçbir / tamamen' or 'özgüvensizdir' flagged."""
        absolutist_text = "Konuşmayı kusursuz tamamlar, hiçbir hata yapmaz ve tüm sınıfın dikkatini tamamen toplar."
        is_valid, violations = AssessmentStandardValidator.check_descriptor_language(absolutist_text)
        self.assertFalse(is_valid)
        self.assertTrue(any("kusursuz" in v or "hiçbir" in v or "tamamen" in v for v in violations))

        mind_reading_text = "Öğrenci sunum yaparken özgüvensizdir ve isteksiz davranır."
        is_valid, violations = AssessmentStandardValidator.check_descriptor_language(mind_reading_text)
        self.assertFalse(is_valid)
        self.assertTrue(any("özgüvensizdir" in v or "isteksizdir" in v for v in violations))

        behavioral_text = "Ses tonunu ve vurguları metnin anlamına uygun olarak çoğunlukla dengeli ayarlar; belirgin bir aksama gözlenmez."
        is_valid, violations = AssessmentStandardValidator.check_descriptor_language(behavioral_text)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_case_6_student_teacher_level_semantics_consistency(self):
        """CASE 6: Divergence between teacher and student performance standards must be caught."""
        teacher_desc = "Konuşma planını bağımsız ve eksiksiz uygular."
        diluted_student_desc = "Konuşma planını öğretmen yardımıyla uygular."
        is_valid, violations = AssessmentStandardValidator.check_student_teacher_consistency(teacher_desc, diluted_student_desc)
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)

        burdened_student_desc = "Konuşma planını bağımsız uygular ve en az 3 kaynak gösterir."
        is_valid, violations = AssessmentStandardValidator.check_student_teacher_consistency(teacher_desc, burdened_student_desc)
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)

        consistent_student_desc = "Konuşmamı hazırladığım plana uygun olarak kendi başıma eksiksiz sunarım."
        is_valid, violations = AssessmentStandardValidator.check_student_teacher_consistency(teacher_desc, consistent_student_desc)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_case_7_feedback_evidence_model(self):
        """CASE 7: Feedback consisting solely of ungrounded praise ('Çok başarılı') flagged."""
        bare_praise = "Çok başarılı bir sunum yaptın, tebrikler."
        is_valid, status, violations = AssessmentStandardValidator.check_feedback_structure(bare_praise)
        self.assertFalse(is_valid)
        self.assertEqual(status, "FAIL")

        structured_feedback = (
            "Karakterin duygu değişimlerini ses tonuna tutarlı biçimde yansıttın; "
            "bu durum anlatımın takip edilmesini ve anlaşılmasını kolaylaştırdı. "
            "Bir sonraki sunumunda göz temasını sınıfın farklı bölümlerine daha dengeli dağıtmayı dene."
        )
        is_valid, status, violations = AssessmentStandardValidator.check_feedback_structure(structured_feedback)
        self.assertTrue(is_valid)
        self.assertEqual(status, "PASS")
        self.assertEqual(len(violations), 0)

    # =========================================================================
    # ANNUAL ASSESSMENT STABILITY & CONSOLIDATION REGRESSION CASES (STABILITY 1 - 9)
    # =========================================================================

    def test_stability_case_1_same_construct_multi_theme_single_annual_artifact(self):
        """STABILITY CASE 1: Same grade + same speaking construct + 3 themes -> Single annual core artifact expected (no 3 separate rubrics)."""
        speaking_gaps = ["MAT_T2_KONUSMA_RUBRIC", "MAT_T3_KONUSMA_RUBRIC", "MAT_T4_KONUSMA_RUBRIC"]
        # In registry, all 3 speaking gaps must be consolidated into TDE9_KONUSMA_RUBRIC
        annual_artifacts = self.registry_data.get("annual_artifacts", [])
        speaking_artifact = next((a for a in annual_artifacts if a.get("artifact_id") == "TDE9_KONUSMA_RUBRIC"), None)
        self.assertIsNotNone(speaking_artifact, "TDE9_KONUSMA_RUBRIC not found in registry.")
        covered = speaking_artifact.get("covered_gap_instances", [])
        for g in speaking_gaps:
            self.assertIn(g, covered, f"Gap '{g}' not consolidated into TDE9_KONUSMA_RUBRIC.")
        self.assertEqual(len(covered), 3)

    def test_stability_case_2_theme_title_change_reuse_annual_core(self):
        """STABILITY CASE 2: Theme title changes but criterion signature same -> REUSE_ANNUAL_CORE / REUSE_WITH_TASK_BINDING."""
        decision = AnnualAssessmentStabilityValidator.evaluate_reuse_decision(
            grade=9,
            skill_domain="Konuşma / Sözlü Anlatım",
            construct="Sözlü İletişim ve Sunum",
            theme_change_only=True,
            has_distinct_construct=False,
            has_official_extension=False
        )
        self.assertEqual(decision, "REUSE_WITH_TASK_BINDING")
        self.assertNotEqual(decision, "GENERATE_NEW_ASSESSMENT")

    def test_stability_case_3_task_title_change_isolates_to_task_binding(self):
        """STABILITY CASE 3: Task title changes -> Task binding changes; core rubric remains unchanged."""
        speaking_artifact = next((a for a in self.registry_data.get("annual_artifacts", []) if a.get("artifact_id") == "TDE9_KONUSMA_RUBRIC"), None)
        self.assertIsNotNone(speaking_artifact)
        bindings = speaking_artifact.get("task_bindings", [])
        self.assertEqual(len(bindings), 3)
        task_titles = [b.get("task_title") for b in bindings]
        self.assertIn("Karakterimin Yolculuğu Değerlendirme Tablosu / Şiir Dinletisi", task_titles)
        self.assertIn("Benim Mekânım Sunumu Değerlendirme Tablosu", task_titles)
        self.assertIn("Dilimizin Zenginlikleri Sunumu Değerlendirme Tablosu", task_titles)
        # Core criteria count remains 5 regardless of 3 tasks
        self.assertEqual(len(speaking_artifact.get("core_criteria", [])), 5)

    def test_stability_case_4_official_extra_criterion_evaluated_as_extension(self):
        """STABILITY CASE 4: An official extra criterion in a theme -> REUSE_WITH_CRITERION_EXTENSION evaluated first."""
        decision = AnnualAssessmentStabilityValidator.evaluate_reuse_decision(
            grade=9,
            skill_domain="Yazma / Yazılı Anlatım",
            construct="Yazılı Anlatım Ürünü",
            theme_change_only=False,
            has_distinct_construct=False,
            has_official_extension=True
        )
        self.assertEqual(decision, "REUSE_WITH_CRITERION_EXTENSION")
        self.assertNotEqual(decision, "GENERATE_NEW_ASSESSMENT")

    def test_stability_case_5_distinct_construct_permits_new_artifact_with_rationale(self):
        """STABILITY CASE 5: Distinct official construct -> Separate artifact allowed with mandatory source locator + rationale."""
        # Process checklist (TDE4.1) vs Product rubric (TDE4.2/4.3)
        checklist_art = next((a for a in self.registry_data.get("annual_artifacts", []) if a.get("artifact_id") == "TDE9_YAZMA_SUREC_KONTROL_LISTESI"), None)
        self.assertIsNotNone(checklist_art)
        self.assertEqual(checklist_art.get("assessment_family"), "PROCESS_CHECKLIST")
        self.assertIn("TDE4.1", checklist_art.get("covered_outcomes", []))
        self.assertIn("curriculum", checklist_art.get("source_locators", {}))

    def test_stability_case_6_consolidation_ratio_and_lower_unique_artifact_count(self):
        """STABILITY CASE 6: 7 gap instances resolve into 3 unique annual artifacts (Consolidation ratio 2.33)."""
        metrics = self.registry_data.get("summary_metrics", {})
        self.assertEqual(metrics.get("required_gap_instance_count"), 7)
        self.assertEqual(metrics.get("required_unique_artifact_count"), 3)
        self.assertAlmostEqual(metrics.get("consolidation_ratio"), 2.33, places=2)

        manifest_metrics = self.manifest_data.get("summary_metrics", {})
        self.assertEqual(manifest_metrics.get("required_gap_instance_count"), 7)
        self.assertEqual(manifest_metrics.get("required_unique_artifact_count"), 3)
        self.assertEqual(len(self.manifest_data.get("production_queue", [])), 3)

    def test_stability_case_7_duplicate_gap_mapping_fails(self):
        """STABILITY CASE 7: Accidental duplicate gap mapping to multiple artifacts must fail validation."""
        corrupted_registry = {
            "annual_artifacts": [
                {
                    "artifact_id": "ART_1",
                    "covered_gap_instances": ["GAP_A", "GAP_B"],
                    "task_bindings": [{}, {}],
                    "core_criteria": [{}, {}, {}]
                },
                {
                    "artifact_id": "ART_2",
                    "covered_gap_instances": ["GAP_B", "GAP_C"],  # Duplicate GAP_B
                    "task_bindings": [{}, {}],
                    "core_criteria": [{}, {}, {}]
                }
            ]
        }
        is_valid, violations = AnnualAssessmentStabilityValidator.validate_registry_mappings(corrupted_registry, expected_required_gap_count=3)
        self.assertFalse(is_valid)
        self.assertTrue(any("Duplicate gap mapping" in v for v in violations))

    def test_stability_case_8_unmapped_required_gap_fails(self):
        """STABILITY CASE 8: Unmapped REQUIRED gap must fail validation."""
        corrupted_registry = {
            "annual_artifacts": [
                {
                    "artifact_id": "ART_1",
                    "covered_gap_instances": ["GAP_1", "GAP_2"],  # Missing other 5 gaps
                    "task_bindings": [{}, {}],
                    "core_criteria": [{}, {}, {}]
                }
            ]
        }
        is_valid, violations = AnnualAssessmentStabilityValidator.validate_registry_mappings(corrupted_registry, expected_required_gap_count=7)
        self.assertFalse(is_valid)
        self.assertTrue(any("Incomplete gap coverage" in v for v in violations))

    def test_stability_case_9_teacher_student_core_criteria_divergence_fails(self):
        """STABILITY CASE 9: Teacher vs. student core criterion set divergence in annual artifact must fail."""
        teacher_crits = [
            {"criterion_id": "CRT_01", "criterion_name": "İçerik"},
            {"criterion_id": "CRT_02", "criterion_name": "Ses ve Diksiyon"}
        ]
        divergent_student_crits = [
            {"criterion_id": "CRT_01", "criterion_name": "İçerik"},
            {"criterion_id": "CRT_03", "criterion_name": "Beden Dili"}  # Divergent criterion
        ]
        is_valid, violations = AnnualAssessmentStabilityValidator.validate_student_teacher_criteria_identity(teacher_crits, divergent_student_crits)
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)

    # =========================================================================
    # CONTRACT & REGISTRY AUDIT: Version 1.4.1 & Hardening Policies Verification
    # =========================================================================

    def test_contract_audit_v1_4_1_and_policies(self):
        """Verifies that assessment_design_contract.json is upgraded to 1.4.1 with all consolidation and construct policies."""
        meta = self.contract_data.get("metadata", {})
        self.assertEqual(meta.get("contract_version"), "1.4.1")
        self.assertEqual(meta.get("schema_version"), "1.4")
        self.assertEqual(meta.get("applied_global_standard"), "ASSESSMENT_GENERATION_STANDARD_VERSION: 1.1.1")
        self.assertEqual(meta.get("required_gap_instance_count"), 7)
        self.assertEqual(meta.get("required_unique_artifact_count"), 3)

        # Baseline Policies
        self.assertIn("unsupported_parameter_policy", self.contract_data)
        self.assertIn("score_band_policy", self.contract_data)
        self.assertIn("criterion_scope_policy", self.contract_data)
        self.assertIn("descriptor_language_policy", self.contract_data)
        self.assertIn("shared_level_semantics_policy", self.contract_data)
        self.assertIn("student_teacher_consistency_policy", self.contract_data)
        self.assertIn("feedback_policy", self.contract_data)
        self.assertIn("pre_generation_assertions", self.contract_data)

        # Annual Stability & Construct Normalization Policies
        self.assertIn("annual_assessment_stability_policy", self.contract_data)
        self.assertIn("cross_theme_consolidation_policy", self.contract_data)
        self.assertIn("normalized_construct_policy", self.contract_data)
        self.assertIn("annual_core_evidence_policy", self.contract_data)
        self.assertIn("task_specific_feature_isolation_policy", self.contract_data)
        self.assertIn("reusable_process_support_policy", self.contract_data)
        self.assertIn("gap_instance_artifact_separation_policy", self.contract_data)
        self.assertIn("task_binding_policy", self.contract_data)
        self.assertIn("criterion_extension_policy", self.contract_data)
        self.assertIn("new_artifact_exception_policy", self.contract_data)

        # All 19 QA dimensions check
        qa_results = self.contract_data.get("qa_verification_results", {})
        expected_qas = [
            "UNSUPPORTED_PARAMETER_QA", "NO_INVENTED_SCORE_BANDS_QA",
            "SHARED_LEVEL_SEMANTICS_QA", "STUDENT_LEVEL_SEMANTICS_QA",
            "DESCRIPTOR_OBSERVABILITY_QA", "DESCRIPTOR_ABSOLUTISM_QA",
            "ADJACENT_LEVEL_DISTINCTION_QA", "CRITERION_SCOPE_PURITY_QA",
            "FEEDBACK_EVIDENCE_QA", "PROVENANCE_BOUNDARY_QA",
            "SOURCE_RIGHTS_QA", "TEACHER_REVIEW_GATE_QA",
            "ANNUAL_ASSESSMENT_STABILITY_QA", "CROSS_THEME_DUPLICATION_QA",
            "GAP_ARTIFACT_MAPPING_QA", "CORE_CRITERIA_STABILITY_QA",
            "TASK_BINDING_ISOLATION_QA", "CRITERION_EXTENSION_JUSTIFICATION_QA",
            "NEW_ARTIFACT_JUSTIFICATION_QA"
        ]
        for qa_name in expected_qas:
            self.assertIn(qa_name, qa_results, f"Missing QA gate: {qa_name}")
            self.assertIn(qa_results[qa_name].get("status"), ["PASS", "REVIEW_REQUIRED"])

    def test_canonical_registry_integrity(self):
        """Verifies that assessment_artifact_registry.json passes full structural and mapping integrity."""
        is_valid, violations = AnnualAssessmentStabilityValidator.validate_registry_mappings(self.registry_data, expected_required_gap_count=7)
        self.assertTrue(is_valid, f"Registry integrity violations: {violations}")

    # =========================================================================
    # GLOBAL STANDARD REFERENCE AUDIT (v1.1.1)
    # =========================================================================

    def test_global_standard_file_audit_v1_1_1(self):
        """Verifies that references/assessment-generation.md is upgraded to 1.1.1 and has normalized constructs & process scope sections."""
        self.assertTrue(len(self.global_ref_content) > 500)
        self.assertIn("ASSESSMENT_GENERATION_STANDARD_VERSION: 1.1.1", self.global_ref_content)
        self.assertIn("Core Invariant — Source-Bound Parameter Generation", self.global_ref_content)
        self.assertIn("No Invented Score Bands", self.global_ref_content)
        self.assertIn("Shared Level Semantics", self.global_ref_content)
        self.assertIn("Criterion Scope Purity", self.global_ref_content)
        self.assertIn("Observable Descriptor Standard", self.global_ref_content)
        self.assertIn("OBSERVED EVIDENCE → EFFECT → NEXT STEP", self.global_ref_content)
        self.assertIn("Pre-Generation Assertions", self.global_ref_content)
        self.assertIn("Post-Generation Multi-Dimensional QA Suite", self.global_ref_content)
        self.assertIn("Annual Assessment Stability and Cross-Theme Reuse", self.global_ref_content)
        self.assertIn("ANNUAL_ASSESSMENT_STABILITY", self.global_ref_content)
        self.assertIn("THEME_CHANGE_ALONE != NEW_RUBRIC", self.global_ref_content)
        self.assertIn("REUSE_ANNUAL_CORE", self.global_ref_content)
        self.assertIn("REUSE_WITH_TASK_BINDING", self.global_ref_content)
        self.assertIn("REUSE_WITH_CRITERION_EXTENSION", self.global_ref_content)
        self.assertIn("GENERATE_NEW_ASSESSMENT", self.global_ref_content)
        self.assertIn("Normalized Shared Constructs vs. Exact Criterion Match", self.global_ref_content)
        self.assertIn("NORMALIZED_SHARED_CONSTRUCT", self.global_ref_content)
        self.assertIn("EXACT_CRITERION_MATCH", self.global_ref_content)
        self.assertIn("Process Support vs. Annual Core Scope Ayrımı", self.global_ref_content)
        self.assertIn("REUSABLE_PROCESS_SUPPORT", self.global_ref_content)

    # =========================================================================
    # TARGETED FIX REGRESSION TEST CASES (CASES A, B, C, D, E, F)
    # =========================================================================

    def test_case_a_normalized_shared_construct_vs_exact_match(self):
        """CASE A: When theme criteria differ in wording but represent higher-level construct -> NORMALIZED_SHARED_CONSTRUCT used."""
        speaking_art = next((a for a in self.registry_data.get("annual_artifacts", []) if a.get("artifact_id") == "TDE9_KONUSMA_RUBRIC"), None)
        self.assertIsNotNone(speaking_art)
        for crit in speaking_art.get("core_criteria", []):
            self.assertEqual(crit.get("normalization_type"), "NORMALIZED_SHARED_CONSTRUCT")
            self.assertIn("source_criteria_by_theme", crit)
            self.assertIn("normalization_rationale", crit)
            self.assertIn("source_locator", crit)

    def test_case_b_unsupported_annual_writing_criterion_prevention(self):
        """CASE B: 'Özgünlük + Gerçeklik + Etkileyicilik' not evidenced across all themes -> Removed from annual core; writing has 4 pure core criteria."""
        writing_art = next((a for a in self.registry_data.get("annual_artifacts", []) if a.get("artifact_id") == "TDE9_YAZMA_RUBRIC"), None)
        self.assertIsNotNone(writing_art)
        core_crits = writing_art.get("core_criteria", [])
        self.assertEqual(len(core_crits), 4, f"Writing rubric expected 4 core criteria, got {len(core_crits)}")
        crit_names = [c.get("criterion_name") for c in core_crits]
        self.assertNotIn("Özgünlük, Gerçeklik ve Etkileyicilik", crit_names)
        self.assertIn("Tema, Anlam ve Ana Düşünce/Duygu Tutarlılığı", crit_names)
        self.assertIn("Metin Yapısı ve Türe Özgü Kurgu", crit_names)
        self.assertIn("Dil, Anlatım ve Söz Varlığının Bağlama Uygunluğu", crit_names)
        self.assertIn("Türkçenin Kuralları (İmla, Noktalama ve Bağdaşıklık)", crit_names)

    def test_case_c_task_specific_features_isolated_in_task_bindings(self):
        """CASE C: Genre/task-specific features (meter/rhyme, infographic multimodal layout, autobiography chronology) isolated in task bindings."""
        writing_art = next((a for a in self.registry_data.get("annual_artifacts", []) if a.get("artifact_id") == "TDE9_YAZMA_RUBRIC"), None)
        self.assertIsNotNone(writing_art)
        for crit in writing_art.get("core_criteria", []):
            desc = crit.get("description", "").lower()
            self.assertNotIn("kafiye", desc)
            self.assertNotIn("redif", desc)
            self.assertNotIn("infografik", desc)
            self.assertNotIn("otobiyografi", desc)

        # Verified in task bindings
        bindings = writing_art.get("task_bindings", [])
        self.assertEqual(len(bindings), 3)
        t2_binding = next(b for b in bindings if b.get("theme_id") == "TEMA_02")
        self.assertIn("kafiye", t2_binding.get("evidence_being_observed", "").lower())
        t3_binding = next(b for b in bindings if b.get("theme_id") == "TEMA_03")
        self.assertIn("infografik", t3_binding.get("evidence_being_observed", "").lower())
        t4_binding = next(b for b in bindings if b.get("theme_id") == "TEMA_04")
        self.assertIn("otobiyografi", t4_binding.get("evidence_being_observed", "").lower())

    def test_case_d_speaking_visual_presentation_material_isolation(self):
        """CASE D: Presentation material / slides not mandatory in core descriptor; isolated to task bindings."""
        speaking_art = next((a for a in self.registry_data.get("annual_artifacts", []) if a.get("artifact_id") == "TDE9_KONUSMA_RUBRIC"), None)
        self.assertIsNotNone(speaking_art)
        crt_02 = next(c for c in speaking_art.get("core_criteria", []) if c.get("criterion_id") == "CRT_SPK_CORE_02")
        desc = crt_02.get("description", "").lower()
        self.assertNotIn("slayt", desc)
        self.assertNotIn("görsel", desc)
        self.assertNotIn("materyal", desc)
        self.assertIn("giriş-gelişme-sonuç", desc)
        self.assertIn("süreyi", desc)

    def test_case_e_process_checklist_reusable_process_support_scope(self):
        """CASE E: Process checklist has scope REUSABLE_PROCESS_SUPPORT, reuse_policy REUSE_ACROSS_THEMES, anchor MAT_T4_YAZMA_KONTROL_LISTESI."""
        checklist_art = next((a for a in self.registry_data.get("annual_artifacts", []) if a.get("artifact_id") == "TDE9_YAZMA_SUREC_KONTROL_LISTESI"), None)
        self.assertIsNotNone(checklist_art)
        self.assertEqual(checklist_art.get("scope"), "REUSABLE_PROCESS_SUPPORT")
        self.assertEqual(checklist_art.get("reuse_policy"), "REUSE_ACROSS_THEMES")
        self.assertEqual(checklist_art.get("official_gap_anchor"), "MAT_T4_YAZMA_KONTROL_LISTESI")
        self.assertEqual(checklist_art.get("required_for"), "TEMA_04")
        self.assertEqual(checklist_art.get("covered_gap_instances"), ["MAT_T4_YAZMA_KONTROL_LISTESI"])

    def test_case_f_flexible_annual_core_criteria_count(self):
        """CASE F: System supports varying evidence-based core criteria count (Speaking = 5, Writing = 4; not rigid 5)."""
        speaking_art = next((a for a in self.registry_data.get("annual_artifacts", []) if a.get("artifact_id") == "TDE9_KONUSMA_RUBRIC"), None)
        writing_art = next((a for a in self.registry_data.get("annual_artifacts", []) if a.get("artifact_id") == "TDE9_YAZMA_RUBRIC"), None)
        self.assertEqual(len(speaking_art.get("core_criteria", [])), 5)
        self.assertEqual(len(writing_art.get("core_criteria", [])), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)

