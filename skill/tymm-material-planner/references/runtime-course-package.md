# Runtime Course Package Standard

This is a global, app-agnostic projection standard for compiling verified TYMM
canonical course knowledge into a deterministic read-only runtime package.

## Invariants

1. Canonical knowledge is authoritative; the runtime package is derived and
   rebuildable.
2. The compiler cannot invent entities, relationships, pedagogical decisions,
   dates, hours, or citations. Only verified canonical entities and relations
   may enter the package.
3. The schema may denormalize for read efficiency, but every projected record
   remains traceable through canonical stable IDs and provenance.
4. Unresolved canonical fields remain `NULL` (or an empty relation), never a
   guessed value.
5. Application/user state is outside the package. Course knowledge is
   immutable for clients and consumed read-only.
6. Every package carries a runtime/schema version and a sorted fingerprint set
   of its relevant canonical inputs.
7. The same canonical input and compiler version produce the same logical rows,
   ordering, manifest fingerprints, and validation result.
8. Runtime SQLite is relational and dependency-free at consumption time. RAG,
   vector stores, embeddings, ONNX, and semantic caches are not runtime
   requirements.
9. Copyrighted textbook bodies, full PDFs, long passages, and model artifacts
   are excluded; only verified navigation metadata and short labels are
   projected.
10. A stale fingerprint is an explicit `RUNTIME_STALE` state; clients must not
    silently consume stale course knowledge.

## Compilation contract

```text
canonical JSON/Markdown
        -> deterministic compiler + validation
        -> runtime/course_runtime.sqlite
        -> Android, desktop, web, CLI, or reporting client
```

The compiler must fail closed on duplicate canonical IDs, unknown relation
targets, conflicting canonical metadata, invented resolved values, user-state
tables, or vector/model dependencies. Runtime rows preserve source locators;
`source_references` is a metadata projection, not a new citation system.

Decision category mappings, when useful for client filtering, must be explicit
deterministic mappings from canonical machine codes and must not alter the
canonical decision.
