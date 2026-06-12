# ARC Protocol: Key Custody

> **Status:** Exploratory draft
>
> **Purpose:** Where keys live, who signs, and the boundary that keeps the runtime away from key material. These are design decisions offered for review, not a finalized custody rulebook.
>
> This document introduces no new primitive, no new event type, and no new authority. Every mechanism it names is the existing Canon — `KEY` lifecycle events, `AUTHORIZE` with `scope`, the `nullifies` field — applied to the question the reference client deliberately left open: *where* keys live ([examples/reference-client](../examples/reference-client/)).
>
> For the event vocabulary, see [event-registry.md](./event-registry.md). For mandates, see [delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md). For the identity layers, see [identity.md](./identity.md). For authority boundaries, see [authority-and-conflict.md](./authority-and-conflict.md).

---

## 1. Why Custody Is the Deferred Question

A signature proves that a key signed a message ([identity.md](./identity.md) §2.2). It proves nothing about where that key lived when it signed — whether it sat in a hardware enclave, an OS keystore, a client process, or a plaintext file readable by every process on the machine.

Every probe so far could run on mock signing because every question so far lived *inside* the log: what events represent, how folds read them, where authority moves. Custody lives *outside* the log. A mock answer to "where do keys live" would not simplify the question; it would falsify it. So this document is a set of design decisions rather than a fixture — with one exception noted in §5, the single slice of custody that does reduce to a probe.

