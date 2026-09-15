#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

PAGE_RE = re.compile(r"^\s*(\d+)\s*(?:[-–—]\s*(\d+)\s*)?$")
Q_RANGE_RE = re.compile(r"(?:^|_)Q(\d+)_(\d+)(?:_|$)")
LABEL_RANGE_RE = re.compile(r"(\d+)\s*[-–—]\s*(\d+)\.?\s*soru", re.I)
FIELDS = ("teacher_moves","follow_up_questions","misconception_interventions","board_notes","assessment_look_fors","support","enrichment")
MAX_COUNTS = {"teacher_moves":4,"follow_up_questions":4,"misconception_interventions":3,"board_notes":2,"assessment_look_fors":4,"support":2,"enrichment":2}
REPEAT_LIMITS = {"teacher_moves":3,"follow_up_questions":3,"misconception_interventions":3,"board_notes":2,"assessment_look_fors":3,"support":3,"enrichment":3}

def read_json(p: Path) -> dict[str, Any]: return json.loads(p.read_text(encoding="utf-8"))
def nonempty(v: Any) -> bool:
    if v is None: return False
    if isinstance(v,str): return bool(v.strip())
    if isinstance(v,(list,dict)): return bool(v)
    return True

def parse_range(v: str) -> tuple[int,int]:
    m=PAGE_RE.match(v)
    if not m: raise ValueError(v)
    a,b=int(m.group(1)),int(m.group(2) or m.group(1))
    if b<a: raise ValueError(v)
    return a,b

def intersects(a: str,b: str)->bool:
    a0,a1=parse_range(a); b0,b1=parse_range(b); return max(a0,b0)<=min(a1,b1)

def classify_phase(section_type: str,title: str)->str:
    if section_type=="THEME_OPENING": return "opening"
    if section_type=="THEME_ASSESSMENT": return "assessment"
    t=title.casefold()
    if any(k in t for k in ("yönet","hazır","planla")): return "manage"
    if any(k in t for k in ("değerl","yansıt","öz değerlend","kontrol")): return "reflect"
    if section_type in {"SPEAKING","WRITING"}: return "analyze_apply"
    if any(k in t for k in ("çözüm","kural","uygula","gerçekleştir")): return "analyze_apply"
    return "meaning"

def question_range(item: dict[str,Any])->tuple[int,int]|None:
    m=Q_RANGE_RE.search(str(item.get("item_id",""))) or LABEL_RANGE_RE.search(str(item.get("label","")))
    if not m:return None
    a,b=int(m.group(1)),int(m.group(2)); return (a,b) if b>=a else None

def split_answers(item: dict[str,Any])->list[tuple[str,Any,str|None]]|None:
    if item.get("item_type")!="QUESTION": return None
    ans=item.get("expected_answer")
    if not nonempty(ans): ans=item.get("expected_response")
    if not nonempty(ans): return None
    if isinstance(ans,dict) and len(ans)>1 and all(re.fullmatch(r"\d+",str(k)) for k in ans):
        return [(str(k),v,None) for k,v in sorted(((int(str(k)),v) for k,v in ans.items()),key=lambda x:x[0])]
    qr=question_range(item)
    if not qr:return None
    a,b=qr; nums=[str(i) for i in range(a,b+1)]; n=len(nums)
    if isinstance(ans,dict) and len(ans)==n:return [(num,val,str(key)) for num,(key,val) in zip(nums,ans.items())]
    if isinstance(ans,list) and len(ans)==n:return [(num,val,None) for num,val in zip(nums,ans)]
    return None

def expected_specs(item: dict[str,Any])->list[dict[str,Any]]:
    split=split_answers(item); iid=item["item_id"]
    if split:return [{"task_id":f"{iid}#Q{n}","question_number":n,"expected_answer":a,"expected_response":None,"answer_component_key":k,"split_from_group":True} for n,a,k in split]
    return [{"task_id":iid,"question_number":None,"expected_answer":item.get("expected_answer"),"expected_response":item.get("expected_response"),"answer_component_key":None,"split_from_group":False}]

