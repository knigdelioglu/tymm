#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF_REL = "source_docs/turk-dili-ve-edebiyati-11sinif-ders-kitabi_compressed.pdf"
PDF_PATH = ROOT / PDF_REL
SOURCE_ID = "textbook_tde11_local_pdf"
COURSE_ID = "TDE_11"
GRADE = 11
TODAY = "2026-09-11"

THEMES = [
    {
        "theme_id": "TEMA_01", "theme_no": 1, "title": "1. TEMA: BİR DİYECEĞİM VAR!", "range": (12, 83),
        "sections": [
            ("T1_SEC_01_OKUMA_KARAGOZ", "OKUMA", "Metin Tahlili-1 (Anlama): Okuma — Karagöz Oyunu (Yazıcı)", 15, 35),
            ("T1_SEC_02_OKUMA_MEKTUP", "OKUMA", "Metin Tahlili-2 (Anlama): Okuma — Mektup (Âli’ye Mektuplar) / Dilekçe", 36, 52),
            ("T1_SEC_03_KONUSMA_DRAMA", "KONUSMA", "Edebiyat Atölyesi-1 (Anlatma): Konuşma — Sözlü İletişim Engellerini Konu Alan Bir Drama", 53, 58),
            ("T1_SEC_04_DINLEME_ILETISIM", "DINLEME", "Metin Tahlili-3 (Anlama): Dinleme / İzleme — Değişen İletişim Araçlarının Hayatımızdaki Yeri", 59, 73),
            ("T1_SEC_05_YAZMA_EPOSTA", "YAZMA", "Edebiyat Atölyesi-2 (Anlatma): Yazma — E-Posta Yazabilme", 74, 78),
            ("T1_SEC_06_TEMA_OLCME", "OLCME", "1. Tema Ölçme ve Değerlendirme Soruları", 79, 83),
        ],
    },
    {
        "theme_id": "TEMA_02", "theme_no": 2, "title": "2. TEMA: KÜLTÜR YOLCULUĞU", "range": (84, 159),
        "sections": [
            ("T2_SEC_01_OKUMA_HIKAYE_ANI", "OKUMA", "Metin Tahlili-1 (Anlama): Okuma — Hikâye / Anı", 88, 112),
            ("T2_SEC_02_OKUMA_ORHUN_DLT", "OKUMA", "Metin Tahlili-2 (Anlama): Okuma — Orhun Abideleri / Dîvânu Lugâti’t-Türk", 113, 128),
            ("T2_SEC_03_KONUSMA_TURK_KULTURU", "KONUSMA", "Edebiyat Atölyesi-1 (Anlatma): Konuşma — Türk Kültürünün Özelliklerini Yansıtan Bir Konuşma", 129, 135),
            ("T2_SEC_04_DINLEME_ASIK_ATISMASI", "DINLEME", "Metin Tahlili-3 (Anlama): Dinleme / İzleme — Âşık Atışması", 136, 147),
            ("T2_SEC_05_YAZMA_MUZE", "YAZMA", "Edebiyat Atölyesi-2 (Anlatma): Yazma — Çevrim İçi Müze Gezisiyle İlgili İzlenimleri Yazabilme", 148, 154),
            ("T2_SEC_06_TEMA_OLCME", "OLCME", "2. Tema Ölçme ve Değerlendirme Soruları", 155, 159),
        ],
    },
    {
        "theme_id": "TEMA_03", "theme_no": 3, "title": "3. TEMA: YAŞAMIN İZİNDE", "range": (160, 235),
        "sections": [
            ("T3_SEC_01_OKUMA_HUZUR", "OKUMA", "Metin Tahlili-1 (Anlama): Okuma — Roman / Huzur", 164, 193),
            ("T3_SEC_02_OKUMA_BIYOGRAFI", "OKUMA", "Metin Tahlili-2 (Anlama): Okuma — Biyografi / Tezkire", 194, 209),
            ("T3_SEC_03_KONUSMA_MULAKAT", "KONUSMA", "Edebiyat Atölyesi-1 (Anlatma): Konuşma — Hayalî Mülakat", 210, 214),
            ("T3_SEC_04_DINLEME_RADYO_TIYATROSU", "DINLEME", "Metin Tahlili-3 (Anlama): Dinleme / İzleme — Radyo Tiyatrosu / Direnişin Ustaları", 215, 224),
            ("T3_SEC_05_YAZMA_DONUSTURME", "YAZMA", "Edebiyat Atölyesi-2 (Anlatma): Yazma — Diyaloğu Başka Bir Türe Dönüştürme", 225, 229),
            ("T3_SEC_06_TEMA_OLCME", "OLCME", "3. Tema Ölçme ve Değerlendirme Soruları", 230, 235),
        ],
    },
    {
        "theme_id": "TEMA_04", "theme_no": 4, "title": "4. TEMA: HAYATIN AYNASI", "range": (236, 307),
        "sections": [
            ("T4_SEC_01_OKUMA_TIYATRO", "OKUMA", "Metin Tahlili-1 (Anlama): Okuma — Tiyatro / Ben, Mimar Sinan", 240, 262),
            ("T4_SEC_02_OKUMA_KUCU_REK", "OKUMA", "Metin Tahlili-2 (Anlama): Okuma — Küçürek Hikâye / Merdiven", 263, 279),
            ("T4_SEC_03_KONUSMA_CANLANDIRMA", "KONUSMA", "Edebiyat Atölyesi-1 (Anlatma): Konuşma — Tiyatro Metnini Yeniden Kurgulayarak Canlandırma", 280, 283),
            ("T4_SEC_04_DINLEME_BELGESEL", "DINLEME", "Metin Tahlili-3 (Anlama): Dinleme / İzleme — Anadolu İnsanı / Fedakârlık", 284, 297),
            ("T4_SEC_05_YAZMA_AFIS", "YAZMA", "Edebiyat Atölyesi-2 (Anlatma): Yazma — Özgün Afiş Hazırlama", 298, 302),
            ("T4_SEC_06_TEMA_OLCME", "OLCME", "4. Tema Ölçme ve Değerlendirme Soruları", 303, 307),
        ],
    },
]

STAGES = {
    "OKUMA": [(1, "Okumayı Yönetebilme"), (2, "Anlam Oluşturabilme"), (3, "Çözümleyebilme"), (4, "Süreci Değerlendirebilme")],
    "DINLEME": [(1, "Dinleme / İzlemeyi Yönetebilme"), (2, "Anlam Oluşturabilme"), (3, "Çözümleyebilme"), (4, "Süreci Değerlendirebilme")],
    "KONUSMA": [(1, "Konuşmayı Yönetebilme"), (2, "İçerik Oluşturabilme"), (3, "Kural Uygulayabilme"), (4, "Süreci Değerlendirebilme")],
    "YAZMA": [(1, "Yazmayı Yönetebilme"), (2, "İçerik Oluşturabilme"), (3, "Kural Uygulayabilme"), (4, "Süreci Değerlendirebilme")],
}
SKILL_OUTCOME_PREFIX = {"DINLEME": 1, "OKUMA": 2, "KONUSMA": 3, "YAZMA": 4}
SKILL_CATEGORY = {"DINLEME": "Dinleme/İzleme", "OKUMA": "Okuma", "KONUSMA": "Konuşma", "YAZMA": "Yazma"}

