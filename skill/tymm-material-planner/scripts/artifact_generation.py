#!/usr/bin/env python3
"""TYMM Artifact Generation Engine V1.

Canonical knowledge and production contracts decide what may be generated. The
engine only renders a validated generation-context snapshot into a draft.
Generation never implies teacher approval.
"""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from knowledge_index import KnowledgeIndexer
from production_schema import build_artifact_maps

GENERATOR_VERSION = "1.0.0"
CONTEXT_SCHEMA_VERSION = "1.0"
ARTIFACT_SCHEMA_VERSION = "1.0"
PILOT_ARTIFACT_ID = "TDE9_KONUSMA_RUBRIC"
LIFECYCLE_REVIEW = "REVIEW_REQUIRED"
LIFECYCLE_APPROVED = "APPROVED"
LIFECYCLE_FROZEN = "FROZEN"


class ArtifactGenerationError(ValueError):
    pass


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ArtifactGenerationError(f"REQUIRED_FILE_MISSING: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ArtifactGenerationError(f"JSON_ROOT_MUST_BE_OBJECT: {path}")
    return data


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stable_hash(data: Any) -> str:
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _find_registry_artifact(registry: Dict[str, Any], artifact_id: str) -> Dict[str, Any]:
    for item in registry.get("annual_artifacts", []):
        if isinstance(item, dict) and item.get("artifact_id") == artifact_id:
            return item
    raise ArtifactGenerationError(f"ARTIFACT_NOT_IN_REGISTRY: {artifact_id}")


def _contract_profile(contract: Dict[str, Any], artifact: Dict[str, Any]) -> Dict[str, Any]:
    family = artifact.get("assessment_family")
    families = contract.get("assessment_families", {})
    if family not in families:
        raise ArtifactGenerationError(f"ASSESSMENT_FAMILY_NOT_IN_CONTRACT: {family}")
    profile_rules = None
    if family == "ANALYTIC_RUBRIC":
        domain = str(artifact.get("skill_domain", "")).lower()
        profile_rules = contract.get("speaking_rubric_profile_rules") if (
            "konuş" in domain or "sözlü" in domain
        ) else contract.get("writing_rubric_profile_rules")
    elif family == "PROCESS_CHECKLIST":
        profile_rules = contract.get("process_checklist_profile_rules")
    return {
        "assessment_family": copy.deepcopy(families[family]),
        "level_model": copy.deepcopy(contract.get("shared_rubric_level_model")),
        "descriptor_writing_standards": copy.deepcopy(contract.get("descriptor_writing_standards")),
        "scoring_model": copy.deepcopy(contract.get("scoring_model")),
        "output_schema": copy.deepcopy(contract.get("rubric_output_schema_specification")),
        "profile_rules": copy.deepcopy(profile_rules),
        "teacher_review_and_qa_gates": copy.deepcopy(contract.get("teacher_review_and_qa_gates", {})),
        "copyright_and_accessibility_standards": copy.deepcopy(
            contract.get("copyright_and_accessibility_standards", {})
        ),
    }


def build_generation_context(course_root: Path | str, artifact_id: str) -> Dict[str, Any]:
    root = Path(course_root).resolve()
    if artifact_id.startswith("MAT_"):
        raise ArtifactGenerationError(
            f"LEGACY_ALIAS_NOT_ARTIFACT_IDENTITY: use canonical artifact_id, not {artifact_id}"
        )

    manifest = _read_json(root / "production" / "production_manifest.json")
    registry = _read_json(root / "production" / "assessment_artifact_registry.json")
    contract = _read_json(root / "production" / "assessment_design_contract.json")
    index_status = KnowledgeIndexer(str(root)).check_status()
    if index_status.get("status") != "INDEX_FRESH":
        raise ArtifactGenerationError(
            "P0_GATE_NOT_READY: knowledge index must be INDEX_FRESH before generation; "
            f"got {index_status.get('status')}"
        )

    _, artifact_by_id, alias_map, provenance_by_gap = build_artifact_maps(manifest)
    if artifact_id not in artifact_by_id:
        raise ArtifactGenerationError(f"ARTIFACT_NOT_IN_PRODUCTION_QUEUE: {artifact_id}")
    production_artifact = copy.deepcopy(artifact_by_id[artifact_id])
    registry_artifact = copy.deepcopy(_find_registry_artifact(registry, artifact_id))

    for field in (
        "artifact_id", "assessment_family", "scope", "covered_gap_instances",
        "covered_themes", "covered_outcomes", "teacher_review_required",
    ):
        if field in production_artifact and production_artifact.get(field) != registry_artifact.get(field):
            raise ArtifactGenerationError(
                f"PRODUCTION_REGISTRY_DRIFT: {artifact_id} field {field}"
            )

    gaps = registry_artifact.get("covered_gap_instances", [])
    gap_provenance = []
    for gap_id in gaps:
        if alias_map.get(gap_id) != artifact_id:
            raise ArtifactGenerationError(f"GAP_ALIAS_MAPPING_DRIFT: {gap_id}")
        row = provenance_by_gap.get(gap_id)
        if not row:
            raise ArtifactGenerationError(f"GAP_PROVENANCE_MISSING: {gap_id}")
        gap_provenance.append(copy.deepcopy(row))

    metadata = contract.get("metadata", {})
    context: Dict[str, Any] = {
        "context_schema_version": CONTEXT_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "course_id": manifest.get("course_id"),
        "artifact_id": artifact_id,
        "artifact_family": registry_artifact.get("assessment_family"),
        "artifact_scope": registry_artifact.get("scope"),
        "artifact": registry_artifact,
        "production_record": production_artifact,
        "gap_provenance": gap_provenance,
        "contract_profile": _contract_profile(contract, registry_artifact),
        "source_versions": {
            "production_schema_version": manifest.get("schema_version"),
            "registry_version": registry.get("registry_version"),
            "contract_id": metadata.get("contract_id"),
            "contract_version": metadata.get("contract_version"),
            "global_standard": metadata.get("applied_global_standard")
            or manifest.get("applied_global_standard"),
            "authoritative_source_hashes": copy.deepcopy(metadata.get("authoritative_source_hashes", {})),
            "knowledge_index_status": index_status.get("status"),
            "production_artifact_count": index_status.get("production_artifact_count"),
            "production_gap_alias_count": index_status.get("production_gap_alias_count"),
        },
    }
    context["context_hash"] = stable_hash(context)
    validate_generation_context(context)
    return context


def validate_generation_context(context: Dict[str, Any]) -> None:
    artifact_id = context.get("artifact_id")
    if not artifact_id or str(artifact_id).startswith("MAT_"):
        raise ArtifactGenerationError("CONTEXT_CANONICAL_ARTIFACT_ID_REQUIRED")
    hash_input = copy.deepcopy(context)
    expected_hash = hash_input.pop("context_hash", None)
    if expected_hash != stable_hash(hash_input):
        raise ArtifactGenerationError("CONTEXT_HASH_MISMATCH")
    artifact = context.get("artifact", {})
    production = context.get("production_record", {})
    if artifact.get("artifact_id") != artifact_id or production.get("artifact_id") != artifact_id:
        raise ArtifactGenerationError("CONTEXT_ARTIFACT_ID_DRIFT")
    aliases = artifact.get("covered_gap_instances", [])
    provenance = context.get("gap_provenance", [])
    if {r.get("gap_instance_id") for r in provenance} != set(aliases):
        raise ArtifactGenerationError("CONTEXT_GAP_PROVENANCE_INCOMPLETE")
    if any(r.get("resolved_artifact_id") != artifact_id for r in provenance):
        raise ArtifactGenerationError("CONTEXT_GAP_PROVENANCE_WRONG_TARGET")
    if artifact.get("teacher_review_required") is not True:
        raise ArtifactGenerationError("TEACHER_REVIEW_MUST_BE_REQUIRED")

    family = artifact.get("assessment_family")
    if family == "ANALYTIC_RUBRIC":
        criteria = artifact.get("core_criteria", [])
        levels = (context.get("contract_profile", {}).get("level_model") or {}).get("levels", [])
        if not criteria:
            raise ArtifactGenerationError("RUBRIC_CRITERIA_MISSING")
        if len(levels) != 4 or {x.get("numeric_value") for x in levels} != {1, 2, 3, 4}:
            raise ArtifactGenerationError("RUBRIC_REQUIRES_SHARED_4_LEVEL_MODEL")
    elif family == "PROCESS_CHECKLIST":
        if not artifact.get("core_stages"):
            raise ArtifactGenerationError("CHECKLIST_STAGES_MISSING")
    else:
        raise ArtifactGenerationError(f"UNSUPPORTED_ASSESSMENT_FAMILY: {family}")


PILOT_DESCRIPTORS: Dict[str, Dict[str, str]] = {
    "CRT_SPK_CORE_01": {
        "LEVEL_4": "Konuşmanın amacı ve bağlamına uygun içeriği açık bir odakta kurgular; seçtiği örnek ve ayrıntılar görevi destekler, konu bütünlüğünü konuşmanın genelinde korur.",
        "LEVEL_3": "Konuşmanın amacı ve bağlamına uygun içeriği büyük ölçüde kurgular; örnek ve ayrıntıların çoğu görevi destekler, küçük odak sapmaları iletişimi belirgin biçimde bozmaz.",
        "LEVEL_2": "Konuşmanın amacı ve bağlamıyla ilişkili içerik sunar ancak örnek veya ayrıntıların bir bölümü görevi zayıf destekler; konu odağını sürdürmek için yönlendirmeye ihtiyaç duyar.",
        "LEVEL_1": "Konuşmanın amacı, bağlamı ve içerik odağı arasındaki ilişki sınırlı düzeyde görünür; görevi destekleyen örnek ve ayrıntıları seçmek için yoğun yönlendirmeye ihtiyaç duyar.",
    },
    "CRT_SPK_CORE_02": {
        "LEVEL_4": "Konuşmayı anlaşılır bir giriş-gelişme-sonuç akışında düzenler; bölümler arası geçişleri ve ayrılan süreyi dengeli yönetir.",
        "LEVEL_3": "Konuşmayı belirgin bir giriş-gelişme-sonuç akışında düzenler; geçiş ve süre kullanımındaki küçük aksamalar genel organizasyonu belirgin biçimde bozmaz.",
        "LEVEL_2": "Konuşmada temel bir sıralama görülür ancak bölümler arası geçişler veya süre kullanımı yer yer dengesizdir; akışı düzenlemek için yönlendirmeye ihtiyaç duyar.",
        "LEVEL_1": "Konuşmanın bölümleri ve süre kullanımı sınırlı bir plan gösterir; anlaşılır bir akış kurmak ve zamanı yönetmek için yoğun yönlendirmeye ihtiyaç duyar.",
    },
    "CRT_SPK_CORE_03": {
        "LEVEL_4": "Sesini işitilebilir ve dengeli kullanır; telaffuz, vurgu, tonlama ve konuşma hızı anlam akışını destekler, gereksiz duraksamalar iletişimi kesintiye uğratmaz.",
        "LEVEL_3": "Ses ve telaffuzu büyük ölçüde anlaşılırdır; vurgu, tonlama veya hızdaki küçük düzensizlikler anlam akışını belirgin biçimde bozmaz.",
        "LEVEL_2": "Konuşmanın bazı bölümlerinde ses, telaffuz, vurgu, tonlama veya hız anlamayı zorlaştırır; akıcılığı sürdürmek için yönlendirmeye ihtiyaç duyar.",
        "LEVEL_1": "Sesin işitilebilirliği, telaffuz veya akıcılık sınırlı düzeyde iletişimi destekler; vurgu, tonlama ve konuşma hızını ayarlamak için yoğun yönlendirmeye ihtiyaç duyar.",
    },
    "CRT_SPK_CORE_04": {
        "LEVEL_4": "Duruş, göz teması, jest ve mimikleri konuşmanın içeriğiyle uyumlu kullanır; dinleyiciyle iletişimi sürdürür ve beden dili anlatımı destekler.",
        "LEVEL_3": "Duruş, göz teması, jest ve mimikleri büyük ölçüde anlatımı destekleyecek biçimde kullanır; küçük uyumsuzluklar dinleyiciyle iletişimi belirgin biçimde bozmaz.",
        "LEVEL_2": "Beden dili ve göz teması bazı bölümlerde anlatımı destekler ancak kullanım tutarsızdır; dinleyiciyle iletişimi sürdürmek için yönlendirmeye ihtiyaç duyar.",
        "LEVEL_1": "Duruş, göz teması, jest ve mimiklerin anlatımı destekleyen kullanımı sınırlı düzeyde gözlenir; dinleyiciyle iletişim kurmak için yoğun yönlendirmeye ihtiyaç duyar.",
    },
    "CRT_SPK_CORE_05": {
        "LEVEL_4": "Sözcükleri bağlama uygun seçer; cümleleri Türkçenin kurallarına uygun ve birbiriyle bağlantılı kurar, anlatım bozukluklarından kaçınır.",
        "LEVEL_3": "Sözcük seçimi ve cümle kuruluşu büyük ölçüde bağlama ve Türkçenin kurallarına uygundur; küçük dil hataları anlamı belirgin biçimde bozmaz.",
        "LEVEL_2": "Sözcük seçimi veya cümle kuruluşunda anlam ve akışı yer yer zorlaştıran hatalar görülür; bağdaşıklığı ve dil kurallarını uygulamak için yönlendirmeye ihtiyaç duyar.",
        "LEVEL_1": "Sözcük seçimi, cümle kuruluşu ve bağdaşıklık sınırlı düzeyde anlamı destekler; Türkçenin kurallarını bağlama uygun kullanmak için yoğun yönlendirmeye ihtiyaç duyar.",
    },
}


def _fallback_descriptor(name: str, level_id: str) -> str:
    templates = {
        "LEVEL_4": "{name} boyutundaki gözlenebilir davranışları performansın genelinde doğru, tutarlı ve bağımsız biçimde gösterir.",
        "LEVEL_3": "{name} boyutundaki gözlenebilir davranışları performansın çoğunda doğru ve tutarlı biçimde gösterir; küçük sapmalar genel niteliği belirgin biçimde bozmaz.",
        "LEVEL_2": "{name} boyutundaki davranışları kısmen gösterir; belirgin eksiklik veya tutarsızlıklar vardır ve yönlendirmeye ihtiyaç duyar.",
        "LEVEL_1": "{name} boyutundaki davranışlar sınırlı düzeyde gözlenir; önemli eksiklikler vardır ve yoğun yönlendirmeye ihtiyaç duyar.",
    }
    return templates[level_id].format(name=name)


def _descriptors(criterion: Dict[str, Any], levels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    overrides = PILOT_DESCRIPTORS.get(str(criterion.get("criterion_id")), {})
    result = []
    for level in sorted(levels, key=lambda x: int(x.get("numeric_value", 0)), reverse=True):
        level_id = level["level_id"]
        result.append({
            "level_id": level_id,
            "numeric_value": level["numeric_value"],
            "descriptor": overrides.get(level_id)
            or _fallback_descriptor(criterion.get("criterion_name", "Ölçüt"), level_id),
            "origin": "pedagogical_recommendation",
        })
    return result


def generate_draft(context: Dict[str, Any], revision: int = 1) -> Dict[str, Any]:
    validate_generation_context(context)
    source = context["artifact"]
    family = source["assessment_family"]
    profile = context["contract_profile"]
    artifact: Dict[str, Any] = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "artifact_revision": revision,
        "generation_context_hash": context["context_hash"],
        "lifecycle_status": LIFECYCLE_REVIEW,
        "material_identity": {
            "artifact_id": source["artifact_id"],
            "title": source.get("title"),
            "assessment_family": family,
            "scope": source.get("scope"),
            "skill_domain": source.get("skill_domain"),
            "reuse_policy": source.get("reuse_policy"),
        },
        "targeted_outcomes": copy.deepcopy(source.get("covered_outcomes", [])),
        "assessment_purpose": source.get("core_construct"),
        "task_and_evidence_being_assessed": {
            "core_construct": source.get("core_construct"),
            "task_bindings": copy.deepcopy(source.get("task_bindings", [])),
        },
        "provenance": {
            "covered_gap_instances": copy.deepcopy(source.get("covered_gap_instances", [])),
            "gap_provenance": copy.deepcopy(context.get("gap_provenance", [])),
            "official_requirements": copy.deepcopy(source.get("official_requirements", [])),
            "source_locators": copy.deepcopy(source.get("source_locators", {})),
            "source_versions": copy.deepcopy(context.get("source_versions", {})),
            "generation_context_hash": context["context_hash"],
            "descriptor_origin": "pedagogical_recommendation",
        },
        "teacher_review_status": {
            "required": True, "status": LIFECYCLE_REVIEW, "approved": False,
            "reviewer": None, "review_note": None,
        },
    }

    if family == "ANALYTIC_RUBRIC":
        levels = (profile.get("level_model") or {}).get("levels", [])
        rows = []
        for criterion in source.get("core_criteria", []):
            rows.append({
                "criterion_id": criterion.get("criterion_id"),
                "criterion_name": criterion.get("criterion_name"),
                "criterion_description": criterion.get("description"),
                "origin": criterion.get("origin"),
                "derived_from": criterion.get("derived_from"),
                "source_locator": criterion.get("source_locator"),
                "normalization_type": criterion.get("normalization_type"),
                "descriptors": _descriptors(criterion, levels),
            })
        n = len(rows)
        artifact.update({
            "criteria_table": rows,
            "performance_levels": copy.deepcopy(levels),
            "scoring_instructions": {
                "primary_model": "RAW_MEAN_1_TO_4",
                "criterion_count": n,
                "min_raw_total": n,
                "max_raw_total": n * 4,
                "primary_result_formula": "sum(criterion_scores) / criterion_count",
                "weighting_strategy": "EQUAL_WEIGHT_DEFAULT",
                "optional_100_scale": {
                    "enabled": True,
                    "is_official_meb_rule": False,
                    "formula": "round_half_up((sum(criterion_scores) / (criterion_count * 4)) * 100)",
                    "interpretation_note": "100'lük dönüşüm yardımcı gösterimdir; rubriğin birincil sonucu 1.00-4.00 ham ortalamadır.",
                },
            },
            "teacher_feedback_area": {
                "observed_strengths": "", "development_focus": "", "evidence_notes": "",
            },
            "optional_next_step_feedback": [
                "Bir sonraki performansta korunacak güçlü davranışı somut kanıtla belirtin.",
                "Geliştirilecek tek öncelikli ölçütü seçip uygulanabilir bir sonraki adım yazın.",
            ],
        })
    elif family == "PROCESS_CHECKLIST":
        items = []
        for stage in source.get("core_stages", []):
            items.append({
                "item_id": f"CHK_{source['artifact_id']}_{int(stage.get('stage_no', 0)):02d}",
                "process_stage": stage.get("stage_name"),
                "check_item": stage.get("focus"),
                "expected_evidence": "İlgili süreç basamağını gösteren taslak, işaretleme, düzeltme veya paylaşım kanıtı.",
                "origin": stage.get("origin"),
                "derived_from": stage.get("derived_from"),
                "source_locator": stage.get("source_locator"),
                "response_type": "DONE_OR_NEEDS_REVISION",
            })
        artifact.update({
            "checklist_items": items,
            "response_labels": ["TAMAMLANDI (DONE)", "GELİŞTİRİLMELİ (NEEDS_REVISION)"],
            "scoring_instructions": {
                "primary_model": "NONE_NO_SUMMATIVE_SCORE",
                "numerical_score": False,
                "summative_score_substitute": False,
            },
            "teacher_feedback_area": {
                "completed_stages": "", "revision_focus": "", "evidence_notes": "",
            },
            "optional_next_step_feedback": [
                "Geliştirilmeli olarak işaretlenen ilk süreç basamağı için somut bir düzeltme adımı belirleyin."
            ],
        })
    validate_generated_artifact(artifact, context)
    return artifact


def _forbidden(context: Dict[str, Any]) -> List[str]:
    standards = context.get("contract_profile", {}).get("descriptor_writing_standards") or {}
    return [str(x).casefold() for x in standards.get("forbidden_phrasing_patterns", [])]


def validate_generated_artifact(artifact: Dict[str, Any], context: Dict[str, Any]) -> None:
    validate_generation_context(context)
    identity = artifact.get("material_identity", {})
    if identity.get("artifact_id") != context["artifact_id"] or str(identity.get("artifact_id", "")).startswith("MAT_"):
        raise ArtifactGenerationError("GENERATED_ARTIFACT_CANONICAL_IDENTITY_INVALID")
    if artifact.get("generation_context_hash") != context.get("context_hash"):
        raise ArtifactGenerationError("GENERATED_ARTIFACT_CONTEXT_HASH_MISMATCH")

    review = artifact.get("teacher_review_status", {})
    if review.get("required") is not True:
        raise ArtifactGenerationError("GENERATED_ARTIFACT_TEACHER_REVIEW_NOT_REQUIRED")
    if artifact.get("lifecycle_status") in {LIFECYCLE_APPROVED, LIFECYCLE_FROZEN} and not review.get("approved"):
        raise ArtifactGenerationError("APPROVED_OR_FROZEN_ARTIFACT_REQUIRES_APPROVAL_RECORD")
    if artifact.get("lifecycle_status") == LIFECYCLE_REVIEW and review.get("approved"):
        raise ArtifactGenerationError("REVIEW_REQUIRED_ARTIFACT_CANNOT_BE_MARKED_APPROVED")

    source = context["artifact"]
    expected_gaps = set(source.get("covered_gap_instances", []))
    prov = artifact.get("provenance", {})
    if set(prov.get("covered_gap_instances", [])) != expected_gaps:
        raise ArtifactGenerationError("GENERATED_ARTIFACT_GAP_COVERAGE_DRIFT")
    if {r.get("gap_instance_id") for r in prov.get("gap_provenance", [])} != expected_gaps:
        raise ArtifactGenerationError("GENERATED_ARTIFACT_PROVENANCE_INCOMPLETE")

    family = identity.get("assessment_family")
    if family == "ANALYTIC_RUBRIC":
        required = (context.get("contract_profile", {}).get("output_schema") or {}).get("required_sections", [])
        missing = [x for x in required if x not in artifact]
        if missing:
            raise ArtifactGenerationError(f"RUBRIC_REQUIRED_SECTIONS_MISSING: {missing}")
        expected_ids = [x.get("criterion_id") for x in source.get("core_criteria", [])]
        rows = artifact.get("criteria_table", [])
        actual_ids = [x.get("criterion_id") for x in rows]
        if actual_ids != expected_ids or len(actual_ids) != len(set(actual_ids)):
            raise ArtifactGenerationError("RUBRIC_CRITERION_ID_DRIFT")
        level_ids = [x.get("level_id") for x in artifact.get("performance_levels", [])]
        if set(level_ids) != {"LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"}:
            raise ArtifactGenerationError("RUBRIC_LEVEL_MODEL_INVALID")
        forbidden = _forbidden(context)
        for row in rows:
            descriptors = row.get("descriptors", [])
            if len(descriptors) != 4 or {x.get("level_id") for x in descriptors} != set(level_ids):
                raise ArtifactGenerationError(f"RUBRIC_DESCRIPTOR_MATRIX_INCOMPLETE: {row.get('criterion_id')}")
            texts = []
            for descriptor in descriptors:
                if descriptor.get("origin") != "pedagogical_recommendation":
                    raise ArtifactGenerationError("DESCRIPTOR_ORIGIN_MUST_BE_PEDAGOGICAL_RECOMMENDATION")
                text = str(descriptor.get("descriptor", "")).strip()
                if not text:
                    raise ArtifactGenerationError("EMPTY_RUBRIC_DESCRIPTOR")
                if any(pattern and pattern in text.casefold() for pattern in forbidden):
                    raise ArtifactGenerationError(f"FORBIDDEN_DESCRIPTOR_PHRASING: {text}")
                texts.append(text)
            if len(set(texts)) != 4:
                raise ArtifactGenerationError(f"ADJACENT_LEVELS_NOT_DISTINCT: {row.get('criterion_id')}")
        scoring = artifact.get("scoring_instructions", {})
        n = len(rows)
        if scoring.get("criterion_count") != n or scoring.get("max_raw_total") != n * 4:
            raise ArtifactGenerationError("SCORING_DIMENSION_MISMATCH")
        if scoring.get("primary_model") != "RAW_MEAN_1_TO_4":
            raise ArtifactGenerationError("SCORING_PRIMARY_MODEL_DRIFT")
    elif family == "PROCESS_CHECKLIST":
        if not artifact.get("checklist_items"):
            raise ArtifactGenerationError("CHECKLIST_ITEMS_MISSING")
        if artifact.get("scoring_instructions", {}).get("numerical_score") is not False:
            raise ArtifactGenerationError("CHECKLIST_MUST_NOT_HAVE_NUMERICAL_SCORE")
    else:
        raise ArtifactGenerationError(f"UNSUPPORTED_ASSESSMENT_FAMILY: {family}")


def _artifact_dir(output_root: Path | str, artifact_id: str) -> Path:
    return Path(output_root).resolve() / artifact_id


def load_current_artifact(output_root: Path | str, artifact_id: str) -> Optional[Dict[str, Any]]:
    path = _artifact_dir(output_root, artifact_id) / "artifact.json"
    return _read_json(path) if path.exists() else None


def assert_generation_order(output_root: Path | str, artifact_id: str) -> None:
    if artifact_id == PILOT_ARTIFACT_ID:
        return
    pilot = load_current_artifact(output_root, PILOT_ARTIFACT_ID)
    if not pilot or pilot.get("lifecycle_status") not in {LIFECYCLE_APPROVED, LIFECYCLE_FROZEN}:
        raise ArtifactGenerationError(
            f"GENERATOR_V1_PILOT_NOT_APPROVED: {PILOT_ARTIFACT_ID} must be approved before {artifact_id}"
        )


def generate_to_directory(
    course_root: Path | str,
    artifact_id: str,
    output_root: Path | str,
    *,
    enforce_order: bool = True,
) -> Tuple[Dict[str, Any], Dict[str, Any], bool]:
    if enforce_order:
        assert_generation_order(output_root, artifact_id)
    context = build_generation_context(course_root, artifact_id)
    out = _artifact_dir(output_root, artifact_id)
    context_path = out / "generation_context.json"
    artifact_path = out / "artifact.json"
    state_path = out / "generation_state.json"
    existing = _read_json(artifact_path) if artifact_path.exists() else None

    if existing and existing.get("generation_context_hash") == context["context_hash"]:
        validate_generated_artifact(existing, context)
        _write_json(context_path, context)
        _write_json(state_path, {
            "artifact_id": artifact_id,
            "current_revision": existing.get("artifact_revision", 1),
            "current_context_hash": context["context_hash"],
            "lifecycle_status": existing.get("lifecycle_status"),
            "generator_version": GENERATOR_VERSION,
            "idempotent_reuse": True,
        })
        return context, existing, False

    revision = 1
    if existing:
        previous_revision = int(existing.get("artifact_revision", 1))
        revision = previous_revision + 1
        archive = out / "revisions" / f"r{previous_revision:04d}"
        archive.mkdir(parents=True, exist_ok=True)
        shutil.copy2(artifact_path, archive / "artifact.json")
        if context_path.exists():
            shutil.copy2(context_path, archive / "generation_context.json")

    generated = generate_draft(context, revision)
    _write_json(context_path, context)
    _write_json(artifact_path, generated)
    _write_json(state_path, {
        "artifact_id": artifact_id,
        "current_revision": revision,
        "current_context_hash": context["context_hash"],
        "lifecycle_status": generated["lifecycle_status"],
        "generator_version": GENERATOR_VERSION,
        "idempotent_reuse": False,
    })
    return context, generated, True


def approve_artifact(
    course_root: Path | str,
    artifact_id: str,
    output_root: Path | str,
    reviewer: str,
    review_note: str = "",
) -> Dict[str, Any]:
    if not reviewer.strip():
        raise ArtifactGenerationError("REVIEWER_REQUIRED")
    context = build_generation_context(course_root, artifact_id)
    out = _artifact_dir(output_root, artifact_id)
    artifact_path = out / "artifact.json"
    artifact = _read_json(artifact_path)
    validate_generated_artifact(artifact, context)
    if artifact.get("generation_context_hash") != context["context_hash"]:
        raise ArtifactGenerationError("STALE_ARTIFACT_CANNOT_BE_APPROVED")
    artifact["lifecycle_status"] = LIFECYCLE_APPROVED
    artifact["teacher_review_status"] = {
        "required": True,
        "status": LIFECYCLE_APPROVED,
        "approved": True,
        "reviewer": reviewer.strip(),
        "review_note": review_note.strip() or None,
    }
    validate_generated_artifact(artifact, context)
    _write_json(artifact_path, artifact)
    state_path = out / "generation_state.json"
    state = _read_json(state_path) if state_path.exists() else {}
    state.update({"lifecycle_status": LIFECYCLE_APPROVED, "teacher_reviewer": reviewer.strip()})
    _write_json(state_path, state)
    return artifact


def freeze_artifact(course_root: Path | str, artifact_id: str, output_root: Path | str) -> Dict[str, Any]:
    context = build_generation_context(course_root, artifact_id)
    out = _artifact_dir(output_root, artifact_id)
    artifact_path = out / "artifact.json"
    artifact = _read_json(artifact_path)
    validate_generated_artifact(artifact, context)
    if artifact.get("lifecycle_status") != LIFECYCLE_APPROVED:
        raise ArtifactGenerationError("ONLY_APPROVED_ARTIFACT_CAN_BE_FROZEN")
    artifact["lifecycle_status"] = LIFECYCLE_FROZEN
    artifact["teacher_review_status"]["status"] = LIFECYCLE_FROZEN
    validate_generated_artifact(artifact, context)
    _write_json(artifact_path, artifact)
    state_path = out / "generation_state.json"
    state = _read_json(state_path) if state_path.exists() else {}
    state["lifecycle_status"] = LIFECYCLE_FROZEN
    _write_json(state_path, state)
    return artifact
