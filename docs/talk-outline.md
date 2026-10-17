# Code Europe AI 2027 talk outline

**Valid JSON, Wrong Update: Preserving Field Presence in Agent Tool Calls**  
Proposed speaker: Shivam Gupta  
Format: 40-minute on-site stage talk, including questions  
Audience: engineers building tool executors, strict structured outputs and API adapters

| Minutes | Material | Concrete takeaway |
|---|---|---|
| 0–5 | A two-field update: preserve the note while changing enabled; then explicitly clear the note. Run the SQLite example. | Omission and null can request different effects. |
| 5–10 | Show a source schema, an all-required wire schema and saved installed-SDK probes. Compare unset and null exclusion. | A validator or field-set tracker cannot recover information missing from its input. |
| 10–18 | Derive the two-to-one collision; extend to 2^c preimages. Walk through selective presence tags and the supported schema boundary. | Use a null sentinel only outside the source's present-value language. |
| 18–27 | Replay exhaustive Boolean updates; change the initial database state from true to null. Display request equality alongside final-state equality. | Include states that separate preservation from clearing in regression fixtures. |
| 27–33 | Show the pinned API inventory, marker-versus-validator distinction and two-tokenizer payload costs. | Distinguish source exposure, compiler support and runtime effect; measure representation overhead. |
| 33–35 | Compare selective tags, full tags, direct optional keys and JSON Patch. Explain admission failures and deployment checks. | Choose an explicit contract that fits the provider and backend. |
| 35–40 | Questions and tradeoffs. | Discuss cross-field dependencies, recursive schemas and future model-efficacy experiments without asserting unmeasured benefits. |

## Runnable demonstration

From the repository root after installation:

```sh
python experiments/demo.py
python -m pytest -q
python experiments/verify.py
```

The short demo is independent of internet access, provider credentials and mutable external data. Saved full replay rows and vector figures provide a fallback if the machine cannot run the full benchmark on stage. No remote production account is changed.

The presentation is based on a newly implemented research artifact. It does not describe a claimed production deployment, customer incident, or measured language-model improvement.