ACTION = {
    ("DINLEME", 1): ("Dinleme/izleme amacını ve stratejisini belirler, ön bilgilerini etkinleştirir ve tahminde bulunur.", "Amaç/strateji kaydı, tahmin ve hazırlık notları."),
    ("DINLEME", 2): ("Dinlenen/izlenen metnin konu, tema, ileti, söz varlığı ve bağlamından anlam oluşturur.", "Anlama sorularına cevaplar ve yapılandırılmış dinleme/izleme notları."),
    ("DINLEME", 3): ("Çok modlu metni yapı, tür, dil-anlatım, kişi/olay/ileti ve bağlam yönlerinden çözümler.", "Tahlil cevapları, karşılaştırma/şema kayıtları ve gerekçeli çıkarımlar."),
    ("DINLEME", 4): ("Dinleme/izleme sürecini ve metne ilişkin değerlendirmelerini ölçütlere dayalı biçimde yansıtır.", "Öz değerlendirme, gözlem/öğrenme günlüğü veya gerekçeli değerlendirme kaydı."),
    ("OKUMA", 1): ("Okuma amacını ve stratejisini belirler, ön bilgilerini etkinleştirir ve metne ilişkin tahmin geliştirir.", "Okuma öncesi cevaplar, tahminler ve hazırlık notları."),
    ("OKUMA", 2): ("Metnin konu, tema, ileti, söz varlığı ve bağlamından anlam oluşturur.", "Anlama sorularına cevaplar, işaretlemeler ve anlamlandırma kayıtları."),
    ("OKUMA", 3): ("Metni yapı, tür, dil-anlatım ve dönem/bağlam özellikleri bakımından çözümler ve karşılaştırır.", "Tahlil cevapları, tablo/şema ve gerekçeli karşılaştırma kayıtları."),
    ("OKUMA", 4): ("Okuma sürecini ve metne ilişkin yargılarını belirlediği ölçütlerle değerlendirir.", "Öz değerlendirme, çıkış kartı, öğrenme günlüğü veya gerekçeli değerlendirme."),
    ("KONUSMA", 1): ("Konuşmanın amacını, hedef kitlesini, yöntem/stratejisini, hazırlık ve uygulama koşullarını planlar.", "Konuşma/canlandırma planı, görev ve hazırlık kayıtları."),
    ("KONUSMA", 2): ("Konuşma için bilgi, örnek, görsel/işitsel destek ve söz varlığını seçerek içeriği yapılandırır.", "Konuşma metni/senaryo/akış taslağı ve içerik düzenleme kayıtları."),
    ("KONUSMA", 3): ("Planladığı konuşmayı bağlama uygun dil, beden dili, ses, zaman ve mekân kullanımıyla gerçekleştirir.", "Canlı sözlü performans/canlandırma ve performans kaydı."),
    ("KONUSMA", 4): ("Konuşma performansını öz/akran/öğretmen değerlendirmesi ve geri bildirimle geliştirir.", "Öz/akran değerlendirme, öğretmen puanlama kanıtı ve yansıtma/revizyon kaydı."),
    ("YAZMA", 1): ("Yazma amacını, hedef kitlesini, türünü, yöntem/stratejisini ve üretim koşullarını planlar.", "Yazma planı, amaç/hedef kitle ve strateji kaydı."),
    ("YAZMA", 2): ("Bilgi, örnek, görsel/işitsel öge ve söz varlığını seçerek yazılı/çok modlu içeriği tasarlar.", "İçerik taslağı, plan/şema ve kaynak-seçim kayıtları."),
    ("YAZMA", 3): ("Taslağını tür, bağlam, Türkçe kullanımı, yazım-noktalama ve bütünlük ilkelerine göre ürüne dönüştürür.", "Düzenlenmiş yazılı veya çok modlu ürün."),
    ("YAZMA", 4): ("Yazma sürecini ve ürünü öz/akran/öğretmen değerlendirmesiyle gözden geçirip geliştirir.", "Öz/akran değerlendirme, öğretmen puanlama kanıtı ve revize edilmiş nihai ürün."),
}


