#!/usr/bin/env python3
"""Apply the approved TDE11 Theme 1 pedagogical-design overlay.

The transformation is deliberately narrow: canonical outcome/activity/form IDs,
materials, grounded references, hour counts, large-class routes and classroom
adaptations are preserved. Only teacher-facing pedagogical fields are revised.
Markdown is regenerated with the repository's canonical renderer.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SCRIPT_DIR))

from render_lesson_plan_markdown import render  # noqa: E402

COURSE_ROOT = REPO_ROOT / "courses/TDE_11"
OVERLAY_PATH = COURSE_ROOT / "planning/pedagogical_package_design.json"
THEME_ROOT = COURSE_ROOT / "generated/lesson_plans/TEMA_01"

TITLE_MAP: dict[str, list[str]] = {
    "BLOCK_T1_01_OKUMA_P01": [
        "Karagöz’e Hazırlık: Okuma Amacı ve İlk Tahmin",
        "Karagöz’e Hazırlık: Strateji Seçimini Gerekçelendirme",
    ],
    "BLOCK_T1_01_OKUMA_P02": [
        "Karagöz’de Anlam İzleri: Kanıtları Belirleme",
        "Karagöz’de Konu, Tema ve İleti: Kanıttan Yoruma",
    ],
    "BLOCK_T1_01_OKUMA_P03": [
        "Karagöz’ü Çözümleme: Yapı, Tür ve Dil Bulguları",
        "Karagöz’ü Çözümleme: Ölçütlerle Karşılaştırma",
    ],
    "BLOCK_T1_01_OKUMA_P04": [
        "Karagöz Okumasını Değerlendirme: Kanıta Bakış",
        "Karagöz’den Sonraki Metne: Okuma Stratejisi Kararı",
    ],
    "BLOCK_T1_01_OKUMA_P05": [
        "Âli’ye Mektuplar ve Dilekçeye Hazırlık: Amaç ve Tahmin",
        "Tahminleri Sınama: Metin ve Bağlam İpuçları",
    ],
    "BLOCK_T1_01_OKUMA_P06": [
        "Âli’ye Mektuplar: Konu, İleti ve Bağlam",
        "Mektuptan Dilekçeye: Anlam ve Bağlam Karşılaştırması",
    ],
    "BLOCK_T1_01_OKUMA_P07": [
        "Mektup ve Dilekçeyi Yakından Çözümleme",
        "Yapı, Tür ve Dilden Karşılaştırmalı Sonuca",
    ],
    "BLOCK_T1_01_OKUMA_P08": [
        "Okuma Bloğunu Kapatma: Öz Değerlendirme ve Transfer",
    ],
    "BLOCK_T1_02_KONUSMA_P01": [
        "Drama İçin Konuşma Planı: Amaç, Hedef Kitle ve Roller",
        "Drama Planını Savunma: Strateji ve Uygulama Koşulları",
    ],
    "BLOCK_T1_02_KONUSMA_P02": [
        "Sözlü İletişim Engelleri Draması: İlk Senaryo Akışı",
        "Senaryoyu Geliştirme: Akran Geri Bildirimi ve Revizyon",
    ],
    "BLOCK_T1_02_KONUSMA_P03": [
        "Drama Performansı I: İlk Canlandırma ve Gözlem",
        "Drama Performansı II: Gözlemden Yeniden Performansa",
    ],
    "BLOCK_T1_02_KONUSMA_P04": [
        "Konuşmada Etkili Kullanımlar: Güçlü Örnekleri Yakalama",
        "Karşı Örnekten İyileştirmeye: Performans Ölçütünü Uygulama",
    ],
    "BLOCK_T1_02_KONUSMA_P05": [
        "Konuşma Performansını Değerlendirme: Kanıtları Birleştirme",
        "Konuşma Becerisinde Sonraki Adım: Öz Değerlendirmeden Transfer",
    ],
    "BLOCK_T1_03_DINLEME_P01": [
        "Değişen İletişim Araçlarına Hazırlık: Amaç ve Tahmin",
        "Dinleme/İzleme Tahminlerini Kanıtla Güncelleme",
    ],
    "BLOCK_T1_03_DINLEME_P02": [
        "İletişim Araçları Metninde Anlam Kanıtlarını Toplama",
        "Konu, Tema ve İleti: Dinleme Kanıtından Yoruma",
    ],
    "BLOCK_T1_03_DINLEME_P03": [
        "Çok Modlu Metni Çözümleme: Yapı, Dil ve Bağlam",
        "Çözümleme Bulgularından Bütüncül Çıkarıma",
    ],
    "BLOCK_T1_03_DINLEME_P04": [
        "Dinleme/İzleme Sürecini Değerlendirme: Gözlem Kanıtı",
        "Çıkış Kartından Sonraki Dinlemeye: Strateji Kararı",
    ],
    "BLOCK_T1_04_YAZMA_P01": [
        "E-Posta Yazmaya Hazırlık: Amaç, Hedef Kitle ve Plan",
        "E-Posta Planını Gerekçelendirme ve Revize Etme",
    ],
    "BLOCK_T1_04_YAZMA_P02": [
        "E-Postanın İçeriğini Kurma: İlk Taslak",
        "E-Posta İçeriğini Geliştirme: Geri Bildirim ve Revizyon",
    ],
    "BLOCK_T1_04_YAZMA_P03": [
        "E-Posta Taslağını Denetleme: Tür, Dil ve Yazım",
        "E-Postayı Düzenleme: Hatalardan Nihai Ürüne",
    ],
    "BLOCK_T1_04_YAZMA_P04": [
        "E-Posta Ürününü Değerlendirme: Öncelikli Geliştirme Alanı",
        "E-Postayı Son Kez Revize Etme: Geri Bildirimden Nihai Sürüme",
    ],
    "BLOCK_T1_04_YAZMA_P05": [
        "Yazma Sürecini Kapatma: Güçlü Yön ve Son Geliştirme Kararı",
        "1. Tema Ölçme ve Değerlendirme: Bağımsız Tema Kanıtı",
    ],
}

# This lesson already has a source-bound, time-budgeted theme-assessment flow.
# Preserve its full body and only replace the generic title.
PRESERVE_BODY = {("BLOCK_T1_04_YAZMA_P05", 2)}

ROUTE_GUIDANCE: dict[str, tuple[str, str]] = {
    "PREDICT_VERIFY": (
        "İlk kanıtın gerekçesini görünür kıl; tahmin/strateji kaydını kaynak göstergeleriyle ilişkilendir.",
        "İkinci saatte ilk tahmini veya strateji kararını eldeki kaynak göstergeleriyle sınat; doğrulanan, değişen veya reddedilen kısmı açıkça kaydettir.",
    ),
    "EVIDENCE_INTERPRET": (
        "Önce öğrencinin hedef beceriye ilişkin somut kanıtı seçmesini ve işaretlemesini sağla.",
        "İkinci saatte seçilen kanıtın ne gösterdiğini, anlam/işlev ilişkisini ve gerekçesini açıklat.",
    ),
    "CLASSIFY_JUSTIFY": (
        "İlk saatte bulguları görünür ölçütlere göre sınıflandır; kategori ile kanıt arasındaki bağı kaydettir.",
        "İkinci saatte sınıflandırma ölçütünü ve tartışmalı örnekleri gerekçelendirt; yalnız listelemeyi yeterli sayma.",
    ),
    "REFLECT_TRANSFER": (
        "İlk saatte mevcut ürün/süreç kanıtını değerlendirme nesnesi yap; güçlü ve geliştirilecek yönü somut kanıtla belirlet.",
        "İkinci saatte değerlendirme sonucunu sonraki görevde uygulanabilecek açık bir strateji veya eylem kararına dönüştürt.",
    ),
    "INTERTEXT_COMPARE": (
        "İlk saatte birinci metne ait hedef kanıtları bağımsız biçimde görünür kıl.",
        "İkinci saatte iki metni aynı ölçütlerle karşılaştır; benzerlik/farklılık sonucunu her iki kaynaktan kanıtla gerekçelendirt.",
    ),
    "CLOSE_READ_SYNTHESIZE": (
        "İlk saatte ayrıntılı çözümleme ve işaretleme yaptır; parçalı bulguların kaydını tuttur.",
        "İkinci saatte bu bulguları tek tek tekrar etmek yerine metnin bütünüyle ilişkilendirip sentez sonucuna dönüştürt.",
    ),
    "CLAIM_EVIDENCE_DEFEND": (
        "İlk saatte öğrencinin plan/yorum/strateji seçimini açık bir karar ve dayanakla kaydetmesini sağla.",
        "İkinci saatte bu seçimin nedenini görev kanıtıyla savundur; karşı soru veya geri bildirim sonucunda gerekirse kararı revize ettir.",
    ),
    "DRAFT_PEER_REVISE": (
        "İlk saatte bağımsız bir ilk taslak veya ürün üret; taslağı bitmiş ürün gibi değerlendirme.",
        "İkinci saatte görev beklentisine dayalı akran geri bildirimi izi bırak ve yalnız geri bildirim verilen noktaları gerekçeli biçimde revize ettir.",
    ),
    "PERFORM_OBSERVE_REPERFORM": (
        "İlk saatte canlı performansı gerçekleştir ve görünür performans davranışlarına ilişkin gözlem kanıtı topla.",
        "İkinci saatte gözlemden seçilen hedefli değişikliği ikinci performansta uygulat; iki performans arasındaki farkı öğrencinin açıklamasını iste.",
    ),
    "EXAMPLE_COUNTEREXAMPLE": (
        "İlk saatte hedef davranışı gösteren güçlü örnekleri somut performans/ürün kanıtından seçtir.",
        "İkinci saatte geliştirilecek karşı örneklerle sınırı görünür kıl; ölçütü yeni performans veya üründe uygulat.",
    ),
    "ERROR_REPAIR": (
        "İlk saatte ürün veya çözümlemedeki hata/eksikliği somut göstergeyle işaretlet; düzeltmeye geçmeden sorunu adlandır.",
        "İkinci saatte yalnız belirlenen sorunları düzelt; değişikliğin ürün üzerindeki etkisini öğrencinin açıklamasını iste.",
    ),
    "INDIVIDUAL_COMPARE": (
        "İlk saatte bireysel çözümleme/ürün kanıtını tamamlat.",
        "İkinci saatte iki çözüm veya yaklaşımı ortak ölçütle karşılaştırıp benzerlik/farklılık sonucunu savundur.",
    ),
    "DIAGNOSE_TARGET_EXIT": (
        "İlk saatte kısa kanıtla güçlü ve eksik yönü belirle.",
        "İkinci saatte belirlenen ihtiyete dönük hedefli uygulama yaptır ve çıkış kanıtıyla değişimi görünür kıl.",
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(plan: dict[str, Any]) -> str:
    return json.dumps(plan, ensure_ascii=False, separators=(",", ":")) + "\n"


def base_objective(text: str) -> str:
    text = text.split(" Bu ders saatinin pedagojik odağı:", 1)[0].strip()
    text = re.sub(r"; ürettiği kanıtı gerekçelendirerek .+? sürecini tamamlar\.$", ".", text)
    return text


def canonical_task(lesson: dict[str, Any]) -> str:
    if lesson.get("student_actions"):
        first = str(lesson["student_actions"][0]).strip()
        if first:
            return first
    return base_objective(str(lesson.get("objective", "")))


def source_guard(lesson: dict[str, Any]) -> str:
    for action in lesson.get("teacher_actions", []):
        text = str(action)
        if "doğrulanmış kapsam" in text or "kaynakta bulunmayan" in text:
            return text
    return "Ders kitabındaki doğrulanmış görev kapsamını uygula; kaynakta bulunmayan içerik, ölçüt veya resmî sıralama ekleme."


def route_guidance(route_id: str, lesson_no: int) -> str:
    guidance = ROUTE_GUIDANCE.get(route_id)
    if guidance is None:
        raise ValueError(f"UNKNOWN_ROUTE_GUIDANCE:{route_id}")
    return guidance[0 if lesson_no == 1 else 1]


def revised_lesson(
    package_id: str,
    route_id: str,
    original: dict[str, Any],
    progression: dict[str, Any],
    title: str,
) -> dict[str, Any]:
    lesson_no = int(original["lesson_no"])
    if (package_id, lesson_no) in PRESERVE_BODY:
        result = copy.deepcopy(original)
        result["title"] = title
        return result

    result = copy.deepcopy(original)
    task = canonical_task(original)
    operation = progression["cognitive_operation"].strip().rstrip(".")
    evidence = progression["student_evidence"].strip().rstrip(".")
    delta = progression["delta_from_previous"].strip().rstrip(".")
    material = str(original.get("materials", ["ders kitabındaki doğrulanmış kaynak"])[0])

    result["title"] = title
    result["objective"] = (
        f"{base_objective(str(original['objective']))} "
        f"Bu ders saatinin pedagojik odağı: {operation.lower()}; somut kanıt: {evidence}."
    )
    result["opening"] = (
        f"{material} üzerinden bu saatin odağı görünür kılınır: {operation}. "
        "Öğrenci önceki/başlangıç kanıtını kısa biçimde önüne alır ve bu saatin sonunda neyin değişmiş veya derinleşmiş olması gerektiğini kendi cümlesiyle belirtir."
    )
    result["teacher_actions"] = [
        source_guard(original),
        f"Canonical görevi koru: {task}",
        route_guidance(route_id, lesson_no),
        f"Bu saate özgü kanıtı topla: {evidence}. Yalnız katılımı yeterli kanıt sayma; öğrencinin yaptığı bilişsel işlemi ürününde veya kaydında görünür kıl.",
    ]
    result["student_actions"] = [
        task,
        f"{operation}.",
        f"Kanıt olarak şunu üretir veya günceller: {evidence}.",
        (
            "İlk kanıtında ikinci saatte sınayacağı, karşılaştıracağı, geliştireceği veya aktaracağı tek noktayı işaretler."
            if lesson_no == 1
            else f"İlk kanıtıyla bu saatin kanıtını karşılaştırır ve değişimi açıklar: {delta}."
        ),
    ]
    result["assessment"] = (
        f"Bu ders saatinin birincil ölçme kanıtı “{evidence}”dir. "
        f"Değerlendirme, öğrencinin “{operation}” işlemini görünür ve gerekçeli biçimde yapıp yapmadığına dayanır; "
        "kaynakta doğrulanmamış puan aralığı veya rubrik ölçütü eklenmez."
    )
    result["closure"] = (
        f"Öğrenci “{evidence}” kanıtında ikinci derse taşıyacağı tek soruyu, varsayımı veya geliştirme noktasını işaretler."
        if lesson_no == 1
        else f"Öğrenci ilk kanıt ile son kanıt arasındaki farkı tek cümlede açıklar ve şu ilerlemeyi görünür kılar: {delta}."
    )
    return result


def locate_package(package_id: str) -> Path:
    matches = list(THEME_ROOT.glob(f"**/{package_id}.json"))
    if len(matches) != 1:
        raise ValueError(f"PACKAGE_LOOKUP:{package_id}:found={len(matches)}")
    return matches[0]


def transform(plan: dict[str, Any], design: dict[str, Any]) -> dict[str, Any]:
    package_id = design["package_id"]
    route_id = design["route_id"]
    progression = {int(item["lesson_no"]): item for item in design["lesson_progression"]}
    titles = TITLE_MAP.get(package_id)
    if titles is None:
        raise ValueError(f"TITLE_MAP_MISSING:{package_id}")
    lessons = plan.get("lessons", [])
    if len(titles) != len(lessons):
        raise ValueError(f"TITLE_COUNT_MISMATCH:{package_id}:{len(titles)}!={len(lessons)}")
    if set(progression) != {int(item["lesson_no"]) for item in lessons}:
        raise ValueError(f"PROGRESSION_LESSON_SET_MISMATCH:{package_id}")

    result = copy.deepcopy(plan)
    result["lessons"] = [
        revised_lesson(package_id, route_id, lesson, progression[int(lesson["lesson_no"])], titles[index])
        for index, lesson in enumerate(lessons)
    ]
    return result


def run(*, write: bool, check: bool) -> dict[str, Any]:
    overlay = load_json(OVERLAY_PATH)
    designs = [item for item in overlay.get("packages", []) if item["package_id"].startswith("BLOCK_T1_")]
    if len(designs) != 22:
        raise ValueError(f"THEME1_DESIGN_COUNT:{len(designs)}!=22")
    if set(TITLE_MAP) != {item["package_id"] for item in designs}:
        missing = sorted({item["package_id"] for item in designs} - set(TITLE_MAP))
        extra = sorted(set(TITLE_MAP) - {item["package_id"] for item in designs})
        raise ValueError(f"TITLE_MAP_COVERAGE:missing={missing}:extra={extra}")

    changed: list[str] = []
    drift: list[str] = []
    for design in designs:
        json_path = locate_package(design["package_id"])
        current = load_json(json_path)
        expected = transform(current, design)
        json_text = canonical_json(expected)
        md_text = render(expected)
        md_path = json_path.with_suffix(".md")

        if json_path.read_text(encoding="utf-8") != json_text:
            changed.append(json_path.relative_to(REPO_ROOT).as_posix())
            if check:
                drift.append(json_path.relative_to(REPO_ROOT).as_posix())
            if write:
                json_path.write_text(json_text, encoding="utf-8")
        if not md_path.exists() or md_path.read_text(encoding="utf-8") != md_text:
            changed.append(md_path.relative_to(REPO_ROOT).as_posix())
            if check:
                drift.append(md_path.relative_to(REPO_ROOT).as_posix())
            if write:
                md_path.write_text(md_text, encoding="utf-8")

    payload = {
        "status": "FAIL" if drift else "PASS",
        "theme": "TEMA_01",
        "packages": len(designs),
        "write": write,
        "check": check,
        "changed_or_would_change": sorted(set(changed)),
        "drift": sorted(set(drift)),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = run(write=args.write, check=args.check)
    return 1 if payload["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
