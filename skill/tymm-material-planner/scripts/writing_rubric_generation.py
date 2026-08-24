#!/usr/bin/env python3
"""Deterministic generator for the annual TDE9 writing analytic rubric.

Artifact Generation Engine V1 intentionally ships a generic descriptor fallback for
non-pilot rubrics. The annual writing rubric needs criterion-specific observable
performance descriptors before teacher review, so this module applies a validated
4x4 writing descriptor matrix while preserving canonical criteria, provenance,
scoring, task bindings, context hash, and lifecycle rules.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Tuple

from artifact_generation import (
    ArtifactGenerationError,
    LIFECYCLE_REVIEW,
    assert_generation_order,
    build_generation_context,
    generate_draft,
    stable_hash,
    validate_generated_artifact,
)

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent
DEFAULT_COURSE_ROOT = REPO_ROOT / "courses" / "TDE_9"
WRITING_RUBRIC_ID = "TDE9_YAZMA_RUBRIC"

WRITING_DESCRIPTORS: Dict[str, Dict[str, str]] = {
    "CRT_WRT_CORE_01": {
        "LEVEL_4": "Yazılı ürünün tema, ana düşünce veya ana duygu odağını açık biçimde kurar; seçtiği ayrıntı ve ifadeler bu odağı ürünün genelinde tutarlı biçimde geliştirir, anlamı zayıflatan çelişkiler görülmez.",
        "LEVEL_3": "Yazılı ürünün tema, ana düşünce veya ana duygu odağı belirgindir; ayrıntı ve ifadelerin büyük bölümü bu odağı destekler, küçük anlam kaymaları ürünün genel tutarlılığını belirgin biçimde bozmaz.",
        "LEVEL_2": "Yazılı ürünün tema, ana düşünce veya ana duygu odağı sezilebilir; ancak bazı bölüm, ayrıntı veya ifadeler bu odaktan uzaklaşır ya da birbiriyle yeterince uyuşmaz, anlam bütünlüğü yer yer zayıflar.",
        "LEVEL_1": "Yazılı üründe tema, ana düşünce veya ana duygu odağı sınırlı düzeyde belirginleşir; bölüm ve ayrıntılar farklı anlam merkezlerine yöneldiği için ürünün genel anlam bütünlüğünü izlemek güçleşir.",
    },
    "CRT_WRT_CORE_02": {
        "LEVEL_4": "Yazılan türün temel yapısal özelliklerini ve ürünün iç düzenini bilinçli biçimde kurar; bölüm, birim, sıra veya yerleşim tercihleri anlamı ve iletişim amacını ürünün genelinde destekler.",
        "LEVEL_3": "Yazılan türün temel yapısal özelliklerini büyük ölçüde uygun kullanır; bölüm, birim, sıra veya yerleşimdeki küçük aksamalar ürünün genel organizasyonunu ve anlaşılmasını belirgin biçimde bozmaz.",
        "LEVEL_2": "Yazılan türe ait bazı yapısal özellikleri kullanır; ancak bölüm, birim, sıra veya yerleşim tercihleri yer yer tutarsızdır ve ürünün anlam akışını ya da işlevini zayıflatır.",
        "LEVEL_1": "Yazılan türün yapısal özellikleri sınırlı düzeyde görünür; bölüm, birim, sıra veya yerleşim arasında açık bir düzen kurulamadığı için ürünün yapısını ve anlam akışını izlemek güçleşir.",
    },
    "CRT_WRT_CORE_03": {
        "LEVEL_4": "Sözcük ve anlatım tercihlerini bağlama, türe ve iletişim amacına uygun seçer; ifadeler anlamı açıklaştırır, hedeflenen ton veya anlatım etkisini ürünün genelinde destekler.",
        "LEVEL_3": "Sözcük ve anlatım tercihleri büyük ölçüde bağlama, türe ve iletişim amacına uygundur; sınırlı sayıdaki genel veya aksayan ifade anlamı ve anlatım etkisini belirgin biçimde bozmaz.",
        "LEVEL_2": "Sözcük ve anlatım tercihlerinin bir bölümü bağlama veya türe uygundur; ancak tekrarlanan genel, belirsiz ya da uyumsuz ifadeler ürünün açıklığını ve anlatım etkisini yer yer zayıflatır.",
        "LEVEL_1": "Sözcük ve anlatım tercihleri bağlam ve türle sınırlı ölçüde uyum gösterir; belirsiz veya uyumsuz ifadeler nedeniyle ürünün anlamını ve hedeflenen anlatım etkisini izlemek güçleşir.",
    },
    "CRT_WRT_CORE_04": {
        "LEVEL_4": "Yazım, noktalama, cümle kuruluşu ve metin içi bağlantıları tutarlı biçimde kullanır; seyrek görülen küçük sapmalar okuma akışını veya anlamı etkilemez.",
        "LEVEL_3": "Yazım, noktalama, cümle kuruluşu ve metin içi bağlantılar büyük ölçüde kurallara uygundur; sınırlı hatalar okuma akışını ve anlam bütünlüğünü belirgin biçimde bozmaz.",
        "LEVEL_2": "Yazım, noktalama, cümle kuruluşu veya metin içi bağlantılarda yinelenen hatalar görülür; temel anlam izlenebilse de okuma akışı ve bağdaşıklık yer yer kesintiye uğrar.",
        "LEVEL_1": "Yazım, noktalama, cümle kuruluşu ve metin içi bağlantılardaki sık hatalar okuma akışını belirgin biçimde kesintiye uğratır ve ürünün anlam ilişkilerini izlemeyi güçleştirir.",
    },
}


def apply_writing_descriptors(artifact: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(artifact)
    rows = result.get("criteria_table", [])
    for row in rows:
        criterion_id = str(row.get("criterion_id"))
        descriptor_map = WRITING_DESCRIPTORS.get(criterion_id)
        if descriptor_map is None:
            raise ArtifactGenerationError(f"WRITING_DESCRIPTOR_OVERRIDE_MISSING: {criterion_id}")
        descriptors = row.get("descriptors", [])
        for descriptor in descriptors:
            level_id = str(descriptor.get("level_id"))
            if level_id not in descriptor_map:
                raise ArtifactGenerationError(
                    f"WRITING_DESCRIPTOR_LEVEL_OVERRIDE_MISSING: {criterion_id}/{level_id}"
                )
            descriptor["descriptor"] = descriptor_map[level_id]
            descriptor["origin"] = "pedagogical_recommendation"
    return result


def render_review(context: Dict[str, Any], artifact: Dict[str, Any]) -> str:
    identity = artifact.get("material_identity", {})
    lines = [
        f"# {identity.get('artifact_id')} — Teacher Review",
        "",
        f"**Lifecycle:** `{artifact.get('lifecycle_status')}`  ",
        f"**Artifact revision:** `{artifact.get('artifact_revision')}`  ",
        f"**Generator:** `{artifact.get('generator_version')}` + `writing_rubric_generation`  ",
        f"**Generation context hash:** `{context.get('context_hash')}`  ",
        "",
        "Bu belge yıllık yazma rubriğinin öğretmen incelemesi için insan-okunur snapshot'ıdır. "
        "Kriter adları ve kapsam canonical kaynaklardan gelir; hücre düzeyi performans "
        "betimleyicileri pedagojik türetimdir. Generation/validation öğretmen onayı değildir.",
        "",
        "## Kimlik ve kapsam",
        "",
        f"- Artifact: `{identity.get('artifact_id')}`",
        f"- Başlık: {identity.get('title')}",
        f"- Aile: `{identity.get('assessment_family')}`",
        f"- Kapsam: `{identity.get('scope')}`",
        f"- Hedef çıktılar: {', '.join(f'`{x}`' for x in artifact.get('targeted_outcomes', []))}",
        "- Birincil puanlama: eşit ağırlıklı `RAW_MEAN_1_TO_4`",
        "- Yardımcı 100'lük dönüşüm resmî MEB puanlama kuralı değildir.",
        "",
        "## Dereceli puanlama anahtarı",
        "",
    ]

    label_by_level = {
        "LEVEL_4": "4 — İleri Düzey",
        "LEVEL_3": "3 — Yetkin Düzey",
        "LEVEL_2": "2 — Gelişmekte Olan",
        "LEVEL_1": "1 — Başlangıç Düzeyi",
    }
    for index, row in enumerate(artifact.get("criteria_table", []), start=1):
        lines.extend([
            f"### {index}. {row.get('criterion_name')}",
            "",
        ])
        descriptors = sorted(
            row.get("descriptors", []),
            key=lambda x: int(x.get("numeric_value", 0)),
            reverse=True,
        )
        for descriptor in descriptors:
            label = label_by_level[str(descriptor.get("level_id"))]
            lines.extend([
                f"**{label}:** {descriptor.get('descriptor')}",
                "",
            ])

    scoring = artifact.get("scoring_instructions", {})
    lines.extend([
        "## Puanlama",
        "",
        f"Her ölçüt 1–4 puanlanır. {scoring.get('criterion_count')} ölçütün ham toplamı "
        f"`{scoring.get('min_raw_total')}–{scoring.get('max_raw_total')}`, birincil sonuç ise "
        "ölçüt puanlarının aritmetik ortalamasıdır (`1.00–4.00`). Yardımcı 100'lük gösterim "
        "kullanılırsa bunun pedagojik dönüşüm olduğu ve resmî MEB kuralı olmadığı belirtilir.",
        "",
        "## Görev bağları",
        "",
    ])
    for binding in artifact.get("task_and_evidence_being_assessed", {}).get("task_bindings", []):
        lines.append(
            f"- **{binding.get('theme_id')} — {binding.get('task_title')}:** "
            f"{binding.get('evidence_being_observed')}"
        )
    lines.extend([
        "",
        "Tema veya türe özgü göstergeler (ör. şiirde ritim/ahenk ve imge, infografikte "
        "metin-görsel düzeni, otobiyografide kronolojik/tematik kurgu) yıllık çekirdek "
        "ölçütleri değiştirmez; ilgili task binding içinde kanıt olarak yorumlanır.",
        "",
        "## Öğretmen incelemesi",
        "",
        "Onay öncesi özellikle şunlar kontrol edilmelidir: dört ölçütün farklı yazılı ürünlerde "
        "adil çalışması, komşu düzeylerin gözlenebilir biçimde ayrışması, Tema 2 şiir görevinin "
        "ritim/ahenk ve imge kanıtlarının doğru task binding altında değerlendirilmesi ve sınıf "
        "içi puanlama yükünün uygulanabilirliği.",
        "",
        "Bu snapshot onaylanana kadar `TDE9_YAZMA_RUBRIC` `REVIEW_REQUIRED` kalır ve "
        "`BLOCK_T2_04_YAZMA_P05` nihai öğretmen rubrik değerlendirmesi tamamlanmış sayılmaz.",
        "",
    ])
    return "\n".join(lines)


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generate_writing_to_directory(
    course_root: Path | str,
    output_root: Path | str,
) -> Tuple[Dict[str, Any], Dict[str, Any], bool]:
    root = Path(course_root).resolve()
    out_root = Path(output_root).resolve()
    assert_generation_order(out_root, WRITING_RUBRIC_ID)
    context = build_generation_context(root, WRITING_RUBRIC_ID)

    out = out_root / WRITING_RUBRIC_ID
    artifact_path = out / "artifact.json"
    context_path = out / "generation_context.json"
    state_path = out / "generation_state.json"
    review_path = out / "REVIEW.md"

    existing = None
    if artifact_path.exists():
        existing = json.loads(artifact_path.read_text(encoding="utf-8"))

    revision = int(existing.get("artifact_revision", 1)) if existing else 1
    draft = generate_draft(context, revision=revision)
    generated = apply_writing_descriptors(draft)
    validate_generated_artifact(generated, context)

    changed = existing is None or stable_hash(existing) != stable_hash(generated)
    if existing is not None and changed:
        previous_revision = int(existing.get("artifact_revision", 1))
        revision = previous_revision + 1
        generated["artifact_revision"] = revision
        archive = out / "revisions" / f"r{previous_revision:04d}"
        archive.mkdir(parents=True, exist_ok=True)
        shutil.copy2(artifact_path, archive / "artifact.json")
        if context_path.exists():
            shutil.copy2(context_path, archive / "generation_context.json")
        validate_generated_artifact(generated, context)

    _write_json(context_path, context)
    _write_json(artifact_path, generated)
    _write_json(state_path, {
        "artifact_id": WRITING_RUBRIC_ID,
        "current_revision": generated.get("artifact_revision", 1),
        "current_context_hash": context["context_hash"],
        "lifecycle_status": LIFECYCLE_REVIEW,
        "generator_version": generated.get("generator_version"),
        "writing_descriptor_profile": "TDE9_WRITING_OBSERVABLE_4X4_V1",
        "idempotent_reuse": not changed,
    })
    review_path.write_text(render_review(context, generated), encoding="utf-8")
    return context, generated, changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the TDE9 annual writing analytic rubric")
    parser.add_argument("--course-root")
    parser.add_argument("--output-root")
    args = parser.parse_args()
    course_root = Path(args.course_root or os.environ.get("TYMM_KNOWLEDGE_ROOT", DEFAULT_COURSE_ROOT)).resolve()
    output_root = Path(args.output_root).resolve() if args.output_root else course_root / "generated"
    try:
        context, artifact, changed = generate_writing_to_directory(course_root, output_root)
        print(json.dumps({
            "artifact_id": WRITING_RUBRIC_ID,
            "changed": changed,
            "revision": artifact.get("artifact_revision"),
            "generation_context_hash": context.get("context_hash"),
            "lifecycle_status": artifact.get("lifecycle_status"),
            "validation": "PASS",
            "review_path": str(output_root / WRITING_RUBRIC_ID / "REVIEW.md"),
        }, ensure_ascii=False, indent=2))
        return 0
    except ArtifactGenerationError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
