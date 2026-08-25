#!/usr/bin/env python3
"""Materialize P5 theme-closure time budgets and align teacher-facing execution notes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

NOMINAL_LESSON_MINUTES = 40


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any], *, pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if pretty:
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    else:
        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")


def classify_activity(activity_id: str) -> set[str]:
    signal = activity_id.upper()
    kinds: set[str] = set()
    is_theme = "TEMA" in signal
    if is_theme and ("OLCME" in signal or "TEST" in signal or "DEGERLENDIR" in signal):
        kinds.add("THEME_ASSESSMENT")
    if (is_theme and ("GUNLUK" in signal or "YANSIT" in signal)) or "OGRENME_GUNLUGU" in signal:
        kinds.add("REFLECTION")
    return kinds


def lesson_signals(lesson: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for activity_id in lesson.get("activity_ids", []):
        if isinstance(activity_id, str):
            result.update(classify_activity(activity_id))
    return result


def optional_extension(kind: str, minutes: int, purpose: str, activation: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "minutes": minutes,
        "placement": "SCHOOL_BASED_IF_SELECTED",
        "required_for_core_completion": False,
        "activation_condition": activation,
        "purpose": purpose,
    }


def budget_for(theme_id: str, lesson_no: int, signals: set[str]) -> tuple[dict[str, Any], str]:
    if signals == {"THEME_ASSESSMENT", "REFLECTION"}:
        required = [
            {
                "kind": "THEME_ASSESSMENT",
                "minutes": 25,
                "purpose": "Kaynak tema sonu ölçme sorularını bağımsız biçimde yanıtlamak.",
            },
            {
                "kind": "REFLECTION",
                "minutes": 10,
                "purpose": "Öğrenme günlüğünde bir güçlü kanıt, bir gelişim alanı ve aktarılabilir stratejiyi kısa biçimde kaydetmek.",
            },
            {
                "kind": "CLOSURE",
                "minutes": 3,
                "purpose": "Tema/yıl kapanışını ve sonraki adımı tek kısa kayıtla netleştirmek.",
            },
        ]
        buffer_minutes = 2
        optional = [
            optional_extension(
                "ANSWER_CORRECTION",
                10,
                "Yanlış veya kararsız cevapları önceki öğrenme kanıtlarına dönerek ayrıntılı biçimde düzeltmek.",
                "Tema sonu ölçmede ortak veya pedagojik olarak anlamlı bir yanılgı görülür ve öğretmen/zümre bu ihtiyaca okul-temelli saat ayırmayı seçerse.",
            ),
            optional_extension(
                "EXTENDED_REFLECTION",
                10,
                "Öğrenme günlüğünü çoklu ürün/performans kanıtlarıyla genişletmek.",
                "Öğrencilerin öz-yansıtma kanıtı yüzeysel kalır ve öğretmen/zümre okul-temelli genişletme seçerse.",
            ),
        ]
        if theme_id == "TEMA_04":
            optional.append(
                optional_extension(
                    "YEAR_PORTFOLIO_REVIEW",
                    12,
                    "Yıl boyunca seçilmiş okuma, dinleme/izleme, konuşma ve yazma kanıtlarını ayrıntılı portfolyo taramasıyla karşılaştırmak.",
                    "Yıl sonu portfolyo sentezi için ihtiyaç ve zaman ayrılırsa; çekirdek kapanışın tamamlanması buna bağlı değildir.",
                )
            )
        else:
            optional.append(
                optional_extension(
                    "NEXT_THEME_PREP",
                    8,
                    "Sonraki temanın hazırlık yönergelerini ayrıntılı incelemek ve ön bilgiyi etkinleştirmek.",
                    "Öğretmen/zümre geçiş ihtiyacı belirler ve okul-temelli saat kullanmayı seçerse.",
                )
            )
        marker = (
            "Süre bütçesi: 25 dk tema ölçme + 10 dk çekirdek yansıtma + 3 dk kapanış + 2 dk tampon. "
            "Ayrıntılı yanlış düzeltme, genişletilmiş portfolyo taraması ve sonraki tema/yıl hazırlığı çekirdek tamamlanma koşulu değildir; "
            "yalnız öğretmen/zümre ihtiyaç görür ve okul-temelli genişletmeyi seçerse sürdürülür."
        )
    elif signals == {"THEME_ASSESSMENT"}:
        required = [
            {
                "kind": "THEME_ASSESSMENT",
                "minutes": 32,
                "purpose": "Kaynak tema sonu ölçme sorularını bağımsız biçimde yanıtlamak.",
            },
            {
                "kind": "CLOSURE",
                "minutes": 5,
                "purpose": "Güçlü/geliştirilecek alanı tek kısa kayıtla belirlemek.",
            },
        ]
        buffer_minutes = 3
        optional = [
            optional_extension(
                "ANSWER_CORRECTION",
                10,
                "Yanlış veya kararsız cevapları önceki tema kanıtlarına dönerek ayrıntılı düzeltmek.",
                "Anlamlı ortak yanılgı görülür ve öğretmen/zümre okul-temelli saat ayırmayı seçerse.",
            )
        ]
        marker = (
            "Süre bütçesi: 32 dk tema ölçme + 5 dk kısa kapanış + 3 dk tampon. "
            "Ayrıntılı yanlış düzeltme çekirdek tamamlanma koşulu değildir; yalnız öğretmen/zümre ihtiyaç görür ve okul-temelli genişletmeyi seçerse yapılır."
        )
    elif signals == {"REFLECTION"}:
        required = [
            {
                "kind": "REFLECTION",
                "minutes": 32,
                "purpose": "Öğrenme günlüğünü gerçek tema ürün/strateji kanıtlarıyla tamamlamak.",
            },
            {
                "kind": "CLOSURE",
                "minutes": 5,
                "purpose": "Bir sonraki temaya taşınacak tek gözlenebilir stratejiyi belirlemek.",
            },
        ]
        buffer_minutes = 3
        optional = [
            optional_extension(
                "EXTENDED_REFLECTION",
                10,
                "Birden çok beceri alanını karşılaştıran ayrıntılı portfolyo/yansıtma taraması yapmak.",
                "Öğretmen/zümre derinleştirme ihtiyacı görür ve okul-temelli saat seçerse.",
            )
        ]
        marker = (
            "Süre bütçesi: 32 dk öğrenme günlüğü/yansıtma + 5 dk kısa kapanış + 3 dk tampon. "
            "Genişletilmiş portfolyo taraması çekirdek tamamlanma koşulu değildir; yalnız öğretmen/zümre ihtiyaç görür ve okul-temelli genişletmeyi seçerse yapılır."
        )
    else:
        raise ValueError(f"Unsupported closure signal set for lesson {lesson_no}: {sorted(signals)}")

    required_total = sum(item["minutes"] for item in required)
    return (
        {
            "lesson_no": lesson_no,
            "signals": sorted(signals),
            "required_segments": required,
            "required_minutes_total": required_total,
            "buffer_minutes": buffer_minutes,
            "optional_extensions": optional,
        },
        marker,
    )


def package_contract(relative_path: str, plan: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    lesson_budgets: list[dict[str, Any]] = []
    changed = False
    for lesson in plan.get("lessons", []):
        if not isinstance(lesson, dict) or lesson.get("assessment_scope") != "THEME":
            continue
        signals = lesson_signals(lesson)
        if not signals:
            continue
        lesson_no = lesson.get("lesson_no")
        if not isinstance(lesson_no, int) or isinstance(lesson_no, bool):
            raise ValueError(f"Invalid theme-closure lesson number in {relative_path}")
        budget, marker = budget_for(str(plan.get("theme_id")), lesson_no, signals)
        lesson_budgets.append(budget)

        actions = lesson.get("teacher_actions")
        if not isinstance(actions, list):
            raise ValueError(f"teacher_actions missing in {relative_path} lesson {lesson_no}")
        filtered = [
            item
            for item in actions
            if not (isinstance(item, str) and item.startswith("Süre bütçesi:"))
        ]
        new_actions = [marker, *filtered]
        if new_actions != actions:
            lesson["teacher_actions"] = new_actions
            changed = True

    if not lesson_budgets:
        raise ValueError(f"Theme-scoped package has no closure signals: {relative_path}")

    note = (
        "P5 süre sözleşmesi: tema kapanışındaki çekirdek tamamlanma yalnız closure_time_budgets.json içindeki required_segments ile belirlenir; "
        "optional_extensions öğretmen/zümre seçimi olmadan zorunlu değildir ve 43 saatlik çekirdek kuyruğu okul-temelli saate bağımlı hâle getirmez."
    )
    current_notes = str(plan.get("teacher_notes") or "")
    cleaned_notes = current_notes.split(" P5 süre sözleşmesi:", 1)[0].rstrip()
    updated_notes = f"{cleaned_notes} {note}".strip()
    if updated_notes != current_notes:
        plan["teacher_notes"] = updated_notes
        changed = True

    return (
        {
            "package_id": Path(relative_path).stem,
            "path": relative_path,
            "theme_id": plan.get("theme_id"),
            "block_id": plan.get("block_id"),
            "lesson_budgets": sorted(lesson_budgets, key=lambda item: item["lesson_no"]),
        },
        changed,
    )


def apply(knowledge_root: Path, *, write: bool) -> dict[str, Any]:
    generated = knowledge_root / "generated" / "lesson_plans"
    if not generated.is_dir():
        raise ValueError(f"generated lesson plans missing: {generated}")

    packages: list[dict[str, Any]] = []
    changed_paths: list[str] = []
    for path in sorted(generated.rglob("*.json")):
        plan = read_json(path)
        if plan.get("assessment_scope") != "THEME":
            continue
        has_theme_lesson = any(
            isinstance(lesson, dict)
            and lesson.get("assessment_scope") == "THEME"
            and bool(lesson_signals(lesson))
            for lesson in plan.get("lessons", [])
        )
        if not has_theme_lesson:
            continue
        relative = path.relative_to(knowledge_root).as_posix()
        contract, changed = package_contract(relative, plan)
        packages.append(contract)
        if changed and write:
            write_json(path, plan, pretty=False)
            changed_paths.append(relative)

    if len(packages) != 4:
        raise ValueError(f"Expected 4 theme-closure packages for {knowledge_root.name}, found {len(packages)}")

    payload = {
        "schema_version": "1.0.0",
        "course_id": knowledge_root.name,
        "nominal_lesson_minutes": NOMINAL_LESSON_MINUTES,
        "policy": {
            "core_completion_independent_of_school_based_extension": True,
            "school_based_extension_is_teacher_selected": True,
            "mixed_closure_split_minutes": {
                "theme_assessment": 25,
                "reflection": 10,
                "closure": 3,
                "buffer": 2,
            },
            "single_focus_buffer_minutes": 3,
            "note": "40 dakika bu repoda pedagojik süre bütçesi için kullanılan nominal ders periyodudur; okul-temelli genişletme otomatik değildir ve çekirdek kapanışın ön koşulu olamaz.",
        },
        "packages": sorted(packages, key=lambda item: (item["theme_id"], item["package_id"])),
    }

    contract_path = knowledge_root / "production" / "closure_time_budgets.json"
    existing = read_json(contract_path) if contract_path.exists() else None
    contract_changed = existing != payload
    if write and contract_changed:
        write_json(contract_path, payload, pretty=True)
        changed_paths.append(contract_path.relative_to(knowledge_root).as_posix())

    return {
        "status": "PASS",
        "course_id": knowledge_root.name,
        "theme_closure_packages": len(packages),
        "changed_paths": changed_paths,
        "contract_changed": contract_changed,
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
