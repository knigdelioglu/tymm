#!/usr/bin/env python3
import sys
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(SCRIPTS))
from production_schema import build_artifact_maps, ProductionSchemaError

valid={"schema_version":"1.1","production_mode":"REUSE_ONLY_NO_NEW_ARTIFACTS","verified_resource_gap_count":0,"production_queue":[],"gap_instance_provenance_registry":[]}
arts,by_id,aliases,prov=build_artifact_maps(valid)
assert arts==[] and by_id=={} and aliases=={} and prov=={}

bad=dict(valid); bad["verified_resource_gap_count"]=1
try:
    build_artifact_maps(bad)
except ProductionSchemaError:
    pass
else:
    raise AssertionError("empty queue accepted with non-zero verified gap count")
print("reuse-only production schema regression: PASS")
