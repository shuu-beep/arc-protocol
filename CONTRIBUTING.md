# Contributing to ARC Protocol

> ARC Protocol is a non-profit, open-source philosophical and design project.
> There is no company behind it. No funding. No roadmap pressure.
> Just one person's attempt to think carefully about what open commerce infrastructure should look like.

Thank you for being here.

---

## What Kind of Project Is This?

ARC Protocol is currently a **philosophy document and architecture proposal**, not a production codebase.

That means contributions right now look less like pull requests and more like:

- Feedback on the design
- Criticism of the philosophy
- Threat models and attack scenarios
- Suggestions for the protocol specification
- Ideas for the governance model
- Improvements to the documentation

Code contributions will matter more as the project moves toward MVP. For now, thinking clearly is the most valuable thing anyone can contribute.

---

## Ways to Contribute

### 1. Open an Issue

Found a flaw in the philosophy? A contradiction in the architecture? A governance edge case we haven't considered?

Open an issue. Describe the problem clearly. We take all serious criticism seriously.

Good issue titles:
- "Pre-authorized low-risk actions need clearer safeguards"
- "Governance model doesn't address cross-community agent identity disputes"
- "Reputation decay mechanism needs more detail"

Not helpful:
- "This will never work"
- "Blockchain is bad"
- "Just use [existing platform]"

### 2. Research Contributions

ARC sits at the intersection of several fields. Contributions from adjacent disciplines are genuinely valuable:

- **Threat models** — what attacks does the current design miss?
- **Protocol comparisons** — how does ARC compare to existing agent communication standards?
- **Governance research** — what can ARC learn from existing federated governance models?
- **Economic analysis** — does the reputation economy hypothesis hold under adversarial conditions?
- **Papers and critiques** — academic or informal writing that engages with the core ideas

If you've thought carefully about agent commerce, decentralized governance, or attention economy dynamics — that thinking is welcome here.

### 3. Improve the Documentation

The `docs/` folder contains the core design documents. If you see something unclear, incomplete, or wrong — fix it and submit a pull request.

Documents that need the most work:
- `docs/protocol.md` — protocol message specification (currently a stub)
- `docs/identity.md` — exploratory identity, credential, and trust model
- `docs/reputation.md` — reputation model detail (currently a stub)

### 4. Propose Protocol Changes

If you have a substantive proposal for how the protocol should work — message formats, identity schemes, reputation algorithms, governance structures — write it up and open an issue or PR.

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

ARC Protocol is written in English but the problems it addresses are global. If you want to translate the core documents into another language, that is a meaningful contribution.

---

## What We're Not Looking For

- Proposals to make ARC into a startup or commercial product
- Blockchain maximalism or Web3 ideology for its own sake
- Fully autonomous agent systems without human approval
- Anything that reduces human sovereignty over economic decisions

ARC has a clear philosophical position. Contributions that contradict the core principles will not be merged — but debate about those principles is always welcome in issues.

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

There is no SLA on reviews right now. This is a one-person project. Patience appreciated.

---

## Code of Conduct

Be direct. Be honest. Disagree openly and argue from evidence.

Don't be cruel. Don't make it personal.

That's it.

---

## Adjacent Ideas

Some future-facing ideas, such as agent-mediated collaboration or information sovereignty, are discussed separately in `docs/adjacent-ideas/`.

These are not core protocol requirements.
They are speculative extensions and should not be treated as current ARC scope.

Future ARC-adjacent ideas may explore machine-readable collaboration intent and opt-in contributor discovery, where projects and contributors publish compatible intent and agents help humans find matches.

For now, contribution remains entirely human-directed. ARC does not support unsolicited agent outreach.

---

## A Note on Scale

This project has zero contributors right now besides the author.

If you're reading this and considering contributing — even just opening an issue with a critique — that matters. The point of open-sourcing a design document is to expose it to people who will find the holes.

Find the holes.
