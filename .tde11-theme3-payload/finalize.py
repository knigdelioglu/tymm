#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path.cwd()
COURSE = ROOT / "courses/TDE_11"
SCRIPTS = ROOT / "skill/tymm-material-planner/scripts"
COMMIT_SHA = os.environ["GITHUB_SHA"]
BRANCH = os.environ["GITHUB_REF_NAME"]
EXPECTED_PAYLOAD_B64_LEN = 29272
EXPECTED_PAYLOAD_SHA256 = "7ef00309b34d160a213d25f8c90b64dcbdfe7bbe28cc054f902c7b56c2fe9ff6"


def run(*args: str, capture: bool = False) -> str:
    print("+", " ".join(args), flush=True)
    result = subprocess.run(args, cwd=ROOT, check=True, text=True,
                            capture_output=capture)
    if capture:
        print(result.stdout, end="")
        return result.stdout
    return ""


# Restore the locally prepared, PDF-grounded Theme 3 guide bundle. Fail before
# touching source files if transport is incomplete or corrupted.
chunks = sorted((ROOT / ".tde11-theme3-payload").glob("payload_*"))
if len(chunks) != 8:
    raise SystemExit(f"Theme 3 payload chunk count mismatch: expected 8, got {len(chunks)}")
encoded = "".join(p.read_text(encoding="utf-8") for p in chunks)
if len(encoded) != EXPECTED_PAYLOAD_B64_LEN:
    raise SystemExit(
        f"Theme 3 payload length mismatch: expected {EXPECTED_PAYLOAD_B64_LEN}, got {len(encoded)}"
    )
try:
    decoded = base64.b64decode(encoded, validate=True)
except Exception as exc:
    raise SystemExit(f"Theme 3 payload base64 validation failed: {exc}") from exc
digest = hashlib.sha256(decoded).hexdigest()
if digest != EXPECTED_PAYLOAD_SHA256:
    raise SystemExit(
        f"Theme 3 payload SHA-256 mismatch: expected {EXPECTED_PAYLOAD_SHA256}, got {digest}"
    )
print(f"PAYLOAD_VERIFIED chunks={len(chunks)} b64_len={len(encoded)} sha256={digest}")
tar_path = Path("/tmp/t3-guide-payload.tar.gz")
tar_path.write_bytes(decoded)
with tarfile.open(tar_path, "r:gz") as archive:
    archive.extractall(ROOT)

sys.path.insert(0, str(SCRIPTS))
import render_lesson_plan_markdown  # noqa: E402

# Same generator sequence shift previously repaired in Themes 1 and 2.
repairs = {
    "generated/lesson_plans/TEMA_03/BLOCK_T3_01_OKUMA/BLOCK_T3_01_OKUMA_P02.json": "TDE2.2",
    "generated/lesson_plans/TEMA_03/BLOCK_T3_01_OKUMA/BLOCK_T3_01_OKUMA_P03.json": "TDE2.3",
    "generated/lesson_plans/TEMA_03/BLOCK_T3_01_OKUMA/BLOCK_T3_01_OKUMA_P04.json": "TDE2.4",
    "generated/lesson_plans/TEMA_03/BLOCK_T3_01_OKUMA/BLOCK_T3_01_OKUMA_P05.json": "TDE2.1",
    "generated/lesson_plans/TEMA_03/BLOCK_T3_01_OKUMA/BLOCK_T3_01_OKUMA_P06.json": "TDE2.2",
    "generated/lesson_plans/TEMA_03/BLOCK_T3_01_OKUMA/BLOCK_T3_01_OKUMA_P07.json": "TDE2.3",
    "generated/lesson_plans/TEMA_03/BLOCK_T3_04_YAZMA/BLOCK_T3_04_YAZMA_P04.json": "TDE4.4",
}
for rel, outcome in repairs.items():
    path = COURSE / rel
    plan = json.loads(path.read_text(encoding="utf-8"))
    plan["outcome_codes"] = [outcome]
    if "assessed_outcome_codes" in plan:
        plan["assessed_outcome_codes"] = [outcome]
    for lesson in plan.get("lessons", []):
        lesson["outcome_codes"] = [outcome]
        if "assessed_outcome_codes" in lesson:
            lesson["assessed_outcome_codes"] = [outcome]
    continuation = plan.get("continuation_summary")
    if isinstance(continuation, dict):
        continuation["covered_outcome_codes"] = [outcome]
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    path.with_suffix(".md").write_text(render_lesson_plan_markdown.render(plan), encoding="utf-8")

manifest_path = COURSE / "teacher_guide/TEMA_03/teacher_guide.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
resolved_ids = {
    "T3_ISSUE_READING_PLAN_SEQUENCE_OUTCOME_MISMATCH",
    "T3_ISSUE_LP_YAZMA_P04_OUTCOME_MISMATCH",
}
found = set()
for issue in manifest.get("known_issues", []):
    if issue.get("issue_id") in resolved_ids:
        issue["status"] = "RESOLVED"
        found.add(issue["issue_id"])
if found != resolved_ids:
    raise SystemExit(f"missing known issues: {sorted(resolved_ids - found)}")
for phase in manifest.get("production_plan", []):
    if phase.get("phase") == 3:
        phase["status"] = "VERIFIED"
