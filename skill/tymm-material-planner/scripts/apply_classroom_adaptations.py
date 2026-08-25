#!/usr/bin/env python3
"""Materialize P6 classroom adaptations for critical media/performance lesson-plan packages."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MEDIA_MARKERS = (
    "DINLEME",
    "IZLEME",
    "İZLEME",
    "PODCAST",
    "VIDEO",
    "VİDEO",
    "BELGESEL",
    "SES_KAYDI",
    "SES KAYDI",
    "AUDIO",
)
DIGITAL_MARKERS = ("EBA", "DIJITAL", "DİJİTAL", "CEVRIMICI", "ÇEVRİMİÇİ")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], *, pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if pretty:
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    else:
        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")


def _append_text(parts: list[str], value: Any) -> None:
    if isinstance(value, str):
        parts.append(value)
    elif isinstance(value, list):
        for item in value:
            _append_text(parts, item)


def plan_signal(plan: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("block_id", "plan_title", "plan_summary"):
        _append_text(parts, plan.get(key))
    _append_text(parts, plan.get("used_activity_ids"))
    for lesson in plan.get("lessons", []):
        if not isinstance(lesson, dict):
            continue
        for key in ("title", "objective", "activity_ids", "materials"):
            _append_text(parts, lesson.get(key))
    return " ".join(parts).upper()


def detect_triggers(plan: dict[str, Any]) -> list[str]:
    signal = plan_signal(plan)
    triggers: list[str] = []
    if any(marker in signal for marker in MEDIA_MARKERS):
        triggers.append("MEDIA_DEPENDENT")
    if isinstance(plan.get("large_class_route"), dict):
        triggers.append("LIVE_PERFORMANCE")
    return triggers


def media_types(plan: dict[str, Any]) -> list[str]:
    signal = plan_signal(plan)
    result: list[str] = []
    if any(marker in signal for marker in ("DINLEME", "PODCAST", "SES_KAYDI", "SES KAYDI", "AUDIO")):
        result.append("AUDIO")
    if any(marker in signal for marker in ("IZLEME", "İZLEME", "VIDEO", "VİDEO", "BELGESEL")):
        result.append("VIDEO")
    if any(marker in signal for marker in DIGITAL_MARKERS):
        result.append("DIGITAL_TOOL")
    if not result:
        result.append("AUDIO_OR_VIDEO")
    return result


def build_adaptations(plan: dict[str, Any], triggers: list[str]) -> dict[str, Any]:
    trigger_text = ", ".join(triggers)
    payload: dict[str, Any] = {
        "trigger_categories": triggers,
        "justification": (
            f"Bu paket {trigger_text} sinyali taşıdığı için farklılaştırma ve erişilebilirlik rotası first-class olarak tutulur; "
            "destek, öğrenme çıktısını veya beklenen kanıtı azaltmaz."
        ),
        "differentiation": {
            "scaffold_route": [
                "Yönergeyi görünür küçük adımlara böl; model/örnek yalnız süreci görünür kılsın, hedef metin veya performans kanıtını azaltmasın.",
                "Hazırlıkta anahtar yönerge ve kısa kontrol sırası kullan; öğrencinin yapacağı işlemleri tek ekranda/sayfada izlenebilir tut.",
            ],
            "enrichment_route": [
                "Çekirdek görevi erken ve yeterli kanıtla tamamlayan öğrenci aynı çıktı üzerinde karşılaştırmalı ikinci kanıt, alternatif bağlam veya daha bağımsız gerekçelendirme üretsin; yeni zorunlu çıktı icat edilmesin."
            ],
            "outcomes_unchanged": True,
        },
        "accessibility": {
            "representation_supports": [
                "Yönergeleri sözlü ve yazılı olarak birlikte sun; metni seçilebilir/büyütülebilir tut ve renk tek başına anlam taşımasın.",
                "Görsel unsur zorunluysa temel bilgiyi kısa sözel açıklama/alt metin eşdeğeriyle de erişilebilir kıl.",
            ],
            "participation_supports": [
                "Hazırlık ve geri bildirim aşamalarında ikili/küçük grup veya öğretmen destekli rota kullanılabilir; bireysel kanıt gereken yerde aynı bireysel kanıt korunur."
            ],
            "environment_supports": [
                "Gerektiğinde dikkat dağıtıcıları azaltılmış oturma/çalışma konumu, okunabilir çıktı ve erişilebilir cihaz kullanımına izin ver; görev ölçütlerini değiştirme."
            ],
            "assessment_construct_preserved": True,
        },
        "evidence_equivalence": (
            "Uyarlama yalnız temsil, süreç, ortam veya katılım yolunu değiştirir; canonical öğrenme çıktısı, görevın temel yapısı ve değerlendirmede aranan kanıt aynı kalır."
        ),
    }

    if "MEDIA_DEPENDENT" in triggers:
        types = ", ".join(media_types(plan))
        payload["media_fallback"] = {
            "required": True,
            "network_independent_core_route": True,
            "same_source_or_equivalent_required": True,
            "transcript_is_support_not_default_substitute": True,
            "offline_route": (
                f"Birincil medya türü ({types}) çevrimiçi açılamazsa aynı kaynak dosyanın önceden hazırlanmış yerel/çevrimdışı kopyasını veya aynı kanıtı taşıyan öğretmen-onaylı eşdeğeri kullan; internet erişimini çekirdek dersin ön koşulu yapma."
            ),
            "access_support_route": (
                "Altyazı/transkript, yeniden oynatma ve sözel/görsel açıklama erişim desteği olarak kullanılabilir. Dinleme/izleme becerisinin kendisi hedef veya ölçme nesnesiyse transkript varsayılan olarak işitsel/görsel kanıtın yerine geçmez; gerekli bireysel uyarlama öğretmen tarafından aynı construct korunarak belirlenir."
            ),
        }

    if "LIVE_PERFORMANCE" in triggers:
        payload["live_performance_access"] = {
            "required": True,
            "alternative_modes": [
                "SMALL_GROUP_LIVE",
                "TEACHER_OBSERVED_LIVE",
                "RECORDED_ORAL_IF_ALLOWED",
            ],
            "same_performance_evidence_required": True,
            "written_only_substitution_allowed": False,
            "recording_requires_consent": True,
        }

    return payload


def apply(knowledge_root: Path, *, write: bool) -> dict[str, Any]:
    generated = knowledge_root / "generated" / "lesson_plans"
    if not generated.is_dir():
        raise ValueError(f"generated lesson plans missing: {generated}")

    packages: list[dict[str, Any]] = []
    changed_paths: list[str] = []
    media_count = 0
    performance_count = 0
    overlap_count = 0

    for path in sorted(generated.rglob("*.json")):
        plan = read_json(path)
        triggers = detect_triggers(plan)
        relative = path.relative_to(knowledge_root).as_posix()
        current = plan.get("classroom_adaptations")

        if not triggers:
            if current is not None:
                if write:
                    plan.pop("classroom_adaptations", None)
                    write_json(path, plan, pretty=False)
                    changed_paths.append(relative)
            continue

        if "MEDIA_DEPENDENT" in triggers:
            media_count += 1
        if "LIVE_PERFORMANCE" in triggers:
            performance_count += 1
        if len(triggers) == 2:
            overlap_count += 1

        expected = build_adaptations(plan, triggers)
        if current != expected and write:
            plan["classroom_adaptations"] = expected
            write_json(path, plan, pretty=False)
            changed_paths.append(relative)

        packages.append(
            {
                "package_id": path.stem,
                "path": relative,
                "theme_id": plan.get("theme_id"),
                "block_id": plan.get("block_id"),
                "trigger_categories": triggers,
                "media_types": media_types(plan) if "MEDIA_DEPENDENT" in triggers else [],
            }
        )

    if not packages:
        raise ValueError(f"No critical adaptation packages discovered for {knowledge_root.name}")

    manifest = {
        "schema_version": "1.0.0",
        "course_id": knowledge_root.name,
        "policy": {
            "critical_trigger_categories": ["MEDIA_DEPENDENT", "LIVE_PERFORMANCE"],
            "non_target_packages_not_forced": True,
            "outcome_and_assessment_construct_preservation_required": True,
            "media_core_route_must_not_require_network": True,
            "transcript_is_support_not_default_listening_substitute": True,
            "written_only_speaking_substitution_forbidden": True,
            "recording_requires_consent": True,
        },
        "summary": {
            "target_packages": len(packages),
            "media_dependent_packages": media_count,
            "live_performance_packages": performance_count,
            "overlap_packages": overlap_count,
        },
        "packages": sorted(packages, key=lambda item: item["path"]),
    }

    manifest_path = knowledge_root / "production" / "classroom_adaptation_manifest.json"
    existing = read_json(manifest_path) if manifest_path.exists() else None
    manifest_changed = existing != manifest
    if write and manifest_changed:
        write_json(manifest_path, manifest, pretty=True)
        changed_paths.append(manifest_path.relative_to(knowledge_root).as_posix())

    return {
        "status": "PASS",
        "course_id": knowledge_root.name,
        "target_packages": len(packages),
        "media_dependent_packages": media_count,
        "live_performance_packages": performance_count,
        "overlap_packages": overlap_count,
        "changed_paths": changed_paths,
        "manifest_changed": manifest_changed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        results = [apply(Path(root), write=args.write) for root in args.knowledge_root]
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL_CLOSED: {exc}")
        return 2
    print(json.dumps({"status": "PASS", "courses": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
