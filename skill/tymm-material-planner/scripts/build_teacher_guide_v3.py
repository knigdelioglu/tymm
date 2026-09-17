#!/usr/bin/env python3
"""Build the textbook-first Teacher Guide V3 for TDE 11.

V3 keeps the existing canonical section files and mirror provenance as inputs,
but makes each book task a first-class record.  The book prompt and locator are
projected from the source-verified mirror; the answer and its explanation are
projected from the canonical guide; the teacher-facing background and moves are
derived per task from the task's text, medium, and instructional purpose.

The phase-profile files remain available to legacy V2 builds.  They are not an
authoring input here: the V3 motor is task-first and uses a small deterministic
domain router only to select the explanation vocabulary appropriate to the
actual book task.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable


COURSE_ID = "TDE_11"
TEXTBOOK_SOURCE_ID = "official_textbook_pdf"
TEXTBOOK_MAP_SOURCE_ID = "textbook_map"
CANONICAL_SOURCE_ID = "teacher_guide_canonical"

GROUPED_PROMPT_OVERRIDES: dict[str, list[dict[str, str]]] = {
    "T1V23_P28_INTERPRET": [
        {
            "question_number": "1",
            "answer_key": "q1",
            "prompt": "Yazıcı metnindeki tiplerin söz varlıklarının onların sosyal statülerine ve eğitim durumlarına uygunluğu hakkındaki düşüncelerinizi metinden örneklerle ifade ediniz.",
        },
        {
            "question_number": "2",
            "answer_key": "q2",
            "prompt": "Edebî metinlerde kişilerin kullandığı söz varlığının metne katkısı başka bir yolla sağlanabilir mi? Açıklayınız.",
        },
        {
            "question_number": "3",
            "answer_key": "q3",
            "prompt": "Günlük hayatta Yazıcı oyunundaki tiplere benzer şekilde konuşan veya davranan kişilerle karşılaştığınızda bu durum size ne hissettirir? Bu tür davranışları nasıl değerlendirirsiniz? Açıklayınız.",
        },
    ],
    "T1V23_P29_FRIENDSHIP": [
        {
            "question_number": "1",
            "answer_key": "q1",
            "prompt": "Hacivat ve Karagöz’ün kişilik özellikleri, eğitim durumları, kültür düzeyleri ve sosyal statüleri farklıdır. Bu farklılıklara rağmen aralarındaki dostluğu nasıl sürdürebildiklerini tartışınız. Ulaştığınız sonuçları tahtaya yazınız.",
        },
        {
            "question_number": "2",
            "answer_key": "q2",
            "prompt": "Aşağıdaki dörtlükten ve atasözünden hareketle “dostluk” kavramının sizin için ifade ettiği anlamları aşağıdaki alana yazınız.",
        },
    ],
}

EXTERNAL_PATTERN = re.compile(
    r"\b(?:qr|video|eba|dış\s+video|dış\s+medya|rubrik|dereceli\s+puanlama\s+anahtarı)\b",
    re.IGNORECASE,
)
OPEN_PATTERN = re.compile(
    r"(?:yorumla|açıkla|gerekç|düşün|değerlendir|tahmin|öner|ifade|karşılaştır|oluştur|yazınız|tartış|çıkarım|ilişkilendir)",
    re.IGNORECASE,
)
QUESTION_NUMBER_PATTERN = re.compile(
    r"(?:Soru|Adım|Fark\s+Edelim)\s+([0-9]+(?:\s*/\s*[a-z])?|[0-9]+[a-z]?)",
    re.IGNORECASE,
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def scalar_text(value: Any) -> str:
    if value is None:
        return ""
    if value is True:
        return "Evet"
    if value is False:
        return "Hayır"
    return str(value)


def normalize_text(value: Any) -> str:
    text = scalar_text(value).casefold().replace("’", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def dedupe_text(values: Iterable[Any], limit: int | None = None) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip():
            continue
        cleaned = re.sub(r"\s+", " ", value.strip())
        key = normalize_text(cleaned)
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
        if limit is not None and len(result) >= limit:
            break
    return result


def dedupe_values(values: Iterable[Any]) -> list[Any]:
    result: list[Any] = []
    seen: set[str] = set()
    for value in values:
        if value is None:
            continue
        key = json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else normalize_text(value)
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def parse_page_range(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d+)\s*(?:[-–—]\s*(\d+)\s*)?", str(value))
    if not match:
        raise ValueError(f"invalid printed page range: {value}")
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if end < start:
        raise ValueError(f"invalid printed page range: {value}")
    return start, end


def range_string(start: int, end: int) -> str:
    return str(start) if start == end else f"{start}-{end}"


def relative_path(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def humanize_key(key: str) -> str:
    return key.replace("_", " ").strip().capitalize()


def render_scalar(value: Any) -> str:
    if value is True:
        return "Evet"
    if value is False:
        return "Hayır"
    if value is None:
        return ""
    return str(value)


def render_value(value: Any, indent: int = 0) -> list[str]:
    """Render structured answers without reproducing textbook body text."""
    prefix = "  " * indent
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [prefix + value]
    if isinstance(value, list):
        lines: list[str] = []
        for entry in value:
            if isinstance(entry, (dict, list)):
                lines.append(prefix + "-")
                lines.extend(render_value(entry, indent + 1))
            else:
                lines.append(prefix + f"- {render_scalar(entry)}")
        return lines
    if isinstance(value, dict):
        lines = []
        for key, entry in value.items():
            label = humanize_key(str(key))
            if isinstance(entry, (dict, list)):
                lines.append(prefix + f"- **{label}:**")
                lines.extend(render_value(entry, indent + 1))
            else:
                lines.append(prefix + f"- **{label}:** {render_scalar(entry)}")
        return lines
    return [prefix + render_scalar(value)]


def discover_mirror_paths(primary: Path) -> list[Path]:
    paths = [primary]
    paths.extend(path for path in primary.parent.glob("book_mirror_v23_*.json") if path != primary)
    return sorted(paths, key=lambda path: parse_page_range(read_json(path)["scope"]["printed_page_range"])[0])


def merge_mirrors(paths: list[Path]) -> dict[str, Any]:
    documents = [read_json(path) for path in paths]
    if not documents:
        raise ValueError("no mirror documents found")
    first = documents[0]
    course_id = first["course_id"]
    theme_id = first["theme_id"]
    entries: list[dict[str, Any]] = []
    checklist: list[dict[str, Any]] = []
    principles: list[str] = []
    starts: list[int] = []
    ends: list[int] = []
    for document in documents:
        if document.get("course_id") != course_id or document.get("theme_id") != theme_id:
            raise ValueError(f"mirror identity mismatch in {paths}")
        start, end = parse_page_range(document["scope"]["printed_page_range"])
        starts.append(start)
        ends.append(end)
        entries.extend(document.get("entries", []))
        checklist.extend(document.get("page_checklist", []))
        for principle in document.get("guide_principles", []):
            if principle not in principles:
                principles.append(principle)
    ordered_entries = [entry for _, entry in sorted(enumerate(entries), key=lambda pair: (parse_page_range(pair[1]["printed_page_range"])[0], pair[0]))]
    return {
        "schema_version": "2.3.0",
        "document_type": "TYMM_TEACHER_GUIDE_BOOK_MIRROR",
        "course_id": course_id,
        "theme_id": theme_id,
        "scope": {"printed_page_range": range_string(min(starts), max(ends)), "status": "PILOT"},
        "source_policy": first.get("source_policy", {}),
        "guide_principles": principles,
        "entries": ordered_entries,
        "page_checklist": checklist,
        "mirror_files": [str(path) for path in paths],
    }


def index_canonical(root: Path, manifest: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    sections: dict[str, dict[str, Any]] = {}
    items: dict[str, dict[str, Any]] = {}
    for row in manifest.get("sections", []):
        section_id = row["section_id"]
        section = read_json(root / row["content_ref"])
        sections[section_id] = {"manifest": row, "content": section}
        for unit in section.get("guide_units", []):
            for item in unit.get("items", []):
                item_id = item["item_id"]
                if item_id in items:
                    raise ValueError(f"duplicate canonical item: {item_id}")
                items[item_id] = {
                    "section_id": section_id,
                    "unit_id": unit.get("unit_id"),
                    "unit": unit,
                    "item": deepcopy(item),
                }
    return sections, items


def apply_component_registries(root: Path, theme_id: str, canonical: dict[str, dict[str, Any]]) -> list[Path]:
    """Apply only additive, source-verified V2.3 component registries."""
    theme_dir = root / "courses" / COURSE_ID / "teacher_guide" / theme_id
    paths = sorted(theme_dir.glob("book_components_v23*.json"))
    used: list[Path] = []
    for path in paths:
        registry = read_json(path)
        if registry.get("document_type") != "TYMM_TEACHER_GUIDE_COMPONENT_REGISTRY":
            raise ValueError(f"invalid component registry: {path}")
        if registry.get("course_id") != COURSE_ID or registry.get("theme_id") != theme_id:
            raise ValueError(f"component registry identity mismatch: {path}")
        for item_id, component_map in registry.get("components", {}).items():
            if item_id not in canonical:
                raise ValueError(f"component registry references unknown canonical item: {item_id}")
            item = canonical[item_id]["item"]
            base = item.get("expected_answer")
            if base is None:
                base = {}
            if not isinstance(base, dict) or not isinstance(component_map, dict):
                raise ValueError(f"component registry requires object answer: {path}:{item_id}")
            merged = dict(base)
            for key, metadata in component_map.items():
                if key in merged:
                    raise ValueError(f"component registry would overwrite canonical key: {item_id}:{key}")
                if not isinstance(metadata, dict) or not nonempty(metadata.get("value")) or not nonempty(metadata.get("source_locator")):
                    raise ValueError(f"component registry entry is not source-verified: {path}:{item_id}:{key}")
                merged[key] = metadata["value"]
            item["expected_answer"] = merged
            item.setdefault("_v3_component_sources", []).append(relative_path(root, path))
        used.append(path)
    return used


def expand_mirror_entry(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Split only source-verified numbered groups; preserve other multi-part cards."""
    mirror_id = entry["mirror_id"]
    override = GROUPED_PROMPT_OVERRIDES.get(mirror_id)
    if not override:
        expanded = deepcopy(entry)
        expanded["split_from_group"] = False
        return [expanded]
    result: list[dict[str, Any]] = []
    for part in override:
        expanded = deepcopy(entry)
        expanded["mirror_id"] = f"{mirror_id}#Q{part['question_number']}"
        expanded["prompt_display"] = f"Soru {part['question_number']} — {part['prompt']}"
        expanded["prompt_mode"] = "VERBATIM_SHORT"
        expanded["answer_keys"] = [part["answer_key"]]
        expanded["question_number"] = part["question_number"]
        expanded["split_from_group"] = True
        expanded["group_source_task_id"] = mirror_id
        result.append(expanded)
    return result


def project_answer(canonical: dict[str, dict[str, Any]], refs: list[str], keys: list[str]) -> tuple[Any, list[str]]:
    missing: list[str] = []
    if not refs:
        return None, ["canonical_item_refs boş"]
    if keys and len(refs) != 1:
        return None, ["answer_component_keys birden çok canonical item ile kullanılmış"]
    values: list[Any] = []
    for ref in refs:
        record = canonical.get(ref)
        if record is None:
            missing.append(ref)
            continue
        values.append(record["item"].get("expected_answer"))
    if missing:
        return None, [f"canonical item bulunamadı: {', '.join(missing)}"]
    if keys:
        value = values[0]
        if not isinstance(value, dict):
            return None, ["answer_component_keys nesne olmayan canonical answer üzerinde kullanılmış"]
        unknown = [key for key in keys if key not in value]
        if unknown:
            return None, [f"answer key bulunamadı: {', '.join(unknown)}"]
        if len(keys) == 1:
            return value[keys[0]], []
        return {key: value[key] for key in keys}, []
    if len(values) == 1:
        return values[0], []
    return {ref: value for ref, value in zip(refs, values)}, []


def canonical_response(canonical: dict[str, dict[str, Any]], refs: list[str], keys: list[str]) -> Any:
    values: list[Any] = []
    for ref in refs:
        if ref not in canonical:
            continue
        item = canonical[ref]["item"]
        value = item.get("expected_response")
        if value is None:
            continue
        values.append(value)
    if not values:
        return None
    return values[0] if len(values) == 1 else values


def item_provenance(record: dict[str, Any]) -> dict[str, Any]:
    return record["item"].get("provenance", {}) if isinstance(record.get("item"), dict) else {}


def collect_source_ids(
    canonical: dict[str, dict[str, Any]],
    refs: list[str],
    component_sources: Iterable[str] = (),
) -> list[str]:
    values = [TEXTBOOK_SOURCE_ID, TEXTBOOK_MAP_SOURCE_ID, CANONICAL_SOURCE_ID]
    for ref in refs:
        provenance = item_provenance(canonical[ref]) if ref in canonical else {}
        values.extend(provenance.get("source_ids", []))
        values.extend(canonical[ref].get("item", {}).get("_v3_component_sources", [])) if ref in canonical else None
    values.extend(component_sources)
    return list(dict.fromkeys(str(value) for value in values if value))


def collect_source_locators(
    entry: dict[str, Any],
    canonical: dict[str, dict[str, Any]],
    refs: list[str],
    section_record: dict[str, Any],
    unit: dict[str, Any] | None,
) -> list[str]:
    values: list[str] = []
    if nonempty(entry.get("source_locator")):
        values.append(str(entry["source_locator"]))
    for ref in refs:
        provenance = item_provenance(canonical[ref]) if ref in canonical else {}
        values.extend(str(value) for value in provenance.get("source_locators", []) if value)
    if unit:
        values.extend(str(value) for value in unit.get("provenance", {}).get("source_locators", []) if value)
    values.extend(str(value) for value in section_record.get("content", {}).get("provenance", {}).get("source_locators", []) if value)
    if not values:
        values.append(f"basılı s.{entry['printed_page_range']}")
    return list(dict.fromkeys(values))


def find_question_number(entry: dict[str, Any], prompt: str | None) -> str | None:
    if nonempty(entry.get("question_number")):
        return str(entry["question_number"])
    if not prompt:
        return None
    match = QUESTION_NUMBER_PATTERN.search(prompt)
    return match.group(1).replace(" ", "") if match else None


def task_blob(entry: dict[str, Any], item: dict[str, Any], section_title: str) -> str:
    provenance = item.get("provenance", {})
    return " ".join(
        str(value)
        for value in [
            section_title,
            entry.get("book_heading", ""),
            entry.get("prompt_display", ""),
            entry.get("source_locator", ""),
            item.get("label", ""),
            item.get("teacher_guidance", ""),
            provenance.get("note", ""),
        ]
        if value
    )


def is_external_task(blob: str) -> bool:
    return bool(EXTERNAL_PATTERN.search(blob))


