# Literature and contribution assessment

Search date: 17 October 2026. This is a targeted primary-source review, not an exhaustive systematic review or a patent search.

## Questions used in the search

- LLM structured outputs, omission, null, optional fields, PATCH and strict schema conversion.
- Presence-preserving or lossless tool schemas and required nullable arguments.
- JSON Schema conformance benchmarks, stateful tool-use evaluation, presence-aware serialization.
- Existing explicit update formats and source SDK conversion implementations.

An initial search also considered token-budget-aware grammar completion, tool-schema evolution and coding-environment reset evaluation. These were not selected: directly relevant prior work already treats those broad questions. They are not part of the final contribution.

## Closest antecedents

| Primary source | Already established | This artifact's narrower contribution |
|---|---|---|
| [JSON Schema object reference](https://json-schema.org/understanding-json-schema/reference/object) | Optionality and nullability differ. | Executable conversion test when a generation interface removes optional-key output. |
| [Protocol Buffers field presence](https://protobuf.dev/programming-guides/field_presence/) | Explicit presence affects merge semantics, including default-valued updates. | Analyze a JSON strict-generation representation and its evaluation boundary. |
| [serde_with double_option](https://docs.rs/serde_with/latest/serde_with/rust/double_option/index.html) | Missing, null, and present values can be represented as nested options. | This mechanism is prior art; the compiler and audit specialize it to required wire properties. |
| [RFC 7396](https://www.rfc-editor.org/rfc/rfc7396) | Null can mean removal; explicit-null documents create limitations. | Do not confuse a merge-patch protocol with an arbitrary partial-update API. |
| [RFC 6902](https://www.rfc-editor.org/rfc/rfc6902) | Explicit operation lists avoid implicit update semantics. | A credible alternative, not a baseline that can be dismissed. Not token-benchmarked here. |
| [JSONSchemaBench](https://arxiv.org/abs/2501.10868) | Constraint compliance, coverage, speed and quality need evaluation. | Compare source and wire languages through a reversible adapter and separating states. |
| [Schema reinforcement learning](https://aclanthology.org/2025.acl-long.243/) | Models can be trained for better schema validity. | Fidelity can fail deterministically even with perfect wire validity. No competing model-training claim. |
| [ToolSandbox](https://arxiv.org/abs/2408.04682) | Stateful execution and milestones are important. | Show exactly how initial state can conceal this adapter's errors and supply a finite verification suite. |
| [RestGPT](https://arxiv.org/abs/2306.06624) | Models need executors that construct API parameters. | Isolate preservation of presence within such an executor. |
| [Pydantic serialization](https://docs.pydantic.dev/latest/concepts/serialization/) | Explicitly supplied fields can be tracked and excluded. | Demonstrate that tracking the converted wire input cannot recover original source presence. |
| [Strict schema documentation](https://developers.openai.com/api/docs/guides/structured-outputs) | Required nullable fields are a documented pattern. | Identify when that representation is insufficient for a source action language. |

## Claim discipline

The presence type, sum type, operation tags, JSON Patch and counting argument are not new inventions. A null-only representation's collision is not an SDK vulnerability by itself. The claimed contribution is a bounded selective compiler plus a reproducible evaluation study joining source schema declarations, actual installed conversion behavior, exact replay, and state-coverage masking. No patentability, industry-first claim or major research-conference acceptance probability is asserted.

## Comparison with the author's earlier papers

The local review extracted all 68 top-level PDF manuscripts present in Downloads/research at the start of this task (plus the remaining local files as inventory context). Prior numerical-wire, streaming-commit, compensation, literal-redaction, text-range, retrieval-provenance, and cache papers concern different primitive failures. The closest previous technical study is *Before the Validator*, which audits numeric value preservation after JSON parsing. PresenceBridge instead concerns injectivity of optional-key-to-required-key representations and the effect of evaluator initial state. No datasets, experiments, figures, or numerical results were reused. This distinction does not guarantee that a reviewer will consider the work wholly unrelated; the manuscript is positioned as another narrowly scoped interface study, not as a new foundation for all agent systems.

## Commercial evidence and limits

Official GitHub and Stripe API contracts establish practical integration surfaces; they do not establish market size, demand, willingness to pay, savings, or customer adoption. Potential buyers include API-integration, agent-platform and enterprise automation teams. The defensible deliverable is verified integration coverage, migration diagnostics and reproducible adapters. Existing presence-aware serializers and update standards make patent claims over the core idea inappropriate without specialist review. No market revenue forecast is presented as evidence.
