# Contributing to ARC Protocol

> ARC Protocol is an open-source protocol research project.
> ARC is published under Apache-2.0 and is currently stewarded by one maintainer. Interoperability and future stewardship remain open work.
> Research collaboration, independent implementation experiments, commercial work, grants, sponsorship, and stewardship proposals are welcome. Proposed changes must identify their semantic layer and any conformance impact.

---

## What Kind of Project Is This?

ARC Protocol is currently an **early-stage protocol research project with an Executable Reference Corpus**, not yet a production codebase or complete conformance suite.

Current contributions may include:

- Feedback on the design
- Criticism of the protocol model and its stated boundaries
- Threat models and attack scenarios
- Suggestions for the protocol specification
- Ideas for the governance model
- Improvements to the documentation

Code, documentation, and research contributions should identify their scope and supporting evidence.

---

## Ways to Contribute

### 1. Open an Issue

Found a flaw in the protocol model? A contradiction in the architecture? A governance edge case we haven't considered?

Open an issue and describe the problem clearly.

Good issue titles:
- "Pre-authorized low-risk actions need clearer safeguards"
- "Governance model doesn't address cross-community agent identity disputes"
- "Reputation decay mechanism needs more detail"

Not helpful:
- "This will never work"
- "Just use [existing platform]"

### 2. Research Contributions

Relevant contributions may draw from several adjacent fields:

- **Threat models** — what attacks does the current design miss?
- **Protocol comparisons** — how does ARC compare to existing agent communication standards?
- **Governance research** — what can ARC learn from existing federated governance models?
- **Economic analysis** — does recomputed, unstored reputation hold up under adversarial conditions?
- **Papers and critiques** — academic or informal writing that engages with the core ideas

Contributions about agent delegation, governance, authority, and audit design should identify the ARC layer they address.

### 3. Improve the Documentation

The `docs/` folder contains normative, explanatory, application, historical, and research material. If you see something unclear, incomplete, or wrong — identify its layer, fix it, and submit a pull request.

Documents that need the most work:
- `docs/protocol.md` — current protocol mechanics, boundaries, and reference-profile distinctions
- `docs/identity.md` — exploratory identity, credential, and trust model
- `docs/reputation.md` — exploratory Commerce reputation Projection/application model

### 4. Propose Protocol Changes

If you have a substantive proposal for how the protocol should work — message formats, identity schemes, reputation algorithms, governance structures — write it up and open an issue or PR.

State whether the proposal changes **Canon**, **Conformance**, a named **Projection**, **Application** policy, **Implementation**, or **Research**. A conformance proposal must also identify whether it affects **Core Event Conformance**, **Named Projection Conformance**, or **Named Functional Profile Conformance**; reference-corpus behavior alone is not the standard.

Good proposals include:
- The problem you're solving
- Your proposed solution
- Trade-offs you're aware of
- Alternatives you considered

### 5. Build Something

The `examples/` directory is intended for working demonstrations of protocol concepts.

If you want to build:
- A simulated consumer agent
- A mock merchant agent
- A basic approval UI
- A reputation scoring prototype

Go ahead. Document what you built and why. Working code that demonstrates a concept is worth more than abstract discussion.

### 6. Translate

ARC Protocol is currently written in English. Translations can make the documents accessible to additional reviewers and implementers.

---

## What We're Not Looking For

- Proposals that let consequential actions bypass Current Coverage traceable to authority granted by the responsible principal or authority holder. Current reference profiles are typically human-rooted.
- Changes that present one fixture, deployment topology, or application policy as universal Canon without supporting protocol evidence

Substantive semantic changes must identify their layer and evidence. Debate about those boundaries is welcome in issues.

---

## Code Style (When Code Exists)

When the codebase grows, we'll add specific style guides. For now:

- TypeScript preferred
- Functional where practical
- Document the why, not just the what
- Tests for anything that handles money or identity

---

## Pull Request Process

1. Fork the repository
2. Create a branch with a descriptive name (`docs/improve-governance-model`, `feat/consumer-agent-prototype`)
3. Make your changes
4. Write a clear PR description explaining what you changed and why
5. Submit

There is no SLA on reviews right now. The project is currently stewarded by a single maintainer. Patience appreciated.

---

## Code of Conduct

Be direct. Be honest. Disagree openly and argue from evidence.

Don't be cruel. Don't make it personal.

That's it.

---

## Adjacent Ideas

Some future-facing ideas, such as agent-mediated collaboration or user-controlled information filtering, are discussed separately in `docs/adjacent-ideas/`.

These are not core protocol requirements.
They are speculative extensions and should not be treated as current ARC scope.

Future ARC-adjacent ideas may explore machine-readable collaboration intent and opt-in contributor discovery, where projects and contributors publish compatible intent and agents help humans find matches.

For now, contribution remains entirely human-directed. The adjacent collaboration proposal assumes opt-in contact; base ARC does not define an outreach policy.

---

## A Note on Scale

This project is stewarded by a single maintainer, with no other contributors yet.

Issues and critiques should cite the affected file, layer, and claim where possible.
