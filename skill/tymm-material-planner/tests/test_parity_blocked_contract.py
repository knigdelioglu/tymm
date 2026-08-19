#!/usr/bin/env python3
import sys
from pathlib import Path
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from production_schema import ProductionSchemaError, build_artifact_maps

blocked = {
    "schema_version": "1.1",
    "production_mode": "PARITY_REVIEW_BLOCKED",
    "verified_resource_gap_count": 0,
    "unresolved_assessment_target_count": 8,
    "expected_new_artifact_count": 0,
    "production_queue": [],
    "gap_instance_provenance_registry": [],
    "generation_authorization": {"allowed": False, "reason": "UNRESOLVED_NORMATIVE_ASSESSMENT_TARGETS"},
}
assert build_artifact_maps(blocked) == ([], {}, {}, {})
invalid = dict(blocked)
invalid["unresolved_assessment_target_count"] = 0
try:
    build_artifact_maps(invalid)
except ProductionSchemaError:
    pass
else:
    raise AssertionError("blocked state without unresolved targets must fail")
print("PARITY_BLOCKED_CONTRACT: PASS")
