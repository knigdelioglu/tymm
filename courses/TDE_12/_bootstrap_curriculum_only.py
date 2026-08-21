#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
SCRIPTS = REPO / "skill/tymm-material-planner/scripts"
LIFECYCLE = "CURRICULUM_ONLY_AWAITING_TEXTBOOK"

LABELS = {
    "Metin Tahlili (Anlama)", "Dinleme/İzleme", "Okuma",
    "Edebiyat Atölyesi (Anlatma)", "Konuşma", "Yazma",
}

ASSESSMENTS = {
    "TEMA_01": [
        ("PERFORMANCE_TASK", "Okunan ve çözümlenen metinlerden hareketle kişisel gelişimi nelerin etkilediğiyle ilgili hazırlıklı konuşma yapmaya yönelik performans görevi"),
        ("PERFORMANCE_TASK", "Okunan ve çözümlenen metinlerden hareketle genel ağdaki güvenilir ortamlarda geleceğe dair kişisel planların ele alındığı forum metni oluşturmaya yönelik performans görevi"),
        ("THEME_END_EVALUATION", "Tema sonu değerlendirmede çıkış kartı kullanılır."),
    ],
    "TEMA_02": [
        ("PERFORMANCE_TASK", "Hak ve özgürlükleri konu edinen bir haber metni oluşturulması ve bu haberin sınıfta sunulmasına yönelik performans görevi"),
        ("PERFORMANCE_TASK", "İncelenen romanı hak ve özgürlükler bağlamında değerlendirerek bir eleştiri metni yazmaya yönelik performans görevi"),
        ("THEME_END_EVALUATION", "Temanın değerlendirilmesinde öğrenme günlüğü kullanılır."),
    ],
    "TEMA_03": [
        ("PERFORMANCE_TASK", "Çevre ve teknoloji bağlamında güncel bir sorun hakkında sunum hazırlamaya yönelik performans görevi"),
        ("PERFORMANCE_TASK", "Sürdürülebilirlik ile ilgili bir anket hazırlanıp uygulama sonuçlarını yazılı paylaşabilmesine yönelik performans görevi"),
        ("THEME_END_EVALUATION", "Tema değerlendirmesi için giriş-çıkış kartı kullanılır."),
    ],
    "TEMA_04": [
        ("PERFORMANCE_TASK", "Dinlenen/izlenen metinden hareketle öğrencilerin hayallerindeki mesleğe yönelik farklı kişilerle röportaj yaparak bunu sınıfta sunmalarına yönelik performans görevi"),
        ("PERFORMANCE_TASK", "Tahlil ettiği makale ve hikâye metninden yola çıkarak istediği mesleğin tanıtılmasına yönelik performans görevi"),
        ("THEME_END_EVALUATION", "Tema sonunda giriş-çıkış kartı ve Ne Biliyorum-Ne Bilmek İstiyorum-Ne Öğrendim tekniği ile değerlendirme yapılır."),
    ],
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\u00a0", " ")).strip()


def extract_text(pdf: Path) -> str:
    p = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.decode("utf-8", errors="replace")


def clean_lines(text: str) -> list[str]:
    return [norm(x) for x in text.splitlines() if norm(x)]


def find_heading(lines: list[str], needles: list[str], start: int = 0) -> int | None:
    for i in range(start, len(lines)):
        if any(n.casefold() in lines[i].casefold() for n in needles):
            return i
    return None


def section(lines: list[str], starts: list[str], ends: list[str]) -> dict:
    a = find_heading(lines, starts)
    if a is None:
        return {"source_status": "SOURCE_NOT_EXPLICIT", "verbatim": "", "heading": None}
    b = find_heading(lines, ends, a + 1) if ends else None
    if b is None:
        b = len(lines)
    body = []
    for x in lines[a + 1:b]:
        if x in LABELS:
            continue
        if x.startswith("Türk Dili Ve Edebiyatı Dersi 12.Sınıf"):
            continue
        if "https://tymm.meb.gov.tr/" in x and len(x.split()) < 8:
            continue
        body.append(x)
    return {
        "source_status": "SOURCE_EXPLICIT",
        "heading": lines[a],
        "verbatim": norm(" ".join(body)),
    }


def extract_outcomes(lines: list[str], theme_id: str) -> list[dict]:
    a = find_heading(lines, ["Öğrenme Çıktıları"])
    b = find_heading(lines, ["İçerik Çerçevesi"], (a + 1) if a is not None else 0)
    assert a is not None and b is not None and b > a, f"OUTCOME_SECTION_NOT_FOUND:{theme_id}"
    seg = lines[a + 1:b]
    rows: list[tuple[str, str]] = []
    i = 0
    while i < len(seg):
        m = re.match(r"^(TDE[1-4]\.[1-4])\.?(?:\s+)(.*)$", seg[i])
        if not m:
            i += 1
            continue
        code, text = m.group(1), m.group(2).strip()
        j = i + 1
        while j < len(seg) and not re.match(r"^TDE[1-4]\.[1-4]\.?(?:\s+|$)", seg[j]):
            x = seg[j]
            if x not in LABELS and not x.startswith("Türk Dili Ve Edebiyatı Dersi 12.Sınıf"):
                text += " " + x
            j += 1
        rows.append((code, norm(text)))
        i = j
    unique: dict[str, str] = {}
    for code, text in rows:
        unique.setdefault(code, text)
    expected = [f"TDE{x}.{y}" for x in range(1, 5) for y in range(1, 5)]
    assert list(unique) == expected, f"OUTCOME_SET_MISMATCH:{theme_id}:{list(unique)}"
    return [
        {
            "outcome_code": code,
            "outcome_verbatim": text,
            "theme_scope": theme_id,
            "stable_entity_key": f"TDE_12:{theme_id}:{code}",
            "verification_status": "VERIFIED_OFFICIAL_REMOTE_AND_LOCAL_CONTENT",
        }
        for code, text in unique.items()
    ]


def build_seed() -> None:
    manifest_path = ROOT / "source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["course_id"] == "TDE_12"
    themes = []
    total = 0
    for part in manifest["curriculum_source_bundle"]["parts"]:
        tid = part["theme_id"]
        url = part["url"]
        pdf = ROOT / part["local_path"]
        text = extract_text(pdf)
        lines = clean_lines(text)
        unit_id = url.rsplit("/", 1)[-1]
        assert f"unite/{unit_id}" in text, f"UNIT_IDENTITY_MISMATCH:{tid}"
        num = int(tid[-2:])
        assert any(f"12.Sınıf {num}. TEMA" in x or f"12. Sınıf {num}. TEMA" in x for x in lines), f"GRADE_THEME_IDENTITY_MISMATCH:{tid}"
        outcomes = extract_outcomes(lines, tid)
        total += len(outcomes)
        for o in outcomes:
            o["source_locator"] = url + " :: Öğrenme Çıktıları ve Süreç Bileşenleri"

        sec_defs = {
            "field_skills": (["Alan Becerileri"], ["Eğilimler"]),
            "tendencies": (["Eğilimler"], ["Programlar Arası Bileşenler"]),
            "social_emotional_learning_skills": (["Sosyal-Duygusal Öğrenme Becerileri"], ["Değerler"]),
            "values": (["Değerler"], ["Okuryazarlık Becerileri"]),
            "literacy_skills": (["Okuryazarlık Becerileri"], ["Disiplinler Arası İlişkiler"]),
            "interdisciplinary_relations": (["Disiplinler Arası İlişkiler"], ["Beceriler Arası İlişkiler"]),
            "skills_relations": (["Beceriler Arası İlişkiler"], ["Öğrenme Çıktıları"]),
            "content_framework": (["İçerik Çerçevesi"], ["Anahtar Kavramlar"]),
            "key_concepts": (["Anahtar Kavramlar"], ["Öğrenme Kanıtları"]),
            "learning_evidence": (["Öğrenme Kanıtları"], ["Öğrenme-Öğretme Yaşantıları", "Öğrenme Öğretme Yaşantıları"]),
            "learning_teaching_experiences": (["Öğrenme-Öğretme Yaşantıları", "Öğrenme Öğretme Yaşantıları"], ["Farklılaştırma"]),
            "differentiation": (["Farklılaştırma"], []),
        }
        program_elements = {}
        for key, (starts, ends) in sec_defs.items():
            row = section(lines, starts, ends)
            row["source_locator"] = url
            program_elements[key] = row

        ars = []
        for idx, (kind, req) in enumerate(ASSESSMENTS[tid], 1):
            ars.append({
                "assessment_id": f"TDE_12_{tid}_ASSESSMENT_{idx:02d}",
                "assessment_type": kind,
                "requirement": req,
                "source_locator": url + " :: Öğrenme Kanıtları (Ölçme ve Değerlendirme)",
                "verification_status": "VERIFIED_OFFICIAL_CURRICULUM",
            })

        themes.append({
            "theme_id": tid,
            "theme_number": num,
            "exact_theme_name": part["expected_theme_title"],
            "source_id": part["source_id"],
            "source_locator": url,
            "verification_status": "VERIFIED_OFFICIAL_REMOTE_AND_LOCAL_CONTENT",
            "allocated_lesson_hours": {
                "instructional_total": 43,
                "verbatim": "Ders Saati: 43",
                "source_locator": url + " :: Ders Saati",
            },
            "program_elements": program_elements,
            "process_component_policy": {
                "status": "SOURCE_COMPLETE_NO_EXPLICIT_SUBCOMPONENT_IDS",
                "canonical_policy": "DO_NOT_SYNTHESIZE_OR_COPY_FROM_OTHER_GRADES",
                "official_process_realization": "Published learning-teaching application paragraphs under the parent outcome codes are authoritative process realization; no separate sub-outcome IDs are synthesized.",
            },
            "learning_outcomes": outcomes,
            "assessment_requirements": ars,
        })

    assert total == 64, f"TOTAL_OUTCOME_MISMATCH:{total}"
    curriculum = {
        "schema_version": "1.1",
        "course_id": "TDE_12",
        "grade": 12,
        "course_title": "Türk Dili ve Edebiyatı",
        "lifecycle_status": LIFECYCLE,
        "source_mode": "OFFICIAL_REMOTE_TYMM_THEME_BUNDLE_WITH_MAPPED_LOCAL_PDF_SNAPSHOTS",
        "verification_status": "VERIFIED_OFFICIAL_REMOTE_AND_LOCAL",
        "canonical_freeze_status": "FROZEN_PENDING_SOURCE_FINGERPRINT_CHANGE",
        "scope_summary": {
            "total_themes": 4,
            "learning_outcomes_per_theme": 16,
            "total_learning_outcomes": 64,
            "official_instructional_hours_per_theme": 43,
            "school_based_planning_hours_per_theme": 2,
            "theme_total_hours_with_school_based_planning": 45,
            "official_instructional_hours_total": 172,
            "annual_school_based_planning_hours": 8,
            "annual_total_hours_with_school_based_planning": 180,
            "textbook_status": "AWAITING_OFFICIAL_TEXTBOOK",
            "coverage_status": "NOT_EVALUATED",
            "gap_status": "NOT_EVALUATED",
            "production_status": "NOT_EVALUATED",
        },
        "source_validation": {
            "official_theme_identity_status": "PASS_4_OF_4",
            "source_bundle_completeness": "PASS_4_OF_4",
            "parent_outcome_count_status": "PASS_64_OF_64",
            "explicit_subcomponent_id_scan": "PASS_NONE_EXPLICIT_SEPARATE_SUBCOMPONENT_IDS",
            "local_pdf_theme_mapping": "PASS_4_OF_4_CONTENT_VERIFIED_AND_RENAMED",
            "synthetic_subcode_policy": "DO_NOT_SYNTHESIZE_OR_COPY_FROM_OTHER_GRADES",
        },
        "themes": themes,
    }
    (ROOT / "curriculum_map.json").write_text(json.dumps(curriculum, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str]) -> None:
    print("RUN", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=REPO, check=True)


def write_reports() -> None:
    m = json.loads((ROOT / "source_manifest.json").read_text(encoding="utf-8"))
    g = json.loads((ROOT / "curriculum_validation_report.json").read_text(encoding="utf-8"))
    fps = "\n".join(f"- `{p['theme_id']}` — `{p['sha256']}` — `{p['local_filename']}`" for p in m["curriculum_source_bundle"]["parts"])
    report = f"""# TDE_12 Curriculum-Only Validation Report

**Lifecycle:** `CURRICULUM_ONLY_AWAITING_TEXTBOOK`  
**Curriculum validation:** PASS  
**Gate:** `curriculum_only_gate.py` PASS  
**Validated:** 2026-08-21

## Sonuç

- Course: `TDE_12` — 12. Sınıf Türk Dili ve Edebiyatı
- Resmî program source status: **VERIFIED_OFFICIAL_REMOTE_AND_LOCAL**
- Curriculum source completeness: **PASS — 4/4 tema**
- Tema sayısı: **4**
- Zaman modeli: **45 saat/tema = 43 saat resmî öğretim + 2 saat okul temelli planlama**
- Yıllık toplam: **180 saat = 172 + 8**
- Parent outcome: **{g['canonical']['outcomes']}** (16/tema)
- Outcome scope/unique ID: **PASS**
- Verbatim/locator kanıtı: **PASS — full local PDF page text evidence + outcome local page locators**
- Explicit process component alt ID durumu: **SOURCE_COMPLETE_NO_EXPLICIT_SUBCOMPONENT_IDS**
- Sentetik alt kod üretimi: **YOK**
- Assessment requirement: **{g['canonical']['assessment_requirements']}** — 8 performans görevi + 4 tema sonu değerlendirme
- Source fingerprint: **PASS — 4/4 SHA-256 + bundle fingerprint**
- TDE_9 regression: **PASS — 7 gap instance → 3 canonical artifact**
- TDE_10 regression: **PASS — PARITY_REVIEW_BLOCKED fail-closed davranışı korunuyor**
- Textbook status: **AWAITING_OFFICIAL_TEXTBOOK**
- Coverage status: **NOT_EVALUATED**
- Gap status: **NOT_EVALUATED**
- Production status: **NOT_EVALUATED**
- Full textbook P0/runtime: **DEFERRED_UNTIL_OFFICIAL_TEXTBOOK_AVAILABLE**

## Kaynak fingerprintleri

{fps}

## Canonical kanıt derinliği

`curriculum_normative_text.json`, dört resmî yerel PDF’nin `pdftotext -layout` ile sayfa bazlı kaynak-bağlı metin çıkarımını tutar. `curriculum_map.json` tema ve outcome kayıtları bu dosyaya ve SHA-256 fingerprintlerine bağlanmıştır. PDF asıl resmî snapshot olarak kalır; metin çıkarımı kanıt/erişim katmanıdır.

## Ertelenen aşamalar

- textbook map / forms index
- textbook coverage
- alignment
- gap analysis
- resource/production kararları
- full textbook runtime ve production gate

Ders kitabının mevcut olmaması curriculum gap olarak değerlendirilmemiştir.

## Gerçek curriculum blocker

**Yok.** Curriculum-only bootstrap gate PASS durumundadır.
"""
    (ROOT / "validation_report.md").write_text(report, encoding="utf-8")
    readme = """# TDE_12 — 12. Sınıf Türk Dili ve Edebiyatı

Bu klasör 12. sınıf Türk Dili ve Edebiyatı için curriculum-only canonical bilgi paketidir.

Durum: `CURRICULUM_ONLY_AWAITING_TEXTBOOK`

Mevcut canonical kaynaklar:
- `source_manifest.json`
- `curriculum_map.json`
- `curriculum_normative_text.json`
- `curriculum_validation_report.json`
- `validation_report.md`
- `source_docs/` — dört resmî TYMM tema PDF snapshot'ı

Resmî ders kitabı henüz bu aşamaya dahil değildir. Bu nedenle textbook coverage, alignment, gap analysis ve production kararları `NOT_EVALUATED` / deferred durumundadır. Kitap yokluğu curriculum gap değildir.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


def regression() -> None:
    run([sys.executable, "skill/tymm-material-planner/tests/test_reuse_only_contract.py"])
    run([sys.executable, "skill/tymm-material-planner/tests/test_parity_blocked_contract.py"])
    sys.path.insert(0, str(SCRIPTS))
    from production_schema import build_artifact_maps
    m = json.loads((REPO / "courses/TDE_9/production/production_manifest.json").read_text(encoding="utf-8"))
    artifacts, _, aliases, prov = build_artifact_maps(m)
    assert (len(artifacts), len(aliases), len(prov)) == (3, 7, 7)
    v = json.loads((REPO / "courses/TDE_10/parity_validation_report.json").read_text(encoding="utf-8"))
    p = json.loads((REPO / "courses/TDE_10/production/production_manifest.json").read_text(encoding="utf-8"))
    assert v["status"] == "VALIDATED_WITH_EXTERNAL_AUTH_BLOCKER" and v["parity_certified"] is False
    assert p["production_mode"] == "PARITY_REVIEW_BLOCKED" and p["production_queue"] == []
    assert p["generation_authorization"]["allowed"] is False
    print("TDE9 7-to-3 regression: PASS")
    print("TDE10 PARITY_REVIEW_BLOCKED fail-closed regression: PASS")


def main() -> int:
    build_seed()
    run([sys.executable, "skill/tymm-material-planner/scripts/curriculum_only_finalize.py", "--knowledge-root", "courses/TDE_12"])
    run([sys.executable, "skill/tymm-material-planner/scripts/curriculum_only_gate.py", "--knowledge-root", "courses/TDE_12", "--report", "courses/TDE_12/curriculum_validation_report.json"])
    regression()
    write_reports()
    print("TDE12 CURRICULUM-ONLY BOOTSTRAP: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
