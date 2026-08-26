#!/usr/bin/env python3
"""Compile verified canonical course JSON into an app-agnostic runtime SQLite package."""
from __future__ import annotations

import argparse, hashlib, json, re, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from process_component_resolver import audit_curriculum, project_effective_components
from runtime_assessment_payload import project_runtime_assessment_payload
from runtime_lesson_plan_payload import project_runtime_lesson_plan_payload

COMPILER_VERSION = "1.2.0"
RUNTIME_PACKAGE_VERSION = "1.2.0"
SCHEMA_VERSION = "1.1.0"

SCHEMA = r'''
PRAGMA foreign_keys = ON;
CREATE TABLE courses (course_id TEXT PRIMARY KEY, grade INTEGER, title TEXT NOT NULL, schema_version TEXT NOT NULL, source_manifest_fingerprint TEXT NOT NULL);
CREATE TABLE themes (theme_id TEXT PRIMARY KEY, course_id TEXT NOT NULL REFERENCES courses(course_id), theme_order INTEGER NOT NULL, title TEXT NOT NULL, page_range TEXT, planned_hours INTEGER, anlama_hours INTEGER, anlatma_hours INTEGER, source_locator TEXT);
CREATE TABLE blocks (block_id TEXT PRIMARY KEY, theme_id TEXT NOT NULL REFERENCES themes(theme_id), block_order INTEGER NOT NULL, title TEXT NOT NULL, skill_domain TEXT, learning_area TEXT, planned_hours INTEGER, time_status TEXT, source_locators_json TEXT NOT NULL);
CREATE TABLE outcomes (outcome_id TEXT PRIMARY KEY, theme_id TEXT NOT NULL REFERENCES themes(theme_id), outcome_code TEXT NOT NULL, official_text TEXT NOT NULL, process_components TEXT, process_component_origin TEXT, source_locator TEXT, verification_status TEXT);
CREATE TABLE block_outcomes (block_id TEXT NOT NULL REFERENCES blocks(block_id), outcome_id TEXT NOT NULL REFERENCES outcomes(outcome_id), PRIMARY KEY(block_id, outcome_id));
CREATE TABLE textbook_sections (section_id TEXT PRIMARY KEY, theme_id TEXT NOT NULL REFERENCES themes(theme_id), title TEXT NOT NULL, genre TEXT, printed_page_range TEXT, pdf_page_range TEXT, source_id TEXT);
CREATE TABLE activities (activity_id TEXT PRIMARY KEY, section_id TEXT REFERENCES textbook_sections(section_id), theme_id TEXT NOT NULL REFERENCES themes(theme_id), title TEXT NOT NULL, activity_type TEXT, student_action TEXT, expected_evidence TEXT, printed_page TEXT, pdf_page TEXT, verification_status TEXT);
CREATE TABLE block_activities (block_id TEXT NOT NULL REFERENCES blocks(block_id), activity_id TEXT NOT NULL REFERENCES activities(activity_id), PRIMARY KEY(block_id, activity_id));
CREATE TABLE activity_outcomes (activity_id TEXT NOT NULL REFERENCES activities(activity_id), outcome_id TEXT NOT NULL REFERENCES outcomes(outcome_id), PRIMARY KEY(activity_id, outcome_id));
CREATE TABLE forms (form_id TEXT PRIMARY KEY, title TEXT NOT NULL, structural_type TEXT, assessment_type TEXT, printed_page INTEGER, pdf_page INTEGER, evaluator TEXT, source_id TEXT, verification_status TEXT);
CREATE TABLE activity_forms (activity_id TEXT NOT NULL REFERENCES activities(activity_id), form_id TEXT NOT NULL REFERENCES forms(form_id), PRIMARY KEY(activity_id, form_id));
CREATE TABLE resource_decisions (resource_plan_id TEXT PRIMARY KEY, theme_id TEXT NOT NULL REFERENCES themes(theme_id), need_id TEXT, resource_type TEXT, decision_code TEXT NOT NULL, app_category TEXT, priority TEXT, purpose TEXT, expected_evidence TEXT, textbook_coverage TEXT, locator TEXT, teacher_review_required INTEGER);
CREATE TABLE assessment_artifacts (artifact_id TEXT PRIMARY KEY, title TEXT NOT NULL, skill_domain TEXT, scope TEXT, assessment_family TEXT, reuse_policy TEXT, generation_priority TEXT, generation_status TEXT, teacher_review_required INTEGER, covered_themes_json TEXT NOT NULL, covered_gap_instances_json TEXT NOT NULL);
CREATE TABLE assessment_gap_mappings (gap_instance_id TEXT PRIMARY KEY, artifact_id TEXT NOT NULL REFERENCES assessment_artifacts(artifact_id), theme_id TEXT NOT NULL REFERENCES themes(theme_id), resource_plan_id TEXT, official_requirement TEXT, exact_remaining_gap TEXT, source_locators_json TEXT NOT NULL);
CREATE TABLE assessment_task_bindings (artifact_id TEXT NOT NULL REFERENCES assessment_artifacts(artifact_id), gap_instance_id TEXT NOT NULL, theme_id TEXT NOT NULL REFERENCES themes(theme_id), block_id TEXT REFERENCES blocks(block_id), activity_id TEXT REFERENCES activities(activity_id), targeted_outcomes_json TEXT NOT NULL, task_title TEXT, evidence TEXT, textbook_locator TEXT, curriculum_locator TEXT, PRIMARY KEY(artifact_id, gap_instance_id));
CREATE TABLE timeline_themes (theme_id TEXT PRIMARY KEY REFERENCES themes(theme_id), theme_order INTEGER NOT NULL, official_total_hours INTEGER, core_instruction_hours INTEGER, school_based_hours INTEGER, school_based_hours_status TEXT, source_locators_json TEXT NOT NULL);
CREATE TABLE timeline_blocks (block_id TEXT PRIMARY KEY REFERENCES blocks(block_id), theme_id TEXT NOT NULL REFERENCES themes(theme_id), block_order INTEGER NOT NULL, planned_hours INTEGER, time_status TEXT, source_locators_json TEXT NOT NULL);
CREATE TABLE source_references (source_id TEXT PRIMARY KEY, source_type TEXT, source_title TEXT NOT NULL, locator TEXT, provenance_category TEXT, authority_rank INTEGER, verification_status TEXT);
CREATE TABLE entity_source_references (entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES source_references(source_id), locator TEXT, PRIMARY KEY(entity_type, entity_id, source_id, locator));
CREATE INDEX idx_blocks_theme_order ON blocks(theme_id, block_order);
CREATE INDEX idx_outcomes_theme_code ON outcomes(theme_id, outcome_code);
CREATE INDEX idx_outcomes_process_origin ON outcomes(process_component_origin);
CREATE INDEX idx_activities_theme_page ON activities(theme_id, printed_page);
CREATE INDEX idx_activity_forms_form ON activity_forms(form_id);
CREATE INDEX idx_resource_theme ON resource_decisions(theme_id, decision_code);
CREATE INDEX idx_gap_artifact ON assessment_gap_mappings(artifact_id);
CREATE INDEX idx_bindings_block ON assessment_task_bindings(block_id);
CREATE INDEX idx_source_entity ON entity_source_references(entity_type, entity_id);
'''

