#!/usr/bin/env python3
"""
TYMM Assessment Generation Standards Regression Test Suite (test_assessment_generation_standards.py)

Verifies the hardened global assessment generation standards and contract policies:
- CASE 1: Source-bound parameters: No ungrounded duration ("3-5 dakika") or tolerance parameters.
- CASE 2: No invented score bands: Mathematical conversion does not permit qualitative cutoffs (70=başarılı).
- CASE 3: Shared level semantics: Generic level model remains strictly criterion-neutral (no "özgünlük").
- CASE 4: Criterion scope purity: No construct contamination (e.g. no "zengin edebî söz varlığı" on grammar).
- CASE 5: Observable descriptor standards: Absolutist ("kusursuz", "hiçbir") and mind-reading ("özgüvensizdir") terms flagged.
- CASE 6: Teacher vs. student level semantics consistency: Divergence or added burdens detected.
- CASE 7: Evidence-based feedback: Bare praise without OBSERVED EVIDENCE -> EFFECT -> NEXT STEP flagged.
- CONTRACT & SPEC AUDIT: Validates contract version 1.3.0, references, and QA gates.
"""

import json
import os
import re
import sys
import unittest
from typing import Any, Dict, List, Tuple

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
        # Case: Grammar criterion contaminated with forced literary devices
        if "türkçenin doğru kullanımı" in criterion_name.lower() or "dil bilgisi" in criterion_name.lower():
            if "zengin edebî söz varlığı" in descriptor_text.lower() or "edebî sanatlar" in descriptor_text.lower():
                violations.append("Construct contamination: Grammar criterion requires literary device enrichment not in construct scope.")
        # Case: Plot structure contaminated with aesthetic style requirements
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
        # Check if student descriptor lowers standard or drops core evidence
        if "bağımsız" in teacher_descriptor.lower() and "öğretmen yardımıyla" in student_descriptor.lower():
            violations.append("Student descriptor diluted cognitive requirement (independent -> with help).")
        # Check if student descriptor adds new ungrounded burden
        if "en az 3 kaynak" in student_descriptor.lower() and "kaynak" not in teacher_descriptor.lower():
            violations.append("Student descriptor introduces additional obligation not present in teacher rubric.")
        return (len(violations) == 0, violations)

    @classmethod
    def check_feedback_structure(cls, feedback_text: str) -> Tuple[bool, str, List[str]]:
        """Validates OBSERVED EVIDENCE -> EFFECT -> NEXT STEP model."""
        # Bare praise check
        bare_praise_patterns = [
            r"^çok başarılı(?:sın| bir (?:sunum|performans|metin))?[.!]?$",
            r"^harika(?:sın)?[.!]?$",
            r"^tebrikler[.!]?$",
            r"^yetersiz(?:sin)?[.!]?$"
        ]
        for pat in bare_praise_patterns:
            if re.match(pat, feedback_text.strip(), re.IGNORECASE):
                return (False, "FAIL", ["Feedback consists solely of ungrounded bare praise or labeling."])

        # Structured component heuristic
        has_evidence = any(kw in feedback_text.lower() for kw in ["yansıttın", "kullandın", "belirttin", "gözlendi", "uyguladın", "yer verdin"])
        has_effect = any(kw in feedback_text.lower() for kw in ["kolaylaştırdı", "sağladı", "destekledi", "anlaşılmasını", "akışını"])
        has_next_step = any(kw in feedback_text.lower() for kw in ["bir sonraki", "önerilir", "geliştirmek için", "daha dengeli", "odaklan"])

        if has_evidence and has_effect and has_next_step:
            return (True, "PASS", [])
        elif has_evidence and (has_effect or has_next_step):
            return (True, "REVIEW_REQUIRED", ["Feedback partially structured; full 3-part chain recommended."])
        else:
            return (False, "FAIL", ["Feedback missing OBSERVED EVIDENCE -> EFFECT -> NEXT STEP structure."])