def dump(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def locate_heading(page_texts: dict[int, str], start: int, end: int, heading: str) -> int | None:
    needle = compact(heading)
    variants = {needle, needle.replace(" / ", "/"), needle.replace("/", " / ")}
    for p in range(start, end + 1):
        hay = compact(page_texts.get(p, ""))
        if any(v in hay for v in variants):
            return p
    return None


def section_for_page(theme: dict[str, Any], printed_page: int) -> tuple | None:
    for sec in theme["sections"]:
        if sec[3] <= printed_page <= sec[4]:
            return sec
    return None


def source_locator(start: int, end: int | None = None) -> str:
    if end is None or end == start:
        return f"{PDF_REL}:s.{start}"
    return f"{PDF_REL}:s.{start}-{end}"


def build_book() -> tuple[dict[str, Any], dict[str, Any], dict[int, str]]:
    doc = fitz.open(PDF_PATH)
    if doc.page_count != 313:
        raise RuntimeError(f"Unexpected textbook PDF page count: {doc.page_count}")
    page_texts: dict[int, str] = {}
    page_links: dict[int, list[str]] = {}
    for printed in range(1, 311):
        idx = printed
        if idx >= doc.page_count:
            break
        page = doc.load_page(idx)
        page_texts[printed] = page.get_text("text")
        links = []
        for link in page.get_links():
            uri = link.get("uri")
            if isinstance(uri, str) and uri.startswith(("http://", "https://")):
                links.append(uri)
        page_links[printed] = sorted(set(links))

    mapped_themes = []
    activity_index: dict[str, dict[str, Any]] = {}
    missing = []
    total_activities = 0
    for theme in THEMES:
        seq = 0
        mapped_sections = []
        for sec_id, domain, title, start, end in theme["sections"]:
            activities = []
            if domain == "OLCME":
                seq += 1
                aid = f"T{theme['theme_no']}_ACT_{seq:02d}_TEMA_OLCME"
                act = {
                    "activity_id": aid,
                    "type": "theme_assessment",
                    "activity_type": "theme_assessment",
                    "exact_title": title,
                    "activity_title": title,
                    "activity_title_status": "EXACT_PRINTED_HEADING",
                    "stage_code": None,
                    "printed_page": start,
                    "printed_page_range": f"{start}-{end}",
                    "pdf_page": start + 1,
                    "pdf_page_range": f"{start + 1}-{end + 1}",
                    "student_action": "Tema boyunca edinilen bilgi ve becerileri farklı soru ve görev türlerinde kullanır.",
                    "expected_product_or_evidence": "Tema ölçme-değerlendirme sorularına verilen cevaplar ve gerekçeli performans kanıtları.",
                    "related_outcomes": [f"TDE{i}.{j}" for i in range(1, 5) for j in range(1, 5)],
                    "related_forms": [],
                    "source_locator": source_locator(start, end),
                    "verification_status": "LOCAL_OFFICIAL_PDF_PAGE_STRUCTURE_VERIFIED",
                }
                activities.append(act)
                activity_index[aid] = act
            else:
                stage_rows = []
                for stage_no, heading in STAGES[domain]:
                    p = locate_heading(page_texts, start, end, heading)
                    if p is None:
                        missing.append({"theme_id": theme["theme_id"], "section_id": sec_id, "domain": domain, "stage": stage_no, "heading": heading, "range": [start, end]})
                    stage_rows.append((stage_no, heading, p))
                observed = [row for row in stage_rows if row[2] is not None]
                if len(observed) != 4:
                    continue
                starts = [int(row[2]) for row in observed]
                for pos, (stage_no, heading, p) in enumerate(observed):
                    p = int(p)
                    next_p = starts[pos + 1] if pos + 1 < len(starts) else end + 1
                    activity_end = max(p, next_p - 1)
                    seq += 1
                    stage_slug = {1: "YONETIM", 2: "ICERIK_ANLAM", 3: "UYGULAMA_COZUMLEME", 4: "DEGERLENDIRME"}[stage_no]
                    aid = f"T{theme['theme_no']}_ACT_{seq:02d}_{domain}_{stage_slug}"
                    action, evidence = ACTION[(domain, stage_no)]
                    code = f"TDE{SKILL_OUTCOME_PREFIX[domain]}.{stage_no}"
                    act = {
                        "activity_id": aid,
                        "type": "curriculum_stage_activity",
                        "activity_type": "curriculum_stage_activity",
                        "exact_title": heading,
                        "activity_title": heading,
                        "activity_title_status": "EXACT_PRINTED_HEADING",
                        "stage_code": stage_no,
                        "skill_domain": SKILL_CATEGORY[domain],
                        "printed_page": p,
                        "printed_page_range": str(p) if activity_end == p else f"{p}-{activity_end}",
                        "pdf_page": p + 1,
                        "pdf_page_range": str(p + 1) if activity_end == p else f"{p + 1}-{activity_end + 1}",
                        "student_action": action,
                        "expected_product_or_evidence": evidence,
                        "related_outcomes": [code],
                        "related_forms": [],
                        "source_locator": source_locator(p, activity_end),
                        "verification_status": "LOCAL_OFFICIAL_PDF_HEADING_AND_RANGE_VERIFIED",
                    }
                    activities.append(act)
                    activity_index[aid] = act
            mapped_sections.append({
                "section_id": sec_id,
                "section_type": domain.lower(),
                "skill_domain": SKILL_CATEGORY.get(domain),
                "section_title": title,
                "title": title,
                "printed_page_range": f"{start}-{end}",
                "pdf_page_range": f"{start + 1}-{end + 1}",
                "source_locator": source_locator(start, end),
                "verification_status": "LOCAL_OFFICIAL_PDF_TOC_AND_PAGE_STRUCTURE_VERIFIED",
                "activities": activities,
            })
            total_activities += len(activities)
        mapped_themes.append({
            "theme_id": theme["theme_id"],
            "theme_no": theme["theme_no"],
            "title": theme["title"],
            "exact_title": theme["title"],
            "printed_page_range": f"{theme['range'][0]}-{theme['range'][1]}",
            "pdf_page_range": f"{theme['range'][0] + 1}-{theme['range'][1] + 1}",
            "sections": mapped_sections,
        })
    if missing:
        raise RuntimeError("Missing required textbook stage headings:\n" + json.dumps(missing, ensure_ascii=False, indent=2))

    def activity_for_page(theme_id: str, sec_id: str, page: int, prefer_stage4: bool = False) -> str | None:
        theme = next(t for t in mapped_themes if t["theme_id"] == theme_id)
        sec = next(s for s in theme["sections"] if s["section_id"] == sec_id)
        if prefer_stage4:
            stage4 = [a for a in sec["activities"] if a.get("stage_code") == 4]
            if stage4:
                return stage4[0]["activity_id"]
        covering = []
        for a in sec["activities"]:
            r = a.get("printed_page_range", "")
            nums = [int(x) for x in re.findall(r"\d+", r)]
            if nums and min(nums) <= page <= max(nums):
                covering.append(a)
        if covering:
            return covering[-1]["activity_id"]
        return sec["activities"][-1]["activity_id"] if sec["activities"] else None

    forms = []
    form_ids = set()
    dpa_count = 0
    form_seq: dict[int, int] = {i: 0 for i in range(1, 5)}

    def add_form(theme: dict[str, Any], page: int, kind: str, title: str, structural_type: str, evaluator: str, related_aid: str | None, *, linked: bool = False, dpa: bool = False) -> None:
        nonlocal dpa_count
        n = theme["theme_no"]
        form_seq[n] += 1
        prefix = "LINK" if linked else "FORM"
        if dpa:
            domain = "GENEL"
            sec = section_for_page(theme, page)
            if sec:
                domain = sec[1]
            fid = f"LINK_T{n}_{domain}_DPA"
            dpa_count += 1
        else:
            fid = f"{prefix}_T{n}_P{page:03d}_{kind}_{form_seq[n]:02d}"
        if fid in form_ids:
            raise RuntimeError(f"Duplicate form id: {fid}")
        form_ids.add(fid)
        txt = page_texts.get(page, "")
        opts = []
        if all(x in txt for x in ("Evet", "Kısmen", "Hayır")):
            opts = ["Evet", "Kısmen", "Hayır"]
        elif "Evet" in txt and "Hayır" in txt:
            opts = ["Evet", "Hayır"]
        candidate_links = [u for u in page_links.get(page, []) if any(host in u.lower() for host in ("eba.gov.tr", "meb.gov.tr"))]
        row = {
            "form_id": fid,
            "title": title,
            "structural_type": structural_type,
            "assessment_type": "dereceli_puanlama_anahtari_link" if dpa else structural_type,
            "printed_page": page,
            "pdf_page": page + 1,
            "source_locator": source_locator(page),
            "evaluator": evaluator,
            "criteria_present": None if linked else structural_type in {"self_assessment_form", "checklist", "observation_form"},
            "level_descriptors_present": None if linked else False,
            "scoring_levels_present": None if linked else bool(opts),
            "response_options": [] if linked else opts,
            "linked_theme_ids": [theme["theme_id"]],
            "linked_activity_ids": [related_aid] if related_aid else [],
            "verification_status": "OFFICIAL_QR_ASSESSMENT_TARGET_PRESENT_STRUCTURE_UNRESOLVED" if linked else "LOCAL_OFFICIAL_PDF_PAGE_STRUCTURE_VERIFIED",
            "canonical_structural_family": "teacher_evaluation_form" if dpa else structural_type,
            "taxonomy_relation": "NORMALIZED_TO_REFERENCE_FAMILY" if dpa else "REFERENCE_FAMILY",
            "structural_subtype": "linked_assessment_resource" if linked else structural_type,
            "audience": evaluator,
            "location_category": "external_official_assessment_link" if linked else "in_theme_section",
            "location_scope": "EXTERNAL_OFFICIAL_QR" if linked else "IN_THEME",
            "structure_details": {
                "scale_type": "unresolved_external_target" if linked else ("3_point_rating_scale" if len(opts) == 3 else "binary_checklist_scale" if len(opts) == 2 else "none_or_not_observed"),
                "criteria_count_observed_estimate": None,
                "has_level_descriptors": None if linked else False,
                "has_scoring_levels": None if linked else bool(opts),
                "response_options": [] if linked else opts,
                "canonicalization_note": "Structure is classified from observed components; title alone is never sufficient.",
            },
        }
        if linked:
            row["target_url"] = candidate_links[0] if len(candidate_links) == 1 else None
            row["target_url_candidates"] = candidate_links
            row["target_probe"] = {
                "provisional_structural_classification": "unresolved",
                "classification_confidence": "LOW",
                "access_note": "QR-linked external assessment structure is not visible in the local textbook PDF; do not infer rubric levels or descriptors.",
            }
        forms.append(row)
        if related_aid:
            activity_index[related_aid]["related_forms"].append(fid)

    for theme in THEMES:
        start, end = theme["range"]
        for p in range(start, end + 1):
            txt = page_texts.get(p, "")
            sec = section_for_page(theme, p)
            if not sec:
                continue
            sec_id, domain = sec[0], sec[1]
            if "Dereceli Puanlama" in txt and "Anahtarı" in txt:
                aid = activity_for_page(theme["theme_id"], sec_id, p, prefer_stage4=True)
                add_form(theme, p, "DPA", "Dereceli Puanlama Anahtarı (QR)", "linked_assessment_resource", "teacher", aid, linked=True, dpa=True)
            if "Öz Değerlendirme Formu" in txt:
                aid = activity_for_page(theme["theme_id"], sec_id, p, prefer_stage4=True)
                add_form(theme, p, "OZ_DEGERLENDIRME", "Öz Değerlendirme Formu", "self_assessment_form", "student_self", aid)
            if "Kontrol Listesi" in txt:
                aid = activity_for_page(theme["theme_id"], sec_id, p)
                add_form(theme, p, "KONTROL_LISTESI", "Kontrol Listesi", "checklist", "student_or_teacher", aid)
            if "Gözlem Formu" in txt:
                aid = activity_for_page(theme["theme_id"], sec_id, p)
                add_form(theme, p, "GOZLEM_FORMU", "Gözlem Formu", "observation_form", "teacher", aid)
            if "ÖĞRENME GÜNLÜĞÜ" in txt:
                aid = activity_for_page(theme["theme_id"], sec_id, p, prefer_stage4=True)
                add_form(theme, p, "OGRENME_GUNLUGU", "Öğrenme Günlüğü", "learning_journal", "student_self", aid)
            if "Çıkış Kartı" in txt:
                aid = activity_for_page(theme["theme_id"], sec_id, p, prefer_stage4=True)
                add_form(theme, p, "CIKIS_KARTI", "Çıkış Kartı", "exit_ticket", "student_self", aid)
            if "Akran Değerlendirme" in txt and "karekod" in txt.casefold():
                aid = activity_for_page(theme["theme_id"], sec_id, p, prefer_stage4=True)
                add_form(theme, p, "AKRAN_QR", "Akran Değerlendirme Formu (QR)", "linked_assessment_resource", "peer", aid, linked=True)
        assessment_sec = theme["sections"][-1]
        sec_id = assessment_sec[0]
        mapped_theme = next(t for t in mapped_themes if t["theme_id"] == theme["theme_id"])
        mapped_sec = next(s for s in mapped_theme["sections"] if s["section_id"] == sec_id)
        aid = mapped_sec["activities"][0]["activity_id"]
        add_form(theme, assessment_sec[3], "TEMA_TEST", f"{theme['theme_no']}. Tema Ölçme ve Değerlendirme Soruları", "test_question_set", "student", aid)

    if dpa_count != 8:
        raise RuntimeError(f"Expected exactly 8 QR-linked Dereceli Puanlama Anahtarı targets, found {dpa_count}")

    textbook = {
        "schema_version": "1.0",
        "course_id": COURSE_ID,
        "grade": GRADE,
        "source_id": SOURCE_ID,
        "book_identity": {
            "title": "Ortaöğretim Türk Dili ve Edebiyatı 11. Sınıf Ders Kitabı",
            "publisher": "Millî Eğitim Bakanlığı Yayınları",
            "edition_year": 2026,
            "meb_publication_no": "10727",
            "series_no": "2477",
            "isbn": "978-605-06002-7-8",
            "ttkb_acceptance": {"date": "2026-07-27", "reference_no": "164960037"},
            "identity_status": "VERIFIED_LOCAL_OFFICIAL_PDF",
        },
        "map_status": "PAGE_LEVEL_MAPPED_FROM_LOCAL_OFFICIAL_PDF",
        "verification_status": "VERIFIED_LOCAL_OFFICIAL_PDF",
        "freeze_status": "FROZEN_TEXTBOOK_ALIGNMENT_2026_09_11",
        "primary_source": {
            "source_id": SOURCE_ID,
            "file_path": PDF_REL,
            "role": "PRIMARY_ANALYSIS_SNAPSHOT",
            "edition_year": 2026,
            "isbn": "978-605-06002-7-8",
            "ttkb_acceptance": {"date": "2026-07-27", "reference_no": "164960037"},
            "page_count_pdf": doc.page_count,
            "sha256": sha256(PDF_PATH),
            "printed_to_pdf_offset": 1,
            "verification_status": "VERIFIED_LOCAL_OFFICIAL_PDF",
        },
        "rights_policy": "No long copyrighted body text; only structure, locators and short paraphrases are stored.",
        "scope_summary": {
            "theme_count": 4,
            "section_count": 24,
            "activity_count": total_activities,
            "printed_theme_ranges": {t["theme_id"]: f"{t['range'][0]}-{t['range'][1]}" for t in THEMES},
        },
        "themes": mapped_themes,
    }
    forms_index = {
        "schema_version": "1.0",
        "course_id": COURSE_ID,
        "source_id": SOURCE_ID,
        "index_status": "LOCAL_PDF_STRUCTURE_MAPPED_EXTERNAL_DPA_TARGETS_UNRESOLVED",
        "classification_rule": "Classify by observed structure, not title. QR-linked Dereceli Puanlama Anahtarı resources are tracked as unresolved linked assessment targets and are not classified as analytic rubrics without direct target inspection.",
        "total_records": len(forms),
        "summary": {
            "physical_or_inbook_forms": sum(1 for f in forms if f["location_scope"] == "IN_THEME"),
            "qr_linked_records": sum(1 for f in forms if f["location_scope"] == "EXTERNAL_OFFICIAL_QR"),
            "unresolved_dereceli_puanlama_anahtari_targets": dpa_count,
            "analytic_rubrics_verified": 0,
        },
        "forms": sorted(forms, key=lambda f: (f["linked_theme_ids"][0], f["printed_page"], f["form_id"])),
    }
    return textbook, forms_index, page_texts


def normalize_curriculum() -> dict[str, Any]:
    path = ROOT / "curriculum_map.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data.get("themes", [])) != 4 or sum(len(t.get("learning_outcomes", [])) for t in data.get("themes", [])) != 64:
        raise RuntimeError("TDE_11 frozen curriculum no longer has expected 4 themes / 64 outcomes")
    data["verification_status"] = "VERIFIED"
    data["canonical_freeze_status"] = "FROZEN"
    data["lifecycle_state"] = "TEXTBOOK_ALIGNED_PARITY_REVIEW_BLOCKED"
    scope = data.setdefault("scope_summary", {})
    scope.update({"textbook_used": True, "alignment_performed": True, "gap_analysis_performed": True, "materials_generated": False})
    for theme in data["themes"]:
        tid = theme["theme_id"]
        tno = theme.get("theme_no", theme.get("theme_number"))
        for outcome in theme.get("learning_outcomes", []):
            code = outcome["outcome_code"]
            outcome.setdefault("outcome_id", f"TDE11_T{tno}_{code.replace('.', '_')}")
            outcome["verification_status"] = "VERIFIED"
            outcome.setdefault("stable_entity_key", f"TDE_11::curriculum_outcome::{tid}::{code}")
    dump(path, data)
    return data


def outcome_target(domain: str, stage: int) -> tuple[str, str]:
    return ACTION[(domain, stage)]


def build_alignment(curriculum: dict[str, Any], textbook: dict[str, Any], forms_index: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    tb_themes = {t["theme_id"]: t for t in textbook["themes"]}
    forms = forms_index["forms"]
    all_alignment = []
    all_resources = []
    for theme in curriculum["themes"]:
        tid = theme["theme_id"]
        tno = int(re.search(r"(\d+)$", tid).group(1))
        tb_theme = tb_themes[tid]
        theme_dir = ROOT / "themes" / f"tema_{tno:02d}"
        alignments = []
        gaps = []
        needs = []
        resources = []
        for outcome in theme["learning_outcomes"]:
            code = outcome["outcome_code"]
            prefix, stage_s = code.replace("TDE", "").split(".", 1)
            prefix_i, stage = int(prefix), int(stage_s[0])
            domain = {1: "DINLEME", 2: "OKUMA", 3: "KONUSMA", 4: "YAZMA"}[prefix_i]
            candidate_sections = [s for s in tb_theme["sections"] if s.get("section_type") == domain.lower()]
            candidate_activities = [a for s in candidate_sections for a in s["activities"] if a.get("stage_code") == stage]
            if not candidate_activities:
                raise RuntimeError(f"No textbook activity for {tid} {code}")
            activity_ids = [a["activity_id"] for a in candidate_activities]
            section_ids = sorted({s["section_id"] for s in candidate_sections if any(a["activity_id"] in activity_ids for a in s["activities"])})
            locators = [a["source_locator"] for a in candidate_activities]
            linked_forms = [f for f in forms if any(aid in f.get("linked_activity_ids", []) for aid in activity_ids)]
            form_ids = [f["form_id"] for f in linked_forms]
            is_unresolved_dpa = stage == 4 and domain in {"KONUSMA", "YAZMA"} and any(f.get("assessment_type") == "dereceli_puanlama_anahtari_link" for f in linked_forms)
            coverage = "PARTIALLY_COVERED" if is_unresolved_dpa else "COVERED"
            need_id = f"NEED_T11_T{tno}_{code.replace('.', '_')}"
            plan_id = f"PLAN_T11_T{tno}_{code.replace('.', '_')}"
            gap_id = f"GAP_T11_T{tno}_{code.replace('.', '_')}"
            action, evidence = outcome_target(domain, stage)
            assessment_req = outcome.get("assessment_requirement_verbatim") or "Öğrencinin ilgili öğrenme çıktısını görünür kanıt ve geri bildirim yolu üzerinden gerçekleştirmesi ve değerlendirmesi."
            program_locator = outcome.get("source_locator") or theme.get("source_locator")
            need = {
                "need_id": need_id,
                "outcome_id": outcome.get("outcome_id"),
                "outcome_code": code,
                "targeted_learning_outcomes": [code],
                "skill_category": outcome.get("skill_category", SKILL_CATEGORY[domain]),
                "outcome_verbatim": outcome.get("outcome_verbatim"),
                "required_student_action": action,
                "expected_student_evidence": evidence,
                "assessment_need": assessment_req,
                "feedback_need": "Öğrenci performansına ilişkin görünür geri bildirim/değerlendirme yolu.",
                "external_content_need": False,
                "coverage_assertion": "NONE_NEEDS_STAGE",
                "provenance": {"program_locator": program_locator},
            }
            needs.append(need)
            observed_structures = sorted({f.get("structural_type") for f in linked_forms if f.get("structural_type")})
            alignment = {
                "outcome_id": outcome.get("outcome_id"),
                "outcome_code": code,
                "skill_category": outcome.get("skill_category", SKILL_CATEGORY[domain]),
                "outcome_verbatim": outcome.get("outcome_verbatim"),
                "process_components_verbatim": outcome.get("process_components_verbatim", []),
                "need_id": need_id,
                "resource_plan_id": plan_id,
                "program_assessment_requirement": {"normative_requirement": assessment_req, "source_locator": program_locator},
                "textbook_sections": section_ids,
                "textbook_activity_ids": activity_ids,
                "textbook_form_ids": form_ids,
                "textbook_locators": locators,
                "textbook_student_action": " | ".join(a["student_action"] for a in candidate_activities),
                "textbook_expected_evidence": " | ".join(a["expected_product_or_evidence"] for a in candidate_activities),
                "observed_assessment_structure": observed_structures,
                "primary_coverage": coverage,
                "need_tags": ["ASSESSMENT_TARGET_STRUCTURE_UNRESOLVED"] if is_unresolved_dpa else [],
                "remaining_gap": "Official QR-linked Dereceli Puanlama Anahtarı target exists but its criterion×level structure is not visible in the local official textbook PDF and remains unresolved." if is_unresolved_dpa else "NONE",
                "production_decision": "NO_ACTION_PENDING_ASSESSMENT_TARGET" if is_unresolved_dpa else "REUSE_TEXTBOOK",
                "priority": "REVIEW_REQUIRED" if is_unresolved_dpa else "NOT_NEEDED",
                "coverage_confidence": "HIGH_WITH_EXTERNAL_TARGET_STRUCTURE_UNRESOLVED" if is_unresolved_dpa else "HIGH",
                "provenance": {"program_locator": program_locator, "textbook_locator": locators},
                "selection_fallback_used": False,
            }
            alignments.append(alignment)
            gap = {
                "gap_id": gap_id,
                "need_id": need_id,
                "resource_plan_id": plan_id,
                "outcome_code": code,
                "outcome_verbatim": outcome.get("outcome_verbatim"),
                "textbook_activity_ids": activity_ids,
                "textbook_form_ids": form_ids,
                "textbook_locators": locators,
                "observed_textbook_structure": {"student_action": alignment["textbook_student_action"], "expected_evidence": alignment["textbook_expected_evidence"], "assessment_structures": observed_structures},
                "primary_coverage": coverage,
                "need_tags": alignment["need_tags"],
                "remaining_gap": alignment["remaining_gap"],
                "why_existing_resources_are_insufficient": "External teacher assessment target cannot be structurally verified from the local PDF; this is not a confirmed material gap and does not authorize generation." if is_unresolved_dpa else "N/A - textbook path is sufficient.",
                "production_decision": alignment["production_decision"],
                "priority": alignment["priority"],
                "provenance": {"program_locator": program_locator, "assessment_requirement": {"normative_requirement": assessment_req, "source_locator": program_locator}, "textbook_locator": locators},
            }
            gaps.append(gap)
            resource = {
                "resource_plan_id": plan_id,
                "need_id": need_id,
                "target_outcomes": [code],
                "resource_type": "assessment_support_review" if is_unresolved_dpa else "reuse_official_textbook_path",
                "purpose": action,
                "expected_student_evidence": evidence,
                "pre_alignment_state": "PENDING_ALIGNMENT_NO_COVERAGE_ASSUMPTION",
                "textbook_coverage": coverage,
                "priority": "REVIEW_REQUIRED" if is_unresolved_dpa else "NOT_NEEDED",
                "production_decision": "NO_ACTION_PENDING_ASSESSMENT_TARGET" if is_unresolved_dpa else "REUSE_TEXTBOOK",
                "reuse_existing_resource": True,
                "textbook_section_ids": section_ids,
                "textbook_activity_ids": activity_ids,
                "textbook_form_ids": form_ids,
                "textbook_resource_locators": locators,
                "textbook_resource_locator": locators[0] if locators else None,
                "external_source_needed": is_unresolved_dpa,
                "teacher_review_required": is_unresolved_dpa,
                "decision_rationale": "Official QR-linked DPA target must be structurally verified before any additional assessment artifact can be authorized." if is_unresolved_dpa else "Official textbook activity/evidence path satisfies the outcome-level need.",
            }
            resources.append(resource)
            all_alignment.append({"theme_id": tid, **alignment})
            all_resources.append({"theme_id": tid, **resource})
        covered = sum(1 for a in alignments if a["primary_coverage"] == "COVERED")
        partial = sum(1 for a in alignments if a["primary_coverage"] == "PARTIALLY_COVERED")
        not_cov = sum(1 for a in alignments if a["primary_coverage"] == "NOT_COVERED")
        if (covered, partial, not_cov) != (14, 2, 0):
            raise RuntimeError(f"Unexpected coverage for {tid}: {(covered, partial, not_cov)}")
        dump(theme_dir / "needs.json", {"schema_version": "1.0", "course_id": COURSE_ID, "grade": GRADE, "theme_id": tid, "theme_no": tno, "theme_title": theme.get("exact_theme_name"), "derivation_status": "CURRICULUM_FIRST_NO_COVERAGE_ASSUMPTION", "total_needs": len(needs), "needs": needs})
        dump(theme_dir / "alignment.json", {"schema_version": "1.1", "course_id": COURSE_ID, "grade": GRADE, "theme_id": tid, "theme_no": tno, "theme_title": theme.get("exact_theme_name"), "alignment_status": "PASS_WITH_UNRESOLVED_ASSESSMENT_TARGETS", "summary": {"total_outcomes": 16, "covered_count": covered, "partially_covered_count": partial, "not_covered_count": not_cov, "unresolved_assessment_target_count": partial}, "alignments": alignments})
        dump(theme_dir / "gap_analysis.json", {"schema_version": "1.1", "course_id": COURSE_ID, "grade": GRADE, "theme_id": tid, "theme_no": tno, "theme_title": theme.get("exact_theme_name"), "analysis_status": "PASS_WITH_UNRESOLVED_ASSESSMENT_TARGETS", "total_outcomes_analyzed": 16, "summary_metrics": {"covered_count": covered, "partially_covered_count": partial, "not_covered_count": not_cov, "confirmed_required_gap_count": 0, "unresolved_assessment_target_count": partial, "generate_count": 0, "review_required_count": partial}, "gap_records": gaps, "gap_rule": "PARTIALLY_COVERED caused only by an unresolved external assessment target is not a confirmed material gap and does not authorize generation."})
        dump(theme_dir / "resource_plan.json", {"schema_version": "1.1", "course_id": COURSE_ID, "grade": GRADE, "theme_id": tid, "theme_no": tno, "theme_title": theme.get("exact_theme_name"), "derivation_rule": "Need first; textbook alignment second; coverage/priority/production decision last.", "summary": {"total_planned_items": 16, "covered_count": covered, "partially_covered_count": partial, "not_covered_count": not_cov, "review_required_count": partial, "generate_authorized_count": 0}, "resources": resources})
        lines = [f"# {theme.get('exact_theme_name')} — Ders Kitabı Uyum Raporu", "", f"- Öğrenme çıktısı: **16**", f"- COVERED: **{covered}**", f"- PARTIALLY_COVERED: **{partial}**", f"- NOT_COVERED: **{not_cov}**", f"- Doğrulanmış materyal açığı: **0**", f"- Çözümlenmemiş normatif değerlendirme hedefi: **{partial}**", "", "| ÖÇ | Beceri | Kapsam | Kitap yolu | Karar |", "|---|---|---|---|---|"]
        for a in alignments:
            lines.append(f"| {a['outcome_code']} | {a['skill_category']} | {a['primary_coverage']} | {', '.join(a['textbook_locators'])} | {a['production_decision']} |")
        write_text(theme_dir / "alignment_report.md", "\n".join(lines))
    return all_alignment, all_resources


def build_teaching_and_timeline(curriculum: dict[str, Any], textbook: dict[str, Any], forms_index: dict[str, Any]) -> None:
    tb_by_theme = {t["theme_id"]: t for t in textbook["themes"]}
    forms = forms_index["forms"]
    blocks = []
    timeline_themes = []
    for theme in curriculum["themes"]:
        tid = theme["theme_id"]
        tno = int(re.search(r"(\d+)$", tid).group(1))
        tb = tb_by_theme[tid]
        specs = [
            ("OKUMA", [s for s in tb["sections"] if s["section_type"] == "okuma"], ["TDE2.1", "TDE2.2", "TDE2.3", "TDE2.4"]),
            ("KONUSMA", [s for s in tb["sections"] if s["section_type"] == "konusma"], ["TDE3.1", "TDE3.2", "TDE3.3", "TDE3.4"]),
            ("DINLEME", [s for s in tb["sections"] if s["section_type"] == "dinleme"], ["TDE1.1", "TDE1.2", "TDE1.3", "TDE1.4"]),
            ("YAZMA", [s for s in tb["sections"] if s["section_type"] in {"yazma", "olcme"}], ["TDE4.1", "TDE4.2", "TDE4.3", "TDE4.4"]),
        ]
        timeline_blocks = []
        for order, (domain, secs, outcomes) in enumerate(specs, 1):
            bid = f"BLOCK_T{tno}_{order:02d}_{domain}"
            aids = [a["activity_id"] for s in secs for a in s["activities"]]
            fids = sorted({f["form_id"] for f in forms if any(aid in f.get("linked_activity_ids", []) for aid in aids)})
            block = {
                "block_id": bid,
                "theme_id": tid,
                "title": " / ".join(s["section_title"] for s in secs),
                "skill_domain": SKILL_CATEGORY.get(domain, "Yazma"),
                "learning_area": "Anlama" if domain in {"OKUMA", "DINLEME"} else "Anlatma",
                "approximate_lesson_hours": None,
                "curriculum_outcomes": outcomes,
                "textbook_sections": [s["section_id"] for s in secs],
                "textbook_activity_ids": aids,
                "textbook_form_ids": fids,
                "expected_student_actions": " ".join(a["student_action"] for s in secs for a in s["activities"] if a.get("student_action")),
                "expected_student_evidence": " ".join(a["expected_product_or_evidence"] for s in secs for a in s["activities"] if a.get("expected_product_or_evidence")),
                "required_resource_ids": [], "recommended_resource_ids": [], "optional_resource_ids": [],
                "block_sequence": order,
                "prerequisite_block_ids": [] if order == 1 else [f"BLOCK_T{tno}_{order-1:02d}_{specs[order-2][0]}"],
                "lesson_hours_status": "UNSPECIFIED_BY_SOURCE",
            }
            blocks.append(block)
            timeline_blocks.append({
                "block_id": bid,
                "block_order": order,
                "title": block["title"],
                "skill_domain": block["skill_domain"],
                "learning_area": block["learning_area"],
                "outcomes": outcomes,
                "planned_hours": None,
                "time_status": "ORDER_ONLY_UNSPECIFIED_BY_SOURCE",
                "source_locators": [s["source_locator"] for s in secs],
            })
        ah = theme.get("allocated_lesson_hours") or {}
        instructional = ah.get("instructional_total", ah.get("total", 43))
        timeline_themes.append({
            "theme_id": tid, "theme_order": tno,
            "official_total_hours": 45,
            "core_instruction_hours": instructional if isinstance(instructional, int) else 43,
            "school_based_hours": 2,
            "school_based_hours_status": "USER_CONFIRMED_PLANNING_RULE",
            "source_locators": [theme.get("source_locator")],
            "blocks": timeline_blocks,
        })
    dump(ROOT / "production" / "teaching_blocks.json", {"schema_version": "1.0", "course_id": COURSE_ID, "grade": GRADE, "summary": {"total_teaching_blocks": len(blocks), "blocks_per_theme": {f"TEMA_{i:02d}": 4 for i in range(1, 5)}, "official_theme_instruction_hours": 43, "school_based_planning_hours_per_theme": 2, "outer_theme_hours": 45, "annual_hours": {"structured_program": 172, "school_based_planning": 8, "planned_total": 180}, "block_lesson_hours_status": "UNSPECIFIED_BY_SOURCE"}, "blocks": blocks})
    dump(ROOT / "planning" / "course_timeline.json", {"schema_version": "1.0", "course_id": COURSE_ID, "grade": GRADE, "timeline_resolution": "ORDER_ONLY_BLOCK_HOURS_UNSPECIFIED_BY_SOURCE", "calendar_binding": {"status": "NOT_BOUND", "weekly_lesson_hours": None}, "themes": timeline_themes})


def build_production(all_alignment: list[dict], all_resources: list[dict], textbook: dict[str, Any], forms_index: dict[str, Any]) -> None:
    covered = sum(1 for a in all_alignment if a["primary_coverage"] == "COVERED")
    partial = sum(1 for a in all_alignment if a["primary_coverage"] == "PARTIALLY_COVERED")
    not_cov = sum(1 for a in all_alignment if a["primary_coverage"] == "NOT_COVERED")
    if (covered, partial, not_cov) != (56, 8, 0):
        raise RuntimeError(f"Annual coverage mismatch: {(covered, partial, not_cov)}")
    production_manifest = {
        "schema_version": "1.1", "course_id": COURSE_ID,
        "production_mode": "PARITY_REVIEW_BLOCKED",
        "production_status": "BLOCKED_UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS",
        "verified_resource_gap_count": 0,
        "unresolved_assessment_target_count": 8,
        "expected_new_artifact_count": 0,
        "production_queue": [],
        "gap_instance_provenance_registry": [],
        "artifact_identity_field": "artifact_id",
        "legacy_gap_alias_policy": "NONE_NO_CONFIRMED_GAPS",
        "generation_authorization": {"allowed": False, "reason": "UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS", "blocking_target_count": 8},
        "canonical_inputs": {"curriculum_map": "curriculum_map.json", "textbook_map": "textbook_map.json", "textbook_forms_index": "textbook_forms_index.json", "cross_theme_audit": "production/cross_theme_audit.json", "consolidated_resource_plan": "production/consolidated_resource_plan.json", "assessment_artifact_registry": "production/assessment_artifact_registry.json"},
        "parity_interpretation": "The official textbook exposes eight QR-linked Dereceli Puanlama Anahtarı targets for speaking/writing performance evaluation. Their criterion×level payload is not visible in the local PDF, so the eight corresponding process-evaluation outcomes remain PARTIALLY_COVERED. This is not a confirmed material gap and does not authorize artifact generation.",
    }
    dump(ROOT / "production" / "production_manifest.json", production_manifest)
    dump(ROOT / "production" / "assessment_artifact_registry.json", {"schema_version": "1.1", "registry_version": "1.0", "course_id": COURSE_ID, "registry_mode": "PARITY_REVIEW_BLOCKED", "verified_resource_gap_count": 0, "unresolved_assessment_target_count": 8, "authorized_new_artifact_count": 0, "external_source_equivalence_status": "Eight official QR-linked DPA targets remain structurally unresolved; no rubric content is inferred.", "annual_artifacts": []})
    dump(ROOT / "production" / "assessment_design_contract.json", {"schema_version": "1.0", "course_id": COURSE_ID, "metadata": {"contract_version": "1.0", "status": "PARITY_REVIEW_BLOCKED"}, "design_policy": "Do not synthesize or infer criterion×level rubric payloads while official normative assessment targets remain structurally unresolved.", "generation_authorization": {"allowed": False, "reason": "UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS"}})
    dump(ROOT / "production" / "consolidated_resource_plan.json", {"schema_version": "1.1", "course_id": COURSE_ID, "consolidation_status": "PARITY_REVIEW_BLOCKED", "summary": {"total_outcome_level_plans": len(all_resources), "covered_count": covered, "partially_covered_count": partial, "not_covered_count": not_cov, "confirmed_required_gap_count": 0, "unresolved_assessment_target_count": 8, "authorized_artifact_count": 0}, "resources": all_resources})
    dump(ROOT / "production" / "cross_theme_audit.json", {"schema_version": "1.0", "course_id": COURSE_ID, "audit_status": "PASS_WITH_PARITY_REVIEW_BLOCKER", "theme_count": 4, "outcome_count": 64, "textbook_section_count": textbook["scope_summary"]["section_count"], "textbook_activity_count": textbook["scope_summary"]["activity_count"], "textbook_form_count": forms_index["total_records"], "coverage": {"covered": covered, "partially_covered": partial, "not_covered": not_cov}, "confirmed_required_gap_count": 0, "unresolved_assessment_target_count": 8, "cross_theme_gap_clusters": [], "authorized_artifacts": [], "production_mode": "PARITY_REVIEW_BLOCKED"})
    write_text(ROOT / "production" / "production_readiness_report.md", f"""# TDE_11 Production Readiness Report

**Durum:** PARITY_REVIEW_BLOCKED

- Tema: 4
- Öğrenme çıktısı: 64
- Ders kitabı bölümü: {textbook['scope_summary']['section_count']}
- Ders kitabı etkinliği: {textbook['scope_summary']['activity_count']}
- Değerlendirme/form kaydı: {forms_index['total_records']}
- COVERED: {covered}
- PARTIALLY_COVERED: {partial}
- NOT_COVERED: {not_cov}
- Doğrulanmış materyal açığı: 0
- Çözümlenmemiş normatif DPA hedefi: 8
- Yetkilendirilmiş yeni artifact: 0

Konuşma ve yazma performans görevlerinde kitapta resmî **Dereceli Puanlama Anahtarı** karekod hedefleri yer alır. Hedeflerin ölçüt×düzey yapısı yerel PDF içinde görünmediği için sekiz süreç-değerlendirme çıktısı fail-closed olarak `PARTIALLY_COVERED` tutulmuştur. Bu durum materyal açığı sayılmaz ve yeni rubrik üretimini yetkilendirmez.
""")


def update_source_manifest(textbook: dict[str, Any], forms_index: dict[str, Any]) -> None:
    path = ROOT / "source_manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["schema_version"] = data.get("schema_version", "1.2")
    data["course_id"] = COURSE_ID
    data["last_validated"] = TODAY
    data["overall_status"] = "TEXTBOOK_ALIGNED_PARITY_REVIEW_BLOCKED"
    data["lifecycle_state"] = "TEXTBOOK_ALIGNED_PARITY_REVIEW_BLOCKED"
    sources = [s for s in data.get("sources", []) if s.get("source_id") != SOURCE_ID and s.get("source_type") != "official_textbook"]
    sources.append({"source_id": SOURCE_ID, "source_type": "official_textbook", "authority_rank": 2, "title": "Ortaöğretim Türk Dili ve Edebiyatı 11. Sınıf Ders Kitabı", "file_path": PDF_REL, "edition_year": 2026, "isbn": "978-605-06002-7-8", "ttkb_acceptance": {"date": "2026-07-27", "reference_no": "164960037"}, "pdf_page_count": 313, "sha256": textbook["primary_source"]["sha256"], "verification_status": "VERIFIED_LOCAL_OFFICIAL_PDF"})
    data["sources"] = sources
    data["textbook"] = {"status": "VERIFIED_AND_ALIGNED", "source_id": SOURCE_ID, "file_path": PDF_REL, "edition_year": 2026, "isbn": "978-605-06002-7-8", "ttkb_acceptance": {"date": "2026-07-27", "reference_no": "164960037"}, "pdf_page_count": 313, "sha256": textbook["primary_source"]["sha256"], "theme_count": 4, "section_count": textbook["scope_summary"]["section_count"], "activity_count": textbook["scope_summary"]["activity_count"], "form_record_count": forms_index["total_records"], "unresolved_normative_assessment_target_count": 8}
    data["scope_status"] = {"curriculum_verified": True, "textbook_verified": True, "textbook_mapped": True, "alignment_performed": True, "gap_analysis_performed": True, "confirmed_required_gap_count": 0, "unresolved_assessment_target_count": 8, "production_mode": "PARITY_REVIEW_BLOCKED", "materials_generated": False}
    data["coverage_summary"] = {"covered": 56, "partially_covered": 8, "not_covered": 0}
    data["deferred_textbook_stages"] = ["Resolve/inspect the eight official QR-linked Dereceli Puanlama Anahtarı payloads before any parity certification or assessment artifact generation."]
    dump(path, data)


def write_reports(curriculum: dict[str, Any], textbook: dict[str, Any], forms_index: dict[str, Any]) -> None:
    parity = {
        "schema_version": "1.0", "course_id": COURSE_ID,
        "validation_status": "PARITY_REVIEW_REQUIRED_EXTERNAL_ASSESSMENT_TARGETS_UNRESOLVED",
        "parity_certified": False,
        "runtime_support_ready": False,
        "counts": {"themes": 4, "outcomes": 64, "sections": textbook["scope_summary"]["section_count"], "activities": textbook["scope_summary"]["activity_count"], "forms": forms_index["total_records"], "covered": 56, "partially_covered": 8, "not_covered": 0, "confirmed_required_gaps": 0, "unresolved_assessment_targets": 8, "authorized_artifacts": 0},
        "blocking_reason": "Eight official QR-linked Dereceli Puanlama Anahtarı targets remain structurally unresolved.",
        "production_mode": "PARITY_REVIEW_BLOCKED",
    }
    dump(ROOT / "parity_validation_report.json", parity)
    dump(ROOT / "parity_contract.json", {"schema_version": "1.0", "course_id": COURSE_ID, "contract_status": "FAIL_CLOSED_UNTIL_EXTERNAL_ASSESSMENT_TARGETS_RESOLVED", "coverage_enum": ["COVERED", "PARTIALLY_COVERED", "NOT_COVERED"], "confirmed_gap_rule": "Unresolved external normative assessment target is not a confirmed material gap.", "generation_rule": "PARITY_REVIEW_BLOCKED requires zero queue/artifacts and generation_authorization.allowed=false.", "required_blocker_resolution": "Inspect and classify the eight official QR-linked Dereceli Puanlama Anahtarı targets."})
    report = f"""# TDE_11 Ders Kitabı Parite Raporu

**Parite sertifikası:** VERİLMEDİ — dış değerlendirme hedefleri çözümlenmemiş

- Tema: 4
- Öğrenme çıktısı: 64
- Ders kitabı bölümü: {textbook['scope_summary']['section_count']}
- Etkinlik: {textbook['scope_summary']['activity_count']}
- Form/değerlendirme kaydı: {forms_index['total_records']}
- COVERED: 56
- PARTIALLY_COVERED: 8
- NOT_COVERED: 0
- Doğrulanmış materyal açığı: 0
- Çözümlenmemiş normatif değerlendirme hedefi: 8
- Üretim modu: PARITY_REVIEW_BLOCKED
- Yeni artifact üretimi: kapalı

Dört temanın her birinde konuşma ve yazma performans görevleri için resmî QR bağlantılı Dereceli Puanlama Anahtarı bulunur. Yerel resmî PDF bu haricî hedeflerin ölçüt×düzey içeriğini göstermediğinden `TDE3.4` ve `TDE4.4` her temada `PARTIALLY_COVERED` tutulmuştur. Bu sekiz kayıt doğrulanmış materyal açığı değildir.
"""
    write_text(ROOT / "parity_report.md", report)
    write_text(ROOT / "validation_report.md", report + "\n\n## Canonical curriculum preservation\n\nDondurulmuş 4 tema / 64 öğrenme çıktısı korunmuş; yalnız lifecycle ve textbook-alignment durum alanları güncellenmiştir.\n")


def main() -> None:
    textbook, forms_index, _ = build_book()
    curriculum = normalize_curriculum()
    dump(ROOT / "textbook_map.json", textbook)
    dump(ROOT / "textbook_forms_index.json", forms_index)
    dump(ROOT / "source_docs" / "textbook_extraction_audit.json", {"schema_version": "1.0", "course_id": COURSE_ID, "source_id": SOURCE_ID, "file_path": PDF_REL, "pdf_page_count": 313, "sha256": textbook["primary_source"]["sha256"], "printed_to_pdf_offset": 1, "toc_theme_ranges_verified": {t["theme_id"]: f"{t['range'][0]}-{t['range'][1]}" for t in THEMES}, "stage_heading_scan": "PASS_4_STAGES_PER_NON_ASSESSMENT_SECTION", "dpa_target_marker_scan": "PASS_EXACTLY_8", "rights_policy": textbook["rights_policy"]})
    all_alignment, all_resources = build_alignment(curriculum, textbook, forms_index)
    build_teaching_and_timeline(curriculum, textbook, forms_index)
    build_production(all_alignment, all_resources, textbook, forms_index)
    update_source_manifest(textbook, forms_index)
    write_reports(curriculum, textbook, forms_index)
    print(json.dumps({"status": "PASS", "themes": 4, "outcomes": 64, "sections": textbook["scope_summary"]["section_count"], "activities": textbook["scope_summary"]["activity_count"], "forms": forms_index["total_records"], "coverage": {"COVERED": 56, "PARTIALLY_COVERED": 8, "NOT_COVERED": 0}, "verified_gaps": 0, "unresolved_assessment_targets": 8, "production_mode": "PARITY_REVIEW_BLOCKED"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