def read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))

def sha256(p: Path) -> str:
    h = hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def j(v: Any) -> str: return json.dumps(v if v is not None else [], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def text(v: Any) -> str | None:
    if v is None: return None
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, sort_keys=True)
def integer(v: Any) -> int | None: return v if isinstance(v, int) and not isinstance(v, bool) else None
def first(d: dict, *keys: str) -> Any:
    for k in keys:
        if k in d: return d[k]
    return None

def process_component_catalog_path(root: Path) -> Path | None:
    local = root.parent / "TDE_SHARED" / "curriculum_process_component_catalog.json"
    if local.exists():
        return local
    repo = Path(__file__).resolve().parents[3] / "courses" / "TDE_SHARED" / "curriculum_process_component_catalog.json"
    return repo if repo.exists() else None

def resolve_curriculum(root: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    raw = read_json(root / "curriculum_map.json")
    contract_path = root / "curriculum_process_component_resolution.json"
    if not contract_path.exists():
        return raw, None
    catalog_path = process_component_catalog_path(root)
    if catalog_path is None:
        raise ValueError("PROCESS_COMPONENT_ROOF_CATALOG_MISSING")
    catalog = read_json(catalog_path)
    contract = read_json(contract_path)
    if contract.get("catalog_id") != catalog.get("catalog_id"):
        raise ValueError("PROCESS_COMPONENT_CATALOG_CONTRACT_MISMATCH")
    if contract.get("course_id") != raw.get("course_id"):
        raise ValueError("PROCESS_COMPONENT_COURSE_CONTRACT_MISMATCH")
    audit = audit_curriculum(raw, catalog)
    if audit.get("final") != "PASS":
        raise ValueError(f"PROCESS_COMPONENT_INHERITANCE_INVALID: {audit.get('counts')}")
    expected = contract.get("expected_counts", {})
    for key, value in expected.items():
        if audit.get("counts", {}).get(key) != value:
            raise ValueError(f"PROCESS_COMPONENT_COUNT_MISMATCH: {key} actual={audit.get('counts', {}).get(key)} expected={value}")
    projected = project_effective_components(raw, catalog)
    return projected, audit

def load_block_hour_bindings(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any] | None]:
    path = root / "planning/block_hour_bindings.json"
    if not path.exists():
        return {}, None
    doc = read_json(path)
    if doc.get("status") != "BLOCK_TIME_RESOLVED":
        return {}, doc
    bindings: dict[str, dict[str, Any]] = {}
    for theme in doc.get("themes", []):
        tid = theme.get("theme_id")
        expected_total = integer(theme.get("normative_total_hours"))
        actual_total = 0
        for item in theme.get("bindings", []):
            bid = item.get("block_id")
            hours = integer(item.get("planned_hours"))
            if not bid or hours is None or hours <= 0:
                raise ValueError(f"invalid block-hour binding in {tid}: {item}")
            if bid in bindings:
                raise ValueError(f"duplicate block-hour binding: {bid}")
            bindings[bid] = {**item, "theme_id": tid}
            actual_total += hours
        if expected_total is not None and actual_total != expected_total:
            raise ValueError(f"block-hour theme total mismatch: {tid} runtime={actual_total} expected={expected_total}")
    expected_count = integer(doc.get("validation", {}).get("expected_block_count"))
    if expected_count is not None and len(bindings) != expected_count:
        raise ValueError(f"block-hour binding count mismatch: runtime={len(bindings)} expected={expected_count}")
    return bindings, doc

