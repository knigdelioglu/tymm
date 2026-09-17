# TDE 11 Teacher Guide V3 pedagogy quality audit

| Contract | Result |
|---|---|
| Reviewed tasks | 36 total; 9 per theme |
| Fields checked side by side | `teacher_background`, `answer_explanation`, `student_explanation`, `teacher_moves`, `follow_up_questions`, `common_misconceptions`, `assessment_look_fors` |
| Additional semantic fields checked | `why_it_matters`, `misconception_interventions`, `support`, `enrichment` |
| Anchor/page/heading-stripped semantic failures | 0 in the release validator |
| Selected-task missing pedagogical fields | 0 |
| Selected same-profile maximum similarity | 0.660 (`teacher_background`, T2V23_P127_DLT_Q07 vs T2V23_P127_DLT_Q04) |
| Starting semantic repetition threshold | 0.85 token-Jaccard |

## Audit sample

The sample was selected to include, where available, three text-analysis tasks,
two open-ended interpretation tasks, one language task, one
speaking/writing/performance task, one assessment task, and one additional task
type per theme. The full task identifiers are retained so this report can be
repeated without relying on generated prose alone.

| Theme | Sampled task IDs |
|---|---|
| TEMA_01 | `T1V23_P28_INTERPRET#Q1`, `T1V23_P40_Q03`, `T1V23_P79_Q01`, `T1V23_P41_SUBJECTIVITY`, `T1V23_P81_Q05`, `T1V23_P46_Q_EVAL`, `T1V23_P29_FRIENDSHIP#Q2`, `T1V23_P48_Q03`, `T1V23_P83_Q12` |
| TEMA_02 | `T2V23_P90_Q01`, `T2V23_P96_Q03`, `T2V23_P100_Q01`, `T2V23_P101_Q09`, `T2V23_P127_DLT_Q07`, `T2V23_P155_Q02`, `T2V23_P86_Q02`, `T2V23_P100_Q06`, `T2V23_P127_DLT_Q04` |
| TEMA_03 | `T3V23_P175_Q02`, `T3V23_P182_Q01_GERCEK_KURGU`, `T3V23_P205_COZUM_Q01`, `T3V23_P190_191_GRAMMAR_Q01`, `T3V23_P193_DEGER_Q03`, `T3V23_P230_Q01`, `T3V23_P176_Q04`, `T3V23_P205_SIRA_Q01_ASIM`, `T3V23_P210_Q02` |
| TEMA_04 | `T4V23_P251_252_Q01`, `T4V23_P255_Q02`, `T4V23_P269_Q05`, `T4V23_P258_Q02`, `T4V23_P262_Q01`, `T4V23_P307_Q11`, `T4V23_P259_Q01`, `T4V23_P280_Q02`, `T4V23_P304_Q03` |

## Findings and fixes

The reviewed packages were task-bound through the book prompt, source context,
canonical answer components, evidence requirement, task focus, and linked
activity action/product. In particular:

- grouped questions now use the matching numbered answer component instead of
  inheriting a neighbouring question's guidance;
- multiple-choice tasks use their canonical choice and source evidence, and
  the teacher moves explicitly require checking distractors rather than only
  the answer letter;
- grammar tasks route through language-specific concepts such as sentence
  elements, sentence structure, period language, and spelling;
- performance and open-ended tasks retain their requested product, evidence,
  and justification structure;
- source-bounded external-media tasks remain `REVIEW_REQUIRED` rather than
  receiving invented answers.

The audit did not find a selected task whose pedagogical package became
interchangeable after removing page, question-number, and heading anchors. The
validator's all-task semantic gate is the release control; this document is a
human-readable 36-task spot audit, not a claim that every one of the 407
questions was manually read.
