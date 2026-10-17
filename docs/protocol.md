# Experiment protocol and claim boundaries

This document records the implemented protocol; it is not a preregistration. The source census was explored before the final study scope was fixed.

1. **Source audit.** Enumerate standard HTTP operation keys in the two pinned descriptions. Select JSON or form body in that order, once per operation. Inspect directly declared top-level properties after local reference resolution. Count optional slots with explicit null markers. Independently validate null at those marked slots using `OAS30Validator`; retain any rejecting constraint keyword. Do not equate optional schema keys with an unconditional operational permission. No production request is sent. Unknown media and non-property roots are reported separately.
2. **SDK conversion.** Use installed, unmodified functions to convert two small Pydantic schemas. Save source/wire schemas, field-set metadata, exclusion results, package versions and source hashes. This probes conversion and hydration, not hosted inference.
3. **Exact source replay.** For each n=1..6, enumerate {omitted, null, true, false}^n. The source oracle writes only source-present keys to a SQLite record initially true. Compare null-as-value, null-as-omit, selective and full tags. Save request equality and final-state equality separately. A second all-null initial state is a masking control.
4. **Independent checks.** Enumerate normalization fibres without importing the implementation. Check 2^c preimages for each normalized output through n=7. Enumerate initial null/true states and verify both lossy policies through n=5. This checks mechanism formulae, not arbitrary program correctness.
5. **Codec checks.** Exhaustive Boolean source vectors through n=5, 20 fixed nested-generation seeds with 50 cases per codec, nullable containers, required null, malformed tags, invalid source types and unsupported schemas. Tests reject rather than coerce invalid values.
6. **Token accounting.** Fixed names `enabled, archived, notify, locked`; 0,2,4 nullable fields; all valid source requests; compact UTF-8 JSON. Count source, nullable, selective and full-tag payloads under two pinned tokenizer encodings. Prompts, schema tokens, reasoning, retries and generation accuracy are not measured.
7. **Timing.** Record in-process encode/decode including schema validation. Do not use this single-machine observation as a serving SLA.

No confidence interval is appropriate for the exhaustive finite counts. API-source selection is purposive. The claim is conditional request preservation and an evaluator-state failure mechanism; the study does not establish customer impact, patentability, deployment prevalence or improved model reasoning.

The extra OpenAPI validation was added during verification after detecting that null markers can conflict with enums and union branches. The final artifact reports both counts; it does not hide the initial marker-based analysis.