def relevant_files(root: Path) -> list[tuple[str, Path]]:
    names = ["curriculum_map.json","curriculum_process_component_resolution.json","textbook_map.json","textbook_forms_index.json","source_manifest.json","planning/course_timeline.json","planning/official_topic_hour_distribution.json","planning/block_hour_bindings.json","planning/lesson_plan_production_plan.json","production/production_manifest.json","production/assessment_artifact_registry.json","production/assessment_design_contract.json","production/consolidated_resource_plan.json","production/teaching_blocks.json"]
    paths: list[tuple[str, Path]] = [(n, root/n) for n in names if (root/n).exists()]
    for pattern in ("themes/tema_*/alignment.json","themes/tema_*/gap_analysis.json","themes/tema_*/resource_plan.json","themes/tema_*/needs.json"):
        paths += [(p.relative_to(root).as_posix(), p) for p in sorted(root.glob(pattern))]
    paths += [(p.relative_to(root).as_posix(), p) for p in sorted(root.glob("generated/lesson_plans/*/*/*.json"))]
    if (root / "curriculum_process_component_resolution.json").exists():
        shared = process_component_catalog_path(root)
        if shared is None:
            raise ValueError("PROCESS_COMPONENT_ROOF_CATALOG_MISSING")
        paths.append(("../TDE_SHARED/curriculum_process_component_catalog.json", shared))
    return paths

def compiler_state(root: Path) -> tuple[dict[str, dict[str, Any]], str]:
    entries = {}
    for rel, p in relevant_files(root):
        entries[rel] = {"path": rel, "sha256": sha256(p), "size_bytes": p.stat().st_size}
    canonical = "\n".join(f"{k}:{v['sha256']}" for k,v in sorted(entries.items()))
    return entries, hashlib.sha256(canonical.encode()).hexdigest()

def decision_category(code: str | None) -> str | None:
    return {"REUSE_TEXTBOOK":"BOOK_SUFFICIENT", "REUSE_WITH_TEACHER_GUIDE":"USE_EXISTING_TEXTBOOK_ACTIVITY", "ADAPT_TEXTBOOK_ACTIVITY":"USE_EXISTING_TEXTBOOK_ACTIVITY", "GENERATE_ASSESSMENT_SUPPORT":"ADDITIONAL_SUPPORT_REQUIRED", "GENERATE_DIFFERENTIATION":"ADDITIONAL_SUPPORT_REQUIRED", "GENERATE_ENRICHMENT":"ADDITIONAL_SUPPORT_REQUIRED", "GENERATE":"ADDITIONAL_SUPPORT_REQUIRED", "NO_ACTION":"BOOK_SUFFICIENT"}.get(code)

