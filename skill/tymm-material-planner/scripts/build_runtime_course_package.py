#!/usr/bin/env python3
"""Compile verified canonical course JSON into an app-agnostic runtime SQLite package."""
from __future__ import annotations

import argparse, hashlib, json, re, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

COMPILER_VERSION = "1.0.0"
RUNTIME_PACKAGE_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"

SCHEMA = r'''
PRAGMA foreign_keys = ON;
CREATE TABLE courses (course_id TEXT PRIMARY KEY, grade INTEGER, title TEXT NOT NULL, schema_version TEXT NOT NULL, source_manifest_fingerprint TEXT NOT NULL);
CREATE TABLE themes (theme_id TEXT PRIMARY KEY, course_id TEXT NOT NULL REFERENCES courses(course_id), theme_order INTEGER NOT NULL, title TEXT NOT NULL, page_range TEXT, planned_hours INTEGER, anlama_hours INTEGER, anlatma_hours INTEGER, source_locator TEXT);
CREATE TABLE blocks (block_id TEXT PRIMARY KEY, theme_id TEXT NOT NULL REFERENCES themes(theme_id), block_order INTEGER NOT NULL, title TEXT NOT NULL, skill_domain TEXT, learning_area TEXT, planned_hours INTEGER, time_status TEXT, source_locators_json TEXT NOT NULL);
CREATE TABLE outcomes (outcome_id TEXT PRIMARY KEY, theme_id TEXT NOT NULL REFERENCES themes(theme_id), outcome_code TEXT NOT NULL, official_text TEXT NOT NULL, process_components TEXT, source_locator TEXT, verification_status TEXT);
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

def relevant_files(root: Path) -> list[Path]:
    paths = [root/n for n in ["curriculum_map.json","textbook_map.json","textbook_forms_index.json","source_manifest.json","planning/course_timeline.json","production/production_manifest.json","production/assessment_artifact_registry.json","production/assessment_design_contract.json","production/consolidated_resource_plan.json","production/teaching_blocks.json"]]
    paths += sorted(root.glob("themes/tema_*/alignment.json")) + sorted(root.glob("themes/tema_*/gap_analysis.json")) + sorted(root.glob("themes/tema_*/resource_plan.json")) + sorted(root.glob("themes/tema_*/needs.json"))
    return [p for p in paths if p.exists()]

def compiler_state(root: Path) -> tuple[dict[str, dict[str, Any]], str]:
    entries = {}
    for p in relevant_files(root):
        rel = p.relative_to(root).as_posix(); entries[rel] = {"path": rel, "sha256": sha256(p), "size_bytes": p.stat().st_size}
    canonical = "\n".join(f"{k}:{v['sha256']}" for k,v in sorted(entries.items()))
    return entries, hashlib.sha256(canonical.encode()).hexdigest()

def decision_category(code: str | None) -> str | None:
    return {"REUSE_TEXTBOOK":"BOOK_SUFFICIENT", "REUSE_WITH_TEACHER_GUIDE":"USE_EXISTING_TEXTBOOK_ACTIVITY", "ADAPT_TEXTBOOK_ACTIVITY":"USE_EXISTING_TEXTBOOK_ACTIVITY", "GENERATE_ASSESSMENT_SUPPORT":"ADDITIONAL_SUPPORT_REQUIRED", "GENERATE_DIFFERENTIATION":"ADDITIONAL_SUPPORT_REQUIRED", "GENERATE_ENRICHMENT":"ADDITIONAL_SUPPORT_REQUIRED", "GENERATE":"ADDITIONAL_SUPPORT_REQUIRED", "NO_ACTION":"BOOK_SUFFICIENT"}.get(code)

def build(root: Path) -> dict[str, Any]:
    root = root.resolve(); out = root / "runtime"; out.mkdir(exist_ok=True)
    curriculum, textbook, forms_data, manifest, timeline = [read_json(root/n) for n in ["curriculum_map.json","textbook_map.json","textbook_forms_index.json","source_manifest.json","planning/course_timeline.json"]]
    reg, prod, contract = [read_json(root/n) for n in ["production/assessment_artifact_registry.json","production/production_manifest.json","production/assessment_design_contract.json"]]
    teaching = read_json(root/"production/teaching_blocks.json")
    teaching_by_id = {b["block_id"]: b for b in teaching.get("blocks", [])}
    files, fingerprint = compiler_state(root)
    dbpath = out/"course_runtime.sqlite"; dbpath.unlink(missing_ok=True)
    db = sqlite3.connect(dbpath); db.execute("PRAGMA foreign_keys=ON"); db.executescript(SCHEMA)
    def ins(sql, vals): db.execute(sql, vals)
    course_id = curriculum["course_id"]
    ins("INSERT INTO courses VALUES (?,?,?,?,?)", (course_id, curriculum.get("grade"), curriculum.get("course_title"), SCHEMA_VERSION, fingerprint))
    # Forms are referenced while textbook activities are projected; load the
    # verified form index first so foreign-key checks remain active throughout.
    for f in sorted(forms_data["forms"],key=lambda x:x["form_id"]):
        ins("INSERT INTO forms VALUES (?,?,?,?,?,?,?,?,?)",(f["form_id"],f.get("title",f["form_id"]),f.get("structural_type"),f.get("assessment_type"),integer(f.get("printed_page")),integer(f.get("pdf_page")),f.get("evaluator"),forms_data.get("source_id"),f.get("verification_status")))
    theme_by_id = {x["theme_id"]: x for x in curriculum["themes"]}; textbook_themes = {x["theme_id"]: x for x in textbook["themes"]}; time_themes = {x["theme_id"]: x for x in timeline["themes"]}
    block_by_id = {}
    for t in curriculum["themes"]:
        tid=t["theme_id"]; th=textbook_themes.get(tid,{}); tt=time_themes.get(tid,{})
        ah=t.get("allocated_lesson_hours") or {}; ins("INSERT INTO themes VALUES (?,?,?,?,?,?,?,?,?)", (tid,course_id,t.get("theme_no"),t.get("exact_theme_name",t.get("theme_title",tid)),t.get("page_range"),integer(first(ah,"total","instructional_total")),integer(ah.get("anlama")),integer(ah.get("anlatma")),t.get("source_locator")))
        for o in t.get("learning_outcomes",[]):
            ins("INSERT INTO outcomes VALUES (?,?,?,?,?,?,?)", ((o.get("outcome_id") or f"{tid}::{o['outcome_code']}"),tid,o["outcome_code"],text(o.get("outcome_verbatim","")) or "",text(o.get("process_components_verbatim")),text(o.get("source_locator")),text(o.get("verification_status"))))
        for s in th.get("sections",[]):
            ins("INSERT INTO textbook_sections VALUES (?,?,?,?,?,?,?)", (s["section_id"],tid,s.get("section_title",s["section_id"]),s.get("genre"),s.get("printed_page_range"),s.get("pdf_page_range"),textbook.get("source_id")))
            for a in s.get("activities",[]):
                ins("INSERT INTO activities VALUES (?,?,?,?,?,?,?,?,?,?)", (a["activity_id"],s["section_id"],tid,a.get("exact_title",a["activity_id"]),a.get("activity_type"),a.get("student_action"),a.get("expected_product_or_evidence"),text(a.get("printed_page")),text(a.get("pdf_page")),a.get("verification_status")))
                for fid in a.get("related_forms",[]):
                    if fid in {f["form_id"] for f in forms_data["forms"]}: ins("INSERT OR IGNORE INTO activity_forms VALUES (?,?)",(a["activity_id"],fid))
        for b in tt.get("blocks",[]):
            bid=b["block_id"]; block_by_id[bid]=b; tb=teaching_by_id.get(bid,{}); ins("INSERT INTO blocks VALUES (?,?,?,?,?,?,?,?,?)",(bid,tid,b.get("block_order",b.get("block_sequence")),text(b.get("title",b.get("block_title",bid))) or bid,text(b.get("skill_domain")),text(b.get("learning_area")),integer(first(b,"planned_hours","approximate_lesson_hours")),text(b.get("time_status",b.get("lesson_hours_status"))),j(b.get("source_locators",[]))))
            outcomes_by_key={(o["outcome_code"],tid):o["outcome_id"] for o in t.get("learning_outcomes",[])}
            block_outcome_codes=tb.get("curriculum_outcomes", b.get("outcomes",b.get("curriculum_outcomes",[])))
            for code in block_outcome_codes:
                if (code,tid) not in outcomes_by_key: raise ValueError(f"unknown canonical outcome relation: {bid} -> {code} in {tid}")
                ins("INSERT INTO block_outcomes VALUES (?,?)",(bid,outcomes_by_key[(code,tid)]))
            for aid in tb.get("textbook_activity_ids",[]):
                if aid in {a[0] for a in db.execute("SELECT activity_id FROM activities")}: 
                    ins("INSERT OR IGNORE INTO block_activities VALUES (?,?)",(bid,aid))
                    for code in block_outcome_codes:
                        oid=outcomes_by_key.get((code,tid));
                        if oid: ins("INSERT OR IGNORE INTO activity_outcomes VALUES (?,?)",(aid,oid))
            for fid in tb.get("textbook_form_ids",[]):
                if fid in {f["form_id"] for f in forms_data["forms"]}:
                    for aid in tb.get("textbook_activity_ids",[]): ins("INSERT OR IGNORE INTO activity_forms VALUES (?,?)",(aid,fid))
        ins("INSERT INTO timeline_themes VALUES (?,?,?,?,?,?,?)",(tid,t.get("theme_no"),integer(tt.get("official_total_hours")),integer(tt.get("core_instruction_hours")),integer(tt.get("school_based_hours")),tt.get("school_based_hours_status"),j(tt.get("source_locators",[]))))
        for b in tt.get("blocks",[]): ins("INSERT INTO timeline_blocks VALUES (?,?,?,?,?,?)",(b["block_id"],tid,b.get("block_order"),integer(b.get("planned_hours")),b.get("time_status"),j(b.get("source_locators",[]))))
    # Canonical resource plans are intentionally projected without generating new resources.
    for p in sorted(root.glob("themes/tema_*/resource_plan.json")):
        d=read_json(p); tid=d.get("theme_id"); arr=d.get("resources",d.get("resource_plans",[]))
        for r in arr:
            code=r.get("production_decision") or r.get("decision") or r.get("production_decision_code")
            ins("INSERT INTO resource_decisions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(r.get("resource_plan_id"),tid,r.get("need_id"),r.get("resource_type"),code,decision_category(code),r.get("priority"),r.get("purpose") or r.get("rationale"),r.get("expected_student_evidence"),r.get("textbook_coverage"),r.get("textbook_resource_locator"),1 if r.get("teacher_review_required") else 0))
    for a in reg.get("annual_artifacts",[]):
        ins("INSERT INTO assessment_artifacts VALUES (?,?,?,?,?,?,?,?,?,?,?)",(a["artifact_id"],a.get("title",a["artifact_id"]),a.get("skill_domain"),a.get("scope"),a.get("assessment_family"),a.get("reuse_policy"),a.get("generation_priority"),a.get("generation_status"),1 if a.get("teacher_review_required") else 0,j(a.get("covered_themes",[])),j(a.get("covered_gap_instances",[]))))
        for b in a.get("task_bindings",[]):
            ins("INSERT INTO assessment_task_bindings VALUES (?,?,?,?,?,?,?,?,?,?)",(a["artifact_id"],b.get("gap_instance_id"),b.get("theme_id"),b.get("block_id"),b.get("activity_id"),j(b.get("targeted_outcomes",[])),b.get("task_title"),b.get("evidence_being_observed"),b.get("textbook_locator"),b.get("curriculum_locator")))
    for m in prod.get("gap_instance_provenance_registry",[]):
        ins("INSERT INTO assessment_gap_mappings VALUES (?,?,?,?,?,?,?)",(m["gap_instance_id"],m["resolved_artifact_id"],m["theme_id"],m.get("resource_plan_id"),m.get("official_requirement_verbatim"),m.get("exact_remaining_gap"),j(m.get("source_locators",{}))))
    for s in manifest.get("sources",[]):
        ins("INSERT INTO source_references VALUES (?,?,?,?,?,?,?)",(s["source_id"],s.get("source_type"),s.get("title",s["source_id"]),None,s.get("source_type"),s.get("authority_rank"),s.get("verification_status")))
    # Stable source links are added only where the canonical locator is already present.
    for t in curriculum["themes"]:
        sid=curriculum.get("source_id"); loc=t.get("source_locator");
        if sid and loc: ins("INSERT OR IGNORE INTO entity_source_references VALUES (?,?,?,?)",("theme",t["theme_id"],sid,loc))
    db.commit(); db.close()
    count_db=sqlite3.connect(dbpath)
    counts={table: count_db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ["courses","themes","blocks","block_activities","outcomes","block_outcomes","textbook_sections","activities","activity_outcomes","forms","activity_forms","resource_decisions","assessment_artifacts","assessment_gap_mappings","assessment_task_bindings","timeline_themes","timeline_blocks","source_references","entity_source_references"]}
    count_db.close()
    now=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
    runtime_manifest={"runtime_package_version":RUNTIME_PACKAGE_VERSION,"schema_version":SCHEMA_VERSION,"course_id":course_id,"grade":curriculum.get("grade"),"build_timestamp":now,"compiler_version":COMPILER_VERSION,"canonical_source_files":sorted(files),"canonical_source_hashes":{k:v["sha256"] for k,v in sorted(files.items())},"canonical_content_fingerprint":fingerprint,"row_counts":counts,"timeline_resolution":timeline.get("timeline_resolution"),"timeline_unresolved_fields":{"weekly_lesson_hours":timeline.get("calendar_binding",{}).get("weekly_lesson_hours"),"calendar_binding":timeline.get("calendar_binding",{}).get("status"),"block_hours":"ORDER_ONLY"},"assessment_registry_version":reg.get("registry_version"),"assessment_contract_version":contract.get("metadata",{}).get("contract_version"),"source_manifest_fingerprint":next((x["sha256"] for k,x in files.items() if k=="source_manifest.json"),None),"runtime_database_path":"runtime/course_runtime.sqlite","validation_status":"PENDING"}
    (out/"runtime_schema.sql").write_text(SCHEMA.strip()+"\n",encoding="utf-8"); (out/"runtime_manifest.json").write_text(json.dumps(runtime_manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    result=validate(root, write_report=True); runtime_manifest["validation_status"]=result["status"]; (out/"runtime_manifest.json").write_text(json.dumps(runtime_manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result

def validate(root: Path, write_report: bool=False) -> dict[str,Any]:
    root=root.resolve(); out=root/"runtime"; mp=read_json(out/"runtime_manifest.json")
    db=sqlite3.connect(out/"course_runtime.sqlite"); db.execute("PRAGMA foreign_keys=ON")
    checks=[]
    def check(name, ok, detail=""): checks.append((name,bool(ok),detail))
    check("schema validation", all(db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()), "runtime schema loaded")
    check("foreign key integrity", db.execute("PRAGMA foreign_key_check").fetchall()==[], "PRAGMA foreign_key_check")
    for table,col in [("themes","theme_id"),("blocks","block_id"),("outcomes","outcome_id"),("activities","activity_id"),("forms","form_id"),("assessment_artifacts","artifact_id")]: check(f"canonical ID uniqueness: {table}", db.execute(f"SELECT {col},COUNT(*) FROM {table} GROUP BY {col} HAVING COUNT(*)>1").fetchall()==[])
    orphan=db.execute("SELECT COUNT(*) FROM assessment_gap_mappings g LEFT JOIN assessment_artifacts a ON a.artifact_id=g.artifact_id WHERE a.artifact_id IS NULL").fetchone()[0]; check("orphan relations",orphan==0,str(orphan))
    fresh=compiler_state(root)[1]==mp.get("canonical_content_fingerprint"); check("source fingerprint status",fresh,"RUNTIME_FRESH" if fresh else "RUNTIME_STALE")
    check("timeline projection status", db.execute("SELECT COUNT(*) FROM timeline_blocks WHERE planned_hours IS NOT NULL").fetchone()[0]==0, "block hours remain ORDER_ONLY")
    check("assessment mapping status", db.execute("SELECT COUNT(*) FROM assessment_gap_mappings").fetchone()[0]>0)
    check("resource decision projection status", db.execute("SELECT COUNT(*) FROM resource_decisions").fetchone()[0]>0)
    # Five application acceptance queries; each returns deterministic entity classes.
    q=[]
    q.append(db.execute("SELECT b.block_id,o.outcome_code,a.activity_id,a.printed_page,f.form_id,aa.artifact_id,r.decision_code FROM blocks b LEFT JOIN block_outcomes bo ON bo.block_id=b.block_id LEFT JOIN outcomes o ON o.outcome_id=bo.outcome_id LEFT JOIN block_activities ba ON ba.block_id=b.block_id LEFT JOIN activities a ON a.activity_id=ba.activity_id LEFT JOIN activity_forms af ON af.activity_id=a.activity_id LEFT JOIN forms f ON f.form_id=af.form_id LEFT JOIN assessment_task_bindings tb ON tb.block_id=b.block_id LEFT JOIN assessment_artifacts aa ON aa.artifact_id=tb.artifact_id LEFT JOIN resource_decisions r ON r.theme_id=b.theme_id WHERE b.theme_id='TEMA_02' AND b.block_id LIKE '%KONUSMA%' LIMIT 1").fetchall())
    q.append(db.execute("SELECT b.block_id,n.block_id FROM blocks b LEFT JOIN blocks n ON n.block_order=b.block_order+1 AND n.theme_id=b.theme_id WHERE b.block_id=?",("BLOCK_T2_02_KONUSMA",)).fetchall())
    q.append(db.execute("SELECT t.theme_id,b.block_id,t.theme_order,b.block_order,t.school_based_hours FROM timeline_themes t JOIN timeline_blocks b ON b.theme_id=t.theme_id ORDER BY t.theme_order,b.block_order").fetchall())
    q.append(db.execute("SELECT r.decision_code,s.section_id,a.activity_id,r.app_category FROM resource_decisions r LEFT JOIN activities a ON a.theme_id=r.theme_id LEFT JOIN textbook_sections s ON s.section_id=a.section_id WHERE r.theme_id=? LIMIT 1",("TEMA_02",)).fetchall())
    q.append(db.execute("SELECT o.outcome_id,b.block_id,a.activity_id,f.form_id,aa.artifact_id,r.resource_plan_id,s.source_id FROM outcomes o LEFT JOIN block_outcomes bo ON bo.outcome_id=o.outcome_id LEFT JOIN blocks b ON b.block_id=bo.block_id LEFT JOIN activities a ON a.theme_id=o.theme_id LEFT JOIN activity_forms af ON af.activity_id=a.activity_id LEFT JOIN forms f ON f.form_id=af.form_id LEFT JOIN assessment_task_bindings tb ON tb.theme_id=o.theme_id LEFT JOIN assessment_artifacts aa ON aa.artifact_id=tb.artifact_id LEFT JOIN resource_decisions r ON r.theme_id=o.theme_id LEFT JOIN entity_source_references es ON es.entity_id=o.theme_id LEFT JOIN source_references s ON s.source_id=es.source_id WHERE o.theme_id=? LIMIT 1",("TEMA_02",)).fetchall())
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
