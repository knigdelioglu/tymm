#!/usr/bin/env python3
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from knowledge_index import (
    EFFECTIVE_INDEX_REQUIRED_ERROR,
    KnowledgeCorpusExtractor as RawKnowledgeCorpusExtractor,
    KnowledgeIndexer as RawKnowledgeIndexer,
)
from process_component_resolver import (
    ProcessComponentError,
    audit_curriculum,
    build_catalog_index,
    resolve_outcome_components,
)


def catalog():
    return {
        "catalog_id": "TEST_ROOF",
        "applicable_grades": [9],
        "parent_count": 1,
        "component_count": 2,
        "parents": [
            {
                "parent_code": "TDE2.1",
                "parent_title_verbatim": "Okumayı Yönetebilme",
                "source_locator": "s. 22",
                "components": [
                    {
                        "component_code": "TDE2.1.1",
                        "component_title_verbatim": "İnceler ve görüş oluşturur.",
                        "source_locator": "s. 22",
                    },
                    {
                        "component_code": "TDE2.1.2",
                        "component_title_verbatim": "Seçim yapar.",
                        "source_locator": "s. 22",
                    },
                ],
            }
        ],
    }


idx = build_catalog_index(catalog())

# 1. Tema explicit yok + roof var -> inherited PASS.
r = resolve_outcome_components(
    {"outcome_id": "A", "outcome_code": "TDE2.1", "process_components_verbatim": []},
    idx,
)
assert r["origin"] == "ROOF_INHERITED"
assert r["effective_count"] == 2

# 2/3. Verified explicit roof'a üstün gelir; aynı alt kod farklı tema specialization taşıyabilir.
r = resolve_outcome_components(
    {
        "outcome_id": "B",
        "outcome_code": "TDE2.1",
        "process_components_verbatim": [
            {
                "component_code": "a) TDE2.1.1",
                "component_title": "Tema bağlamına özgü resmî specialization.",
                "source_locator": "s. 66",
            }
        ],
    },
    idx,
)
assert r["origin"] == "THEME_EXPLICIT"
assert r["effective_count"] == 1
assert r["roof_count"] == 2

# 4. Roof bulunmayan ve verified-none olmayan boş parent unresolved kalır.
r = resolve_outcome_components(
    {"outcome_id": "C", "outcome_code": "TDE9.9", "process_components_verbatim": []},
    idx,
)
assert r["status"] == "PROCESS_COMPONENT_INHERITANCE_MISSING"

# 5. Boş efektif set yalnız SOURCE_VERIFIED_NONE ile yasaldır.
r = resolve_outcome_components(
    {
        "outcome_id": "D",
        "outcome_code": "TDE9.9",
        "process_components_verbatim": [],
        "process_component_status": "SOURCE_VERIFIED_NONE",
    },
    idx,
)
assert r["origin"] == "SOURCE_VERIFIED_NONE"
assert r["components"] == []

# 6. Roof locator eksikliği fail-closed.
bad = catalog()
bad["parents"][0]["components"][0] = dict(bad["parents"][0]["components"][0])
bad["parents"][0]["components"][0].pop("source_locator")
try:
    build_catalog_index(bad)
except ProcessComponentError:
    pass
else:
    raise AssertionError("missing inherited locator must fail")

# 7. Duplicate component code fail-closed.
bad = catalog()
bad["parents"][0]["components"][1] = {
    **bad["parents"][0]["components"][1],
    "component_code": "TDE2.1.1",
}
try:
    build_catalog_index(bad)
except ProcessComponentError:
    pass
else:
    raise AssertionError("duplicate roof component must fail")

# 8. Catalog applicability guard prevents scope leakage.
curriculum = {
    "course_id": "TDE_10",
    "grade": 10,
    "themes": [{"theme_id": "T1", "learning_outcomes": []}],
}
try:
    audit_curriculum(curriculum, catalog())
except ProcessComponentError:
    pass
else:
    raise AssertionError("grade leakage must fail")

# Completeness report explicit ve inherited outcome'ları ayrı sayar.
curriculum = {
    "course_id": "TDE_9",
    "grade": 9,
    "themes": [
        {
            "theme_id": "T1",
            "learning_outcomes": [
                {
                    "outcome_id": "A",
                    "outcome_code": "TDE2.1",
                    "process_components_verbatim": [],
                },
                {
                    "outcome_id": "B",
                    "outcome_code": "TDE2.1",
                    "process_components_verbatim": [
                        {
                            "component_code": "TDE2.1.1",
                            "component_title": "Tema specialization",
                            "source_locator": "s. 66",
                        }
                    ],
                },
            ],
        }
    ],
}
report = audit_curriculum(curriculum, catalog())
assert report["final"] == "PASS"
assert report["counts"]["explicit_component_outcomes"] == 1
assert report["counts"]["inherited_component_outcomes"] == 1
assert report["counts"]["inheritance_missing_count"] == 0

# 9. A resolution-contract course can never be rebuilt/extracted through the raw legacy facade.
tde9_root = SCRIPTS.parents[2] / "courses" / "TDE_9"
for operation in (
    lambda: RawKnowledgeCorpusExtractor(str(tde9_root)).extract_all(),
    lambda: RawKnowledgeIndexer(str(tde9_root)).build_index(force=True),
):
    try:
        operation()
    except RuntimeError as exc:
        assert EFFECTIVE_INDEX_REQUIRED_ERROR in str(exc), str(exc)
    else:
        raise AssertionError("raw legacy process-component path must fail closed")

print("PROCESS_COMPONENT_INHERITANCE: PASS")