def values(block: dict[str,Any],field: str)->list[str]:
    if field in {"support","enrichment"}:
        d=block.get("differentiation"); x=d.get(field,[]) if isinstance(d,dict) else []
    else:x=block.get(field,[])
    return x if isinstance(x,list) else []
def fingerprint(block: dict[str,Any])->tuple[Any,...]: return tuple(tuple(values(block,f)) for f in FIELDS)

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",type=Path,default=Path(".")); ap.add_argument("--overlay",default="courses/TDE_11/teacher_guide/TEMA_01/pedagogy_v2.json"); ap.add_argument("--manifest",default="courses/TDE_11/teacher_guide/TEMA_01/teacher_guide.json"); ap.add_argument("--schema",default="skill/tymm-material-planner/schemas/teacher_guide_pedagogy_overlay.schema.json"); ap.add_argument("--profiles",default="skill/tymm-material-planner/data/teacher_guide_v2_profiles.json"); ap.add_argument("--markdown",default=None); a=ap.parse_args(); root=a.repo_root.resolve()
    op=root/a.overlay; mp=root/a.manifest; sp=root/a.schema; mdp=root/a.markdown if a.markdown else op.with_name("TEACHER_GUIDE_V2.md"); failures=[]; warnings=[]
    for p,label in ((op,"overlay"),(mp,"manifest"),(sp,"schema")):
        if not p.is_file():failures.append(f"MISSING_{label.upper()}:{p}")
    if failures:print(json.dumps({"status":"FAIL","failures":failures},ensure_ascii=False,indent=2));return 1
    overlay=read_json(op); manifest=read_json(mp); schema=read_json(sp); version=overlay.get("schema_version"); v21=version in {"2.1.0","2.2.0"}; v22=version=="2.2.0"; profiles=read_json(root/a.profiles) if v22 and (root/a.profiles).is_file() else None; markdown=mdp.read_text(encoding="utf-8") if v21 and mdp.is_file() else ""
    if v21 and not mdp.is_file():failures.append(f"MISSING_TEACHER_MARKDOWN:{mdp}")
    if v22 and profiles is None:failures.append(f"MISSING_PROFILES:{root/a.profiles}")
    for err in sorted(Draft202012Validator(schema).iter_errors(overlay),key=lambda e:list(e.absolute_path)):
        failures.append(f"SCHEMA:{'.'.join(map(str,err.absolute_path)) or '$'}:{err.message}")
    if overlay.get("course_id")!=manifest.get("course_id"):failures.append("COURSE_ID_MISMATCH")
    if overlay.get("theme_id")!=manifest.get("theme_id"):failures.append("THEME_ID_MISMATCH")
    if v22 and overlay.get("status")=="REFERENCE_QUALITY":
        review=overlay.get("quality_review")
        if not isinstance(review,dict) or review.get("decision")!="APPROVED":failures.append("REFERENCE_QUALITY_REQUIRES_EXPLICIT_APPROVED_REVIEW")

    sections={};items={}
    for idx in manifest.get("sections",[]):
        sid,ref=idx.get("section_id"),idx.get("content_ref")
        if not isinstance(sid,str) or not isinstance(ref,str):failures.append(f"INVALID_MANIFEST_SECTION:{idx!r}");continue
        p=root/ref
        if not p.is_file():failures.append(f"MISSING_SECTION:{ref}");continue
        sec=read_json(p);sections[sid]=sec
        for unit in sec.get("guide_units",[]):
            for item in unit.get("items",[]):
                iid=item.get("item_id")
                if not isinstance(iid,str) or not iid:failures.append(f"ITEM_WITHOUT_ID:{ref}");continue
                if iid in items:failures.append(f"DUPLICATE_CANONICAL_ITEM:{iid}");continue
                items[iid]={"section_id":sid,"pages":item.get("printed_page_range"),"item":item}

    refs=[];cards_by_id={};block_ids=set();by_section=defaultdict(list);sentence_counts={f:Counter() for f in REPEAT_LIMITS};fp_seen=defaultdict(dict);blocks=overlay.get("blocks",[]) if isinstance(overlay.get("blocks"),list) else []
    phase_templates={f:{text for ph in (profiles or {}).get("phase_profiles",{}).values() if isinstance(ph,dict) for text in ph.get(f,[]) if isinstance(text,str)} for f in REPEAT_LIMITS}
    theme_profiles=(profiles or {}).get("section_profiles",{}).get(overlay.get("theme_id"),{}) if isinstance(profiles,dict) else {}

    for block in blocks:
        if not isinstance(block,dict):failures.append("INVALID_BLOCK_OBJECT");continue
        bid=block.get("block_id");sid=block.get("section_id");pages=block.get("printed_page_range")
        if isinstance(bid,str):
            if bid in block_ids:failures.append(f"DUPLICATE_BLOCK_ID:{bid}")
            block_ids.add(bid)
        sec=sections.get(sid)
        if sec is None:failures.append(f"UNKNOWN_SECTION_REF:{bid}:{sid}")
        else:by_section[sid].append(block)
        if not block.get("teacher_moves"):failures.append(f"TEACHER_MOVES_REQUIRED:{bid}")
        if not block.get("follow_up_questions"):warnings.append(f"NO_FOLLOW_UP_QUESTIONS:{bid}")
        if not block.get("misconception_interventions"):warnings.append(f"NO_MISCONCEPTION_INTERVENTION:{bid}")
        for note in values(block,"board_notes"):
            if not isinstance(note,str) or not note.startswith("Tahtaya yaz:"):failures.append(f"INVALID_BOARD_NOTE:{bid}:{note!r}")

        if v22 and sec is not None:
            expected=classify_phase(str(sec.get("section_type","")),str(block.get("title","")))
            if block.get("phase_name")!=expected:failures.append(f"PHASE_MISMATCH:{bid}:{block.get('phase_name')}!={expected}")
            if sec.get("section_type") in {"SPEAKING","WRITING"} and block.get("phase_name")=="meaning":failures.append(f"PRODUCTION_SKILL_MISCLASSIFIED_AS_MEANING:{bid}")
            sec_prof=theme_profiles.get(sid,{}) if isinstance(theme_profiles,dict) else {}
            for field,maximum in MAX_COUNTS.items():
                vals=values(block,field);curated=set(sec_prof.get(field,[])) if isinstance(sec_prof,dict) and isinstance(sec_prof.get(field,[]),list) else set()
                if len(vals)>maximum:failures.append(f"PEDAGOGY_FIELD_TOO_DENSE:{bid}:{field}:{len(vals)}>{maximum}")
                for text in vals:
                    if isinstance(text,str):
                        sentence_counts[field][text]+=1
                        if text in phase_templates.get(field,set()) and text not in curated:failures.append(f"UNCONTEXTUALIZED_PHASE_TEMPLATE:{bid}:{field}:{text}")
            if values(block,"board_notes"):
                curated=set(sec_prof.get("board_notes",[])) if isinstance(sec_prof,dict) else set()
                for note in values(block,"board_notes"):
                    if note not in curated:failures.append(f"NON_CURATED_BOARD_NOTE:{bid}:{note}")
            fp=fingerprint(block);prev=fp_seen[sid].get(fp)
            if prev:failures.append(f"DUPLICATE_PEDAGOGICAL_PACKAGE:{sid}:{prev}:{bid}")
            else:fp_seen[sid][fp]=str(bid)

        source_refs=block.get("source_item_refs",[])
        if not isinstance(source_refs,list) or not source_refs:failures.append(f"SOURCE_ITEM_REFS_REQUIRED:{bid}");continue
        for iid in source_refs:
            if not isinstance(iid,str):failures.append(f"INVALID_SOURCE_ITEM_REF:{bid}:{iid!r}");continue
            refs.append(iid);canon=items.get(iid)
            if canon is None:failures.append(f"UNKNOWN_SOURCE_ITEM_REF:{bid}:{iid}");continue
            if canon["section_id"]!=sid:failures.append(f"SOURCE_ITEM_SECTION_MISMATCH:{bid}:{iid}")
            if isinstance(pages,str) and isinstance(canon["pages"],str):
                try:
                    if not intersects(pages,canon["pages"]):failures.append(f"SOURCE_ITEM_PAGE_MISMATCH:{bid}:{iid}:block={pages}:item={canon['pages']}")
                except ValueError:failures.append(f"INVALID_PAGE_RANGE:{bid}:{pages}:{canon['pages']}")

        if v21:
            cards=block.get("task_cards")
            if not isinstance(cards,list) or not cards:failures.append(f"TASK_CARDS_REQUIRED:{bid}")
            else:
                card_refs=Counter()
                for card in cards:
                    if not isinstance(card,dict):failures.append(f"INVALID_TASK_CARD:{bid}");continue
                    tid=card.get("task_id");src=card.get("source_item_ref")
                    if not isinstance(tid,str) or not tid:failures.append(f"TASK_ID_REQUIRED:{bid}");continue
                    if tid in cards_by_id:failures.append(f"DUPLICATE_TASK_ID:{tid}")
                    cards_by_id[tid]=card
                    if isinstance(src,str):card_refs[src]+=1
                    if src not in source_refs:failures.append(f"TASK_CARD_SOURCE_NOT_IN_BLOCK:{bid}:{tid}:{src}")
                    canon=items.get(src) if isinstance(src,str) else None
                    if canon is None:failures.append(f"TASK_CARD_UNKNOWN_SOURCE:{bid}:{tid}:{src}");continue
                    item=canon["item"]
                    for cf,srcf,label in (("acceptance_criteria","acceptance_criteria","ACCEPTANCE"),("canonical_teacher_guidance","teacher_guidance","TEACHER_GUIDANCE"),("canonical_common_misconceptions","common_misconceptions","MISCONCEPTION"),("canonical_assessment_evidence","assessment_evidence","ASSESSMENT"),("canonical_differentiation","differentiation","DIFFERENTIATION")):
                        if card.get(cf)!=item.get(srcf):failures.append(f"TASK_CARD_{label}_DRIFT:{tid}")
                for iid in source_refs:
                    if card_refs[iid]==0:failures.append(f"SOURCE_ITEM_WITHOUT_TASK_CARD:{bid}:{iid}")

    c=Counter(refs);missing=sorted(set(items)-set(refs));dup=sorted(i for i,n in c.items() if n>1)
    if missing:failures.append("UNCOVERED_CANONICAL_ITEMS:"+", ".join(missing))
    if dup:failures.append("MULTI_COVERED_CANONICAL_ITEMS:"+", ".join(dup))

    if v21:
        specs={}
        for iid,canon in items.items():
            for spec in expected_specs(canon["item"]):specs[spec["task_id"]]=(iid,canon["item"],spec)
        mt=sorted(set(specs)-set(cards_by_id));ut=sorted(set(cards_by_id)-set(specs))
        if mt:failures.append("MISSING_FIRST_CLASS_TASKS:"+", ".join(mt))
        if ut:failures.append("UNEXPECTED_TASK_CARDS:"+", ".join(ut))
        unanswered=set()
        for tid,(iid,item,spec) in specs.items():
            card=cards_by_id.get(tid)
            if card is None:continue
            for field in ("question_number","split_from_group","expected_answer","expected_response"):
                if card.get(field)!=spec[field]:failures.append(f"{field.upper()}_DRIFT:{tid}")
            if spec.get("answer_component_key") is not None and card.get("answer_component_key")!=spec["answer_component_key"]:failures.append(f"ANSWER_COMPONENT_KEY_DRIFT:{tid}")
            has_ans=nonempty(spec["expected_answer"]) or nonempty(spec["expected_response"])
            if item.get("item_type")=="QUESTION" and not has_ans:unanswered.add(iid)
            if has_ans and f"<!-- answer:{tid} -->" not in markdown:failures.append(f"ANSWER_NOT_RENDERED_TO_MARKDOWN:{tid}")
            if f"<!-- task:{tid} -->" not in markdown:failures.append(f"TASK_NOT_RENDERED_TO_MARKDOWN:{tid}")
        warnings.extend(f"QUESTION_WITHOUT_CANONICAL_ANSWER:{i}" for i in sorted(unanswered))
        for iid,canon in items.items():
            if split_answers(canon["item"]) and iid in cards_by_id:failures.append(f"BUNDLED_QUESTION_NOT_SPLIT:{iid}")

    if v22 and isinstance(profiles,dict):
        if not isinstance(theme_profiles,dict):failures.append(f"MISSING_THEME_PROFILES:{overlay.get('theme_id')}")
        else:
            for sid,prof in theme_profiles.items():
                if not isinstance(prof,dict) or sid not in sections:continue
                sec_blocks=by_section.get(sid,[])
                for field in (*FIELDS,"source_limitations"):
                    expected=prof.get(field,[])
                    if not isinstance(expected,list):continue
                    if field=="board_notes":expected=expected[:2*len(sec_blocks)]
                    actual=[]
                    for b in sec_blocks:
                        actual.extend((b.get(field,[]) if isinstance(b.get(field),list) else []) if field=="source_limitations" else values(b,field))
                    for entry in expected:
                        if isinstance(entry,str) and entry.strip() and actual.count(entry)!=1:failures.append(f"SECTION_GUIDANCE_NOT_EXACTLY_ONCE:{sid}:{field}:{actual.count(entry)}:{entry}")
        for field,limit in REPEAT_LIMITS.items():
            for text,count in sentence_counts[field].items():
                if count>limit:failures.append(f"PEDAGOGY_TEXT_OVERREPEATED:{field}:{count}>{limit}:{text}")
        intents=defaultdict(Counter)
        for b in blocks:
            if isinstance(b,dict) and isinstance(b.get("section_id"),str) and isinstance(b.get("pedagogical_intent"),str):intents[b["section_id"]][b["pedagogical_intent"]]+=1
        for sid,counter in intents.items():
            for text,count in counter.items():
                if count>1:failures.append(f"DUPLICATE_PEDAGOGICAL_INTENT:{sid}:{count}:{text}")

    for block in blocks:
        if not isinstance(block,dict):continue
        bid=block.get("block_id","<unknown>")
        if not block.get("assessment_look_fors"):failures.append(f"ASSESSMENT_LOOK_FORS_REQUIRED:{bid}")
        d=block.get("differentiation")
        if not isinstance(d,dict):failures.append(f"DIFFERENTIATION_REQUIRED:{bid}");continue
        if not d.get("support"):failures.append(f"SUPPORT_SCAFFOLD_REQUIRED:{bid}")
        if not d.get("enrichment"):failures.append(f"ENRICHMENT_REQUIRED:{bid}")

    status="FAIL" if failures else "PASS_WITH_WARNINGS" if warnings else "PASS";report={"status":status,"course_id":overlay.get("course_id"),"theme_id":overlay.get("theme_id"),"schema_version":version,"overlay_status":overlay.get("status"),"canonical_item_count":len(items),"covered_item_count":len(set(refs)&set(items)),"task_card_count":len(cards_by_id) if v21 else None,"question_task_card_count":sum(1 for x in cards_by_id.values() if x.get("item_type")=="QUESTION") if v21 else None,"block_count":len(blocks),"blocks_with_board_notes":sum(1 for b in blocks if isinstance(b,dict) and b.get("board_notes")),"semantic_quality_gates":v22,"failures":failures,"warnings":warnings};print(json.dumps(report,ensure_ascii=False,indent=2));return 1 if failures else 0
if __name__=="__main__":sys.exit(main())
