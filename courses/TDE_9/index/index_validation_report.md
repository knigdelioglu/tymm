# Knowledge Index Validation Report

- **Course ID**: TDE_9
- **Build Timestamp**: 2026-08-14T10:58:20.287637+00:00
- **Status**: SUCCESS
- **Total Indexed Records**: 355
- **Database Engine**: SQLite 3.53.1 + sqlite-vec (v0.1.9)
- **Vector Backend**: `sqlite-vec` (EXPLICIT_ACCEPTED_DEVIATION)
- **Base Embedding Model**: `intfloat/multilingual-e5-small` (Dim: 384)
- **Runtime Model Repository**: `Xenova/multilingual-e5-small` (`model_quantized.onnx`)
- **Model File SHA256**: `f80102d3f2a1229f387d3c81909990d8945513e347b0eab049f7de3c6f98c193`
- **Pooling & Normalization**: `attention_masked_mean_pooling` / `L2`
- **Index Content Hash**: `f3733250285779dbffb76c7f235cdf1c7ccb412e632cc90ffbce61423a994a26`

## Vector Backend Architecture Decision
- **Requested Backend**: `sqlite-vector/sqliteai-vector`
- **Selected Backend**: `sqlite-vec`
- **Status**: `EXPLICIT_ACCEPTED_DEVIATION`
- **Rationale**: sqlite-vec is the modern official lightweight native C SQLite extension by Alex Garcia supporting fast vector search without heavy external AI dependencies, works seamlessly on macOS ARM64/x86_64, whereas sqlite-vector/sqliteai-vector has packaging/build complexities and deprecations.

## Indexed Entity Types & Counts
- **alignment_record**: 54
- **curriculum_outcome**: 54
- **curriculum_theme**: 4
- **instructional_need**: 32
- **process_component**: 9
- **production_material**: 7
- **remaining_gap**: 12
- **resource_plan**: 50
- **school_based_option**: 20
- **textbook_activity**: 61
- **textbook_form**: 28
- **textbook_section**: 24

## Source Files Fingerprint
- `curriculum_map.json`: SHA-256 `1386a7efac987b84...` (178910 bytes) - VERIFIED
- `textbook_map.json`: SHA-256 `99daf4190472f729...` (56504 bytes) - VERIFIED
- `textbook_forms_index.json`: SHA-256 `a66d77a84cd1da60...` (35027 bytes) - VERIFIED
- `themes/tema_01/alignment.json`: SHA-256 `db3aa78cfdd648da...` (42702 bytes) - VERIFIED
- `themes/tema_01/gap_analysis.json`: SHA-256 `b7bfc6c56137ca6b...` (19064 bytes) - VERIFIED
- `themes/tema_01/needs.json`: SHA-256 `fe2045257aea7daa...` (27854 bytes) - VERIFIED
- `themes/tema_01/resource_plan.json`: SHA-256 `8bb371c3470cd993...` (12823 bytes) - VERIFIED
- `themes/tema_02/alignment.json`: SHA-256 `07744a32313ce229...` (27188 bytes) - VERIFIED
- `themes/tema_02/gap_analysis.json`: SHA-256 `3fa9e0b30bef2aaf...` (21572 bytes) - VERIFIED
- `themes/tema_02/needs.json`: SHA-256 `af24a7d8c6c4127b...` (32273 bytes) - VERIFIED
- `themes/tema_02/resource_plan.json`: SHA-256 `8b9f205398471fbf...` (15917 bytes) - VERIFIED
- `themes/tema_03/alignment.json`: SHA-256 `b9b5b033f7d5f094...` (30140 bytes) - VERIFIED
- `themes/tema_03/gap_analysis.json`: SHA-256 `b231addc50ce222a...` (23039 bytes) - VERIFIED
- `themes/tema_03/needs.json`: SHA-256 `95b96d0ff17e8d2c...` (11389 bytes) - VERIFIED
- `themes/tema_03/resource_plan.json`: SHA-256 `ae1e07d2dac85257...` (7921 bytes) - VERIFIED
- `themes/tema_04/alignment.json`: SHA-256 `829ae5de65a41374...` (49845 bytes) - VERIFIED
- `themes/tema_04/gap_analysis.json`: SHA-256 `dd8b5c03ed2ddf65...` (31034 bytes) - VERIFIED
- `themes/tema_04/needs.json`: SHA-256 `65207b3b390ddc08...` (41602 bytes) - VERIFIED
- `themes/tema_04/resource_plan.json`: SHA-256 `cb9f80b601bcfaaa...` (18482 bytes) - VERIFIED
- `production/production_manifest.json`: SHA-256 `35b40bc54ed82dce...` (9999 bytes) - VERIFIED
- `production/teaching_blocks.json`: SHA-256 `a997e616b307f932...` (24491 bytes) - VERIFIED
- `production/school_based_planning_options.json`: SHA-256 `ac0983834e9f516d...` (72098 bytes) - VERIFIED