manifest["validation_contract"]["current_status"] = "PASS_WITH_WARNINGS"
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Deterministic plan parity first.
run(sys.executable, str(SCRIPTS / "validate_lesson_plan_markdown.py"),
    "--knowledge-root", str(COURSE), "--report", "/tmp/tde11-markdown-parity.json")
run(sys.executable, str(SCRIPTS / "resolve_course_timeline_hours.py"),
    "--knowledge-root", str(COURSE))

# Seal-safe repair sequence: build canonical runtime while temporarily skipping
# the stale lesson-plan projection, validate all plans, reseal, then rebuild the
# normal runtime with lesson-plan payloads enabled.
import build_runtime_course_package as runtime  # noqa: E402
runtime.project_runtime_lesson_plan_payload = lambda root: {"status": "PROVISIONAL_SKIP"}
result = runtime.build(COURSE)
if result.get("status") != "PASS":
    raise SystemExit(f"provisional runtime failed: {result}")
print("PROVISIONAL_RUNTIME_PASS")

run(sys.executable, str(SCRIPTS / "validate_all_lesson_plans.py"),
    "--knowledge-root", str(COURSE), "--commit-sha", COMMIT_SHA,
    "--report", "/tmp/tde11-lesson-plan-validation.json")
report = json.loads(Path("/tmp/tde11-lesson-plan-validation.json").read_text(encoding="utf-8"))
assert report["status"] == "PASS", report
assert report["summary"]["packages"] == 88, report["summary"]
assert report["summary"]["markdown_packages"] == 88, report["summary"]
assert report["summary"]["lesson_hours"] == 172, report["summary"]
assert report["summary"]["failure_records"] == 0, report["summary"]
assert report["summary"]["warning_records"] == 0, report["summary"]

run(sys.executable, str(SCRIPTS / "finalize_lesson_plan_production.py"),
    "--knowledge-root", str(COURSE),
    "--validation-report", "/tmp/tde11-lesson-plan-validation.json",
    "--expected-head", COMMIT_SHA)
run(sys.executable, str(SCRIPTS / "build_runtime_course_package.py"), "build",
    "--knowledge-root", str(COURSE))

reports_dir = Path("/tmp/tde11-teacher-guides")
reports_dir.mkdir(exist_ok=True)
for theme in ("TEMA_01", "TEMA_02", "TEMA_03"):
    out = reports_dir / f"{theme}.json"
    run(sys.executable, str(SCRIPTS / "validate_teacher_guide.py"),
        "--manifest", f"courses/TDE_11/teacher_guide/{theme}/teacher_guide.json",
        "--report", str(out))
    guide_report = json.loads(out.read_text(encoding="utf-8"))
    assert guide_report["status"] == "PASS_WITH_WARNINGS", (theme, guide_report["status"])
    assert not guide_report["failures"], (theme, guide_report["failures"])

t3 = json.loads((reports_dir / "TEMA_03.json").read_text(encoding="utf-8"))
assert t3["sections_checked"] == 7, t3
assert t3["unique_unit_ids"] == 22, t3
assert t3["unique_item_ids"] == 65, t3
assert len(t3["outcomes_covered"]) == 16, t3
assert t3["core_instruction_hours"] == 43, t3
messages = "\n".join(w["message"] for w in t3["warnings"])
assert "T3_ISSUE_READING_PLAN_SEQUENCE_OUTCOME_MISMATCH" not in messages
assert "T3_ISSUE_LP_YAZMA_P04_OUTCOME_MISMATCH" not in messages
for required in (
    "T3_ISSUE_TDE3_4_EXTERNAL_RUBRIC",
    "T3_ISSUE_TDE4_4_EXTERNAL_RUBRIC",
    "T3_ISSUE_EXTERNAL_MULTIMODAL_MEDIA",
):
    assert required in messages, (required, messages)

for validator in (
    "validate_package_topology.py",
    "validate_grounded_references.py",
    "validate_classroom_adaptations.py",
    "validate_closure_time_budgets.py",
):
    run(sys.executable, str(SCRIPTS / validator), "--knowledge-root", str(COURSE))

# Runtime is derived; keep build artifacts out of the source-alignment commit.
run("git", "checkout", "--", "courses/TDE_11/runtime")

# Remove temporary non-workflow transport. Workflow files are removed later via
# the repository connector because Actions tokens cannot update workflow files.
shutil.rmtree(ROOT / ".tde11-theme3-payload")

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "-A", "--",
    ".tde11-theme3-payload",
    "courses/TDE_11/teacher_guide/TEMA_03",
    "courses/TDE_11/generated/lesson_plans/TEMA_03/BLOCK_T3_01_OKUMA",
    "courses/TDE_11/generated/lesson_plans/TEMA_03/BLOCK_T3_04_YAZMA/BLOCK_T3_04_YAZMA_P04.json",
    "courses/TDE_11/generated/lesson_plans/TEMA_03/BLOCK_T3_04_YAZMA/BLOCK_T3_04_YAZMA_P04.md",
    "courses/TDE_11/planning/lesson_plan_production_plan.json",
    "courses/TDE_11/planning/lesson_plan_validation_seal.json",
    "courses/TDE_11/planning/course_timeline.json")
run("git", "diff", "--cached", "--stat")
if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
    raise SystemExit("No final changes to commit")
run("git", "commit", "-m", "feat(TDE11): complete Theme 3 teacher guide and repair plan alignment")
run("git", "push", "origin", f"HEAD:{BRANCH}")