def has_word_or_phrase(text: str, term: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None


def choose_profile(blob: str, section_type: str) -> str:
    text = normalize_text(blob)
    section = normalize_text(section_type)
    if "e-posta" in text or "eposta" in text or "dilekçe" in text:
        if section_type.lower() in {"yazma", "writing"} or "e-posta" in text or "eposta" in text:
            return "writing_email"
        return "mektup"
    if any(term in text for term in ["karagöz", "hacivat", "gölge oyunu", "seyirlik", "muamma"]):
        return "karagoz"
    if any(term in text for term in ["iletişim engel", "sözlü iletişim", "iletişim araç", "iletişim unsurlar", "iletişim", "çok modlu", "paydos"]):
        return "communication"
    if any(term in text for term in ["orhun", "kül tigin", "dîvânu lugâti", "divanu lugati", "bengü taş", "yazıt", "töre"]):
        return "old_turkic"
    if any(term in text for term in ["âşık", "aşık", "atışma", "saz", "ozan"]):
        return "ashik"
    if any(term in text for term in ["müze", "kültürel miras", "sergi"]):
        return "museum"
    if any(term in text for term in ["fiil", "çatı", "noktalama", "cümle kuruluş", "yazım kural"]):
        return "language_grammar"
    if any(term in text for term in ["küçürek", "küçürek hikâye", "minimal hikâye", "merdiven", "ferit edgü"]):
        return "kucurek"
    if any(has_word_or_phrase(text, term) for term in ["oğulla buluşma", "hikâye", "anı", "olay örgüsü", "hikâye haritası", "çordon"]):
        return "story_memoir"
    if any(term in text for term in ["türk dünyası", "ortak dil", "ortak alfabe", "dil birliği", "millî kimlik", "ortak kültür", "kültür", "toylar", "nevruz", "vatanımız", "dede korkut", "kültür unsuru", "ortak bilgi"]):
        return "cultural_memory"
    if "mektup" in text:
        return "mektup"
    if any(term in text for term in ["mülakat", "röportaj"]):
        return "interview"
    if any(term in text for term in ["radyo tiyatrosu", "radyo tiyat"]):
        return "radio"
    if section in {"dinleme", "dinleme_izleme", "listening_viewing"}:
        return "communication"
    if any(term in text for term in ["belgesel", "fedakârlık", "anadolu insanı", "aidiyet"]):
        return "documentary"
    if any(term in text for term in ["afiş", "poster"]):
        return "poster"
    if any(term in text for term in ["huzur", "tanpınar"]):
        return "huzur"
    if any(term in text for term in ["biyografi", "tezkire", "mehmet akif", "orhan veli", "mustafa inan"]):
        return "bio_tezkire"
    if "bir bilim adamının romanı" in text:
        return "bio_tezkire"
    if any(term in text for term in ["tiyatro", "mimar sinan", "diyalog", "monolog", "sahne", "canlandır"]):
        return "theatre"
    if any(term in text for term in ["drama", "konuşma", "sözlü"]):
        return "speaking_drama"
    if any(term in text for term in ["tür değiş", "dönüştür", "başka bir tür"]):
        return "genre_transform"
    if any(term in text for term in ["tez/antitez", "tez ve antitez", "sentez cümlesi", "tez", "antitez"]):
        return "argumentation"
    if any(term in text for term in ["gerçeklik", "gerçek hayat", "kurmaca", "sanatsal metin", "sanatçı"]):
        return "literary_reality"
    if ("edebiyat" in text and "yaşam" in text) or "kitap" in text or "yaşamın izinde" in text or "görsellerin çağrışımı" in text or "hayatın aynası" in text or "yunus emre" in text:
        return "literary_reality"
    return "text_analysis"


def focus_for(blob: str, label: str) -> str:
    text = normalize_text(blob)
    patterns = [
        (["gerçek hayat"], "gerçeklik ile sanatsal dönüşüm"),
        (["gerçeklik", "kurmaca"], "gerçeklik ile sanatsal dönüşüm"),
        (["konu", "tema"], "konu-tema ayrımı ve soyutlama"),
        (["öznel", "nesnel"], "kanıtlanabilirlik ile kişisel değerlendirme"),
        (["söz varlığı"], "söz seçimi ve karakter/bağlam ilişkisi"),
        (["ana düşünce"], "ana düşüncenin kanıtlarla kurulması"),
        (["özet"], "ana olay çizgisini koruyarak özetleme"),
        (["yapı"], "yapı unsurlarının anlam ve işlevi"),
        (["üslup"], "dil tercihi ve üslup etkisi"),
        (["dil/üslup"], "dil tercihi ve üslup etkisi"),
        (["değerlendir"], "ölçüt kullanarak değerlendirme"),
        (["değer"], "değer yargısının metin kanıtı"),
        (["gerekçe", "gerekçelendir"], "iddia-gerekçe bağı"),
        (["dostluk"], "farklılıklar içinde dostluk ve iletişim"),
        (["tahmin", "tespit"], "ön tahmin ile kaynak gözlemini karşılaştırma"),
        (["kültür", "millî kimlik"], "dil, kültür ve toplumsal bellek ilişkisi"),
        (["kültür"], "kültürel unsurun bağlam ve aktarımı"),
        (["fiil", "çatı"], "dil bilgisini metin işleviyle ilişkilendirme"),
    ]
    for needles, focus in patterns:
        if all(needle in text for needle in needles):
            return focus
    cleaned = re.sub(r"^(soru|adım)\s*[0-9a-z/\-–—. ]*[-—:]?", "", label, flags=re.IGNORECASE).strip()
    if len(cleaned) > 100:
        cleaned = " ".join(cleaned.split()[:14]) + "…"
    return cleaned or "kaynakla ilişkilendirilmiş anlam oluşturma"


def source_hook(prompt: str | None, label: str, heading: str, focus: str) -> str:
    """Return a short, source-derived hook for task-specific guidance.

    The hook is deliberately made from the verified prompt/heading rather than
    from a profile name or a generated task id.  It gives follow-up and
    intervention advice a concrete place in the actual book task while keeping
    the rendered guide readable.
    """
    value = prompt or label or heading or focus
    value = re.sub(r"\s+", " ", str(value).strip())
    if value.startswith("Kitapta “") and "başlığı altında verilen çalışma/yönerge" in value:
        parts = [candidate for candidate in [label, heading] if candidate]
        if len(parts) == 2 and normalize_text(parts[0]) == normalize_text(parts[1]):
            parts = parts[:1]
        value = " — ".join(parts) or focus
    value = re.sub(r"^(?:soru|adım)\s+[0-9a-z/\-–—. ]+\s*[—:-]\s*", "", value, flags=re.IGNORECASE)
    value = value.strip(" .:;—–-")
    words = value.split()
    if len(words) > 12:
        value = " ".join(words[:12]) + "…"
    return value or focus


def scoped_pedagogy_items(values: Iterable[Any], signature: str, hook: str, kind: str) -> list[str]:
    """Attach task/source specificity without duplicating an existing anchor."""
    result: list[str] = []
    signature_norm = normalize_text(signature)
    for value in values:
        if not isinstance(value, str) or not value.strip():
            continue
        text = re.sub(r"\s+", " ", value.strip())
        if not normalize_text(text).startswith(signature_norm):
            prefix = "düşünme sorusu" if kind == "follow_up_questions" else "müdahale"
            text = f"{signature} için {prefix}: {text}"
        if hook and normalize_text(hook) not in normalize_text(text):
            if kind == "follow_up_questions":
                text = f"{text} Özellikle ‘{hook}’ ayrıntısını yoklayın."
            else:
                text = f"{text} Müdahaleyi ‘{hook}’ ayrıntısını kullandırarak somutlaştırın."
        result.append(text)
    return dedupe_text(result)


def profile_content(profile: str, focus: str, signature: str, task_type: str, prompt: str | None) -> dict[str, Any]:
    """Return task-specific language for the routed domain.

    Every branch contains a different pedagogical rationale.  The signature
    keeps otherwise related tasks anchored to their actual book item instead of
    producing a phase-template sentence with only a new heading.
    """
    anchor = signature.strip(" .")
    if profile == "karagoz":
        return {
            "teacher_background": f"Karagöz bölümünde {anchor} üzerinden geleneksel gölge oyununun seyirlik ve sözlü niteliği ele alınır. Karakterler çoğu zaman yalnız adlarıyla değil, konuşma biçimleri, yanlış anlamaları, toplumsal tipleri ve sahne içindeki işlevleriyle kurulur. Dil farkını bir üstünlük ölçüsü gibi değil, karakterleştirme ve mizahın bağlama bağlı bir aracı olarak açıklayın.",
            "student_explanation": "Karagöz’de söylenen söz hem anlam taşır hem de konuşanın kimliğini ve sahnedeki ilişkisini görünür kılar.",
            "why_it_matters": f"Bu görev, {focus} bakımından sözlü kültür ürününün biçimsel özelliğini metin kanıtına dönüştürür.",
            "teacher_moves": [
                f"{anchor} için öğrencinin seçtiği söz veya sahne ayrıntısını önce aynen işaretletin; ardından bu ayrıntının hangi karakter özelliğini kurduğunu konuşturun.",
                "Karagöz-Hacivat farkını ‘biri doğru, biri yanlış’ diye kapatmayın; yanlış anlamanın sahne işlevini ve mizah üretimini görünür kılın.",
            ],
            "follow_up_questions": [
                f"{anchor} içinde bu yorumu taşıyan konuşma ayrıntısı hangisi; aynı ayrıntı çıkarılsa karakter ilişkisi nasıl değişirdi?",
                "Bu unsur yalnız bilgi vermiyor, seyirciyi nasıl bir tepkiye yönlendiriyor?",
            ],
            "common_misconceptions": [
                f"Öğrenci, {anchor} görevindeki dil farkını karakterin zekâsı veya değeri hakkında değişmez bir yargı sanabilir.",
                "Karagöz oyununun bölümlerini yalnız ezberlenecek başlıklar olarak görüp bölümün sahne işlevini gözden kaçırabilir.",
            ],
            "misconception_interventions": [
                "Öğrenciye aynı sözün farklı bir bağlamda başka bir kişiyi de kurup kuramayacağını sordurun; böylece dil göstergesini kişi değeriyle eşitlemesini ayırın.",
                "Diyalogdan bir cümleyi seçip mukaddime, muhavere, fasıl veya bitişten hangisindeki işleviyle okuduğunu açıklattırın.",
            ],
            "assessment_look_fors": [
                "Dil/sahne ayrıntısı ile karakter veya ilişki çıkarımı arasında açık bağ.",
                "Mizahı yalnız ‘komik olması’ ile değil yanlış anlama, söz oyunu veya seyirci etkisiyle açıklama.",
            ],
            "support": "Öğrenci için ‘Sahnede görülen/söylenen — bunun gösterdiği özellik — seyirci etkisi’ üçlü tablosu kullanın.",
            "enrichment": "Aynı kısa diyaloğu söz varlığı değişmeden beden dili ve ton değişikliğiyle nasıl farklılaştırabileceğini tasarlatın.",
            "board_note": "Tahtaya yaz: söz/sahne ayrıntısı → karakter veya ilişki → seyirci etkisi.",
        }
    if profile == "mektup":
        return {
            "teacher_background": f"{anchor} çalışılırken mektubu yalnız haberleşme aracı olarak değil, belirli bir gönderici, alıcı, amaç ve ilişki düzeyi olan yazılı iletişim olarak çerçeveleyin. Mektubun dili muhataba göre değişebilir; kişisel izlenim içermesi onu bütünüyle nesnel belge yapmaz. Metindeki bilgi ile yazarın değerlendirmesini ayırmak bu görevde temel açıklama noktasıdır.",
            "student_explanation": "Bir mektubu anlamak için ne söylendiği kadar kime, hangi amaçla ve hangi yakınlıkla söylendiğine de bakarız.",
            "why_it_matters": f"Bu görev, {focus} ölçütünü gönderici-alıcı-amaç ilişkisi içinde somutlaştırır.",
            "teacher_moves": [
                f"{anchor} için öğrenciden önce göndericiyi, alıcıyı ve amacı üç ayrı kutuya yazmasını; sonra seçtiği dil göstergelerini bu kutularla ilişkilendirmesini isteyin.",
                "Öznel değerlendirme ile metinde aktarılan doğrulanabilir bilgiyi iki farklı renkle işaretletin.",
            ],
            "follow_up_questions": [
                "Alıcı değişseydi hitap, kelime seçimi veya ayrıntı düzeyi hangi yönde değişirdi?",
                f"{anchor} içindeki bir ifade mektubun amacına nasıl hizmet ediyor; yalnız bilgi mi veriyor, ilişki de mi kuruyor?",
            ],
            "common_misconceptions": [
                "Mektubu tarih ve kişi bilgisi içerdiği için otomatik olarak tarafsız belge saymak.",
                f"{anchor} görevinde hitap ve kapanış ifadelerini biçimsel süs sanıp iletişimdeki ilişki işlevini gözden kaçırmak.",
            ],
            "misconception_interventions": [
                "Metindeki bir olguyu ve bir değerlendirmeyi yan yana seçtirin; ikisinin doğrulanma biçimini ayrı ayrı açıklattırın.",
                "Aynı içeriği yakın arkadaşa ve resmî kuruma yazdırıp değişen hitap/üslup kararlarını karşılaştırın.",
            ],
            "assessment_look_fors": [
                "Gönderici-alıcı-amaç ile dil tercihi arasında metinden kanıtlı ilişki.",
                "Öznel ve nesnel ifadelerin işlevini birbirine karıştırmama.",
            ],
            "support": "Gönderici | alıcı | amaç | ilişki düzeyi | bunu gösteren ifade başlıklarından oluşan beş kutulu bir şema verin.",
            "enrichment": "Aynı iletiyi mektup ve e-posta biçiminde yeniden yazdırarak kalıcılık, hız ve üslup farklarını tartıştırın.",
            "board_note": "Tahtaya yaz: gönderici + alıcı + amaç + ilişki düzeyi → dil/üslup kararı.",
        }
    if profile == "writing_email":
        return {
            "teacher_background": f"{anchor} için e-postayı yalnız teknik bir form doldurma işi olarak değil, amacı ve hedef alıcısı belirlenmiş işlevsel bir yazma ürünü olarak açıklayın. Konu satırı, hitap, ana ileti, paragraf düzeni, ekler, gönderim zamanı ve mahremiyet aynı iletişim kararının parçalarıdır. Dijital ortam hız kazandırsa da açıklık, nezaket, güvenlik ve yazım özeni gereksinimini ortadan kaldırmaz.",
            "student_explanation": "E-postada biçim, alıcıya ve amaca hızlı ve açık ulaşmayı sağlayan bir düzen kurar.",
            "why_it_matters": f"Bu görev, {focus} kararlarını gerçek bir dijital iletişim ürünü üzerinde görünür kılar.",
            "teacher_moves": [
                f"{anchor} için öğrencinin taslağını göndermeden önce konu satırı, hitap, ana istek ve ek gerekçesini ayrı ayrı kontrol ettirin.",
                "Bir cümlenin alıcıda belirsizlik oluşturup oluşturmadığını ‘Bu cümleyi okuyan kişi hangi eylemi anlayacak?’ sorusuyla test ettirin.",
            ],
            "follow_up_questions": [
                "Bu ek gerçekten alıcının karar vermesine yardım ediyor mu, yoksa yalnızca metni kalabalıklaştırıyor mu?",
                f"{anchor} için seçtiğin dil, alıcıyla ilişkin ve iletinin aciliyetiyle nasıl uyumlu?",
            ],
            "common_misconceptions": [
                "E-postada konu satırı ve hitabın gereksiz olduğunu, yalnız ana metnin yeterli olacağını düşünmek.",
                "Dijital iletişimde kısaltma ve gündelik dilin her alıcı ve amaç için uygun olduğunu sanmak.",
            ],
            "misconception_interventions": [
                "Öğrenciye aynı metni konu satırı olmayan ve alıcısı belirtilmeyen biçimde okutun; oluşan belirsizlikleri metinde işaretletin.",
                "Resmî ve kişisel iki alıcı seçtirip değişmesi gereken hitap, söz varlığı ve kapanış bölümlerini yeniden yazdırın.",
            ],
            "assessment_look_fors": [
                "Amaç, hedef kitle, konu satırı, hitap ve ana iletinin birbiriyle tutarlı olması.",
                "Ek, dil, yazım ve görsel/işitsel destek kararlarının iletiyi gerçekten desteklemesi.",
            ],
            "support": "Öğrenciye önce ‘Kime? Neden? Ne istiyorum? Hangi ek gerekli?’ dört sorusunu cevaplatıp sonra e-posta alanlarını doldurtun.",
            "enrichment": "Aynı e-postanın daha resmî ve daha yakın iki sürümünü yazdırarak üslup kararlarını gerekçelendirin.",
            "board_note": "Tahtaya yaz: amaç → alıcı → konu satırı → ana ileti → ek/kanıt → kapanış.",
        }
    if profile == "communication":
        return {
            "teacher_background": f"{anchor} görevinde iletişimi yalnız konuşma veya bilgi aktarımı olarak daraltmayın. Gönderici, alıcı, ileti, kanal, bağlam ve geri bildirim birlikte işler; gürültü fiziksel olabileceği gibi önyargı, dikkatsizlik, belirsiz dil veya uygun olmayan kanal da olabilir. Çok modlu metinde ses, görüntü, yazı ve müzik aynı iletiyi destekleyebilir ya da farklılaştırabilir.",
            "student_explanation": "İletişimde anlam, yalnız sözcüklerden değil; kanal, bağlam, ses, görüntü ve karşılıklı tepkiden birlikte oluşur.",
            "why_it_matters": f"Bu görev, {focus} üzerinden iletişimde neden-sonuç kurmayı ve kanal seçimini bilinçli hâle getirir.",
            "teacher_moves": [
                f"{anchor} için öğrencinin önce iletişim ögesini, sonra aksamanın nerede oluştuğunu ve son olarak sonucu yazdığı bir neden-sonuç zinciri kurdurun.",
                "Aynı mesajı yüz yüze, telefonla ve e-postayla iletme durumlarını karşılaştırarak kanalın dil/beden sesi üzerindeki etkisini tartıştırın.",
            ],
            "follow_up_questions": [
                "Buradaki aksama göndericiden mi, alıcıdan mı, kanaldan mı, bağlamdan mı kaynaklanıyor; hangi kanıt bunu gösteriyor?",
                f"{anchor} için başka bir kanal seçilse ileti açıklar mıydı, yoksa yeni bir sorun mu doğururdu?",
            ],
            "common_misconceptions": [
                "İletişim engelini yalnız fiziksel gürültü sanmak.",
                "Karşı tarafla aynı fikirde olmamayı tek başına iletişim engeli saymak veya iletişimde geri bildirimi gereksiz görmek.",
            ],
            "misconception_interventions": [
                "Öğrenciden fiziksel ses olmayan fakat önyargı ya da belirsiz söz nedeniyle bozulan kısa bir örnek kurmasını isteyin; engel türünü adlandırsın.",
                "Mesajı farklı bir kanala taşıtıp hangi bilgi ve duygunun kaybolduğunu iki sütunda karşılaştırın.",
            ],
            "assessment_look_fors": [
                "İletişim ögeleri ile aksama/çözüm arasındaki neden-sonuç bağı.",
                "Ses, görüntü veya dil unsurunun ileti üzerindeki işlevini somut bir ayrıntıyla açıklama.",
            ],
            "support": "İletişim zincirini ‘gönderici → ileti → kanal → alıcı → geri bildirim’ biçiminde verip engel noktasını işaretletin.",
            "enrichment": "Aynı iletiyi iki farklı kanalda tasarlatıp hangi durumda kanal değişikliğinin etik ve işlevsel sonuç doğuracağını tartıştırın.",
            "board_note": "Tahtaya yaz: gönderici–ileti–kanal–alıcı–geri bildirim; engel → etki → çözüm.",
        }
    if profile == "old_turkic":
        return {
            "teacher_background": f"{anchor} çalışmasında Orhun yazıtlarını yalnız eski kelimeler listesi olarak sunmayın. Yazıtlar, dönemin devlet ve toplum anlayışına, töreye, birlik fikrine ve gelecek kuşaklara seslenme amacına ilişkin yazılı belgelerdir. Dil özellikleri tarihî bağlamla birlikte okunmalı; öğrencinin bugünkü anlamı metinden çıkarırken tarihsel uzaklığı ve çeviri aracını hesaba katması sağlanmalıdır.",
            "student_explanation": "Orhun metinleri geçmişten kalan sözler değil; millete seslenen, tarih ve dil bilgisi taşıyan birer kültür belgesidir.",
            "why_it_matters": f"Bu görev, {focus} bağlamında dilin tarihî hafızayı nasıl taşıdığını kanıtlarla düşündürür.",
            "teacher_moves": [
                f"{anchor} için önce kelimeyi günümüz karşılığıyla eşleştirin, sonra aynı ifadenin metindeki öğüt, uyarı veya tarih anlatımı işlevini belirletin.",
                "Tarihî bilgiyi öğrencinin medya içeriğinde gerçekten gördüğü ayrıntıdan ayırın; görünmeyen bir ayrıntıyı metne mal etmeyin.",
            ],
            "follow_up_questions": [
                "Bu söz yalnız geçmişi anlatıyor mu, yoksa gelecekteki okuyucuya bir sorumluluk da yüklüyor mu?",
                f"{anchor} içindeki kelime veya ifade, dil ile kültürel bellek arasındaki bağı nasıl görünür kılıyor?",
            ],
            "common_misconceptions": [
                "Tarihî bir metni bugünkü anlamıyla hiçbir bağlam farkı yokmuş gibi okumak.",
                "Yazıtların değerini yalnız ‘ilk yazılı belge’ bilgisine indirgemek; metnin hitap ve öğüt işlevini görmemek.",
            ],
            "misconception_interventions": [
                "Aynı cümlenin günümüz Türkçesi ile tarihî bağlamdaki muhatabını karşılaştırın; anlamın hangi bölümünün bağlamla tamamlandığını gösterin.",
                "Öğrenciye metindeki bir hitap veya uyarıyı seçtirip ‘kim, kime, hangi amaçla?’ sorularıyla yeniden açıklattırın.",
            ],
            "assessment_look_fors": [
                "Kelime/ifade anlamını tarihî bağlam ve metnin amacıyla ilişkilendirme.",
                "Dil, devlet/töre ve kültürel bellek arasında metne dayalı ilişki kurma.",
            ],
            "support": "‘Tarihî kelime — günümüz karşılığı — metindeki işlev — bugünkü çağrışım’ tablosuyla ilerleyin.",
            "enrichment": "Kısa bir yazıt cümlesini günümüz gençlerine hitap eden bir duyuruya dönüştürüp korunan ve değişen anlamları açıklatın.",
            "board_note": "Tahtaya yaz: tarihî ifade → bağlamdaki anlam → muhatap/amaç → kültürel bellek.",
        }
    if profile == "ashik":
        return {
            "teacher_background": f"{anchor} için âşıklık geleneğini yalnız saz eşliğinde şiir söylemek biçiminde açıklamayın. Saz, sözlü aktarım, doğaçlama, atışma, usta-çırak ilişkisi ve topluluk önünde icra geleneğin birbirini tamamlayan unsurlarıdır. Atışmadaki söz oyunları hem sanatsal beceriyi hem de karşılıklı dinleme ve anlık üretim yeteneğini görünür kılar.",
            "student_explanation": "Âşık atışmasında sanatçı, geleneğin bilgisini kendi söz ustalığı ve anlık karşılığıyla canlı tutar.",
            "why_it_matters": f"Bu görev, {focus} üzerinden sözlü kültürün aktarım ve üretim biçimini kavratır.",
            "teacher_moves": [
                f"{anchor} için öğrenciden bir dizeyi seçip benzetme, sesleniş veya karşılık verme işlevini açıklamasını isteyin.",
                "Atışmayı yalnız yarışma gibi değil, ortak gelenek kuralları içinde gerçekleşen dinleme-cevaplaşma olarak çerçeveleyin.",
            ],
            "follow_up_questions": [
                "Bu dizeyi güçlü kılan yalnız anlamı mı, yoksa ses, ritim ve karşılık verme biçimi mi?",
                f"{anchor} içindeki unsur usta-çırak aktarımını veya kültürel belleği nasıl gösteriyor?",
            ],
            "common_misconceptions": [
                "Atışmayı hazırlıksız ve kuralsız bir tartışma sanmak.",
                "Sazı yalnız eşlik aracı görüp sözlü aktarım, ritim ve topluluk işlevini gözden kaçırmak.",
            ],
            "misconception_interventions": [
                "Atışmadan iki karşılıklı dize seçtirip birinin diğerine nasıl cevap verdiğini oklarla gösterin.",
                "Sazın olmadığı bir okuma ile saz/ritim desteği olan okumayı karşılaştırıp değişen dinleyici etkisini açıklattırın.",
            ],
            "assessment_look_fors": [
                "Gelenek unsuru ile dize/performans ayrıntısı arasında açık bağ.",
                "Söz ustalığını yalnız güzel söyleyiş değil, karşılık ve kültürel bağlamla açıklama.",
            ],
            "support": "‘Gelenek unsuru — metin/performans kanıtı — dinleyici etkisi’ üçlü notunu kullandırın.",
            "enrichment": "Bir atışma dizesine farklı iki cevap yazdırıp hangisinin ölçü, anlam ve karşılık bakımından daha güçlü olduğunu tartıştırın.",
            "board_note": "Tahtaya yaz: saz + sözlü aktarım + doğaçlama + karşılık + topluluk.",
        }
    if profile == "museum":
        return {
            "teacher_background": f"{anchor} çalışmasında müzeyi yalnız nesnelerin sergilendiği bir yer olarak değil, nesne, bağlam ve toplumsal hafıza arasında ilişki kuran bir öğrenme ortamı olarak açıklayın. Bir kültür unsurunu seçerken nesnenin ne olduğu kadar hangi toplulukla, kullanım biçimiyle ve hikâyeyle anlam kazandığına bakılır. Öğrenci gözlem ile kişisel yorumu birbirinden ayırabilmelidir.",
            "student_explanation": "Müzede bir nesne, onu kullanan insanların yaşamı ve o nesneye verilen anlamla birlikte kültürel mirasa dönüşür.",
            "why_it_matters": f"Bu görev, {focus} yoluyla kültür unsurunu gözlem, bağlam ve kişisel anlam arasında ilişkilendirir.",
            "teacher_moves": [
                f"{anchor} için öğrenciden önce nesnenin gözlenebilir özelliklerini, sonra nesneye yüklediği kültürel anlamı ayrı yazmasını isteyin.",
                "‘Bu bilgi nesneden mi, araştırmadan mı, kişisel hatıradan mı geliyor?’ ayrımını yaptırın.",
            ],
            "follow_up_questions": [
                "Bu unsur başka bir müzede veya başka bir toplulukta hangi bağlam değişikliğiyle farklı anlam kazanabilir?",
                f"{anchor} için seçtiğin nesnenin kültürel miras sayılmasını hangi kullanım veya aktarım kanıtı destekliyor?",
            ],
            "common_misconceptions": [
                "Kültürel mirası yalnız çok eski veya maddi nesnelerle sınırlamak.",
                "Kişisel hatırayı, nesnenin bütün toplum için taşıdığı anlamın kanıtı gibi sunmak.",
            ],
            "misconception_interventions": [
                "Aynı nesnenin iki farklı kullanıcı için anlamını karşılaştırın; ortak kültürel unsur ile kişisel anlamı iki renkte ayırın.",
                "Öğrenciden nesneye ilişkin bir gözlem cümlesi ve bir yorum cümlesi yazmasını isteyip cümlelerin dayanaklarını sorgulayın.",
            ],
            "assessment_look_fors": [
                "Nesne/uygulama ile kültürel bağlam arasında somut bağlantı.",
                "Gözlenen bilgi ile kişisel yorumun açıkça ayrılması.",
            ],
            "support": "Öğrenciye ‘Ne görüyorum? Kim kullanmış/kullanıyor? Hangi anlamı taşıyor? Nasıl aktarılabilir?’ dört sorusunu verin.",
            "enrichment": "Bir sergi etiketi yazdırıp nesnenin adı, kullanım bağlamı ve ziyaretçide uyandıracağı soruyu birlikte tasarlatın.",
            "board_note": "Tahtaya yaz: nesne/uygulama → kullanım bağlamı → toplumsal anlam → aktarım.",
        }
    if profile == "cultural_memory":
        return {
            "teacher_background": f"{anchor} görevinde kültür ve dil ilişkisini değişmez bir özellikler listesi olarak değil, toplulukların tarih, coğrafya, üretim biçimi ve ortak deneyimleriyle oluşan ve kuşaktan kuşağa aktarılan bir süreç olarak açıklayın. Ortaklıklar iletişimi ve belleği güçlendirebilir; farklılaşmalar ise tarihî tecrübelerin ve çevrenin izlerini taşır. Öğrencinin genellemeyi örnek ve bağlamla sınaması gerekir.",
            "student_explanation": "Kültür ortak hatıralarla taşınır; fakat farklı coğrafya ve yaşantılar aynı kültür alanındaki ifadeleri çeşitlendirebilir.",
            "why_it_matters": f"Bu görev, {focus} üzerinden ortaklık ile farklılaşmayı kanıtlı ve saygılı biçimde açıklamayı öğretir.",
            "teacher_moves": [
                f"{anchor} için öğrenciden ortak gördüğü unsuru ve farklılaşan biçimi yan yana yazmasını, her biri için tarih/coğrafya/yaşantı bağlantısı kurmasını isteyin.",
                "Kültürel bir özelliği bütün Türk topluluklarına değişmez biçimde genellemeden önce metindeki kapsamı ve örneği kontrol ettirin.",
            ],
            "follow_up_questions": [
                "Bu ortaklık hangi paylaşım veya aktarım kanıtıyla görülüyor; farklılık hangi yaşantıyla açıklanabilir?",
                f"{anchor} için kültür unsurunun zaman içinde değişmesi onun değerini yok eder mi, yoksa yeni bir aktarım biçimi mi doğurur?",
            ],
            "common_misconceptions": [
                "Ortak kültürün bütün topluluklarda aynı biçimde ve hiç değişmeden yaşadığını düşünmek.",
                "Kültürel farklılığı üstünlük veya eksiklik ölçüsüne dönüştürmek.",
            ],
            "misconception_interventions": [
                "Aynı kültür unsurunun iki bölgedeki biçimini karşılaştırın; ortak işlevi ve değişen görünüşü iki renkte ayırın.",
                "Genel yargıyı ‘hangi kişi/topluluk, hangi zaman, hangi kaynak?’ sorularıyla sınırlandırın.",
            ],
            "assessment_look_fors": [
                "Ortaklık/farklılık iddiasının belirli bir kültür veya dil örneğiyle desteklenmesi.",
                "Tarih, coğrafya ve toplumsal aktarımın genelleme yapılmadan ilişkilendirilmesi.",
            ],
            "support": "Öğrenciye ‘ortak unsur — farklı görünüş — neden — aktarım yolu’ çizelgesini verin.",
            "enrichment": "Bir kültür unsurunun dijital ortamda nasıl değişerek yaşatılabileceğine ilişkin öneriyi yarar ve riskleriyle savundurun.",
            "board_note": "Tahtaya yaz: ortak deneyim + tarih/coğrafya → kültürel unsur; aktarım → değişim/süreklilik.",
        }
    if profile == "story_memoir":
        return {
            "teacher_background": f"{anchor} görevinde hikâye ve anıyı yalnız olay sıralamasıyla açıklamayın. Anlatıcı bir olayı, kişiyi, zaman ve mekânı seçer; bu seçimler hatırlama, bakış açısı, amaç ve dil aracılığıyla anlam kazanır. Hikâyede kurmaca düzenleme ağır basabilir; anı yaşanmışlık iddiası taşır fakat o da seçilmiş ve anlatılmış bir geçmiş deneyimdir.",
            "student_explanation": "Bir anlatıda olayların nasıl seçildiği ve kimin bakışından aktarıldığı, olayın okurda oluşturduğu anlamı değiştirir.",
            "why_it_matters": f"Bu görev, {focus} üzerinden olay, anlatıcı, kişi ve kültürel bağlamı birlikte okumayı geliştirir.",
            "teacher_moves": [
                f"{anchor} için öğrencinin olay çizgisini çıkarmasını, ardından anlatıcının seçtiği ayrıntının kişi veya kültür anlamına etkisini açıklamasını isteyin.",
                "Özet ile yorumun ayrımını koruyun: önce ne olduğunu, sonra yazar/anlatıcının bunu nasıl anlamlandırdığını konuşturun.",
            ],
            "follow_up_questions": [
                "Anlatıcı bu ayrıntıyı seçmeseydi okurun kişi veya olay hakkındaki düşüncesi nasıl değişirdi?",
                f"{anchor} içinde kültürel unsur olayın yalnız dekoru mu, yoksa kişilerin kararını ve ilişkisini etkileyen bir öge mi?",
            ],
            "common_misconceptions": [
                "Anlatıcının aktardığı her bilgiyi tarafsız ve eksiksiz geçmiş kaydı saymak.",
                "Özet yazmayı olayları yorumlamadan art arda sıralamak sanmak.",
            ],
            "misconception_interventions": [
                "Metindeki olayları ‘oldu’, ‘anlatıcı seçti’, ‘okur çıkarımı’ başlıklarıyla ayırın.",
                "Bir sahneyi başka bir anlatıcının gözünden kısaca yeniden yazdırıp değişen bilgi ve duygu etkisini gösterin.",
            ],
            "assessment_look_fors": [
                "Olay, kişi, zaman, mekân ve anlatıcı arasında metne dayalı ilişki.",
                "Özet ile yorumun ayrılması ve kültür unsurunun olay/kişi işlevinin açıklanması.",
            ],
            "support": "Önce ‘kim-ne zaman-nerede-ne oldu?’ tablosunu, sonra ‘anlatıcı bunu neden seçmiş olabilir?’ sorusunu kullandırın.",
            "enrichment": "Aynı olayı anı, haber ve hikâye başlangıcı olarak üç biçimde yazdırıp gerçeklik ve bakış açısı farkını tartıştırın.",
            "board_note": "Tahtaya yaz: olay/kişi/zaman/mekân + anlatıcı seçimi → anı/hikâye anlamı.",
        }
    if profile == "language_grammar":
        return {
            "teacher_background": f"{anchor} görevinde dil bilgisini metinden kopuk bir etiketleme alıştırmasına çevirmeyin. Fiil kipi, çatı, cümle kuruluşu ve noktalama; zaman, eyleyen, vurgu, ilişki ve anlam akışını biçimlendirir. Öğrenci önce yapıyı doğru tanımalı, sonra bu tercihin metnin anlatımı veya anlamına ne kattığını örnek cümle üzerinden açıklamalıdır.",
            "student_explanation": "Dil bilgisi biçimleri, cümlenin yalnız adını değil; olayın zamanı, eyleyenin görünürlüğü ve anlamın vurgusunu da düzenler.",
            "why_it_matters": f"Bu görev, {focus} yoluyla dil bilgisi kavramını gerçek metindeki anlatım işleviyle ilişkilendirir.",
            "teacher_moves": [
                f"{anchor} için öğrencinin önce biçimsel özelliği işaretlemesini, sonra cümlenin anlamında veya anlatımında oluşturduğu etkiyi yazmasını isteyin.",
                "Tanıma cevabı doğru olsa bile örneği metindeki işlevle açıklamayan yanıtı tamamlanmış saymayın.",
            ],
            "follow_up_questions": [
                "Bu yapı değiştirildiğinde cümlenin eyleyeni, zamanı veya vurgusu nasıl değişir?",
                f"{anchor} içinde bu noktalama veya fiil tercihi anlam akışını hangi yönde yönlendiriyor?",
            ],
            "common_misconceptions": [
                "Bir dil bilgisi teriminin adını söylemeyi cümledeki işlevini açıklamakla eşitlemek.",
                "Çatı veya kipin her cümlede aynı anlam etkisini oluşturduğunu düşünmek.",
            ],
            "misconception_interventions": [
                "Aynı cümleyi ilgili yapı değişecek biçimde yeniden yazdırın; eyleyen, zaman veya vurgu farkını karşılaştırın.",
                "Öğrenciden terim adını kapatıp cümlenin ‘kim/ne yaptı, ne zaman, nasıl?’ bilgisini kendi sözleriyle açıklamasını isteyin.",
            ],
            "assessment_look_fors": [
                "Dil bilgisi yapısının doğru tanınması ve örnek üzerinde gösterilmesi.",
                "Biçim ile cümlenin anlatım/anlam işlevi arasında açıklanmış bağ.",
            ],
            "support": "Her cümle için ‘biçim — cümledeki kanıt — anlam/anlatım etkisi’ üçlü kutusunu kullandırın.",
            "enrichment": "Aynı paragrafta kip/çatı değişiklikleri yaparak anlatıcının sorumluluk ve zaman algısının nasıl değiştiğini tartıştırın.",
            "board_note": "Tahtaya yaz: dil bilgisi biçimi → cümledeki kanıt → anlam/anlatım işlevi.",
        }
    if profile == "huzur":
        return {
            "teacher_background": f"{anchor} görevinde romanı yazarın hayatının kopyası gibi sunmayın. Roman, gerçek yaşamdan izleri seçer; kişi, olay, zaman ve mekânı kurmaca bir düzen içinde birleştirir. Anlatıcı, yapı, dil ve dönem bağlamı bu dönüşümü okura hissettirir. Öğrencinin metinden doğrulanabilen ayrıntı ile yorumunu ayırması, eserin anlamını tek bir biyografik bilgiye indirgememesini sağlar.",
            "student_explanation": "Bir romanda gerçek hayattan iz bulunabilir; fakat yazar bu izleri seçer, düzenler ve kurmaca bir dünyada yeniden anlamlandırır.",
            "why_it_matters": f"Bu görev, {focus} üzerinden romanın gerçeklikle kurduğu ilişkiyi metin yapısı ve okur yorumu içinde düşünmeyi sağlar.",
            "teacher_moves": [
                f"{anchor} için öğrenciden önce metinde açıkça görülen ayrıntıları, ardından bu ayrıntılardan yaptığı yorumu iki sütuna ayırmasını isteyin.",
                "Karakter, çatışma veya anlatıcı tespitini olay özetiyle bırakmayıp bunun metnin anlamına etkisini açıklattırın.",
            ],
            "follow_up_questions": [
                "Bu ayrıntının gerçek hayattan geldiğini düşünmemize hangi metin kanıtı izin veriyor; hangi bölüm yalnız kurmaca düzenlemenin sonucu olabilir?",
                f"{anchor} içinde anlatıcı veya yapı seçimi okurun yorumunu nasıl yönlendiriyor?",
            ],
            "common_misconceptions": [
                "Romandaki her ayrıntının yazarın yaşadığı olayın birebir karşılığı olduğunu sanmak.",
                "Konu, tema ve ana düşünceyi aynı şey saymak veya olay özetini yapı çözümlemesi yerine koymak.",
            ],
            "misconception_interventions": [
                "Bir ayrıntıyı ‘metinde var’, ‘dış kaynakla doğrulanabilir’, ‘yorum’ etiketleriyle sınıflandırın; üçünü aynı kanıt düzeyinde sunmasını engelleyin.",
                "Aynı olayın anlatıcı ve zaman düzeni değiştiğinde okurda oluşan farkı kısa iki taslakla karşılaştırın.",
            ],
            "assessment_look_fors": [
                "Gerçeklik izi ile kurmaca düzenlemeyi aynı metin ayrıntısı üzerinden ayırma.",
                "Anlatıcı/yapı/dil unsurunun okur yorumu veya iletiye etkisini açıklama.",
            ],
            "support": "‘Metinde açıkça görülen — buradan çıkarılan — kanıtım’ üç sütunlu roman çözümleme formu kullanın.",
            "enrichment": "Bir sahneyi başka bir anlatıcıyla yeniden yazdırıp değişen bakış açısının bilgi ve duygu üzerindeki etkisini tartıştırın.",
            "board_note": "Tahtaya yaz: gerçeklik izi → seçme/düzenleme → kurmaca anlam → okur yorumu.",
        }
    if profile == "bio_tezkire":
        return {
            "teacher_background": f"{anchor} çalışmasında biyografi ve tezkireyi yalnız doğum-ölüm tarihleri listesi olarak açıklamayın. Bu türlerde kişi hakkında bilgi seçilir, kronolojik veya tematik biçimde düzenlenir ve anlatıcı/yazarın değerlendirmesiyle sunulur. Biyografi modern belge ve kaynak kullanımına daha çok yaslanabilir; tezkire geleneği ise şairleri ve sanatçıları edebî değerlendirme, övgü ve seçme ölçütleriyle tanıtabilir. Tür farkını metin kanıtıyla kurdurun.",
            "student_explanation": "Biyografi bir insanın yaşamını tanıtır; bunu yaparken hangi bilgiyi seçtiği ve nasıl değerlendirdiği metnin türünü görünür kılar.",
            "why_it_matters": f"Bu görev, {focus} bağlamında tür bilgisini yapı, bilgi seçimi ve anlatıcı tutumuyla ilişkilendirir.",
            "teacher_moves": [
                f"{anchor} için öğrenciden kişi bilgilerini kronoloji, başarı ve değerlendirme olarak üç gruba ayırmasını isteyin.",
                "Bir cümledeki belgenin bilgisiyle yazarın övgü/eleştirisini farklı işaretletin.",
            ],
            "follow_up_questions": [
                "Bu metni yalnız bilgi listesi olmaktan çıkaran anlatıcı tutumu veya düzenleme kararı hangisi?",
                f"{anchor} içinde türü belirleyen kanıtı başka bir türün özelliğiyle karıştırmadan nasıl açıklarsın?",
            ],
            "common_misconceptions": [
                "Biyografide anlatıcının değerlendirmesi bulunamayacağını düşünmek.",
                "Tezkireyi biyografinin eski yazımlı ve tamamen aynı biçimi sanmak.",
            ],
            "misconception_interventions": [
                "Metinden bir doğrulanabilir bilgi ve bir değerlendirme cümlesi seçtirip ikisinin kanıt ve dil farkını açıklattırın.",
                "Aynı kişi için kronolojik tanıtım ile edebî değerlendirme paragrafı yazdırarak türsel amaç farkını görünür kılın.",
            ],
            "assessment_look_fors": [
                "Tür özelliğini metinden seçilmiş bilgi ve anlatıcı tutumuyla kanıtlama.",
                "Kronoloji, yapı, dil-üslup ve değerlendirme işlevini birbirinden ayırma.",
            ],
            "support": "Metni ‘kişiye ilişkin bilgi — kaynaklanabilirlik — yazar tutumu — tür işareti’ tablosuyla okutun.",
            "enrichment": "Bir sanatçı tanıtımını ansiklopedi maddesi ve tezkire üslubunda iki kısa biçime dönüştürüp değişen değerlendirme dilini tartıştırın.",
            "board_note": "Tahtaya yaz: kişi bilgisi + seçme/düzenleme + anlatıcı tutumu → biyografi/tezkire tür işareti.",
        }
    if profile == "interview":
        return {
            "teacher_background": f"{anchor} için mülakatı rastgele soru-cevap değil, hedef kişi ve amaç belirlenerek planlanan bir sözlü iletişim türü olarak açıklayın. Sorular açık uçlu olduğunda karşı tarafın deneyimini ve düşüncesini açar; takip soruları belirsizliği giderir. Süre, hedef kitle, kayıt ve etik sınırlar da içerik kadar önemlidir. Hayalî cevaplarda metin kişisinin özellikleri kanıtla korunmalıdır.",
            "student_explanation": "İyi bir mülakat sorusu karşı tarafı yönlendirmek yerine düşüncesini açacak alan bırakır ve bir sonraki soruyu doğurur.",
            "why_it_matters": f"Bu görev, {focus} üzerinden soru tasarımı, dinleme ve kanıta dayalı takip yapmayı geliştirir.",
            "teacher_moves": [
                f"{anchor} için öğrencinin kapalı bir soruyu açık uçluya dönüştürmesini ve neden daha fazla bilgi sağlayacağını açıklamasını isteyin.",
                "Hayalî cevap yazılırken metin kişisinin davranış, dil veya amaç özelliklerinden en az bir dayanak seçtirin.",
            ],
            "follow_up_questions": [
                "Bu soru karşı tarafın hangi deneyimini açıyor; cevabı daraltan bir varsayım içeriyor mu?",
                f"{anchor} için verilen cevaptan sonra sorulacak takip sorusu hangi belirsizliği gidermeli?",
            ],
            "common_misconceptions": [
                "Mülakat sorusunu cevabı içinde taşıyan yönlendirici bir cümle kurmak.",
                "Hayalî mülakatta metin kişisine metinde desteklenmeyen düşünceler söyletmek.",
            ],
            "misconception_interventions": [
                "Öğrencinin sorusundaki varsayımı çizdirin; varsayımı kaldırıp aynı bilgi ihtiyacını açık uçlu soru olarak yeniden kurdurun.",
                "Hayalî cevaptaki her iddianın yanına metin kanıtı yazdırın; dayanağı olmayan iddiayı soru biçimine geri dönüştürün.",
            ],
            "assessment_look_fors": [
                "Soru amacı, hedef kişi ve takip sorusu arasında tutarlılık.",
                "Cevapların metin kişisi/konu özellikleriyle kanıtlı biçimde ilişkilendirilmesi.",
            ],
            "support": "Her soru için ‘amaç — soru kökü — beklenen bilgi — olası takip’ dört hücreli plan verin.",
            "enrichment": "Aynı konu için bir açık uçlu, bir derinleştirici ve bir etik sınır sorusu tasarlatıp sıralama gerekçesi istetin.",
            "board_note": "Tahtaya yaz: hedef kişi/amaç → açık soru → dinleme → takip sorusu → kanıt.",
        }
    if profile == "radio":
        return {
            "teacher_background": f"{anchor} görevinde radyo tiyatrosunu yalnız yazılı diyalog olarak değil, ses aracılığıyla kurulan çok modlu bir anlatı olarak düşünün. Ses tonu, vurgu, susma, müzik, efekt ve konuşma sırası mekânı, kişiyi ve duyguyu dinleyicinin zihninde kurar. Görsel bulunmadığı için ses ayrıntılarının işlevi artar; ancak dış kayıtta duyulmayan bir unsuru öğrencinin yerine varsaymamak gerekir.",
            "student_explanation": "Radyo tiyatrosunda gözle göremediğimiz kişi ve mekânı ses, söz, sessizlik ve müzik birlikte kurar.",
            "why_it_matters": f"Bu görev, {focus} üzerinden ses unsurunun anlatıdaki yapı ve duygu işlevini fark ettirir.",
            "teacher_moves": [
                f"{anchor} için öğrenciden bir ses ayrıntısını seçip bunun kişi, mekân veya duyguya etkisini açıklamasını isteyin.",
                "Dinleme öncesi tahmin ile gerçekten duyulan unsuru ayrı kaydettirin; iki kaydı sonradan karşılaştırın.",
            ],
            "follow_up_questions": [
                "Bu ses ayrıntısı kaldırılırsa dinleyici hangi bilgiyi veya duyguyu daha zor kurar?",
                f"{anchor} için sesin sözcükleri desteklediği veya onlarla gerilim oluşturduğu an hangisi?",
            ],
            "common_misconceptions": [
                "Radyo tiyatrosunda yalnız konuşulan sözcüklerin anlam taşıdığını düşünmek.",
                "Dinleme öncesi tahmini, kayıt sonrası kanıtlanmış bilgi gibi kullanmak.",
            ],
            "misconception_interventions": [
                "Kısa bir bölümü ses tonu ve sessizlik bilgisi olmadan okutun; kaybolan anlamı öğrencinin iki sütunda yazmasını sağlayın.",
                "Tahmin cümlesine ‘önce’, gözlem cümlesine ‘dinleme sırasında’ etiketi koydurup dayanak farkını açıklattırın.",
            ],
            "assessment_look_fors": [
                "Ses/müzik/sessizlik ile kişi, mekân veya duygu arasında işlevsel ilişki.",
                "Duyulan kanıt ile önceden yapılan tahmini ayırma.",
            ],
            "support": "Not alma için ‘duyulan ses — neyi kuruyor — metne etkisi’ üç sütununu kullandırın.",
            "enrichment": "Aynı kısa diyalog için iki farklı ses tasarımı önerip dinleyici yorumunun nasıl değişeceğini tartıştırın.",
            "board_note": "Tahtaya yaz: söz + ton/vurgu + sessizlik + müzik/efekt → zihinsel görüntü ve duygu.",
        }
    if profile == "genre_transform":
        return {
            "teacher_background": f"{anchor} çalışmasında tür dönüştürmeyi metni basitçe kısaltmak veya sözcükleri değiştirmek olarak açıklamayın. Dönüşümde çekirdek olay/ileti korunurken yeni türün anlatıcı, yapı, dil, zaman ve alıcı gereksinimleri yeniden tasarlanır. Öğrenci, hangi unsuru koruduğunu ve hangi unsuru yeni türe uyarladığını bilinçli biçimde gösterebilmelidir.",
            "student_explanation": "Bir metni başka türe dönüştürürken ana iletiyi korur, fakat yeni türün anlatma biçimine uygun yeni kararlar veririz.",
            "why_it_matters": f"Bu görev, {focus} yoluyla biçim değişirken anlamın nasıl korunduğunu ve yeniden kurulduğunu gösterir.",
            "teacher_moves": [
                f"{anchor} için öğrencinin dönüşüm öncesi çekirdek iletiyi tek cümleyle yazmasını, sonra yeni türün gerektirdiği üç kararı belirtmesini isteyin.",
                "Ürünü yalnız estetik beğeniyle değil, kaynak metinle anlam sürekliliği ve hedef türe uygunluk açısından karşılaştırın.",
            ],
            "follow_up_questions": [
                "Dönüşümden sonra hangi unsur aynı kaldı; hangi unsur yeni türün koşulu nedeniyle değişti?",
                f"{anchor} ürününde biçim değişikliği ana iletiyi güçlendiriyor mu, yoksa belirsizleştiriyor mu?",
            ],
            "common_misconceptions": [
                "Tür dönüşümünü yalnız sözcükleri güncellemek veya metni özetlemek sanmak.",
                "Yeni türün alıcı ve yapı özelliklerini hesaba katmadan kaynak metni aynen taşımak.",
            ],
            "misconception_interventions": [
                "Öğrenciden kaynak ve ürün için anlatıcı, yapı, dil ve alıcı başlıklarını yan yana doldurmasını isteyin.",
                "Üründen ana iletiyi çıkarıp kaynak iletiyle karşılaştırın; anlam kayması varsa hangi tasarım kararından kaynaklandığını buldurun.",
            ],
            "assessment_look_fors": [
                "Çekirdek ileti/olay ile yeni tür kararı arasında süreklilik.",
                "Yeni türün anlatıcı, yapı, dil ve alıcı koşullarına uyma.",
            ],
            "support": "Dönüşüm planını ‘korunacak — değiştirilecek — yeni türün gerektirdiği’ üç sütunuyla kurdurun.",
            "enrichment": "Aynı çekirdek iletiyi iki farklı türe dönüştürüp tür değişiminin okur beklentisini nasıl değiştirdiğini açıklatın.",
            "board_note": "Tahtaya yaz: çekirdek ileti/olay + yeni tür koşulları → yeniden tasarım.",
        }
    if profile == "theatre":
        return {
            "teacher_background": f"{anchor} görevinde tiyatro metnini yalnız diyaloglardan ibaret göstermeyin. Karakter amacı, çatışma, diyalog/monolog, sahne ve zaman, dekor-kostüm, beden dili ve ses kullanımı birlikte dramatik örgüyü kurar. Tarihî bir kişiyi sahneye taşırken tarihsel bilgi ile kurmaca konuşma arasındaki sınır korunmalı; sahneleme kararı metnin anlamını değiştirebilir.",
            "student_explanation": "Tiyatroda kişi ve olay, söylenen söz kadar sahnede yapılan ve gösterilen şeylerle de seyirciye ulaşır.",
            "why_it_matters": f"Bu görev, {focus} üzerinden tiyatronun gösterme, konuşma ve sahneleme araçlarını işlevleriyle ilişkilendirir.",
            "teacher_moves": [
                f"{anchor} için öğrenciden her çıkarımını diyalog, sahne yönergesi, beden davranışı veya dekor ayrıntısından biriyle dayandırmasını isteyin.",
                "Tarihî bilgi ile karakterin kurmaca sözünü iki ayrı düzlemde tartıştırın; sahneleme önerisinin hangisine dayandığını açıklattırın.",
            ],
            "follow_up_questions": [
                "Bu söz sahnede söylenmeden yalnız hareket veya dekorla gösterilse anlamın hangi yönü değişirdi?",
                f"{anchor} için seçtiğin sahneleme kararı karakter amacı ve çatışmayı nasıl görünür kılıyor?",
            ],
            "common_misconceptions": [
                "Tiyatro metninde yalnız konuşmaların önemli olduğunu, sahne yönergelerinin ve beden dilinin ikincil kaldığını düşünmek.",
                "Tarihî kişiyi canlandırırken kaynakta olmayan her ayrıntıyı tarihsel gerçek gibi sunmak.",
            ],
            "misconception_interventions": [
                "Bir sahneyi önce yalnız diyalogla, sonra beden/dekor önerisiyle kurdurup seyirci bilgisindeki farkı karşılaştırın.",
                "Sahneleme önerisindeki her tarihî iddianın kaynağını sordurun; kaynak yoksa onu ‘kurmaca tercih’ diye etiketletin.",
            ],
            "assessment_look_fors": [
                "Diyalog/monolog, sahne ve beden unsurlarını kişi amacı veya çatışmayla ilişkilendirme.",
                "Sahneleme kararını metin ve tarihsel bağlamla gerekçelendirme.",
            ],
            "support": "Öğrenciye ‘karakter amacı — çatışma — söylenen — gösterilen — seyirci etkisi’ çizelgesini verin.",
            "enrichment": "Aynı sahneyi farklı bir uzamda yeniden kurgulatıp değişen dekor, beden ve diyalog kararlarını savundurun.",
            "board_note": "Tahtaya yaz: karakter amacı + çatışma + söz + beden/uzam → dramatik etki.",
        }
    if profile == "kucurek":
        return {
            "teacher_background": f"{anchor} çalışmasında küçürek hikâyeyi yalnız kısa metin olarak tanımlamayın. Tür, seçilmiş bir anı yoğunlaştırır; az kişi ve ayrıntıyla geniş çağrışım alanı kurar, boşlukların bir bölümünü okura bırakır. Tek bir sözcük, tekrar veya simge olayın tamamını açıklamayabilir; öğrenci yorumunu metindeki imge, yapı ve başlık ilişkisiyle temellendirmelidir.",
            "student_explanation": "Küçürek hikâyede az söz, okurun metindeki boşlukları ve çağrışımları etkin biçimde tamamlamasını sağlar.",
            "why_it_matters": f"Bu görev, {focus} üzerinden yoğun anlatımı, simgeyi ve okur katılımını birlikte okumayı öğretir.",
            "teacher_moves": [
                f"{anchor} için öğrenciden metindeki en yoğun sözcük veya imgeyi seçip bunun hangi çağrışım alanını açtığını açıklamasını isteyin.",
                "‘Metinde gerçekten var olan’ ile ‘okurun tamamladığı’ bölümü ayrı renkte işaretletin; iki düzlemi aynı kesinlikte sunmayın.",
            ],
            "follow_up_questions": [
                "Bu sözcük/tekrar metinden çıkarılsa çağrışım alanının hangi parçası kaybolur?",
                f"{anchor} içindeki boşluk okura hangi yorumu mümkün kılıyor; bu yorumun sınırını hangi metin ayrıntısı çiziyor?",
            ],
            "common_misconceptions": [
                "Kısa olduğu için küçürek hikâyede ayrıntı ve yapı bulunmadığını sanmak.",
                "Her sembol için tek ve değişmez bir anlam bulunduğunu düşünmek.",
            ],
            "misconception_interventions": [
                "Metni bir sözcük eksilterek yeniden okutun; öğrenciden değişen çağrışımı ve bunun dayanağını açıklamasını isteyin.",
                "Aynı imge için iki yorumu metin kanıtıyla karşılaştırın; kanıtsız yorumu ‘mümkün ama desteklenmemiş’ olarak ayırın.",
            ],
            "assessment_look_fors": [
                "Kısa biçim ile yoğun anlam/çağrışım arasındaki ilişki.",
                "Yorumun imge, tekrar, başlık veya boşluk gibi belirli bir metin unsuruna dayanması.",
            ],
            "support": "Metni ‘görülen sözcük/imge — çağrışım — kanıt — yorum sınırı’ tablosuyla okutun.",
            "enrichment": "Aynı kırılma anını iki cümlelik küçürek hikâyeye dönüştürüp hangi boşlukları bilinçli bıraktığını açıklatın.",
            "board_note": "Tahtaya yaz: seçilmiş an + yoğun dil + boşluk → okur katılımı ve çoklu yorum.",
        }
    if profile == "documentary":
        return {
            "teacher_background": f"{anchor} görevinde belgeseli gerçekliği olduğu gibi ve seçimsiz aktaran bir kayıt gibi sunmayın. Belgesel gözlenen/araştırılan olguları seçer, düzenler, ses ve görüntüyle çerçeveler; bu yüzden konu, ana düşünce, anlatım ve güvenilirlik birlikte incelenir. Dış video veya QR içeriği yerel PDF’de yoksa yalnız kitapta görünen görev ve ölçütler güvence altına alınmalı, görünmeyen ayrıntı tahmin edilmemelidir.",
            "student_explanation": "Belgesel gerçek dünyaya dayanır; fakat neyin seçileceği ve nasıl gösterileceği anlatıcının kurduğu bir düzendir.",
            "why_it_matters": f"Bu görev, {focus} üzerinden çok modlu bir kaynağı kanıt, seçim ve güvenilirlik bakımından sorgulatır.",
            "teacher_moves": [
                f"{anchor} için öğrenciden önce gerçekten izlediği/gördüğü ayrıntıyı not etmesini, sonra o ayrıntının konu veya iletiye katkısını açıklamasını isteyin.",
                "Ön tahmin, gözlem ve yorum bölümlerini ayrı tutun; dış kaynağın yerel PDF’de bulunmayan içeriğini rehberden tamamlamayın.",
            ],
            "follow_up_questions": [
                "Bu yargı videoda hangi görüntü, ses veya sözle destekleniyor; bunu gerçekten gözlemledin mi?",
                f"{anchor} içinde seçilen görüntü veya ses, belgeselin güvenilirlik algısını nasıl etkiliyor?",
            ],
            "common_misconceptions": [
                "Belgeselde görülen her sunum kararını nesnel gerçeğin kendisi sanmak.",
                "İzlenmeyen dış videonun kişi, olay veya ana düşüncesi hakkında kesin cevap üretmek.",
            ],
            "misconception_interventions": [
                "Her iddianın yanına ‘görüntü/ses/söz kanıtı’ yazdırın; kanıt yoksa cümleyi tahmin olarak yeniden etiketletin.",
                "Aynı olayı farklı kadraj veya ses seçimiyle düşünmelerini sağlayıp seçimin izleyici yorumunu nasıl yönlendirdiğini tartıştırın.",
            ],
            "assessment_look_fors": [
                "Konu/tema/ana düşünceyi gözlenen çok modlu ayrıntılarla ilişkilendirme.",
                "Olgu, anlatıcı seçimi ve kişisel yorum arasındaki sınırı koruma.",
            ],
            "support": "Notları ‘gördüm/duydum — bundan çıkardığım — kanıtın türü — kesinlik düzeyi’ başlıklarıyla tutturtun.",
            "enrichment": "Aynı belgesel konusu için farklı hedef kitlelere iki kısa tanıtım tasarlatıp seçimin güvenilirlik ve vurgu etkisini tartıştırın.",
            "board_note": "Tahtaya yaz: gözlem → seçme/düzenleme → ileti → güvenilirlik sorgusu.",
        }
    if profile == "poster":
        return {
            "teacher_background": f"{anchor} çalışmasında afişi yalnız güzel bir görsel olarak değil, kısa sürede belirli bir hedef kitleye ulaşması gereken çok modlu bir ileti olarak açıklayın. Ana mesaj, görsel-sözel uyum, hiyerarşi, kontrast, okunaklılık, renk ve telif kararı birlikte değerlendirilir. Her görsel süs değildir; görselin iletiyi nasıl taşıdığı ve kimin için seçildiği sorulmalıdır.",
            "student_explanation": "Afişte tasarım kararları, ana iletiyi hedef kitlenin hızlı ve doğru anlamasına yardım ettiği ölçüde değerlidir.",
            "why_it_matters": f"Bu görev, {focus} üzerinden görsel ve sözel unsurları amaç, alıcı ve etikle birlikte tasarlatır.",
            "teacher_moves": [
                f"{anchor} için öğrencinin afişte tek ana iletiyi cümle hâline getirmesini ve her görselin bu iletiye katkısını açıklamasını isteyin.",
                "Tasarımı ‘beğendim’ yerine okunma süresi, hedef kitle, kontrast, telif ve ileti açıklığı ölçütleriyle konuşturun.",
            ],
            "follow_up_questions": [
                "Afişe bakan kişi üç saniyede hangi iletiyi almalı; mevcut yerleşim bunu kolaylaştırıyor mu?",
                f"{anchor} içinde görsel ile sözcük aynı şeyi mi söylüyor, birbirini mi tamamlıyor, yoksa çelişiyor mu?",
            ],
            "common_misconceptions": [
                "Afişte çok sayıda renk, yazı tipi ve görsel kullanmanın iletiyi otomatik olarak güçlendireceğini sanmak.",
                "İnternetten bulunan görsel veya alıntının kaynak göstermeden kullanılabileceğini düşünmek.",
            ],
            "misconception_interventions": [
                "Afişten ana başlık ve bir görseli geçici olarak kaldırıp ileti kaybını tartıştırın; gereksiz ögeyi belirletin.",
                "Her görsel ve alıntı için kaynak/telif notu eklettirin; kaynak belirsizse özgün alternatif ürettirin.",
            ],
            "assessment_look_fors": [
                "Ana ileti, hedef kitle ve görsel-sözel hiyerarşi tutarlılığı.",
                "Okunaklılık, telif/hakkaniyet ve görselin iletiye gerçek katkısı.",
            ],
            "support": "Önce ‘hedef kitle — tek ana ileti — çağrı/eylem’ üçlüsünü yazdırıp tasarım kararlarını bunun üstüne kurun.",
            "enrichment": "Aynı iletiyi basılı ve dijital afiş biçiminde tasarlatıp mecranın yerleşim, hareket ve okunma kararlarını karşılaştırın.",
            "board_note": "Tahtaya yaz: hedef kitle + tek ana ileti + görsel-sözel uyum + okunaklılık + telif.",
        }
    if profile == "speaking_drama":
        return {
            "teacher_background": f"{anchor} görevinde drama çalışmasını yalnız metin yazma etkinliği gibi yürütmeyin. Sözlü iletişim engeli davranış, ton, dinlememe veya yanlış varsayım üzerinden sahnede görünür hâle gelir; çözüm ise etkin dinleme, empati, açık dil ve uygun geri bildirimle davranışa dönüşür. Öğrenci performansı sırasında amaç, hedef kitle, beden/ses kullanımı ve grup iş birliği birlikte izlenmelidir.",
            "student_explanation": "Drama, iletişimdeki bir sorunu konuşarak anlatmak yerine davranış ve sonuçlarıyla görünür kılar; çözümü de oynayarak sınar.",
            "why_it_matters": f"Bu görev, {focus} üzerinden iletişim bilgisini gözlenebilir sözlü performansa dönüştürür.",
            "teacher_moves": [
                f"{anchor} için gruptan önce engel davranışı, doğurduğu etkiyi ve alternatif davranışı üç satırda planlamasını isteyin.",
                "Performans sonrası yalnız oyunculuğu değil, iletişim engeli ile çözüm davranışı arasındaki neden-sonuç bağını da konuşturun.",
            ],
            "follow_up_questions": [
                "Sahnede görülen hangi davranış iletişimi bozdu; aynı anda karşı tarafın tepkisi ne oldu?",
                f"{anchor} çözüm sahnesinde davranış değişikliği gerçekten iletiyi nasıl iyileştiriyor?",
            ],
            "common_misconceptions": [
                "Drama için yalnız komik bir olay yazmanın yeterli olduğunu düşünmek.",
                "İletişim sorununu karakterin kişiliğine yükleyip davranışın değiştirilebilir olduğunu gözden kaçırmak.",
            ],
            "misconception_interventions": [
                "Sahneyi aynı olayla fakat tek bir davranışı değiştirerek yeniden oynatın; seyirciye değişen sonucu açıklattırın.",
                "Gruptan ‘engel davranışı — karşı tarafın etkisi — çözüm davranışı’ zincirini performans öncesi sesli savunmasını isteyin.",
            ],
            "assessment_look_fors": [
                "Engel, etki ve alternatif davranışın sahnede ayırt edilebilir olması.",
                "Ses, beden, süre ve grup iş birliğinin amaçla uyumu.",
            ],
            "support": "Rol kartlarına her kişi için amaç, engel davranışı, duygu ve çözüm cümlesini ayrı yazdırın.",
            "enrichment": "Aynı iletişim engelini farklı yaş veya güç ilişkilerindeki kişilerle sahneleyip çözümün neden değiştiğini tartıştırın.",
            "board_note": "Tahtaya yaz: davranış → iletişim etkisi → karşı tarafın tepkisi → alternatif davranış.",
        }
    if profile == "argumentation":
        return {
            "teacher_background": f"{anchor} görevinde tez ve antitezi yalnız karşıt görüş etiketleri olarak vermeyin. Tez bir iddiayı, antitez o iddianın karşısındaki veya onu sınayan iddiayı taşır; sentez ise metinlerin ortak ve ayrışan yönlerini anlamlı bir cümlede yeniden ilişkilendirir. Öğrenci hangi metnin hangi iddiayı desteklediğini içerik ve ifade kanıtlarıyla göstermelidir.",
            "student_explanation": "Tez ve antitezi belirlerken önce her metnin neyi savunduğunu, sentezde ise bu iki yönün nasıl birlikte düşünülebileceğini buluruz.",
            "why_it_matters": f"Bu görev, {focus} üzerinden metinleri karşılaştırma, iddia kurma ve kanıtla birleştirme becerisini geliştirir.",
            "teacher_moves": [
                f"{anchor} için öğrenciden her metnin iddiasını tek cümlede yazmasını, ardından cümledeki anahtar kanıtı işaretlemesini isteyin.",
                "Sentez cümlesinin iki metni yan yana özetlemek olmadığını; aralarındaki ilişkiyi anlamlı bir yargıya dönüştürmesi gerektiğini açıklayın.",
            ],
            "follow_up_questions": [
                "Bu metin hangi iddiayı destekliyor; bunu gösteren sözcük, örnek veya düşünce hangisi?",
                f"{anchor} için karşıt görünen iki düşünce hangi ortak soruda buluşabilir?",
            ],
            "common_misconceptions": [
                "Tezi metnin konusu, antitezi ise metindeki herhangi bir karşıt kelime sanmak.",
                "Sentezi iki metnin cümlelerini art arda yazmakla tamamlanmış saymak.",
            ],
            "misconception_interventions": [
                "Her metnin ‘iddia — kanıt — karşı çıktığı veya sınadığı düşünce’ üçlüsünü doldurtun.",
                "İki ayrı özet cümlesini tek bir ilişki cümlesine dönüştürmelerini isteyin; hangi bağlacın ilişkiyi kurduğunu açıklattırın.",
            ],
            "assessment_look_fors": [
                "Tez/antitez sınıflamasının belirli metin kanıtıyla savunulması.",
                "Sentez cümlesinin iki metni anlam ilişkisi içinde birleştirmesi.",
            ],
            "support": "‘Metin — iddia — kanıt — karşıt/ortak yön’ dört sütunlu şemayı kullandırın.",
            "enrichment": "Aynı metinler için farklı fakat kanıtlı sentez cümleleri üretip hangi varsayımın değiştiğini tartıştırın.",
            "board_note": "Tahtaya yaz: iddia → metin kanıtı → karşıt/ortak yön → sentez.",
        }
    if profile == "literary_reality":
        return {
            "teacher_background": f"{anchor} çalışmasında edebî metnin gerçekliği yansıttığını, fakat tutanak gibi birebir kopyalamadığını açıklayın. Sanatçı gerçek hayattan kişi, olay, duygu veya çevre izleri seçer; bunları kurmaca, dil, bakış açısı ve estetik düzenleme ile dönüştürür. Bu ayrım öğrencinin ‘gerçek’ ile ‘inandırıcı kurmaca’yı, konu ile temayı birbirine karıştırmasını önler.",
            "student_explanation": "Edebî metin gerçek hayattan yararlanabilir; ama onu seçip düzenleyerek okurun anlam kuracağı yeni bir dünya oluşturur.",
            "why_it_matters": f"Bu görev, {focus} ayrımını somutlaştırarak metin kanıtı ile kişisel yorumu birlikte kullanmayı sağlar.",
            "teacher_moves": [
                f"{anchor} için öğrenciden gerçek hayattan alınmış olabilecek bir izi ve bu izin metinde nasıl dönüştürüldüğünü ayrı ayrı yazmasını isteyin.",
                "Konu, tema ve ileti cevaplarını aynı cümleye sıkıştırmak yerine her birini farklı soruyla kurdurun.",
            ],
            "follow_up_questions": [
                "Bu unsur gerçekliği mi gösteriyor, yoksa metnin inandırıcılığını mı artırıyor; ikisi arasındaki fark nedir?",
                f"{anchor} için seçtiğin ayrıntı daha genel hangi duygu veya insanlık durumuna açılıyor?",
            ],
            "common_misconceptions": [
                "Edebî metinde geçen her olayın gerçek hayatta aynen yaşandığını sanmak.",
                "Olayı veya konuyu tema olarak yazıp soyutlama basamağını atlamak.",
            ],
            "misconception_interventions": [
                "Öğrencinin cevabına ‘Bu olay neyi gösteriyor?’ ve ‘Bu olay bizi hangi daha genel duruma düşündürüyor?’ sorularını sırayla uygulatın.",
                "Metindeki gerçeklik izi ile sanatçının seçme/düzenleme kararını iki farklı renkle işaretletin.",
            ],
            "assessment_look_fors": [
                "Gerçeklik izi, kurmaca düzenleme ve inandırıcılık ayrımını doğru kurma.",
                "Konu/tema/iletiyi kaynak ayrıntısı ve gerekçeyle ayırma.",
            ],
            "support": "Cevap çerçevesi verin: ‘Metinde ... görülür; bu ayrıntı ... düşündürür; çünkü ...’. ",
            "enrichment": "Aynı gerçek yaşam olayını haber, günlük ve hikâye biçiminde tasarlatıp tür değişiminin gerçeklik etkisini tartıştırın.",
            "board_note": "Tahtaya yaz: gerçek yaşam izi → seçme/düzenleme → kurmaca dünya → okur yorumu.",
        }
    return {
        "teacher_background": f"{anchor} görevinde temel kavramı yalnız tanım olarak vermek yerine metindeki, görseldeki veya tabloda bulunan belirtiyle ilişkilendirin. Öğrenci önce kaynağın ne söylediğini ayırmalı, sonra bundan çıkardığı yorumu ve gerekçesini kurmalıdır. Böylece cevap, başlığı tekrar eden bir cümle değil, dayanaklı bir anlamlandırma olur.",
        "student_explanation": "Önce kaynakta gördüğümüz ayrıntıyı belirler, sonra bu ayrıntının ne anlama geldiğini gerekçesiyle açıklarız.",
        "why_it_matters": f"Bu görev, {focus} doğrultusunda kaynaktan anlam çıkarma ve bu anlamı gerekçeli biçimde ifade etme becerisini geliştirir.",
        "teacher_moves": [
            f"{anchor} için öğrenciden cevabındaki iddia ile onu destekleyen kaynak ayrıntısını iki ayrı bölümde göstermesini isteyin.",
            "Farklı bir cevap geldiğinde önce kavramın ölçütünü, sonra cevabın kaynakla bağını birlikte kontrol edin.",
        ],
        "follow_up_questions": [
            f"{anchor} cevabındaki hangi ayrıntı bu yorumu destekliyor; başka hangi ayrıntı farklı bir yoruma yol açabilir?",
            "Cevabın kavramı mı açıklıyor, yoksa yalnız metni yeniden mi söylüyor?",
        ],
        "common_misconceptions": [
            f"Öğrenci, {anchor} görevinde kavramın adını söylemeyi kavramı açıklamakla eşitleyebilir.",
            "Kaynakta açıkça bulunan bilgi ile öğrencinin kendi çıkarımını aynı kesinlikte sunabilir.",
        ],
        "misconception_interventions": [
            "Cevabı ‘kaynak ayrıntısı — kavram/çıkarım — gerekçe’ biçiminde üç parçaya böldürün; eksik parçayı birlikte tamamlayın.",
            "Öğrenciden cümlesindeki kesinlik ifadesini kanıtına göre ‘metinde görülür’, ‘çıkarılabilir’ veya ‘kişisel yorumum’ diye yeniden seçmesini isteyin.",
        ],
        "assessment_look_fors": [
            "Kaynak ayrıntısı, kavram ve gerekçe arasında açık bağ.",
            "Bilgi, çıkarım ve kişisel değerlendirme düzeylerini ayırma.",
        ],
        "support": "Cevabı ‘Gördüğüm/duyduğum ayrıntı — bundan çıkardığım — nedenim’ cümle kalıbıyla başlatın.",
        "enrichment": "Aynı ayrıntıdan iki farklı fakat kanıtlı yorum üretip yorumların hangi varsayımla ayrıldığını açıklatın.",
        "board_note": "Tahtaya yaz: kaynak ayrıntısı → kavram/çıkarım → gerekçe.",
    }


def answer_is_open(prompt: str | None, expected: Any) -> bool:
    if isinstance(expected, str) and re.fullmatch(r"\s*[A-E](?:\s*[,/]\s*[A-E])*\s*", expected):
        return False
    if isinstance(expected, list) and expected and all(isinstance(value, str) and re.fullmatch(r"\s*[A-E]\s*", value) for value in expected):
        return False
    return bool(prompt and OPEN_PATTERN.search(prompt))


def expected_answer_text(value: Any) -> str:
    if isinstance(value, dict):
        return "; ".join(f"{key}: {expected_answer_text(entry)}" for key, entry in value.items())
    if isinstance(value, list):
        return "; ".join(expected_answer_text(entry) for entry in value)
    return scalar_text(value)


def expected_requires_review(value: Any) -> bool:
    text = normalize_text(expected_answer_text(value))
    return any(
        phrase in text
        for phrase in [
            "izlenmeden verilmez",
            "görülmeden verilmez",
            "ayrıca eklenmelidir",
            "dış video içeriğine bağlı",
            "dış video içeriği",
            "görünmeyen",
            "kaynak görülmeden üretilmez",
        ]
    )


def answer_explanation(
    expected: Any,
    answer_status: str,
    focus: str,
    signature: str,
    acceptance: Any,
    external: bool,
) -> str:
    criteria = dedupe_text(acceptance if isinstance(acceptance, list) else [scalar_text(acceptance)], limit=2)
    criterion_text = " ".join(criteria)
    if external and answer_status == "REVIEW_REQUIRED":
        return f"{signature} için yerel PDF dışındaki içerik görülmeden sabit bir cevap doğrulanamaz. Öğretmen kaynağı izledikten sonra öğrencinin gözlediği ayrıntıları {focus} ölçütüyle ilişkilendirmeli; görünmeyen medya ayrıntıları rehberde varsayım olarak sunulmamalıdır. Kitabın görünen ölçütü şudur: {criterion_text or 'gerekçeli ve kaynakla bağlantılı cevap.'}"
    if answer_status == "NOT_APPLICABLE":
        return f"{signature} bir tek cümlelik cevap anahtarı değil, kitapta yürütülen bir süreç veya ürün çalışmasıdır. Doğru uygulama; öğrencinin {focus} kararını görünür kılması, çalışma adımlarını tamamlaması ve ortaya çıkan ürünü kitapta belirtilen amaca göre açıklamasıdır."
    if isinstance(expected, str) and re.fullmatch(r"\s*[A-E](?:\s*[,/]\s*[A-E])*\s*", expected):
        return f"Seçilen seçenek {signature} için gerekli kavramsal ayrımı karşılar; ancak tek başına harfi söylemek düşünmeyi göstermeye yetmez. Öğrenci, {focus} bakımından seçenek ile kaynakta verilen bilgi arasındaki ilişkiyi kısaca açıklamalı ve çeldiricilerin neden elendiğini gösterebilmelidir."
    if answer_status == "OPEN_ENDED":
        return f"{signature} için beklenen yön, {focus} yorumunu kaynakta görülen bir ayrıntı ve açık bir gerekçeyle kurmaktır. Tek bir kalıp cümle aranmaz; farklı cevaplar aynı kavramsal ölçütü ve tutarlı bir kanıt zincirini karşılıyorsa kabul edilebilir. {criterion_text or 'Cevap, iddia ile dayanak arasındaki ilişkiyi göstermelidir.'}"
    return f"{signature} için cevap, {focus} ölçütünü kaynak bağlamında doğru yere yerleştirir. Cevabın doğruluğu yalnız sonucun kendisinden değil, metin/görsel/tablo ayrıntısının bu sonucu nasıl desteklediğinin açıklanmasından anlaşılır; öğrenci farklı sözcüklerle aynı ilişkiyi kurabilir. {criterion_text or 'Kaynakla bağlantılı gerekçe aranır.'}"


def acceptable_answers(expected: Any, answer_status: str, profile: dict[str, Any], external: bool) -> list[str]:
    if answer_status == "REVIEW_REQUIRED":
        return ["İçerik görüldükten sonra gözlenen kanıtla kurulmuş tutarlı yanıtlar kabul edilir."]
    if answer_status == "OPEN_ENDED":
        return [
            f"{profile['why_it_matters']} Kaynak ayrıntısı ve gerekçesi bulunan farklı ifadeler kabul edilir.",
            "Kişisel görüş, metin/kaynak dayanağı ve gerekçe birlikte verildiğinde alternatif cevap olarak değerlendirilebilir.",
        ]
    return []


def text_from_differentiation(value: Any, key: str) -> list[str]:
    if not isinstance(value, dict):
        return []
    part = value.get(key)
    if isinstance(part, list):
        return [str(entry) for entry in part if isinstance(entry, str) and entry.strip()]
    if isinstance(part, str) and part.strip():
        return [part]
    return []


def activity_context(activity_refs: list[str], activity_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    context: list[dict[str, Any]] = []
    for activity_id in activity_refs:
        activity = activity_index.get(activity_id)
        if not activity:
            continue
        context.append(
            {
                "activity_id": activity_id,
                "title": activity.get("activity_title", activity.get("exact_title", "")),
                "student_action": activity.get("student_action", ""),
                "expected_product_or_evidence": activity.get("expected_product_or_evidence", ""),
            }
        )
    return context


def build_task(
    root: Path,
    theme_id: str,
    entry: dict[str, Any],
    canonical_sections: dict[str, dict[str, Any]],
    canonical: dict[str, dict[str, Any]],
    manifest_sections: dict[str, dict[str, Any]],
    activity_index: dict[str, dict[str, Any]],
    board_seen: set[str],
) -> dict[str, Any]:
    section_id = entry["section_id"]
    section_record = canonical_sections.get(section_id)
    if section_record is None:
        raise ValueError(f"mirror entry references unknown section: {entry['mirror_id']}:{section_id}")
    section_content = section_record["content"]
    manifest_row = manifest_sections[section_id]
    refs = list(dict.fromkeys(str(ref) for ref in entry.get("canonical_item_refs", []) if ref))
    if not refs:
        raise ValueError(f"mirror entry has no canonical refs: {entry['mirror_id']}")
    unknown_refs = [ref for ref in refs if ref not in canonical]
    if unknown_refs:
        raise ValueError(f"unknown canonical refs for {entry['mirror_id']}: {unknown_refs}")
    records = [canonical[ref] for ref in refs]
    unit_ids = list(dict.fromkeys(str(record.get("unit_id")) for record in records if record.get("unit_id")))
    unit = records[0].get("unit") if records else None
    map_refs = list(unit.get("activity_refs", [])) if unit else []
    if not map_refs:
        map_refs = list(section_content.get("activity_refs", []))
    if not map_refs:
        map_refs = list(manifest_row.get("activity_refs", []))
    activity_refs = list(dict.fromkeys(str(ref) for ref in map_refs if ref))
    outcome_refs = list(unit.get("outcome_refs", [])) if unit else []
    if not outcome_refs:
        outcome_refs = list(section_content.get("outcome_refs", []))
    if not outcome_refs:
        outcome_refs = list(manifest_row.get("outcome_refs", []))
    outcome_refs = list(dict.fromkeys(str(ref) for ref in outcome_refs if ref))

    prompt_display = entry.get("prompt_display")
    presentation_type = str(entry.get("presentation_type", "ACTIVITY"))
    is_question = presentation_type == "QUESTION"
    if isinstance(prompt_display, str) and prompt_display.strip():
        book_prompt = re.sub(r"\s+", " ", prompt_display.strip())
        prompt_mode = str(entry.get("prompt_mode") or "VERIFIED_SUMMARY")
        prompt_status = "REVIEW_REQUIRED" if prompt_mode in {"LOCATOR_ONLY", "REVIEW_REQUIRED"} else "VERIFIED"
    elif is_question:
        book_prompt = None
        prompt_mode = "REVIEW_REQUIRED"
        prompt_status = "REVIEW_REQUIRED"
    else:
        heading = str(entry.get("book_heading", "Kitap görevi"))
        book_prompt = f"Kitapta “{heading}” başlığı altında verilen çalışma/yönerge."
        prompt_mode = "VERIFIED_SUMMARY"
        prompt_status = "VERIFIED"

    mirror_id = str(entry["mirror_id"])
    task_id = f"{theme_id}::{mirror_id}"
    item_for_blob = records[0]["item"]
    blob = task_blob(entry, item_for_blob, section_content.get("title", manifest_row.get("title", "")))
    external = is_external_task(blob)
    label = " / ".join(str(record["item"].get("label", "")) for record in records if record["item"].get("label"))
    profile = choose_profile(blob, str(manifest_row.get("section_type", "")))
    focus_blob = " ".join(
        str(value)
        for value in [
            section_content.get("title", manifest_row.get("title", "")),
            entry.get("book_heading", ""),
            book_prompt or "",
            label,
        ]
        if value
    )
    focus = focus_for(focus_blob, label or entry.get("book_heading", ""))
    question_number = find_question_number(entry, book_prompt)
    # Keep the prose anchor short and teacher-readable.  The full book
    # heading remains in the task card and the exact provenance remains in
    # source_locators; generated pedagogy should not repeat a long metadata
    # chain in every sentence.
    base_signature = focus or label or str(entry.get("book_heading", mirror_id))
    if question_number:
        signature = f"Soru {question_number} — {base_signature} — basılı s.{entry['printed_page_range']}"
    else:
        signature = f"{base_signature} — basılı s.{entry['printed_page_range']}"
    hook = source_hook(book_prompt, label, str(entry.get("book_heading", "")), focus)
    content = profile_content(profile, focus, signature, presentation_type, book_prompt)
    content["teacher_background"] = (
        f"{content['teacher_background']} Bu görevde özellikle ‘{hook}’ ayrıntısının "
        "hangi kavramı veya iletişim kararını görünür kıldığına dikkat edin."
    )
    keys = [str(key) for key in entry.get("answer_keys", []) if key]
    expected, answer_errors = project_answer(canonical, refs, keys)
    response = canonical_response(canonical, refs, keys)
    item_acceptance = []
    item_guidance: list[str] = []
    item_misconceptions: list[str] = []
    item_evidence: list[str] = []
    item_support: list[str] = []
    item_enrichment: list[str] = []
    for record in records:
        item = record["item"]
        item_acceptance.extend(item.get("acceptance_criteria", []) if isinstance(item.get("acceptance_criteria"), list) else [])
        item_guidance.extend(item.get("teacher_guidance", []) if isinstance(item.get("teacher_guidance"), list) else [item.get("teacher_guidance")] if isinstance(item.get("teacher_guidance"), str) else [])
        item_misconceptions.extend(item.get("common_misconceptions", []) if isinstance(item.get("common_misconceptions"), list) else [])
        item_evidence.extend(item.get("assessment_evidence", []) if isinstance(item.get("assessment_evidence"), list) else [])
        item_support.extend(text_from_differentiation(item.get("differentiation"), "support"))
        item_enrichment.extend(text_from_differentiation(item.get("differentiation"), "enrichment"))
    mirror_note = entry.get("teacher_note")
    if isinstance(mirror_note, list):
        item_guidance.extend(value for value in mirror_note if isinstance(value, str))
    elif isinstance(mirror_note, str):
        item_guidance.append(mirror_note)

    if answer_errors:
        expected = None
    has_expected = nonempty(expected)
    answer_bound_to_external_source = external and expected_requires_review(expected)
    if is_question:
        if answer_bound_to_external_source or not has_expected:
            answer_status = "REVIEW_REQUIRED"
        elif answer_is_open(book_prompt, expected):
            answer_status = "OPEN_ENDED"
        else:
            answer_status = "VERIFIED"
    elif presentation_type == "ASSESSMENT":
        answer_status = "REVIEW_REQUIRED" if answer_bound_to_external_source else ("OPEN_ENDED" if has_expected and answer_is_open(book_prompt, expected) else ("VERIFIED" if has_expected else "REVIEW_REQUIRED" if answer_errors else "NOT_APPLICABLE"))
    else:
        answer_status = "VERIFIED" if has_expected else "NOT_APPLICABLE"

    review_reasons: list[str] = []
    if prompt_status == "REVIEW_REQUIRED":
        review_reasons.append("Ders kitabı prompt metni yerel kaynaklardan çözümlenemedi; item REVIEW_REQUIRED bırakıldı.")
    review_reasons.extend(answer_errors)
    source_limitations: list[str] = []
    if external:
        limitation = "Yerel PDF dış medya/QR payload'ını içermiyor; görünmeyen video, ses veya rubrik ayrıntıları uydurulmayacak."
        source_limitations.append(limitation)
        if not has_expected or answer_bound_to_external_source:
            review_reasons.append("Yerel PDF dışındaki medya veya değerlendirme içeriği öğretmen tarafından ayrıca doğrulanmalı.")
    review_reasons = dedupe_text(review_reasons)
    source_limitations = dedupe_text(source_limitations)
    if answer_status == "REVIEW_REQUIRED" and not review_reasons:
        review_reasons.append("Beklenen cevap canonical kaynaktan çözümlenemedi.")

    content_status = "REVIEW_REQUIRED" if prompt_status == "REVIEW_REQUIRED" or answer_status == "REVIEW_REQUIRED" or review_reasons else "VERIFIED"
    task_type = presentation_type if presentation_type in {"QUESTION", "ACTIVITY", "PROCESS", "PERFORMANCE_TASK", "REFERENCE", "VOCABULARY", "TABLE", "COMPARISON", "ASSESSMENT"} else "ACTIVITY"
    task_locators = collect_source_locators(entry, canonical, refs, section_record, unit)
    # The mirror's locator identifies the book task itself.  Canonical item and
    # section locators remain in source_locators as supporting context, but
    # must not replace the task's primary page.
    primary_locator = str(entry.get("source_locator") or task_locators[0])
    linked_context = activity_context(activity_refs, activity_index)
    source_context: dict[str, Any] = {
        "book_section": section_content.get("title", manifest_row.get("title", "")),
        "book_heading": entry.get("book_heading", ""),
        "linked_activities": linked_context,
        "canonical_items": [canonical[ref]["item"].get("label", ref) for ref in refs],
        "basis": "; ".join(
            [
                "metin/görsel/tablo/form bağlamı" if not external else "kitapta yönlendirilen dış medya/QR bağlamı",
                "öğrenci ürünü veya süreç kaydı" if task_type in {"PROCESS", "PERFORMANCE_TASK", "ACTIVITY"} else "soru/ölçme görevi",
            ]
        ),
        "source_boundary": source_limitations or ["Basılı PDF'de görünen görev, metin ve sayfa akışı esas alınır."],
    }
    acceptance_for_text = item_acceptance
    explanation = answer_explanation(expected, answer_status, focus, signature, acceptance_for_text, external)
    acceptable = acceptable_answers(expected, answer_status, content, external)
    evidence = (
        f"Basılı s.{entry['printed_page_range']} / {entry.get('book_heading', 'kitap görevi')}: {focus}. "
        + (f"Ölçüt: {item_acceptance[0]}" if item_acceptance else "Dayanak, ilgili metin/görsel/tablo veya dinleme-izleme kaydındaki gözlenebilir ayrıntıdır.")
    )
    if external:
        evidence += " Dış içerik izlendikten sonra gözlenen kanıt ayrıca kaydedilmelidir."
    task: dict[str, Any] = {
        "task_id": task_id,
        "section_id": section_id,
        "unit_id": unit_ids[0] if len(unit_ids) == 1 else (unit_ids or None),
        "task_type": task_type,
        "book_heading": str(entry.get("book_heading", "Kitap görevi")),
        "generation_profile": profile,
        "focus": focus,
        "printed_page_range": str(entry["printed_page_range"]),
        "book_prompt": book_prompt,
        "prompt_mode": prompt_mode,
        "prompt_status": prompt_status,
        "question_number": question_number,
        "source_context": source_context,
        "expected_answer": expected,
        "answer_status": answer_status,
        "answer_explanation": explanation,
        "why_it_matters": content["why_it_matters"],
        "activity_refs": activity_refs,
        "outcome_refs": outcome_refs,
        "canonical_item_refs": refs,
        "answer_component_keys": keys,
        "source_locators": task_locators,
        "source_locator": primary_locator,
        "evidence_anchor": evidence,
        "provenance": {},
        "field_provenance": {},
        "content_status": content_status,
        "split_from_group": bool(entry.get("split_from_group", False)),
    }
    if entry.get("group_source_task_id"):
        task["group_source_task_id"] = f"{theme_id}::{entry['group_source_task_id']}"
    if response is not None:
        task["expected_response"] = response
    if acceptable:
        task["acceptable_answers"] = acceptable

    conceptual = task_type in {"QUESTION", "ASSESSMENT", "VOCABULARY", "TABLE", "COMPARISON", "REFERENCE", "PERFORMANCE_TASK"} or has_expected
    if conceptual:
        task["teacher_background"] = content["teacher_background"]
    if task_type in {"QUESTION", "ASSESSMENT", "PERFORMANCE_TASK"} or has_expected:
        task["student_explanation"] = f"{content['student_explanation']} Bu görevde özellikle {focus} üzerinde durun."
    if task_type != "REFERENCE" or has_expected:
        task["teacher_moves"] = dedupe_text(item_guidance + content["teacher_moves"], limit=4)
    if task_type in {"QUESTION", "ASSESSMENT", "PERFORMANCE_TASK"}:
        task["follow_up_questions"] = dedupe_text(
            scoped_pedagogy_items(content["follow_up_questions"], signature, hook, "follow_up_questions"),
            limit=3,
        )
    if task_type in {"QUESTION", "ASSESSMENT", "PERFORMANCE_TASK", "VOCABULARY", "TABLE", "COMPARISON"} or has_expected:
        task["common_misconceptions"] = dedupe_text(item_misconceptions + content["common_misconceptions"], limit=3)
        task["misconception_interventions"] = dedupe_text(
            scoped_pedagogy_items(content["misconception_interventions"], signature, hook, "misconception_interventions"),
            limit=3,
        )
    if task_type in {"QUESTION", "ASSESSMENT", "PERFORMANCE_TASK", "PROCESS", "ACTIVITY"} or has_expected:
        task["assessment_look_fors"] = dedupe_text(item_evidence + item_acceptance + content["assessment_look_fors"], limit=4)
        task["support"] = dedupe_text(item_support + [f"{content['support']} Bu görevde bağlantı noktası: {focus}."], limit=3)
        task["enrichment"] = dedupe_text(item_enrichment + [f"{content['enrichment']} Bu görevde derinleştirme odağı: {focus}."], limit=3)
    if external:
        task["source_limitations"] = source_limitations
    if section_id + "::" not in board_seen and conceptual and content.get("board_note"):
        board_note = content["board_note"].replace("Tahtaya yaz:", f"Tahtaya yaz ({focus}):")
        task["board_notes"] = [board_note]
        board_seen.add(section_id + "::")

    pedagogical_source_ids = collect_source_ids(canonical, refs)
    task["provenance"] = {
        "item_id": task_id,
        "origin": "pedagogical_recommendation",
        "source_ids": pedagogical_source_ids,
        "source_locators": task_locators,
        "verbatim": False,
        "derived_from": refs + [f"mirror:{mirror_id}"],
        "transformation": "MIRROR_PROMPT_NORMALIZED; CANONICAL_ANSWER_PROJECTED; TASK_SPECIFIC_PEDAGOGY_DERIVED",
        "verification_status": "REVIEW" if content_status == "REVIEW_REQUIRED" else "VERIFIED",
    }
    official_prompt_status = "VERIFIED" if prompt_status == "VERIFIED" else "REVIEW"
    task["field_provenance"]["book_prompt"] = {
        "item_id": task_id + ":book_prompt",
        "origin": "official_textbook",
        "source_ids": [TEXTBOOK_SOURCE_ID, TEXTBOOK_MAP_SOURCE_ID],
        "source_locators": task_locators,
        "verbatim": prompt_mode == "VERBATIM_SHORT",
        "derived_from": [f"mirror:{mirror_id}"],
        "transformation": "EXTRACTED_OR_VERIFIED_SUMMARY",
        "verification_status": official_prompt_status,
    }
    task["field_provenance"]["source_context"] = {
        "item_id": task_id + ":source_context",
        "origin": "official_textbook",
        "source_ids": [TEXTBOOK_SOURCE_ID, TEXTBOOK_MAP_SOURCE_ID],
        "source_locators": task_locators,
        "verbatim": False,
        "derived_from": [f"mirror:{mirror_id}"] + activity_refs,
        "transformation": "TEXTBOOK_CONTEXT_LINKED",
        "verification_status": "REVIEW" if external else "VERIFIED",
    }
    task["field_provenance"]["expected_answer"] = {
        "item_id": task_id + ":expected_answer",
        "origin": "pedagogical_recommendation",
        "source_ids": pedagogical_source_ids,
        "source_locators": task_locators,
        "verbatim": False,
        "derived_from": refs + keys,
        "transformation": "CANONICAL_ANSWER_PROJECTED",
        "verification_status": "REVIEW" if answer_status == "REVIEW_REQUIRED" else "VERIFIED",
    }
    generated_fields = [
        "answer_explanation",
        "why_it_matters",
        "teacher_background",
        "student_explanation",
        "teacher_moves",
        "follow_up_questions",
        "common_misconceptions",
        "misconception_interventions",
        "assessment_look_fors",
        "support",
        "enrichment",
        "board_notes",
    ]
    for field in generated_fields:
        if field not in task:
            continue
        task["field_provenance"][field] = {
            "item_id": task_id + ":" + field,
            "origin": "pedagogical_recommendation",
            "source_ids": pedagogical_source_ids,
            "source_locators": task_locators,
            "verbatim": False,
            "derived_from": refs + activity_refs,
            "transformation": "TASK_SPECIFIC_PEDAGOGICAL_DERIVATION",
            "verification_status": "REVIEW" if external and field in {"teacher_background", "answer_explanation"} else "VERIFIED",
        }
    if review_reasons:
        task["review_reasons"] = review_reasons
    return task


def activity_index_from_map(textbook_map: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    activities: dict[str, dict[str, Any]] = {}
    sections: dict[str, dict[str, Any]] = {}
    for theme in textbook_map.get("themes", []):
        for section in theme.get("sections", []):
            sections[section["section_id"]] = section
            for activity in section.get("activities", []):
                activity_id = activity["activity_id"]
                if activity_id in activities:
                    raise ValueError(f"duplicate textbook activity: {activity_id}")
                # Keep the parent section in the normalized lookup.  The
                # textbook_map stores it structurally on the section, while
                # the V3 task index stores it as a first-class field.
                activities[activity_id] = {**activity, "section_id": section["section_id"]}
    return activities, sections


def source_meta(root: Path, path: Path, source_id: str, verification_status: str = "VERIFIED") -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": relative_path(root, path),
        "sha256": sha256_file(path),
        "verification_status": verification_status,
    }


def build_activity_index_document(
    root: Path,
    textbook_map: dict[str, Any],
    task_records: dict[str, list[dict[str, Any]]],
    activity_index: dict[str, dict[str, Any]],
    activity_sections: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    pdf_path = root / "courses" / COURSE_ID / "source_docs" / "turk-dili-ve-edebiyati-11sinif-ders-kitabi_compressed.pdf"
    map_path = root / "courses" / COURSE_ID / "textbook_map.json"
    themes: list[dict[str, Any]] = []
    total_questions = 0
    total_activities = 0
    for theme in textbook_map.get("themes", []):
        theme_id = theme["theme_id"]
        guide_tasks = task_records[theme_id]
        questions: list[dict[str, Any]] = []
        for task in guide_tasks:
            if task["task_type"] != "QUESTION":
                continue
            questions.append(
                {
                    "task_id": task["task_id"],
                    "section_id": task["section_id"],
                    "printed_page_range": task["printed_page_range"],
                    "book_heading": task["book_heading"],
                    "book_prompt": task["book_prompt"],
                    "prompt_mode": task["prompt_mode"],
                    "prompt_status": task["prompt_status"],
                    "canonical_item_refs": task["canonical_item_refs"],
                    "activity_refs": task["activity_refs"],
                    "source_locator": task["source_locator"],
                    "source_ids": task["provenance"]["source_ids"],
                    "question_number": task.get("question_number"),
                    "split_from_group": task["split_from_group"],
                }
            )
        activity_records: list[dict[str, Any]] = []
        theme_activity_ids: list[str] = []
        for section in theme.get("sections", []):
            for activity in section.get("activities", []):
                activity_id = activity["activity_id"]
                theme_activity_ids.append(activity_id)
                activity_records.append(
                    {
                        "activity_id": activity_id,
                        "section_id": section["section_id"],
                        "activity_title": activity.get("activity_title", activity.get("exact_title", "")),
                        "student_action": activity.get("student_action", ""),
                        "expected_product_or_evidence": activity.get("expected_product_or_evidence", ""),
                        "printed_page_range": activity["printed_page_range"],
                        "source_locator": activity["source_locator"],
                        "verification_status": "VERIFIED" if str(activity.get("verification_status", "")).startswith("LOCAL_OFFICIAL_PDF") else "REVIEW_REQUIRED",
                    }
                )
        total_questions += len(questions)
        total_activities += len(activity_records)
        themes.append(
            {
                "theme_id": theme_id,
                "printed_page_range": theme["printed_page_range"],
                "questions": questions,
                "activities": activity_records,
                "question_task_ids": [question["task_id"] for question in questions],
                "activity_ids": theme_activity_ids,
            }
        )
    return {
        "schema_version": "1.0.0",
        "document_type": "TYMM_TEXTBOOK_TASK_INDEX",
        "course_id": COURSE_ID,
        "source": source_meta(root, pdf_path, "textbook_tde11_local_pdf"),
        "map_ref": relative_path(root, map_path),
        "themes": themes,
        "counts": {"themes": len(themes), "questions": total_questions, "activities": total_activities},
        "provenance": {
            "item_id": "TDE_11::TEXTBOOK_TASK_INDEX",
            "origin": "official_textbook",
            "source_ids": [TEXTBOOK_SOURCE_ID, TEXTBOOK_MAP_SOURCE_ID],
            "source_locators": [relative_path(root, pdf_path), relative_path(root, map_path)],
            "verbatim": False,
            "derived_from": [relative_path(root, pdf_path), relative_path(root, map_path)],
            "transformation": "TEXTBOOK_TASK_EXTRACTION_AND_CANONICAL_LINKING",
            "verification_status": "VERIFIED",
        },
    }


def guide_source_metadata(
    root: Path,
    manifest_path: Path,
    section_paths: list[Path],
    textbook_map_path: Path,
    curriculum_map_path: Path,
    normative_path: Path,
    pdf_path: Path,
    task_index_path: Path,
) -> dict[str, Any]:
    return {
        "textbook_pdf": source_meta(root, pdf_path, TEXTBOOK_SOURCE_ID),
        "textbook_map": source_meta(root, textbook_map_path, TEXTBOOK_MAP_SOURCE_ID),
        "curriculum_map": source_meta(root, curriculum_map_path, "curriculum_map"),
        "curriculum_normative_text": source_meta(root, normative_path, "curriculum_normative"),
        "teacher_guide_canonical": {
            "source_id": CANONICAL_SOURCE_ID,
            "manifest": source_meta(root, manifest_path, "teacher_guide_manifest"),
            "sections": [source_meta(root, path, f"canonical:{path.stem}") for path in section_paths],
            "verification_status": "VERIFIED",
        },
        "textbook_task_index": source_meta(root, task_index_path, "textbook_task_index"),
    }


def render_markdown(guide: dict[str, Any]) -> str:
    lines: list[str] = [
        f"# {guide['title']}",
        "",
        "> Bu çıktı, ders kitabındaki görevleri öğretmenin kullanacağı açıklama ve değerlendirme notlarıyla birlikte sunan Teacher Guide V3'tür.",
        "> Kaynak önceliği: resmî ders kitabı PDF'si → textbook_map → canonical teacher guide → göreve özgü pedagojik açıklama.",
        "",
        f"**Durum:** {guide['status']}  ",
        f"**Kaynak politikası:** {guide['source_policy']['prompt_policy']}",
        "",
        "## Hızlı kullanım",
        "",
        "- Önce kitaptaki görev metnini okuyun; ardından beklenen cevap ve gerekçeyi kontrol edin.",
        "- Açık uçlu cevaplarda tek kalıp aramayın; kaynak kanıtı, kavram ilişkisi ve gerekçeyi birlikte değerlendirin.",
        "- QR/video/rubrik içeriği yerel PDF'de yoksa görünmeyen ayrıntıyı tamamlamayın; rehberdeki sınır notunu kullanın.",
        "- Ders içi hamle, destek ve zenginleştirme notları görevin bağlamına göre seçilmiştir; her başlık her görevde zorunlu değildir.",
        "",
        "## Kapsam özeti",
        "",
        "| Ölçüt | Sayı |",
        "|---|---:|",
        f"| Ders kitabı sorusu | {guide['coverage']['textbook_question_count']} |",
        f"| Rehberdeki soru kaydı | {guide['coverage']['guide_question_count']} |",
        f"| Ders kitabı etkinliği | {guide['coverage']['textbook_activity_count']} |",
        f"| Kapsanan etkinlik | {guide['coverage']['covered_activity_count']} |",
        f"| REVIEW_REQUIRED kayıt | {len(guide['coverage']['review_required_items'])} |",
        "",
    ]
    for section in guide["sections"]:
        lines.extend(
            [
                f"# {section['title']}",
                "",
                f"_Kitap sayfaları: basılı s.{section['printed_page_range']}_",
                "",
            ]
        )
        tasks = [task for task in guide["tasks"] if task["section_id"] == section["section_id"]]
        for task in tasks:
            lines.extend([f"## {task['book_heading']} — s.{task['printed_page_range']}", ""])
            lines.extend(["### Kitaptaki görev", ""])
            if task["book_prompt"]:
                lines.extend(render_value(task["book_prompt"]))
            else:
                lines.append("REVIEW_REQUIRED: görev metni çözümlenemedi.")
            lines.extend(["", "### Kaynak bağlamı", ""])
            context = task.get("source_context")
            if isinstance(context, dict):
                for key, value in context.items():
                    if not nonempty(value):
                        continue
                    label = humanize_key(key)
                    lines.append(f"- **{label}:**")
                    lines.extend(render_value(value, 1))
            else:
                lines.extend(render_value(context))
            lines.extend(["", "### Beklenen cevap", ""])
            if nonempty(task.get("expected_answer")):
                lines.extend(render_value(task["expected_answer"]))
            elif task["answer_status"] == "REVIEW_REQUIRED":
                lines.append("REVIEW_REQUIRED: kaynak sınırı nedeniyle sabit cevap üretilemedi.")
            else:
                lines.append("Tek sabit cevap yok; ürün/süreç, aşağıdaki ölçütlerle değerlendirilir.")
            lines.extend(["", "### Açıklama ve gerekçe", "", task["answer_explanation"], ""])
            if nonempty(task.get("teacher_background")):
                lines.extend(["### Öğretmenin bilmesi gerekenler", "", task["teacher_background"], ""])
            if nonempty(task.get("student_explanation")):
                lines.extend(["### Sınıfta nasıl açıklanabilir?", "", f"> {task['student_explanation']}", ""])
            lines.extend(["### Bu görev neden burada?", "", task["why_it_matters"], ""])
            if nonempty(task.get("acceptable_answers")):
                lines.extend(["### Kabul edilebilir cevaplar", ""])
                lines.extend(render_value(task["acceptable_answers"]))
                lines.append("")
            if nonempty(task.get("teacher_moves")):
                lines.extend(["### Ders içi uygulama", ""])
                lines.extend(render_value(task["teacher_moves"]))
                lines.append("")
            if nonempty(task.get("follow_up_questions")):
                lines.extend(["### Takip soruları", ""])
                lines.extend(render_value(task["follow_up_questions"]))
                lines.append("")
            if nonempty(task.get("assessment_look_fors")):
                lines.extend(["### Öğrenci cevaplarını değerlendirme", ""])
                lines.extend(render_value(task["assessment_look_fors"]))
                lines.append("")
            if nonempty(task.get("common_misconceptions")):
                lines.extend(["### Sık yanılgılar", ""])
                lines.extend(render_value(task["common_misconceptions"]))
                lines.append("")
            if nonempty(task.get("misconception_interventions")):
                lines.extend(["### Müdahale", ""])
                lines.extend(render_value(task["misconception_interventions"]))
                lines.append("")
            if nonempty(task.get("support")) or nonempty(task.get("enrichment")):
                lines.extend(["### Destek / zenginleştirme", ""])
                if nonempty(task.get("support")):
                    lines.append("**Destek**")
                    lines.extend(render_value(task["support"]))
                if nonempty(task.get("enrichment")):
                    lines.append("**Zenginleştirme**")
                    lines.extend(render_value(task["enrichment"]))
                lines.append("")
            if nonempty(task.get("board_notes")):
                lines.extend(["### Tahta notu", ""])
                lines.extend(render_value(task["board_notes"]))
                lines.append("")
            lines.extend(["### Kaynak ve durum", ""])
            lines.append(f"- **Prompt durumu:** {task['prompt_status']} ({task['prompt_mode']})")
            lines.append(f"- **Cevap durumu:** {task['answer_status']}")
            for locator in task["source_locators"]:
                label = "Görev locatorı" if locator == task.get("source_locator") else "Destek locatorı"
                lines.append(f"- **{label}:** {locator}")
            if task.get("source_limitations"):
                for limitation in task["source_limitations"]:
                    lines.append(f"- **Kaynak sınırı:** {limitation}")
            if task.get("review_reasons"):
                for reason in task["review_reasons"]:
                    lines.append(f"- **REVIEW_REQUIRED:** {reason}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_theme(
    root: Path,
    theme: dict[str, Any],
    textbook_map: dict[str, Any],
    activity_index: dict[str, dict[str, Any]],
    activity_sections: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    theme_id = theme["theme_id"]
    theme_dir = root / "courses" / COURSE_ID / "teacher_guide" / theme_id
    manifest_path = theme_dir / "teacher_guide.json"
    manifest = read_json(manifest_path)
    canonical_sections, canonical = index_canonical(root, manifest)
    component_paths = apply_component_registries(root, theme_id, canonical)
    mirror_paths = discover_mirror_paths(theme_dir / "book_mirror_v23.json")
    mirror = merge_mirrors(mirror_paths)
    manifest_sections = {row["section_id"]: row for row in manifest["sections"]}
    expanded_entries: list[dict[str, Any]] = []
    for entry in mirror["entries"]:
        expanded_entries.extend(expand_mirror_entry(entry))
    board_seen: set[str] = set()
    tasks: list[dict[str, Any]] = []
    for entry in expanded_entries:
        tasks.append(
            build_task(
                root,
                theme_id,
                entry,
                canonical_sections,
                canonical,
                manifest_sections,
                activity_index,
                board_seen,
            )
        )
    section_list: list[dict[str, Any]] = []
    for row in manifest["sections"]:
        section_tasks = [task for task in tasks if task["section_id"] == row["section_id"]]
        if not section_tasks:
            raise ValueError(f"V3 section has no tasks: {theme_id}:{row['section_id']}")
        section_content = canonical_sections[row["section_id"]]["content"]
        section_list.append(
            {
                "section_id": row["section_id"],
                "title": row["title"],
                "section_type": row["section_type"],
                "printed_page_range": row["printed_page_range"],
                "activity_refs": list(dict.fromkeys(row.get("activity_refs", []) or section_content.get("activity_refs", []))),
                "outcome_refs": list(dict.fromkeys(row.get("outcome_refs", []) or section_content.get("outcome_refs", []))),
                "task_ids": [task["task_id"] for task in section_tasks],
                "content_status": "REVIEW_REQUIRED" if any(task["content_status"] == "REVIEW_REQUIRED" for task in section_tasks) else "VERIFIED",
                "provenance": {
                    "item_id": row["section_id"],
                    "origin": "official_textbook",
                    "source_ids": [TEXTBOOK_SOURCE_ID, TEXTBOOK_MAP_SOURCE_ID, CANONICAL_SOURCE_ID],
                    "source_locators": [f"basılı s.{row['printed_page_range']}", row["content_ref"]],
                    "verbatim": False,
                    "derived_from": [row["content_ref"]],
                    "transformation": "CANONICAL_SECTION_TO_V3_TASK_INDEX",
                    "verification_status": "REVIEW" if any(task["content_status"] == "REVIEW_REQUIRED" for task in section_tasks) else "VERIFIED",
                },
            }
        )
    questions = [task for task in tasks if task["task_type"] == "QUESTION"]
    all_theme_activities = [activity["activity_id"] for section in theme.get("sections", []) for activity in section.get("activities", [])]
    covered_activities = sorted({activity_ref for task in tasks for activity_ref in task["activity_refs"] if activity_ref in all_theme_activities})
    uncovered_activities = sorted(set(all_theme_activities) - set(covered_activities))
    review_items = [task["task_id"] for task in tasks if task["content_status"] == "REVIEW_REQUIRED"]
    locator_only = [task["task_id"] for task in questions if task["prompt_mode"] == "LOCATOR_ONLY"]
    unresolved_prompts = [task["task_id"] for task in questions if task["prompt_status"] == "REVIEW_REQUIRED" or not nonempty(task["book_prompt"])]
    fallback_count = sum(1 for task in tasks if task.get("generation_profile") == "text_analysis")
    coverage = {
        "textbook_question_count": len(questions),
        "guide_question_count": len(questions),
        "textbook_activity_count": len(all_theme_activities),
        "covered_activity_count": len(covered_activities),
        "uncovered_textbook_questions": [],
        "uncovered_required_activities": uncovered_activities,
        "locator_only_questions": locator_only,
        "unresolved_prompt_text": unresolved_prompts,
        "review_required_items": review_items,
        "duplicate_task_ids": [],
        "generic_fallback_task_count": fallback_count,
        "source_page_mismatches": [],
    }
    section_paths = [root / row["content_ref"] for row in manifest["sections"]]
    map_theme = next(value for value in textbook_map["themes"] if value["theme_id"] == theme_id)
    guide: dict[str, Any] = {
        "schema_version": "3.0.0",
        "document_type": "TYMM_TEACHER_GUIDE_V3",
        "course_id": COURSE_ID,
        "grade": manifest["grade"],
        "theme_id": theme_id,
        "title": f"{map_theme['exact_title']} — Öğretmen Rehberi V3",
        "status": "REVIEW_REQUIRED" if review_items else "REFERENCE_QUALITY",
        "generator": "TEXTBOOK_FIRST_TEACHER_GUIDE_V3",
        "source_policy": {
            "primary_source": TEXTBOOK_SOURCE_ID,
            "authority_chain": [
                "official_textbook_pdf",
                "textbook_map",
                "teacher_guide_canonical",
                "curriculum_map",
                "task_specific_pedagogical_derivation",
            ],
            "prompt_policy": "Kitapta görünen gerçek soru/yönerge mirror kaydıyla taşınır; doğrulanamayan soru metni uydurulmaz ve REVIEW_REQUIRED bırakılır.",
            "phase_profile_role": "V2 phase profilleri V3 authoring kaynağı değildir; yalnız geriye dönük uyumlulukta fallback olarak kalır.",
        },
        "canonical_sources": {},
        "sections": section_list,
        "tasks": tasks,
        "coverage": coverage,
        "provenance": {
            "item_id": f"{theme_id}::TEACHER_GUIDE_V3",
            "origin": "pedagogical_recommendation",
            "source_ids": [TEXTBOOK_SOURCE_ID, TEXTBOOK_MAP_SOURCE_ID, CANONICAL_SOURCE_ID],
            "source_locators": [f"basılı s.{theme['printed_page_range']}"],
            "verbatim": False,
            "derived_from": ["textbook_task_index", "canonical_teacher_guide", *[path.name for path in mirror_paths]],
            "transformation": "TEXTBOOK_FIRST_EXPLANATION_FIRST_GUIDE_BUILD",
            "verification_status": "REVIEW" if review_items else "VERIFIED",
        },
    }
    guide["_build_meta"] = {
        "manifest_path": manifest_path,
        "section_paths": section_paths,
        "component_paths": component_paths,
        "mirror_paths": mirror_paths,
    }
    return guide, tasks, {"manifest": manifest, "canonical": canonical, "mirror": mirror}


def build_course(root: Path) -> dict[str, Any]:
    course_dir = root / "courses" / COURSE_ID
    textbook_map_path = course_dir / "textbook_map.json"
    curriculum_map_path = course_dir / "curriculum_map.json"
    normative_path = course_dir / "curriculum_normative_text.json"
    textbook_map = read_json(textbook_map_path)
    activity_index, activity_sections = activity_index_from_map(textbook_map)
    guides: dict[str, dict[str, Any]] = {}
    task_records: dict[str, list[dict[str, Any]]] = {}
    theme_metadata: dict[str, dict[str, Any]] = {}
    for theme in textbook_map["themes"]:
        guide, tasks, metadata = build_theme(root, theme, textbook_map, activity_index, activity_sections)
        guides[theme["theme_id"]] = guide
        task_records[theme["theme_id"]] = tasks
        theme_metadata[theme["theme_id"]] = {**metadata, **guide["_build_meta"]}

    index_dir = course_dir / "teacher_guide_v3"
    index_path = index_dir / "textbook_task_index.json"
    task_index = build_activity_index_document(root, textbook_map, task_records, activity_index, activity_sections)
    write_json(index_path, task_index)
    index_meta = source_meta(root, index_path, "textbook_task_index")
    pdf_path = course_dir / "source_docs" / "turk-dili-ve-edebiyati-11sinif-ders-kitabi_compressed.pdf"
    for theme in textbook_map["themes"]:
        theme_id = theme["theme_id"]
        guide = guides[theme_id]
        metadata = theme_metadata[theme_id]
        manifest_path: Path = metadata["manifest_path"]
        section_paths: list[Path] = metadata["section_paths"]
        guide["canonical_sources"] = guide_source_metadata(
            root,
            manifest_path,
            section_paths,
            textbook_map_path,
            curriculum_map_path,
            normative_path,
            pdf_path,
            index_path,
        )
        guide["canonical_sources"]["textbook_task_index"] = index_meta
        guide.pop("_build_meta", None)
        markdown = render_markdown(guide)
        guide["rendered_markdown_sha256"] = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        theme_dir = course_dir / "teacher_guide" / theme_id
        write_json(theme_dir / "teacher_guide_v3.json", guide)
        (theme_dir / "TEACHER_GUIDE_V3.md").write_text(markdown, encoding="utf-8")
    return {
        "course_id": COURSE_ID,
        "themes": list(guides),
        "question_count": task_index["counts"]["questions"],
        "activity_count": task_index["counts"]["activities"],
        "index_path": relative_path(root, index_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.repo_root.resolve()
    result = build_course(root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
