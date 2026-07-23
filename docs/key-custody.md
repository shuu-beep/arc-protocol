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

Under a declared security profile, a valid signature supports the conclusion that the corresponding key signed the covered bytes ([identity.md](./identity.md) §2.2). It does not establish who controlled the key or where it lived when signing — whether in a hardware enclave, an OS keystore, a client process, or a plaintext file readable by other processes.

Earlier Event and Projection questions could be explored with mock signing. Later custody probes use Ed25519 keys and process separation to establish bounded fixture properties, but they do not establish production custody quality. Custody remains partly outside the log, so this document describes a reference custody profile and its open dependencies rather than a base ARC requirement.

The corpus has already dug the holes these decisions fill: [event-registry.md](./event-registry.md) §4.3 names a **subkey binding** among the things `AUTHORIZE` subsumes but never specifies it (§4 here); [delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §10 asks whether scope enforcement can be checked independently of the consumer agent (§2 here); the reference client draws the line — *the runtime proposes, the client signs* — and stops at "where keys live is out of scope" (§2–§3 here). What follows connects lines already drawn.

## 2. Reference Custody Profile: Signer-Side Scope Enforcement

The reference client's write path established the shape: a runtime proposes events; a boundary checks each proposal against the active mandate and either signs or escalates; the key never crosses the proposal line. Custody is the question of what stands on the signing side of that line.

The reference profile uses a signer boundary rather than exposing key material to the agent runtime. It accepts a proposal, applies the profile's mandate check, and returns a signature, refusal, or escalation result. Three custody placements are compared below as profile recommendations:

1. **Inside the runtime process — not used by this profile.** A key readable by a runtime increases exposure to prompt injection and runtime compromise, and a runtime-side mandate check does not provide process separation.
2. **Inside the client process, runtime proposes across a process boundary — the minimum.** This is the reference client's line made real: the runtime's only verb is `propose_event`, and signing happens in a process the runtime does not control.
3. **Inside an OS keystore or secure element, where even the client receives only a `sign()` capability and never the bytes — the recommendation.** Signing becomes a capability, not a possession.

In this reference profile, scope enforcement lives in the signer's trusted base with the key, rather than in the agent. A compromised runtime can then propose but cannot directly sign; the signer may refuse or route proposals under its declared policy. This addresses part of the open approval-surface question in [delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §10. A compromised signer and an unfaithful mandate interpretation remain open (§8).

## 3. Two Tiers of Keys

Not all keys carry the same risk. This reference profile applies different custody recommendations according to the authority each key holds; base ARC does not mandate these placements.

- **A root key** belongs to the responsible principal or authority holder; in the current reference profile, that holder is typically human. It signs rarely and consequentially: mandates (`AUTHORIZE`), key rotations and revocations (`KEY`), out-of-scope escalations. This profile recommends cold storage and a deliberate, human-present ceremony.
- **An agent or device key** signs often and boundedly: the in-scope `ATTEST`s a mandate covers. This profile permits hot storage in a device keystore, with risk bounded only to the extent that the mandate and signer enforcement are effective.

The tier boundary reuses the mandate boundary. In this profile, the signer may sign without a human present only within the mandate it interprets; proposals outside that coverage require refusal or a separately authorized escalation path. Narrow mandates can limit modeled exposure, but do not establish custody safety ([delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §5).

## 4. Multi-Device Custody Is Delegation Applied to Yourself

A human may act from a phone, a laptop, or more devices. This reference profile avoids synchronizing one key across them because copying key material increases exposure and prevents a signature from distinguishing which device-associated key was used.

The profile keeps key material on each device and moves authority through `AUTHORIZE`. Each device generates its own key, and the root binds it with the *subkey binding* that [event-registry.md](./event-registry.md) §4.3 already names, scoped like any mandate. One `nullifies` can then end that device key's coverage without withdrawing another device key. An approval signed by a phone-associated key is evidence that the key signed; it does not prove that the physical phone or its intended user approved.

This is the delegation graph of the reference client applied to one's own devices — multi-level authority, scoped grants, branch revocation — with no new event type. Multi-device custody was already expressible; it had simply not been read as custody before.

## 5. Compromise: Modeled Exposure Under the Reference Profile

A stolen hot key can sign bytes directly; whether a resulting act is honored depends on the declared mandate and fold. The compromise fixture models how budget, category, expiry, and revocation constrain selected cases. Recovery in that model composes two mechanisms the Canon already has:

- the key is withdrawn by a `KEY` revocation whose `nullifies` is read **time-scoped** ([event-registry.md](./event-registry.md) §4.6): what the key signed before the revoke stays readable; nothing it signs after is honored;
- the mandates that depended on the key end with it ([delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §6).

No new compromise machinery is introduced; the compromise model *is* the composition of revocation semantics and mandate scope. This is the one slice of custody that reduces to a probe — and the probe has since run, on real Ed25519 keys rather than mock signatures ([compromise_fixture.py](../examples/reference-client/compromise_fixture.py)). It returned this section's claim sharpened rather than confirmed, in two findings offered — like every probe finding in this corpus — as probe results, not settled rules.

First, the fixture's modeled exposure depends on mandate scope and detection latency. Its fold rejects the tested over-ceiling, out-of-context, and self-elevating acts, while its record checks do not distinguish intended from compromised in-scope use before the effective revocation point. The fixture does not quantify real damage or prove that these are the only relevant dimensions.

Second, **revocation is not surgical**. Revocation bounds future authority; it does not retroactively distinguish compromised from intended in-scope use. In the fixture, record verification cannot distinguish intended from compromised use of the same key before the effective revocation point. A preserve policy honors both completed acts; a cascade policy declines to honor both. Additional custody evidence may support a per-act `CHALLENGE`, while an authorized `ADJUDICATE` can void a referenced act under a named governance profile. The signature record, current honoring policy, and custody provenance remain distinct layers; the fixture does not establish custody integrity.

A later fixture ([embodiment_fixture.py](../examples/reference-client/embodiment_fixture.py)) carries §2's boundary into a running object graph: the key is resident in a separate signer and the agent holds none. Within that fixture, the agent can propose but cannot directly produce a signed act, and the signer refuses the tested out-of-scope and self-elevating proposals before appending them. It still auto-signs tested in-scope proposals regardless of who composed them, so process separation does not resolve the legitimacy ambiguity. The fixture localizes the mandate check to its signer while retaining that signer, the escalation path, and the human review surface as trusted dependencies. This is a bounded probe result, not a production security guarantee.

The approval-seam fixture ([approval_seam_fixture.py](../examples/reference-client/approval_seam_fixture.py)) models a routed proposal, an authored approval decision, and a return path. Its counterfactual shows that a scope-only approval would permit the tested payee re-aim. The fixture's proposal binding blocks the tested in-process re-aim, replay, and bare-scope cases under its stored state; it does not establish persistent single use, an exact-byte production binding, or faithful human review. Availability, the return path, renderer fidelity, and the human review surface remain dependencies.

A third fixture ([signer_fidelity_fixture.py](../examples/reference-client/signer_fidelity_fixture.py)) tests a premise of sign-time enforcement: how the signer interprets the mandate. [custody.ts](../examples/canon-ts/custody.ts) §8 places ceiling arithmetic in the signer's trusted base, where neither the type layer nor the log can observe the implementation's reading. The fixture compares two readings of the same mandate. A spend over a recorded ceiling reaches the log under the drifted signer but is declined by the fixture's observer folds; an ambiguous adjacent category produces different policy-relative readings. An in-scope Event can be byte-identical under either signer implementation, so record verification does not establish faithful mandate interpretation. Process separation narrows key exposure in the fixture; it does not certify the signer's reading. Hardware or software attestation would add an external trust dependency rather than settle that interpretation within ARC.

The same dependency appears in the optional federation fixture ([federation-fidelity-demo](../examples/federation-fidelity-demo/)). Under its binding-recognition policy, an importing community accepts a remote authority's acts without re-folding them against the mandate and therefore depends on the remote signer's interpretation. Under its advisory policy, the importer applies its own reading: it catches a spend over a recorded ceiling but does not resolve an ambiguous term. This is a bounded result of the fixture's named policies, not a required federation topology or a certification of either signer's fidelity.

The view-fidelity probe ([view-fidelity-demo](../examples/view-fidelity-demo/)) varies the renderer between signed bytes and a simulated human-facing view. A `view_hash` can detect the tested mismatch only when the verifier already has the expected rendered bytes or equivalent trusted input; recomputing through the same deterministic-but-unfaithful renderer does not establish what was displayed or whether the renderer was faithful. The renderer and human perception therefore remain off-log dependencies. A rendered-view `ATTEST` records another claim; it does not certify presentation fidelity.

## 6. Root Loss Is a Cold Start Carrying a Continuity Claim

Losing the root key breaks the continuity path used by this reference profile. Base ARC supplies no root-recovery authority. A deployment may rely on a custodial or external recovery authority, but that authority and its precedence must be declared outside the base Canon.

Without such an external recovery authority, ARC can represent continuity claims. A holder may prepare a pre-signed rotation or assert succession using a new root plus supporting `ATTEST`s and a community process. These are records, not verdicts. A named observer policy decides whether to honor the asserted continuity; the Events alone do not establish that the claimant controls the prior identity ([trust-model-tradeoffs.md](./trust-model-tradeoffs.md) §6, [threat-model.md](./threat-model.md) §18.1).

This is offered in the same spirit as the probe findings it extends: a sharp formulation, not a settled rule.

## 7. ARC Does Not Custody Keys — and Does Not Forbid Custodial Signers

[event-registry.md](./event-registry.md) §10 holds that ARC never custodies value. The custody version: **ARC never custodies keys.** There is no protocol-level escrow, no recovery service, no mandated keystore. Custody is a deployment decision made by the principal or authority holder the keys answer to.

That includes the decision to use a custodial signer — a service holding keys and signing within a mandate granted by the relevant authority holder. The arrangement is representable with the existing `AUTHORIZE`, and base ARC neither requires nor forbids it. The named profile should disclose that the authority holder's authority is then available only through an intermediary that can fail, be compromised, or be compelled ([threat-model.md](./threat-model.md) §13).

One evidence boundary applies to every arrangement in this document: **custody quality is not established by the log.** Under a declared security profile, a signature can support a key-and-bytes check; it does not show how the key was kept or who controlled it. An `ATTEST` claiming enclave-grade custody remains a claim evaluated under the observer's policy, not a property ARC certifies.

## 8. Open Questions

- **Enclave attestation.** Hardware attestation could make a custody claim *checkable* — but checkable against the hardware vendor's authority, importing a trust root ARC does not govern. Whether that import is worth it is undecided.
- **Threshold custody.** Splitting the root across M-of-N holders changes the loss and compromise model entirely (and would make §6's pre-signed rotation unnecessary). Representable in principle as multiple keys plus policy; not designed here.
- **A compromised signer.** §2 moves the reference profile's key and mandate check from the runtime to the signer; it does not eliminate that dependency. If the signer is compromised, the fixture's process separation no longer constrains direct signing. The resulting real-world exposure is not quantified here.
- **The signer's reading.** Sign-time enforcement depends on how the signer implements the mandate grammar. The fidelity fixture ([signer_fidelity_fixture.py](../examples/reference-client/signer_fidelity_fixture.py)) compares two implementations and shows that their Events do not encode which interpretation produced them. Some differences surface when observer folds re-check recorded bounds; ambiguous terms remain policy-relative. Attesting the signer would add an external trust dependency rather than prove faithful interpretation within ARC. Open.
- **The escalation return path.** The approval-seam fixture (§5, [approval_seam_fixture.py](../examples/reference-client/approval_seam_fixture.py)) blocks its tested re-aim, replay, and scope-only cases under in-memory state. It does not establish production exact-byte binding, persistent single use, faithful human review, availability, or renderer fidelity. The view-fidelity probe shows that recomputing a hash through the same deterministic-but-unfaithful renderer does not establish what was displayed. Open.
- **In-flight acts at rotation.** What a rotation does to acts initiated under the old key but completing after it is the same divergence the delegation probes surfaced (preserve vs cascade) — a fold-policy choice, deliberately not made here.
- **Ceremony fatigue.** Frequent root-key ceremonies may reduce review quality ([delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md) §7). The appropriate threshold is unmeasured.
- **Detection latency.** The compromise fixture (§5) includes time-to-revocation as one modeled exposure variable. Counterparty confirmations, signer heuristics, and rate controls are custody-adjacent possibilities, not designed or evaluated here.

## 9. Current ARC Position

Custody in ARC remains exploratory. This document's reference profile separates the runtime from a signer and enforces its declared scope at that signer; base ARC does not mandate the process boundary, key tier, keystore, or custody provider. The profile recommends cold root keys, bounded device keys, per-device subkey bindings, and forward revocation. The probes show selected consequences of those choices, including the inability of revocation to distinguish compromised from legitimate pre-revocation use. Root-loss continuity claims remain observer-policy inputs. ARC itself operates no key-custody or recovery service and does not forbid custodial signers.

These profile choices are offered for review, not settled doctrine. The probes use real keys where process/key separation is relevant, but they do not establish production custody security. The TypeScript examples encode selected structural constraints such as scope attenuation and referenced adjudication; they do not prove custody provenance, faithful mandate interpretation, detection latency, or runtime enforcement ([examples/canon-ts/custody.ts](../examples/canon-ts/custody.ts)).

The document, reference-client fixtures, and TypeScript examples cover different bounded aspects of custody, authority, and revocation. None certifies the full arrangement. A compromised signer, interpretation fidelity, the escalation path, human review, threshold custody, enclave attestation, and detection latency remain open.