class TestAssessmentGenerationStandards(unittest.TestCase):
    """Test suite covering the 7 regression cases and contract specification integrity."""

    @classmethod
    def setUpClass(cls):
        contract_path = _resolve_contract_path()
        cls.contract_path = contract_path
        if os.path.exists(contract_path):
            with open(contract_path, "r", encoding="utf-8") as f:
                cls.contract_data = json.load(f)
        else:
            cls.contract_data = {}

        global_ref_path = os.path.join(SKILL_DIR, "references", "assessment-generation.md")
        cls.global_ref_path = global_ref_path
        if os.path.exists(global_ref_path):
            with open(global_ref_path, "r", encoding="utf-8") as f:
                cls.global_ref_content = f.read()
        else:
            cls.global_ref_content = ""

    # -------------------------------------------------------------------------
    # CASE 1: Source-bound parameters: No invented durations or tolerances
    # -------------------------------------------------------------------------
    def test_case_1_source_bound_no_invented_durations_or_parameters(self):
        """CASE 1: When source has no duration, model must not invent '3-5 dakika' or '±30 saniye'."""
        # Negative test: Ungrounded invented parameter should fail
        invented_text = "Öğrenci konuşmasını 3–5 dakika içinde tamamlar ve ±30 saniye süre toleransına uyar."
        is_valid, violations = AssessmentStandardValidator.check_unsupported_parameters(invented_text, canonical_has_duration=False)
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)
        self.assertTrue(any("3–5 dakika" in v or "±30 saniye" in v for v in violations))

        # Positive test: Parameterized source-safe phrasing should pass
        safe_text = "Öğrenci konuşmasını etkinlik için belirlenen süre içinde tamamlar ve süreyi dengeli kullanır."
        is_valid, violations = AssessmentStandardValidator.check_unsupported_parameters(safe_text, canonical_has_duration=False)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    # -------------------------------------------------------------------------
    # CASE 2: No invented score bands from mathematical conversion
    # -------------------------------------------------------------------------
    def test_case_2_no_invented_score_bands(self):
        """CASE 2: Optional 100 conversion does not permit deriving cutoffs like 70=başarılı."""
        # Negative test: Invented cutoff should fail
        invented_cutoffs = "Puanlama Sonucu: 70=başarılı, 50=geçer, 89=ileri düzey kabul edilir."
        is_valid, violations = AssessmentStandardValidator.check_score_band_purity(invented_cutoffs, contract_defines_qualitative_bands=False)
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)

        # Positive test: Pure mathematical conversion table without qualitative cutoffs should pass
        pure_math_table = "Ham Puan 16 = 100, Ham Puan 12 = 75, Ham Puan 8 = 50, Ham Puan 4 = 25 (İsteğe bağlı gösterim)."
        is_valid, violations = AssessmentStandardValidator.check_score_band_purity(pure_math_table, contract_defines_qualitative_bands=False)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    # -------------------------------------------------------------------------
    # CASE 3: Shared level model criterion-neutrality
    # -------------------------------------------------------------------------
    def test_case_3_shared_level_semantics_neutrality(self):
        """CASE 3: Generic shared level model must not contain criterion-specific constructs like 'özgünlük'."""
        # Negative test: Generic level containing 'özgünlük' should fail
        contaminated_levels = {
            "LEVEL_4": "Hedeflenen ölçütü eksiksiz, özgün ve yaratıcı biçimde bağımsız sergiler.",
            "LEVEL_3": "Hedeflenen ölçütü büyük ölçüde doğru sergiler."
        }
        is_valid, violations = AssessmentStandardValidator.check_shared_level_neutrality(contaminated_levels)
        self.assertFalse(is_valid)
        self.assertTrue(any("özgünlük" in v or "yaratıcı" in v for v in violations))

        # Positive test: Contract's shared level model should be 100% criterion-neutral
        contract_levels = self.contract_data.get("shared_rubric_level_model", {}).get("levels", [])
        self.assertTrue(len(contract_levels) >= 4)
        level_map = {lvl["level_id"]: lvl["general_meaning"] for lvl in contract_levels}
        is_valid, violations = AssessmentStandardValidator.check_shared_level_neutrality(level_map)
        self.assertTrue(is_valid, f"Contract shared levels contained violations: {violations}")

    # -------------------------------------------------------------------------
    # CASE 4: Criterion scope purity (no construct contamination)
    # -------------------------------------------------------------------------
    def test_case_4_criterion_scope_purity(self):
        """CASE 4: 'Türkçenin Doğru Kullanımı' cannot be burdened with ungrounded 'zengin edebî söz varlığı'."""
        # Negative test: Contaminating grammar with forced literary vocabulary
        contaminated_desc = "Cümle yapısını doğru kurar, imla kurallarına uyar ve zengin edebî söz varlığı ile mecazlar kullanır."
        is_valid, violations = AssessmentStandardValidator.check_criterion_scope_purity(
            criterion_name="Türkçenin Doğru Kullanımı",
            descriptor_text=contaminated_desc,
            allowed_constructs=["dil_bilgisi", "imla", "bagdasiklik", "sozcuk_uyumu"]
        )
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)

        # Positive test: Pure grammar descriptor should pass
        pure_desc = "Cümle yapısını ve bağdaşıklık ögelerini kurallara uygun kullanır; yazım ve noktalama hataları yapmaz."
        is_valid, violations = AssessmentStandardValidator.check_criterion_scope_purity(
            criterion_name="Türkçenin Doğru Kullanımı",
            descriptor_text=pure_desc,
            allowed_constructs=["dil_bilgisi", "imla", "bagdasiklik", "sozcuk_uyumu"]
        )
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    # -------------------------------------------------------------------------
    # CASE 5: Observable descriptors and absolutism detection
    # -------------------------------------------------------------------------
    def test_case_5_descriptor_absolutism_and_mental_state_detection(self):
        """CASE 5: Descriptors with 'kusursuz / hiçbir / tamamen' or 'özgüvensizdir' flagged."""
        # Negative test: Absolutist language
        absolutist_text = "Konuşmayı kusursuz tamamlar, hiçbir hata yapmaz ve tüm sınıfın dikkatini tamamen toplar."
        is_valid, violations = AssessmentStandardValidator.check_descriptor_language(absolutist_text)
        self.assertFalse(is_valid)
        self.assertTrue(any("kusursuz" in v or "hiçbir" in v or "tamamen" in v for v in violations))

        # Negative test: Mind-reading / internal state attribution
        mind_reading_text = "Öğrenci sunum yaparken özgüvensizdir ve isteksiz davranır."
        is_valid, violations = AssessmentStandardValidator.check_descriptor_language(mind_reading_text)
        self.assertFalse(is_valid)
        self.assertTrue(any("özgüvensizdir" in v or "isteksizdir" in v for v in violations))

        # Positive test: Behavior-based evidence language
        behavioral_text = "Ses tonunu ve vurguları metnin anlamına uygun olarak çoğunlukla dengeli ayarlar; belirgin bir aksama gözlenmez."
        is_valid, violations = AssessmentStandardValidator.check_descriptor_language(behavioral_text)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    # -------------------------------------------------------------------------
    # CASE 6: Teacher vs. student level semantics consistency
    # -------------------------------------------------------------------------
    def test_case_6_student_teacher_level_semantics_consistency(self):
        """CASE 6: Divergence between teacher and student performance standards must be caught."""
        teacher_desc = "Konuşma planını bağımsız ve eksiksiz uygular."
        
        # Negative test: Student view dilutes the requirement
        diluted_student_desc = "Konuşma planını öğretmen yardımıyla uygular."
        is_valid, violations = AssessmentStandardValidator.check_student_teacher_consistency(teacher_desc, diluted_student_desc)
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)

        # Negative test: Student view adds ungrounded extra burden
        burdened_student_desc = "Konuşma planını bağımsız uygular ve en az 3 kaynak gösterir."
        is_valid, violations = AssessmentStandardValidator.check_student_teacher_consistency(teacher_desc, burdened_student_desc)
        self.assertFalse(is_valid)
        self.assertTrue(len(violations) >= 1)

        # Positive test: Student-friendly consistent wording
        consistent_student_desc = "Konuşmamı hazırladığım plana uygun olarak kendi başıma eksiksiz sunarım."
        is_valid, violations = AssessmentStandardValidator.check_student_teacher_consistency(teacher_desc, consistent_student_desc)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    # -------------------------------------------------------------------------
    # CASE 7: Evidence-based feedback (EVIDENCE -> EFFECT -> NEXT STEP)
    # -------------------------------------------------------------------------
    def test_case_7_feedback_evidence_model(self):
        """CASE 7: Feedback consisting solely of ungrounded praise ('Çok başarılı') flagged."""
        # Negative test: Bare ungrounded praise
        bare_praise = "Çok başarılı bir sunum yaptın, tebrikler."
        is_valid, status, violations = AssessmentStandardValidator.check_feedback_structure(bare_praise)
        self.assertFalse(is_valid)
        self.assertEqual(status, "FAIL")

        # Positive test: Full OBSERVED EVIDENCE -> EFFECT -> NEXT STEP model
        structured_feedback = (
            "Karakterin duygu değişimlerini ses tonuna tutarlı biçimde yansıttın; "
            "bu durum anlatımın takip edilmesini ve anlaşılmasını kolaylaştırdı. "
            "Bir sonraki sunumunda göz temasını sınıfın farklı bölümlerine daha dengeli dağıtmayı dene."
        )
        is_valid, status, violations = AssessmentStandardValidator.check_feedback_structure(structured_feedback)
        self.assertTrue(is_valid)
        self.assertEqual(status, "PASS")
        self.assertEqual(len(violations), 0)

    # -------------------------------------------------------------------------
    # CONTRACT AUDIT: Version 1.3.0 & Hardening Policies Verification
    # -------------------------------------------------------------------------
    def test_contract_audit_v1_3_0_and_policies(self):
        """Verifies that assessment_design_contract.json is upgraded to 1.3.0 with all hardening policies."""
        meta = self.contract_data.get("metadata", {})
        self.assertEqual(meta.get("contract_version"), "1.3.0")
        self.assertEqual(meta.get("schema_version"), "1.3")
        self.assertEqual(meta.get("applied_global_standard"), "ASSESSMENT_GENERATION_STANDARD_VERSION: 1.0.0")

        # Policy checks
        self.assertIn("unsupported_parameter_policy", self.contract_data)
        self.assertIn("score_band_policy", self.contract_data)
        self.assertIn("criterion_scope_policy", self.contract_data)
        self.assertIn("descriptor_language_policy", self.contract_data)
        self.assertIn("shared_level_semantics_policy", self.contract_data)
        self.assertIn("student_teacher_consistency_policy", self.contract_data)
        self.assertIn("feedback_policy", self.contract_data)
        self.assertIn("pre_generation_assertions", self.contract_data)

        # 12 QA dimensions check
        qa_results = self.contract_data.get("qa_verification_results", {})
        expected_qas = [
            "UNSUPPORTED_PARAMETER_QA", "NO_INVENTED_SCORE_BANDS_QA",
            "SHARED_LEVEL_SEMANTICS_QA", "STUDENT_LEVEL_SEMANTICS_QA",
            "DESCRIPTOR_OBSERVABILITY_QA", "DESCRIPTOR_ABSOLUTISM_QA",
            "ADJACENT_LEVEL_DISTINCTION_QA", "CRITERION_SCOPE_PURITY_QA",
            "FEEDBACK_EVIDENCE_QA", "PROVENANCE_BOUNDARY_QA",
            "SOURCE_RIGHTS_QA", "TEACHER_REVIEW_GATE_QA"
        ]
        for qa_name in expected_qas:
            self.assertIn(qa_name, qa_results, f"Missing QA gate: {qa_name}")
            self.assertIn(qa_results[qa_name].get("status"), ["PASS", "REVIEW_REQUIRED"])

    # -------------------------------------------------------------------------
    # GLOBAL STANDARD REFERENCE AUDIT
    # -------------------------------------------------------------------------
    def test_global_standard_file_audit(self):
        """Verifies that references/assessment-generation.md is non-empty and has required sections."""
        self.assertTrue(len(self.global_ref_content) > 500)
        self.assertIn("ASSESSMENT_GENERATION_STANDARD_VERSION: 1.0.0", self.global_ref_content)
        self.assertIn("Core Invariant — Source-Bound Parameter Generation", self.global_ref_content)
        self.assertIn("No Invented Score Bands", self.global_ref_content)
        self.assertIn("Shared Level Semantics", self.global_ref_content)
        self.assertIn("Criterion Scope Purity", self.global_ref_content)
        self.assertIn("Observable Descriptor Standard", self.global_ref_content)
        self.assertIn("OBSERVED EVIDENCE → EFFECT → NEXT STEP", self.global_ref_content)
        self.assertIn("Pre-Generation Assertions", self.global_ref_content)
        self.assertIn("Post-Generation Multi-Dimensional QA Suite", self.global_ref_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
