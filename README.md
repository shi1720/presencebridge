# PresenceBridge

**Valid JSON, Wrong Update: Preserving Field Presence in Agent Tool Calls**  
Shivam Gupta · Independent Researcher; Founder, Siloed

A bounded, reversible schema adapter and reproducible research artifact for strict tool interfaces. It preserves omission separately from explicit null when every declared wire property must be present.

```python
from presencebridge import Codec

source_schema = {
    "type": "object",
    "properties": {
        "enabled": {"type": "boolean"},
        "note": {"type": ["string", "null"]},
    },
    "required": [],
    "additionalProperties": False,
}
codec = Codec(source_schema)
wire = codec.encode({"note": None})
# {"enabled": None, "note": {"op": "set", "value": None}}
assert codec.decode(wire) == {"note": None}
# Send codec.wire as the generation schema. Validate and decode the generated
# value before dispatch. Decoding preserves the represented request; it cannot
# establish whether a model understood the user's intent.
```

## Findings

- Two pinned official OpenAPI descriptions: 3,528 inspected top-level request-field slots. GitHub has 76 optional fields with null markers; 62 accept null under OpenAPI validation, spanning 37 operations. Stripe has zero explicit null markers in this scope. Counts describe source schemas, not deployed failures.
- 5,460 exhaustive Boolean update requests. Each reversible codec preserves all requests. Either null-only baseline preserves 1,092 (20%); at six fields, 729/4,096 (17.80%). These are equally weighted constructed cases, not model accuracy or production rates.
- Initializing every destination field to null conceals all final-state errors of forwarding normalized nulls, while request fidelity remains unchanged.
- An independent checker verifies 3,279 normalization fibres and 124 state-policy configurations. The 26-test codec suite includes nested data and malformed-input rejection.
- On the four-field benchmark with two nullable fields, selective tags use 28.00 vs 37.33 mean payload tokens (`cl100k_base`), and 28.50 vs 38.17 (`o200k_base`). Total inference cost was not measured.

## Reproduce

Python 3.12 was used for the experiments. Create an isolated environment:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m pip install -e .
python -m pytest -q
python experiments/audit.py
python experiments/benchmark.py
python experiments/verify.py
python experiments/figures.py
python experiments/demo.py
cd paper
tectonic main.tex
```

`audit.py` downloads approximately 22 MB of public specifications from pinned commits into `.cache/` and verifies their SHA-256 hashes. It does not contact production APIs. The other experiments require no credentials. Tiktoken may fetch its public tokenizer resources on first use. Timings vary across machines; exhaustive counts and payload token totals should match.

The implementation can be installed alone with `pip install .`; the lock file includes all experiment and plotting dependencies. [Companion paper](paper/PresenceBridge_Shivam_Gupta.pdf), [source](paper/main.tex), [source manifest](data/sources.json), [literature and positioning](docs/literature-and-positioning.md), and [protocol](docs/protocol.md).

## Scope

Supported: finite-tree closed objects, homogeneous arrays, scalar types and specified scalar constraints, enums/constants, nullable single-type alternatives. Rejected: arbitrary unions, references/recursive schemas, open maps, dependencies, conditionals, formats, and unknown validation keywords. See `src/presencebridge/codec.py` for the exact admission rules.

The compiler builds closed, all-required object schemas. This is a structural profile, not a claim that a hosted provider accepts every schema keyword or complexity level. No language-model efficacy comparison or production deployment was conducted. The census domain is broader than the compiler's supported fragment; the project does not compile the full GitHub or Stripe schema.

This work applies established presence-aware types and explicit update semantics. It does not claim to invent missing-versus-null distinctions, tagged unions, or a patentable primitive. Its contribution is the connected compiler and evaluation artifact. Original code is MIT-licensed; upstream specifications retain their licenses and are fetched rather than redistributed here.

## Artifact layout

- `src/presencebridge/`: compiler, validated encoder and decoder.
- `tests/`: exhaustive, nested and rejection tests.
- `experiments/`: source audit, effect replay, independent verification, token accounting, figures and local SQLite demonstration.
- `data/`: source hashes and per-operation-field evidence.
- `results/`: saved exact rows, summaries, SDK probes and environment.
- `paper/`: manuscript PDF, LaTeX, bibliography and vector figures.

## Citation

See `CITATION.cff`. This is a technical research report and companion to a Code Europe AI 2027 speaker proposal. It is not a claim of conference acceptance or archival publication.
