#!/usr/bin/env python3
"""Add deterministic large-class execution routes to speaking-performance lesson plans."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def is_speaking_block(plan: dict[str, Any]) -> bool:
    return "KONUSMA" in str(plan.get("block_id") or "").upper()


def is_performance_activity(activity_id: str) -> bool:
    signal = activity_id.upper()
    return any(
        (
            "KONUSMA_SIRASI" in signal,
            ("SUNUM" in signal and "PLAN" not in signal),
            ("PODCAST_URETIM" in signal),
            ("CANLANDIR" in signal and "PLAN" not in signal),
            (("DINLETI" in signal or "DİNLETİ" in signal) and "PLAN" not in signal),
        )
    )


def performance_lesson_numbers(plan: dict[str, Any]) -> list[int]:
    if not is_speaking_block(plan):
        return []
    result: list[int] = []
    for lesson in plan.get("lessons", []):
        if not isinstance(lesson, dict):
            continue
        activity_ids = lesson.get("activity_ids", [])
        if not isinstance(activity_ids, list):
            continue
        if any(isinstance(item, str) and is_performance_activity(item) for item in activity_ids):
            number = lesson.get("lesson_no")
            if isinstance(number, int) and not isinstance(number, bool) and number > 0:
                result.append(number)
    return sorted(set(result))


def route_for(plan: dict[str, Any], lesson_numbers: list[int]) -> dict[str, Any]:
    activity_ids = [
        item
        for item in plan.get("used_activity_ids", [])
        if isinstance(item, str) and is_performance_activity(item)
    ]
    signal = " ".join(activity_ids + [str(plan.get("plan_title") or ""), str(plan.get("plan_summary") or "")]).upper()

    if "CANLANDIR" in signal or "DINLETI" in signal or "DİNLETİ" in signal:
        group_count = 4
        time_limit = 180
    elif "YENIDEN" in signal or "YENİDEN" in signal or "TELAFI" in signal or "TELAFİ" in signal:
        group_count = 5
        time_limit = 90
    else:
        group_count = 5
        time_limit = 120

    return {
        "mode": "PARALLEL_GROUPS",
        "activation_condition": "Tek sıra canlı performans rotası mevcut ders saatinde tüm öğrenciler için güvenilir biçimde tamamlanamıyorsa kullan.",
        "applies_to_lesson_numbers": lesson_numbers,
        "parallel_group_count": group_count,
        "grouping_strategy": "Sınıfı 4-6 kişilik paralel performans gruplarına ayır; konuşmacı ve gözlemci rollerini her turda döndür, hiçbir öğrenciyi yalnız gözlemci rolünde bırakma.",
        "teacher_rotation_strategy": "Öğretmen gruplar arasında planlı olarak döner; her öğrenciden en az bir doğrudan performans kanıtı toplar ve diğer kanıtları akran kayıtlarıyla çapraz kontrol eder.",
        "peer_observer_strategy": "Her gruptaki akran gözlemci yalnız plandaki mevcut performans ölçütlerinden bir güçlü davranış ve bir geliştirme kanıtı kaydeder; kişilik veya genel beğeni yorumu yapmaz.",
        "performance_time_limit_seconds": time_limit,
        "evidence_equivalence": "Standart sınıf rotasındaki aynı etkinlik, öğrenme çıktıları, performans ölçütleri ve öğrenci kanıtları korunur; yalnız yürütme paralelleştirilir ve öğretmen gözlemi rotasyonla örneklenir.",
        "core_hours_independent_of_school_based_extension": True,
        "optional_school_based_extension": {
            "allowed": True,
            "purpose": "Yalnız hedefli ek prova veya kısa yeniden performans için kullanılabilir; çekirdek paketin tamamlanması okul-temelli saate bağlı değildir.",
        },
    }


def insert_before_lessons(plan: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    inserted = False
    for key, value in plan.items():
        if key == "lessons" and not inserted:
            result["large_class_route"] = route
            inserted = True
        result[key] = value
    if not inserted:
        result["large_class_route"] = route
    return result


def dump_preserving_style(path: Path, original: str, payload: dict[str, Any]) -> None:
    compact = "\n" not in original.strip()
    if compact:
        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    else:
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    if original.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def migrate(root: Path, *, check: bool = False) -> tuple[int, list[str]]:
    changed: list[str] = []
    plans_root = root / "generated" / "lesson_plans"
    for path in sorted(plans_root.rglob("*.json")):
        original = path.read_text(encoding="utf-8")
        plan = json.loads(original)
        lesson_numbers = performance_lesson_numbers(plan)
        if not lesson_numbers:
            continue
        if isinstance(plan.get("large_class_route"), dict):
            continue
        changed.append(str(path.relative_to(root)))
        if not check:
            migrated = insert_before_lessons(plan, route_for(plan, lesson_numbers))
            dump_preserving_style(path, original, migrated)
    return len(changed), changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-root", action="append", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    total = 0
    all_changed: list[str] = []
    for value in args.knowledge_root:
        root = Path(value).resolve()
        count, changed = migrate(root, check=args.check)
        total += count
        all_changed.extend(f"{root.name}/{item}" for item in changed)

    print(json.dumps({"status": "PASS" if not args.check or total == 0 else "FAIL", "packages": total, "paths": all_changed}, ensure_ascii=False, indent=2))
    return 1 if args.check and total else 0


if __name__ == "__main__":
    raise SystemExit(main())
