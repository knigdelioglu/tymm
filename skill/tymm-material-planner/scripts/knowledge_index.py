#!/usr/bin/env python3
"""Compatibility facade for the TYMM knowledge index.

The historical implementation lives in ``_knowledge_index_legacy.py``. Courses that
carry ``curriculum_process_component_resolution.json`` must never rebuild or extract
through the raw legacy path because ``process_components_verbatim`` is explicitly only
the theme-explicit layer for those courses. Use ``effective_knowledge_index.py`` for
build/rebuild in that case.

Read-only status/query compatibility remains available here so existing consumers can
open a correctly built effective index without migration churn.
"""
from __future__ import annotations

import argparse
import json
import os

from _knowledge_index_legacy import *  # noqa: F401,F403
from _knowledge_index_legacy import KnowledgeCorpusExtractor as _LegacyKnowledgeCorpusExtractor
from _knowledge_index_legacy import KnowledgeIndexer as _LegacyKnowledgeIndexer


EFFECTIVE_INDEX_REQUIRED_ERROR = "PROCESS_COMPONENT_EFFECTIVE_INDEX_REQUIRED"


def _requires_effective_process_component_projection(knowledge_root: str) -> bool:
    return os.path.exists(
        os.path.join(
            os.path.abspath(knowledge_root),
            "curriculum_process_component_resolution.json",
        )
    )


def _raise_if_effective_projection_required(knowledge_root: str) -> None:
    if _requires_effective_process_component_projection(knowledge_root):
        raise RuntimeError(
            f"{EFFECTIVE_INDEX_REQUIRED_ERROR}: {os.path.abspath(knowledge_root)} contains "
            "curriculum_process_component_resolution.json; build/rebuild/extract through "
            "effective_knowledge_index.py so ROOF_INHERITED components and provenance cannot be lost."
        )


class KnowledgeCorpusExtractor(_LegacyKnowledgeCorpusExtractor):
    """Raw extractor compatibility for courses without a resolution contract."""

    def extract_all(self):
        _raise_if_effective_projection_required(self.knowledge_root)
        return super().extract_all()


class KnowledgeIndexer(_LegacyKnowledgeIndexer):
    """Legacy read compatibility with fail-closed rebuild protection."""

    def build_index(self, force: bool = False):
        _raise_if_effective_projection_required(self.knowledge_root)
        return super().build_index(force=force)


def main() -> None:
    parser = argparse.ArgumentParser(description="TYMM Knowledge Index compatibility CLI")
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "rebuild"):
        p = subs.add_parser(name)
        p.add_argument("--knowledge-root", required=True)
    p_status = subs.add_parser("status")
    p_status.add_argument("--knowledge-root", required=True)
    p_query = subs.add_parser("query")
    p_query.add_argument("--knowledge-root", required=True)
    p_query.add_argument("--query", required=True)
    p_query.add_argument("--top-k", type=int, default=8)
    p_query.add_argument("--theme-id")
    p_query.add_argument("--entity-type")
    args = parser.parse_args()

    indexer = KnowledgeIndexer(args.knowledge_root)
    if args.command in ("build", "rebuild"):
        print(json.dumps(indexer.build_index(force=True), indent=2, ensure_ascii=False))
    elif args.command == "status":
        print(json.dumps(indexer.check_status(), indent=2, ensure_ascii=False))
    else:
        etypes = [e.strip() for e in args.entity_type.split(",")] if args.entity_type else None
        print(
            json.dumps(
                indexer.search_hybrid(args.query, args.top_k, args.theme_id, etypes),
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