The corpus has already dug the holes these decisions fill: [event-registry.md](./event-registry.md) §4.3 names a **subkey binding** among the things `AUTHORIZE` subsumes but never specifies it (§4 here); [delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §10 asks whether scope enforcement can be checked independently of the consumer agent (§2 here); the reference client draws the line — *the runtime proposes, the client signs* — and stops at "where keys live is out of scope" (§2–§3 here). What follows connects lines already drawn.

## 2. The Custody Boundary Is the Mandate Boundary

The reference client's write path established the shape: a runtime proposes events; a boundary checks each proposal against the active mandate and either signs or escalates; the key never crosses the proposal line. Custody is the question of what stands on the signing side of that line.

The design decision: the signer is an **oracle, not a vault**. It exposes one operation — take a proposal, apply the mandate check, return a signature or an escalation — and never exposes key material. Three positions for key material follow, in order of preference:

1. **Inside the runtime process — rejected.** An LLM runtime is an untrusted interpreter of untrusted input; a key readable by the runtime is a key exfiltrated by the first successful prompt injection. No mandate can bound a key the runtime holds, because the mandate check itself runs on stolen ground.
2. **Inside the client process, runtime proposes across a process boundary — the minimum.** This is the reference client's line made real: the runtime's only verb is `propose_event`, and signing happens in a process the runtime does not control.
3. **Inside an OS keystore or secure element, where even the client receives only a `sign()` capability and never the bytes — the recommendation.** Signing becomes a capability, not a possession.

The consequence that matters constitutionally: **scope enforcement must live in the signer's trusted base, with the key — not in the agent.** If the mandate check runs runtime-side, a compromised runtime signs without limit; if it runs signer-side, a compromised runtime can only *propose*, and everything out of scope still escalates to a human. This takes a position on the first half of the open question in [delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §10 (*compromised approval surface*): the check can be independent of the consumer agent, by co-locating it with the key. The residue — a compromised *signer* — remains open, and §8 keeps it that way honestly.

## 3. Two Tiers of Keys

Not all keys carry the same risk, so they should not share custody requirements. The Canon already contains the dividing line; this section only reads it as a custody rule.

- **A root key** (the human's) signs rarely and consequentially: mandates (`AUTHORIZE`), key rotations and revocations (`KEY`), out-of-scope escalations. It should live cold — used through a deliberate, human-present ceremony, never resident where any runtime can reach it.
- **An agent or device key** signs often and boundedly: the in-scope `ATTEST`s a mandate covers. It may live hot — resident in the keystore of the device running the client — *because* the mandate bounds what it can do without re-asking.

The tier boundary is not a new concept: it is the mandate boundary again. What a key may sign without a human present is exactly what a mandate covers; everything above that line requires the root key, and the root key's custody requirement *is* the human-present ceremony. Hot keys are tolerable precisely to the degree that their mandates are narrow ([delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §5: scope you cannot express precisely is scope you should not delegate — and, here, scope you should not leave resident on a device).

## 4. Multi-Device Custody Is Delegation Applied to Yourself

A human acts from a phone, a laptop, perhaps more. The tempting answer — synchronize the key across devices — is rejected: copying key material multiplies the attack surface by the number of devices, and it destroys attribution, because the log can no longer say *which* device signed.

The design decision: **key material never moves; authority does.** Each device generates its own key, and the root binds it with an `AUTHORIZE` — the *subkey binding* that [event-registry.md](./event-registry.md) §4.3 already names — scoped like any mandate (budget, category, duration, device-appropriate limits). A lost phone is then not a custody catastrophe but an ordinary withdrawal: one `nullifies` ends that device key's coverage, and the laptop's key is untouched. Per-device keys are also what makes the threat model's "device-bound approval records" ([threat-model.md](./threat-model.md) §8.1) meaningful: an approval signed by the phone's key is evidence *the phone* approved.

This is the delegation graph of the reference client applied to one's own devices — multi-level authority, scoped grants, branch revocation — with no new event type. Multi-device custody was already expressible; it had simply not been read as custody before.

## 5. Compromise: The Blast Radius Is the Mandate's Scope

What a stolen hot key can do is exactly what its mandate covers — nothing more. The attacker holds a key whose every out-of-scope proposal still escalates to a human (§2), and whose in-scope ceiling was set in advance by the mandate's budget, category, and expiry. Recovery composes two mechanisms the Canon already has:

- the key is withdrawn by a `KEY` revocation whose `nullifies` is read **time-scoped** ([event-registry.md](./event-registry.md) §4.6): what the key signed before the revoke stays readable; nothing it signs after is honored;
- the mandates that depended on the key end with it ([delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §6).

No new compromise machinery is introduced; the compromise model *is* the composition of revocation semantics and mandate scope. This is the one slice of custody that reduces to a probe — and the probe has since run, on real Ed25519 keys rather than mock signatures ([compromise_fixture.py](../examples/reference-client/compromise_fixture.py)). It returned this section's claim sharpened rather than confirmed, in two findings offered — like every probe finding in this corpus — as probe results, not settled rules.

First, the blast radius is not the mandate's scope; it is the mandate's scope **× detection latency**. Every out-of-scope forgery fell exactly where this section predicts — the over-ceiling and out-of-context acts to scope, the self-elevation to the tier line (§3: a hot key cannot forge the cold root, so it cannot mint itself authority). But the number of *in-scope* acts an attacker gets honored is bounded by nothing in the mandate — only by the time until the revocation lands. Scope sets the height of the damage; detection latency sets its width; the blast radius is the product.

Second, **revocation is not surgical**. Revocation bounds future authority; it does not retroactively distinguish compromise from legitimate in-scope use. An in-scope forgery signed before the revoke is byte-indistinguishable from an honest act — signature valid, context right, ceiling respected — and the log holds no fact that separates them. Read time-scoped, the revocation preserves both; read as a cascade, it voids both, the honest history included. Neither reading excises only the compromise. Recovery of that window is therefore partly extra-log: the missing fact is not signature validity but custody provenance, which only the key's holder can supply, and it enters the log as a per-act dispute — a `CHALLENGE` and an honored `ADJUDICATE` voiding the specific event. This is the revocation probes' divergence ([authority-and-conflict.md](./authority-and-conflict.md) §9) arriving on the custody side, and the same three-layer split: the signature is a log fact, the honoring is a fold choice, the voiding is an authority's decision. Signature validity, mandate validity, and custody integrity are three different layers, and the probe shows the log can witness only the first two.

## 6. Root Loss Is a Cold Start Carrying a Continuity Claim

Losing the root key is the hard case. Every mandate, device binding, and history attribution chains up to it, and there is no authority of last resort to appeal to ([authority-and-conflict.md](./authority-and-conflict.md)): a protocol that could restore a lost root would be a central identity authority — the corner ARC has already declined, and the failure mode ("identity verified by protocol") the threat model warns against.

The design decision: **the protocol does not resurrect roots; it represents continuity claims.** A holder may prepare for loss in advance (a pre-signed rotation held cold) or assert succession after it (a new root, supported by counterparties' `ATTEST`s and a community's process). Both are evidence in the log. Neither is a verdict. Whether an observer honors a continuity claim is that observer's fold policy — exactly the cold-start finding: **recovery legitimacy, like legitimacy itself, is a relation between an observer's fold policy and the log** ([trust-model-tradeoffs.md](./trust-model-tradeoffs.md) §6, [threat-model.md](./threat-model.md) §18.1). A lost root is a cold start whose claimant arrives carrying a history they want recognized as theirs — and observers may legitimately disagree about whether it is.

This is offered in the same spirit as the probe findings it extends: a sharp formulation, not a settled rule.

## 7. ARC Does Not Custody Keys — and Does Not Forbid Custodial Signers

[event-registry.md](./event-registry.md) §10 holds that ARC never custodies value. The custody version: **ARC never custodies keys.** There is no protocol-level escrow, no recovery service, no mandated keystore. Custody is a deployment decision made by the human the keys answer to.

That includes the decision to hand keys to someone else. A custodial signer — a service holding keys and signing within a mandate the human granted — is fully representable with the existing `AUTHORIZE`, and this document does not forbid it. It names the trade-off instead: a custodial signer is a re-platforming of exactly the kind the threat model warns about ([threat-model.md](./threat-model.md) §13) — the human's authority becomes available to them only through an intermediary that can fail, be captured, or be compelled. Choosing that trade-off knowingly is sovereignty exercised; having it chosen silently by a default is not.

One honesty constraint binds every arrangement in this document: **custody quality is unverifiable from the log.** A signature proves that a key signed; it proves nothing about how the key was kept. An `ATTEST` claiming enclave-grade custody is a claim like any other. Counterparties read custody the way they read everything else in ARC — as evidence weighed by their own policy, not as a property the protocol certifies.

## 8. Open Questions

- **Enclave attestation.** Hardware attestation could make a custody claim *checkable* — but checkable against the hardware vendor's authority, importing a trust root ARC does not govern. Whether that import is worth it is undecided.
- **Threshold custody.** Splitting the root across M-of-N holders changes the loss and compromise model entirely (and would make §6's pre-signed rotation unnecessary). Representable in principle as multiple keys plus policy; not designed here.
- **A compromised signer.** §2 relocates trust from the runtime to the signer; it does not eliminate it. What bounds a signer that lies about its mandate check is open — the same residue as the approval-surface question it descends from.
- **In-flight acts at rotation.** What a rotation does to acts initiated under the old key but completing after it is the same divergence the delegation probes surfaced (preserve vs cascade) — a fold-policy choice, deliberately not made here.
- **Ceremony fatigue.** A root ceremony that fires too often degrades into the click-through approval this protocol exists to avoid ([delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §7). Where the ceremony threshold sits is a mandate-design question, unsolved there and inherited here.
- **Detection latency.** The compromise probe (§5) made time-to-revocation a first-class term of the blast radius, and nothing in this document shortens it. What would — counterparty confirmation ceremonies, anomaly heuristics in the signer, rate floors in mandate design — is custody-adjacent but undesigned, and at least one candidate (a signer that profiles its holder's behavior to flag anomalies) edges toward the stored profile ARC refuses.

## 9. Current ARC Position

Custody in ARC is exploratory and additive by reuse. The custody boundary and the mandate boundary are one trusted base: the runtime proposes, the signer signs, and scope is enforced where the key lives. Root keys are cold and ceremonial; agent and device keys are hot exactly as far as their mandates are narrow. Multi-device custody is the subkey binding already named in the registry — authority moves, key material does not. Compromise recovery composes time-scoped revocation with mandate death — and, the probe suggests, per-act adjudication for the in-scope window revocation cannot reach: revocation bounds future authority, it does not sort the past. Root loss is not resurrected by protocol; it is a continuity claim read by observer policy. ARC custodies no keys and forbids no custodial signer; it fixes the evidence and returns the reading — including the reading of a custody arrangement — to the observer.

These are design decisions offered for review, not settled doctrine. No new event type, primitive, or authority was needed to state them — nor to probe them: the compromise slice has now met its adversarial probe with real keys (§5), which sharpened it rather than overturned it. The remaining decisions still await theirs. Three of the invariants this document states are now also compiler-locked ([examples/canon-ts/custody.ts](../examples/canon-ts/custody.ts)) — scope attenuation, forward-bound revocation, adjudication-only surgical invalidation — with the limits of that lock (ceiling arithmetic, custody provenance, detection latency) stated in the file rather than papered over.