def build(root: Path) -> dict[str, Any]:
    root = root.resolve(); out = root / "runtime"; out.mkdir(exist_ok=True)
    curriculum, process_audit = resolve_curriculum(root)
    textbook, forms_data, manifest, timeline = [read_json(root/n) for n in ["textbook_map.json","textbook_forms_index.json","source_manifest.json","planning/course_timeline.json"]]
    reg, prod, contract = [read_json(root/n) for n in ["production/assessment_artifact_registry.json","production/production_manifest.json","production/assessment_design_contract.json"]]
    teaching = read_json(root/"production/teaching_blocks.json")
    teaching_by_id = {b["block_id"]: b for b in teaching.get("blocks", [])}
    block_hours, block_hours_doc = load_block_hour_bindings(root)
    files, fingerprint = compiler_state(root)
    dbpath = out/"course_runtime.sqlite"; dbpath.unlink(missing_ok=True)
    db = sqlite3.connect(dbpath); db.execute("PRAGMA foreign_keys=ON"); db.executescript(SCHEMA)
    def ins(sql, vals): db.execute(sql, vals)
    course_id = curriculum["course_id"]
    ins("INSERT INTO courses VALUES (?,?,?,?,?)", (course_id, curriculum.get("grade"), curriculum.get("course_title") or course_id, SCHEMA_VERSION, fingerprint))
    for f in sorted(forms_data["forms"],key=lambda x:x["form_id"]):
        ins("INSERT INTO forms VALUES (?,?,?,?,?,?,?,?,?)",(f["form_id"],f.get("title") or f["form_id"],f.get("structural_type"),f.get("assessment_type"),integer(f.get("printed_page")),integer(f.get("pdf_page")),f.get("evaluator"),forms_data.get("source_id"),f.get("verification_status")))
    textbook_themes = {x["theme_id"]: x for x in textbook["themes"]}; time_themes = {x["theme_id"]: x for x in timeline["themes"]}
    block_by_id = {}
    for t in curriculum["themes"]:
        tid=t["theme_id"]; th=textbook_themes.get(tid,{}); tt=time_themes.get(tid,{})
        ah=t.get("allocated_lesson_hours") or {}; ins("INSERT INTO themes VALUES (?,?,?,?,?,?,?,?,?)", (tid,course_id,t.get("theme_no",t.get("theme_number")),t.get("exact_theme_name") or t.get("theme_title") or tid,t.get("page_range"),integer(first(ah,"total","instructional_total")),integer(ah.get("anlama")),integer(ah.get("anlatma")),t.get("source_locator")))
        for o in t.get("learning_outcomes",[]):
            oid=o.get("outcome_id") or f"{tid}::{o['outcome_code']}"
            effective=o.get("process_components_effective",o.get("process_components_verbatim"))
            origin=o.get("process_component_resolution",{}).get("origin","LEGACY_RAW")
            ins("INSERT INTO outcomes VALUES (?,?,?,?,?,?,?,?)", (oid,tid,o["outcome_code"],text(o.get("outcome_verbatim","")) or "",text(effective),origin,text(o.get("source_locator")),text(o.get("verification_status"))))
        for s in th.get("sections",[]):
            ins("INSERT INTO textbook_sections VALUES (?,?,?,?,?,?,?)", (s["section_id"],tid,s.get("section_title") or s["section_id"],s.get("genre"),s.get("printed_page_range"),s.get("pdf_page_range"),textbook.get("source_id")))
            for a in s.get("activities",[]):
                ins("INSERT INTO activities VALUES (?,?,?,?,?,?,?,?,?,?)", (a["activity_id"],s["section_id"],tid,a.get("exact_title") or a.get("activity_title") or a["activity_id"],a.get("activity_type",a.get("type")),a.get("student_action"),a.get("expected_product_or_evidence",a.get("expected_student_evidence")),text(a.get("printed_page")),text(a.get("pdf_page")),a.get("verification_status")))
                for fid in a.get("related_forms",[]):
                    if fid in {f["form_id"] for f in forms_data["forms"]}: ins("INSERT OR IGNORE INTO activity_forms VALUES (?,?)",(a["activity_id"],fid))
        for b in tt.get("blocks",[]):
            bid=b["block_id"]; block_by_id[bid]=b; tb=teaching_by_id.get(bid,{}); hb=block_hours.get(bid)
            if hb and hb.get("theme_id") != tid: raise ValueError(f"block-hour theme mismatch: {bid} -> {hb.get('theme_id')} expected {tid}")
            planned_hours=integer(hb.get("planned_hours")) if hb else integer(first(b,"planned_hours","approximate_lesson_hours"))
            time_status="OFFICIAL_ANNUAL_PLAN_DERIVED" if hb else text(b.get("time_status",b.get("lesson_hours_status")))
            skill_domain=text(hb.get("domain")) if hb else text(b.get("skill_domain"))
            block_sources=list(b.get("source_locators",[]))
            if hb: block_sources.append(f"planning/block_hour_bindings.json#{tid}.{bid}")
            ins("INSERT INTO blocks VALUES (?,?,?,?,?,?,?,?,?)",(bid,tid,b.get("block_order",b.get("block_sequence")),text(b.get("title",b.get("block_title",bid))) or bid,skill_domain,text(b.get("learning_area")),planned_hours,time_status,j(block_sources)))
            outcomes_by_key={(o["outcome_code"],tid):(o.get("outcome_id") or f"{tid}::{o['outcome_code']}") for o in t.get("learning_outcomes",[])}
            block_outcome_codes=tb.get("curriculum_outcomes", b.get("outcomes",b.get("curriculum_outcomes",[])))
            for code in block_outcome_codes:
                if (code,tid) not in outcomes_by_key: raise ValueError(f"unknown canonical outcome relation: {bid} -> {code} in {tid}")
                ins("INSERT INTO block_outcomes VALUES (?,?)",(bid,outcomes_by_key[(code,tid)]))
            activity_ids={a[0] for a in db.execute("SELECT activity_id FROM activities")}
            for aid in tb.get("textbook_activity_ids",[]):
                if aid in activity_ids:
                    ins("INSERT OR IGNORE INTO block_activities VALUES (?,?)",(bid,aid))
                    for code in block_outcome_codes:
                        oid=outcomes_by_key.get((code,tid));
                        if oid: ins("INSERT OR IGNORE INTO activity_outcomes VALUES (?,?)",(aid,oid))
            form_ids={f["form_id"] for f in forms_data["forms"]}
            for fid in tb.get("textbook_form_ids",[]):
                if fid in form_ids:
                    for aid in tb.get("textbook_activity_ids",[]):
                        if aid in activity_ids: ins("INSERT OR IGNORE INTO activity_forms VALUES (?,?)",(aid,fid))
        theme_order=t.get("theme_no",t.get("theme_number"))
        ins("INSERT INTO timeline_themes VALUES (?,?,?,?,?,?,?)",(tid,theme_order,integer(tt.get("official_total_hours")),integer(tt.get("core_instruction_hours")),integer(tt.get("school_based_hours")),tt.get("school_based_hours_status"),j(tt.get("source_locators",[]))))
        for b in tt.get("blocks",[]):
            hb=block_hours.get(b["block_id"]); planned_hours=integer(hb.get("planned_hours")) if hb else integer(b.get("planned_hours")); time_status="OFFICIAL_ANNUAL_PLAN_DERIVED" if hb else b.get("time_status"); sources=list(b.get("source_locators",[]))
            if hb: sources.append(f"planning/block_hour_bindings.json#{tid}.{b['block_id']}")
            ins("INSERT INTO timeline_blocks VALUES (?,?,?,?,?,?)",(b["block_id"],tid,b.get("block_order"),planned_hours,time_status,j(sources)))
    if block_hours_doc and block_hours_doc.get("status") == "BLOCK_TIME_RESOLVED":
        unknown=set(block_hours)-set(block_by_id); missing=set(block_by_id)-set(block_hours)
        if unknown: raise ValueError(f"unknown block-hour IDs: {sorted(unknown)}")
        if missing: raise ValueError(f"missing block-hour bindings: {sorted(missing)}")
    for p in sorted(root.glob("themes/tema_*/resource_plan.json")):
        d=read_json(p); tid=d.get("theme_id"); arr=d.get("resources",d.get("resource_plans",[]))
        for r in arr:
            code=r.get("production_decision") or r.get("decision") or r.get("production_decision_code")
            ins("INSERT INTO resource_decisions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(r.get("resource_plan_id"),tid,r.get("need_id"),r.get("resource_type"),code,decision_category(code),r.get("priority"),r.get("purpose") or r.get("rationale"),r.get("expected_student_evidence"),r.get("textbook_coverage"),r.get("textbook_resource_locator"),1 if r.get("teacher_review_required") else 0))
    for a in reg.get("annual_artifacts",[]):
        ins("INSERT INTO assessment_artifacts VALUES (?,?,?,?,?,?,?,?,?,?,?)",(a["artifact_id"],a.get("title") or a["artifact_id"],a.get("skill_domain"),a.get("scope"),a.get("assessment_family"),a.get("reuse_policy"),a.get("generation_priority"),a.get("generation_status"),1 if a.get("teacher_review_required") else 0,j(a.get("covered_themes",[])),j(a.get("covered_gap_instances",[]))))
        for b in a.get("task_bindings",[]):
            ins("INSERT INTO assessment_task_bindings VALUES (?,?,?,?,?,?,?,?,?,?)",(a["artifact_id"],b.get("gap_instance_id"),b.get("theme_id"),b.get("block_id"),b.get("activity_id"),j(b.get("targeted_outcomes",[])),b.get("task_title"),b.get("evidence_being_observed"),b.get("textbook_locator"),b.get("curriculum_locator")))
    for m in prod.get("gap_instance_provenance_registry",[]):
        ins("INSERT INTO assessment_gap_mappings VALUES (?,?,?,?,?,?,?)",(m["gap_instance_id"],m["resolved_artifact_id"],m["theme_id"],m.get("resource_plan_id"),m.get("official_requirement_verbatim"),m.get("exact_remaining_gap"),j(m.get("source_locators",{}))))
    for s in manifest.get("sources",[]):
        ins("INSERT INTO source_references VALUES (?,?,?,?,?,?,?)",(s["source_id"],s.get("source_type"),s.get("title") or s["source_id"],s.get("file_path") or s.get("url"),s.get("source_type"),s.get("authority_rank"),s.get("verification_status")))
    for t in curriculum["themes"]:
        sid=curriculum.get("source_id"); loc=t.get("source_locator")
        if sid and loc and db.execute("SELECT 1 FROM source_references WHERE source_id=?",(sid,)).fetchone(): ins("INSERT OR IGNORE INTO entity_source_references VALUES (?,?,?,?)",("theme",t["theme_id"],sid,loc))
    db.commit(); db.close()
    count_db=sqlite3.connect(dbpath)
    counts={table: count_db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ["courses","themes","blocks","block_activities","outcomes","block_outcomes","textbook_sections","activities","activity_outcomes","forms","activity_forms","resource_decisions","assessment_artifacts","assessment_gap_mappings","assessment_task_bindings","timeline_themes","timeline_blocks","source_references","entity_source_references"]}
    count_db.close()
    now=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
    resolved_block_hours=bool(block_hours_doc and block_hours_doc.get("status") == "BLOCK_TIME_RESOLVED")
    runtime_manifest={"runtime_package_version":RUNTIME_PACKAGE_VERSION,"schema_version":SCHEMA_VERSION,"course_id":course_id,"grade":curriculum.get("grade"),"build_timestamp":now,"compiler_version":COMPILER_VERSION,"canonical_source_files":sorted(files),"canonical_source_hashes":{k:v["sha256"] for k,v in sorted(files.items())},"canonical_content_fingerprint":fingerprint,"row_counts":counts,"timeline_resolution":"BLOCK_TIME_RESOLVED" if resolved_block_hours else timeline.get("timeline_resolution"),"timeline_unresolved_fields":{"weekly_lesson_hours":timeline.get("calendar_binding",{}).get("weekly_lesson_hours"),"calendar_binding":timeline.get("calendar_binding",{}).get("status"),"block_hours":None if resolved_block_hours else "ORDER_ONLY"},"block_hour_binding_status":block_hours_doc.get("status") if block_hours_doc else "NOT_PRESENT","block_hour_binding_file":"planning/block_hour_bindings.json" if block_hours_doc else None,"assessment_registry_version":reg.get("registry_version"),"assessment_contract_version":contract.get("metadata",{}).get("contract_version"),"source_manifest_fingerprint":next((x["sha256"] for k,x in files.items() if k=="source_manifest.json"),None),"process_component_resolution_status":"PASS" if process_audit else "LEGACY_NOT_RESOLVED","process_component_counts":process_audit.get("counts") if process_audit else None,"runtime_database_path":"runtime/course_runtime.sqlite","validation_status":"PENDING"}
    (out/"runtime_schema.sql").write_text(SCHEMA.strip()+"\n",encoding="utf-8"); (out/"runtime_manifest.json").write_text(json.dumps(runtime_manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    result=validate(root, write_report=True); runtime_manifest["validation_status"]=result["status"]; (out/"runtime_manifest.json").write_text(json.dumps(runtime_manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    project_runtime_assessment_payload(root)
    project_runtime_lesson_plan_payload(root)
    final_manifest=read_json(out/"runtime_manifest.json")
    result["row_counts"]=final_manifest.get("row_counts",result.get("row_counts",{}))
    return result

def validate(root: Path, write_report: bool=False) -> dict[str,Any]:
    root=root.resolve(); out=root/"runtime"; mp=read_json(out/"runtime_manifest.json")
    production=read_json(root/"production/production_manifest.json")
    block_hours, block_hours_doc=load_block_hour_bindings(root)
    db=sqlite3.connect(out/"course_runtime.sqlite"); db.execute("PRAGMA foreign_keys=ON")
    checks=[]
    def check(name, ok, detail=""): checks.append((name,bool(ok),detail))
    check("schema validation", all(db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()), "runtime schema loaded")
    check("foreign key integrity", db.execute("PRAGMA foreign_key_check").fetchall()==[], "PRAGMA foreign_key_check")
    for table,col in [("themes","theme_id"),("blocks","block_id"),("outcomes","outcome_id"),("activities","activity_id"),("forms","form_id"),("assessment_artifacts","artifact_id")]: check(f"canonical ID uniqueness: {table}", db.execute(f"SELECT {col},COUNT(*) FROM {table} GROUP BY {col} HAVING COUNT(*)>1").fetchall()==[])
    orphan=db.execute("SELECT COUNT(*) FROM assessment_gap_mappings g LEFT JOIN assessment_artifacts a ON a.artifact_id=g.artifact_id WHERE a.artifact_id IS NULL").fetchone()[0]; check("orphan relations",orphan==0,str(orphan))
    fresh=compiler_state(root)[1]==mp.get("canonical_content_fingerprint"); check("source fingerprint status",fresh,"RUNTIME_FRESH" if fresh else "RUNTIME_STALE")
    if mp.get("process_component_resolution_status") == "PASS":
        empty_pc=db.execute("SELECT COUNT(*) FROM outcomes WHERE process_components IS NULL OR process_components='' OR process_components='[]'").fetchone()[0]
        invalid_origin=db.execute("SELECT COUNT(*) FROM outcomes WHERE process_component_origin NOT IN ('THEME_EXPLICIT','ROOF_INHERITED','SOURCE_VERIFIED_NONE')").fetchone()[0]
        origin_counts=dict(db.execute("SELECT process_component_origin,COUNT(*) FROM outcomes GROUP BY process_component_origin").fetchall())
        expected=mp.get("process_component_counts") or {}
        check("effective process components projected",empty_pc==expected.get("verified_no_component_outcomes",0),f"empty={empty_pc}, verified_none={expected.get('verified_no_component_outcomes',0)}")
        check("process component origins valid",invalid_origin==0,f"invalid={invalid_origin}")
        check("process component origin counts",origin_counts.get("THEME_EXPLICIT",0)==expected.get("explicit_component_outcomes",0) and origin_counts.get("ROOF_INHERITED",0)==expected.get("inherited_component_outcomes",0),f"runtime={origin_counts}, canonical={expected}")
    resolved_count=db.execute("SELECT COUNT(*) FROM timeline_blocks WHERE planned_hours IS NOT NULL").fetchone()[0]
    if block_hours_doc and block_hours_doc.get("status") == "BLOCK_TIME_RESOLVED":
        expected_count=integer(block_hours_doc.get("validation",{}).get("expected_block_count")) or len(block_hours)
        check("timeline projection status",resolved_count==expected_count,f"resolved={resolved_count}, expected={expected_count}")
        expected_theme_totals={x.get("theme_id"):integer(x.get("normative_total_hours")) for x in block_hours_doc.get("themes",[])}
        actual_theme_totals={tid:hours for tid,hours in db.execute("SELECT theme_id,SUM(planned_hours) FROM timeline_blocks GROUP BY theme_id")}
        check("block-hour theme totals",all(actual_theme_totals.get(tid)==hours for tid,hours in expected_theme_totals.items()),f"runtime={actual_theme_totals}, expected={expected_theme_totals}")
        parity=db.execute("SELECT COUNT(*) FROM blocks b JOIN timeline_blocks t ON t.block_id=b.block_id WHERE b.planned_hours=t.planned_hours AND b.time_status=t.time_status").fetchone()[0]
        check("block-hour projection parity",parity==expected_count,f"runtime={parity}, expected={expected_count}")
    else:
        check("timeline projection status",resolved_count==0,"block hours remain ORDER_ONLY")
    mapping_count=db.execute("SELECT COUNT(*) FROM assessment_gap_mappings").fetchone()[0]
    expected_gap_count=production.get("verified_resource_gap_count")
    if expected_gap_count is None: expected_gap_count=production.get("summary_metrics",{}).get("required_gap_instance_count",len(production.get("gap_instance_provenance_registry",[])))
    check("assessment mapping status", mapping_count==expected_gap_count, f"runtime={mapping_count}, canonical={expected_gap_count}")
    artifact_count=db.execute("SELECT COUNT(*) FROM assessment_artifacts").fetchone()[0]
    expected_artifact_count=production.get("expected_new_artifact_count",len(production.get("production_queue",[])))
    check("assessment artifact projection status", artifact_count==expected_artifact_count, f"runtime={artifact_count}, canonical={expected_artifact_count}")
    check("resource decision projection status", db.execute("SELECT COUNT(*) FROM resource_decisions").fetchone()[0]>0)
    q=[]
    q.append(db.execute("SELECT b.block_id,o.outcome_code,a.activity_id,a.printed_page,f.form_id,aa.artifact_id,r.decision_code FROM blocks b LEFT JOIN block_outcomes bo ON bo.block_id=b.block_id LEFT JOIN outcomes o ON o.outcome_id=bo.outcome_id LEFT JOIN block_activities ba ON ba.block_id=b.block_id LEFT JOIN activities a ON a.activity_id=ba.activity_id LEFT JOIN activity_forms af ON af.activity_id=a.activity_id LEFT JOIN forms f ON f.form_id=af.form_id LEFT JOIN assessment_task_bindings tb ON tb.block_id=b.block_id LEFT JOIN assessment_artifacts aa ON aa.artifact_id=tb.artifact_id LEFT JOIN resource_decisions r ON r.theme_id=b.theme_id WHERE b.theme_id='TEMA_02' AND b.block_id LIKE '%KONUSMA%' LIMIT 1").fetchall())
    q.append(db.execute("SELECT b.block_id,n.block_id FROM blocks b LEFT JOIN blocks n ON n.block_order=b.block_order+1 AND n.theme_id=b.theme_id WHERE b.theme_id='TEMA_02' ORDER BY b.block_order LIMIT 1").fetchall())
    q.append(db.execute("SELECT t.theme_id,b.block_id,t.theme_order,b.block_order,t.school_based_hours FROM timeline_themes t JOIN timeline_blocks b ON b.theme_id=t.theme_id ORDER BY t.theme_order,b.block_order").fetchall())
    q.append(db.execute("SELECT r.decision_code,s.section_id,a.activity_id,r.app_category FROM resource_decisions r LEFT JOIN activities a ON a.theme_id=r.theme_id LEFT JOIN textbook_sections s ON s.section_id=a.section_id WHERE r.theme_id=? LIMIT 1",("TEMA_02",)).fetchall())
    q.append(db.execute("SELECT o.outcome_id,b.block_id,a.activity_id,f.form_id,aa.artifact_id,r.resource_plan_id FROM outcomes o LEFT JOIN block_outcomes bo ON bo.outcome_id=o.outcome_id LEFT JOIN blocks b ON b.block_id=bo.block_id LEFT JOIN activities a ON a.theme_id=o.theme_id LEFT JOIN activity_forms af ON af.activity_id=a.activity_id LEFT JOIN forms f ON f.form_id=af.form_id LEFT JOIN assessment_task_bindings tb ON tb.theme_id=o.theme_id LEFT JOIN assessment_artifacts aa ON aa.artifact_id=tb.artifact_id LEFT JOIN resource_decisions r ON r.theme_id=o.theme_id WHERE o.theme_id=? LIMIT 1",("TEMA_02",)).fetchall())
    for i,x in enumerate(q,1): check(f"application query {chr(64+i)}",bool(x),f"rows={len(x)}")
    names={x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}; check("copyright payload check", "text_body" not in names and "embeddings" not in names)
    check("user state excluded", not any(re.search(r"(student|teacher|user|note|preference|progress|app_state)",n,re.I) for n in names))
    check("vector/model dependency excluded", not any(re.search(r"(vector|embedding|onnx|model)",n,re.I) for n in names))
    db.close(); status="PASS" if all(x[1] for x in checks) else ("REVIEW_REQUIRED" if fresh else "FAIL")
    report=["# Runtime Course Package Validation Report","",f"**Final:** {status}","","| Check | Status | Detail |","|---|---|---|"]+[f"| {n} | {'PASS' if ok else 'FAIL'} | {d} |" for n,ok,d in checks]
    report += ["","## Row counts",""]+[f"- `{k}`: {v}" for k,v in mp.get("row_counts",{}).items()]
    if write_report: (out/"runtime_validation_report.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    return {"status":status,"checks":checks,"row_counts":mp.get("row_counts",{})}

def main() -> int:
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="command",required=True)
    for cmd in ("build","validate","status"):
        p=sub.add_parser(cmd); p.add_argument("--knowledge-root",required=True)
    a=ap.parse_args(); root=Path(a.knowledge_root)
    try:
        if a.command=="build": r=build(root); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r["status"]=="PASS" else 1
        if not (root/"runtime/runtime_manifest.json").exists(): print("RUNTIME_MISSING"); return 1
        m=read_json(root/"runtime/runtime_manifest.json"); fresh=compiler_state(root)[1]==m.get("canonical_content_fingerprint"); print("RUNTIME_FRESH" if fresh else "RUNTIME_STALE")
        if a.command=="validate": r=validate(root,write_report=True); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r["status"]=="PASS" else 1
        return 0 if fresh else 1
    except (KeyError,sqlite3.Error,ValueError) as e: print(f"FAIL_CLOSED: {e}",file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())