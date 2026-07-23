# ARC Protocol: Identity

> **Status:** Exploratory draft
> **Purpose:** Agent identity model, verification layers, and professional credential binding
> For architecture overview, see [architecture.md](./architecture.md).

This document is a design proposal, not a finalized protocol rulebook.

Identity in ARC is intentionally incomplete at this stage. The goal is to describe the direction of a possible identity profile, identify its evidence boundaries, and support review before a normative or production identity profile is selected.

---

## 1. Why Identity Matters

Commerce identity profiles need declared evidence linking agent keys to the principals or organizations whose authority they claim.

An agent can claim to be a merchant, licensed professional, or logistics provider. A named identity profile needs to distinguish self-assertion from external evidence and disclose the limits of each check; ARC does not itself determine that a claimant is legitimate.

This exploratory identity model starts from one narrower principle:

> **Where a claimed authority requires a principal, a named profile may require evidence linking the agent key to that principal. Such evidence does not establish generalized trust.**

This principle is directional, not solved.

ARC does not currently solve the identity-reputation bootstrap problem. A named application profile may combine external identity evidence, limited transaction scope, probation, visible uncertainty, and human review; the effects of those choices are not established. This remains an open design problem rather than a completed layer.

---

## 2. Identity Layers

ARC explores three layers of agent identity.

### 2.1 Principal Identity (Owner Layer)

Where a profile requires principal accountability, it should declare what evidence links an agent key to the responsible principal, including a person, organization, or legal entity, and what that evidence does and does not establish.

Possible identity providers:

- Google Account
- Apple ID
- Microsoft Account
- National ID systems (country-specific)
- Business registration systems
- Payment-account checks under a named provider profile

**A known tension:** ARC values open and portable infrastructure, yet an accessible early identity model may rely on centralized providers such as Google Account or Apple ID. This is a pragmatic starting point, not a final position.

A consumer-grade identity provider account is not merchant verification.

Google, Apple, Microsoft, or similar accounts may help establish account continuity. They do not prove business legitimacy, inventory ownership, fulfillment capability, professional authority, safe operations, or legal compliance.

Business identity may require additional checks such as business registration review, payment account verification, local community onboarding, address or domain verification, professional credential review, or provider-specific merchant checks. ARC does not define a universal verification process at this stage.

One direction worth exploring is progressive evidence: initial provider checks supplemented over time by transaction claims that pass a named profile's record checks and by community rulings. Cross-context portability remains an open design problem.

The owner layer records evidence relevant to the question: **who claims responsibility for this agent, under this profile?**

It does not fully answer: **is this agent safe, legitimate, solvent, licensed, or capable of fulfillment?**

### 2.2 Agent Identity (Cryptographic Layer)

Each agent may have a unique cryptographic identity:

```json
{
  "agent_id": "merchant_abc_001",
  "owner_id": "user_xyz",
  "owner_type": "individual",
  "identity_provider": "google",
  "public_key": "ed25519:...",
  "community": "seoul-local-commerce",
  "created_at": "2026-01-01T00:00:00Z"
}
```

What this illustrative agent identity record *holds* is minimal and anchoring: an owner reference, a public key, and the community it registered in. It does not define `status`, `standing`, `reputation`, or `verification` as authoritative fields. Those are **Projections** folded from declared Events and inputs (see §4 and [object-model.md](./object-model.md) §4). An implementation may cache a derived view, but that cache is not canonical identity state.

Offers, approvals, and Canon Events carrying reputation evidence may be signed under a declared security profile where covered-byte integrity and key attribution matter. Interfaces should distinguish records that pass the declared checks from messages that have not been checked; neither label establishes payload truth.

Under a declared security profile, a valid signature supports the conclusion that the corresponding key signed the covered bytes. It does not establish who controlled the key, covering authority, honesty, fulfillment capacity, merchant legitimacy, or human understanding.

### 2.3 Professional License Layer (Credential Layer)

For agents operating in regulated domains — law, medicine, finance, architecture — ARC may support an optional credential layer that binds professional licenses to agent identity.

The key idea is narrower: **a named professional profile may record limited delegation from a license holder when the declared credential evidence passes that profile's checks. ARC does not determine the delegation's legal effect.**

```json
{
  "agent_id": "legal_agent_001",
  "owner_id": "lawyer_kim",
  "owner_type": "professional",
  "identity_provider": "google",
  "public_key": "ed25519:...",
  "credential": {
    "type": "professional_license",
    "profession": "lawyer",
    "license_number_hash": "sha256:...",
    "issuing_authority": "대한변호사협회",
    "issued_at": "2020-03-01",
    "expires_at": "2026-03-01",
    "declared_credential_check_passed": true,
    "credential_check_source": "https://example.org/credential-status"
  },
  "agent_scope": ["legal_information", "contract_review_support", "dispute_summary"],
  "community": "seoul-legal-services"
}
```

The `credential` block is a reference to a credential claim, recorded as a signed credential `ATTEST` and evaluated under a named profile. It is not a trust score or proof that the license is valid. Whether the credential is treated as active (`credentialed`, `suspended`, `revoked`) is a Projection over those credential Events and any commons `ADJUDICATE`, not a stored field on the record (see §4).

---

## 3. Professional License Binding

This credential layer is speculative and high-risk. Real deployment would require legal, regulatory, and institutional review in each jurisdiction before implementation.

**Legal warning:** An agent associated with a licensed professional does not automatically gain authority to provide regulated services. Legal, medical, financial, tax, architectural, or other professional assistance must remain within what the responsible licensed human and local law permit; even information-support workflows may be restricted in some jurisdictions.

ARC does not propose this layer for an MVP or pilot. Many professional authorities may never provide public verification APIs, and verification may remain manual, legally restricted, or unavailable without formal institutional cooperation.

Unauthorized practice risk is a core boundary. A future ARC-compatible system must not imply that credential metadata, community review, or agent association authorizes services that local law reserves to licensed humans or regulated entities.

### 3.1 Core Principle

A named professional profile may require agent scope to trace to a license holder's recorded delegation and credential evidence. ARC itself does not determine professional authority.

- A lawyer's agent may support legal workflows within boundaries set by that lawyer, the relevant jurisdiction, and applicable professional rules.
- A doctor's agent may support medical information workflows only within boundaries permitted by the responsible professional and regulator.
- If the professional's license is suspended or revoked, the agent's credential status should be reviewed and restricted.

The agent does not itself hold the professional license in this model. A profile may record a limited delegation from the license holder, but that delegation does not transfer the license or generalized trust.

### 3.2 Possible Credential Types

| Credential Type | Example Scope | Example Authority |
| --- | --- | --- |
| `lawyer` | Legal information, contract review support, dispute summary | 대한변호사협회, State Bar |
| `doctor` | Medical information, triage support | 대한의사협회, Medical Board |
| `pharmacist` | Medication information | 대한약사회 |
| `accountant` | Tax information, financial review support | 한국공인회계사회, CPA Board |
| `architect` | Design consultation, code compliance support | 대한건축사협회 |
| `financial_advisor` | Investment information | 금융감독원, SEC |

### 3.3 Credential Verification Flow

```txt
Professional registers agent
          |
          v
Agent submits credential claim
          |
          v
Issuing authority API queried, or manual verification performed
          |
          v
Credential evidence reviewed under the named process
          |
          v
Credentialed scope recorded as a signed credential event
          |
          v
Credential expiry monitored or periodically rechecked
          |
          v
On expiry or revocation, agent scope is restricted or reviewed
```

Where permissible and institutionally supported, ARC could explore layered verification: API verification where available, cryptographic credential issuance where supported, and community-reviewed manual verification as a pragmatic fallback.

This flow is illustrative. It should not be interpreted as a claim that professional authorities will cooperate, that manual verification is legally sufficient, or that community governance can grant professional authority.

### 3.4 Scope Declaration

A credentialed agent should declare its operating scope. It should not imply authority outside that scope.

Example:

```json
{
  "agent_scope": ["legal_information", "contract_review_support"],
  "agent_scope_excluded": ["court_representation", "notarization"]
}
```

Scope violations should be handled as governance issues, not as automatic protocol assumptions. Different jurisdictions may require different treatment.

---

## 4. Identity Status Levels

These levels are illustrative and may change as the design matures.

| Status | Meaning |
| --- | --- |
| `unverified` | No disclosed identity evidence satisfies the named profile's checks |
| `basic` | Account-continuity evidence passes the named checks; this does not prove merchant legitimacy or professional authority |
| `verified` | The named profile records that declared community or institutional evidence passed its checks, with scope and limits disclosed |
| `credentialed` | The named profile treats credential evidence as active within a declared scope; legal effect remains external |
| `suspended` | A temporary governance ruling is active under the named profile |
| `revoked` | A withdrawal or revocation ruling is active under the named profile |

These are illustrative Projection labels, not base ARC identity states. A claim using one should identify the profile and disclose the evidence check or ruling it represents.

Identity status is not a stored field. It is a projection — a fold over a key's `KEY` lifecycle events, credential `ATTEST`s, and any commons `ADJUDICATE` (`gov.*`) — recomputed on demand (see [object-model.md](./object-model.md) §4, [event-registry.md](./event-registry.md) §7).

---

## 5. Agent Identity Lifecycle

```txt
Agent key created; principal link claimed
          |
          v
Identity-provider evidence checked under profile
          |
          v
Community onboarding or probation period
          |
          v
Profile-specific identity status projected
          |
          v
[Optional] Professional credential binding
          |
          v
Credentialed agent with declared scope
          |
          v
Credential expiry, license revocation, or governance review
          |
          v
Scope restricted, credential removed, or agent suspended
```

New agents may enter a probation period during which:

- Temporary risk controls may apply during the probation period
- These temporary limits are intended as anti-fraud safeguards, not economic controls.
- Reputation signal growth is rate-limited
- Community moderators may flag unusual activity

These are optional Commerce policies intended to let entrants accumulate relevant evidence while constraining selected early risks; their fairness and effectiveness are not established.

---

## 6. Key Design Decisions

### 6.1 Self-Assertion Is Not Independent Verification

A named identity profile should not treat an agent's self-assertion as independent verification. It may require evidence from declared external identity providers, professional authorities, payment providers, business registries, or community processes, each with stated scope and limitations.

Community governance may review evidence, but it should not pretend to replace institutional authority where such authority is legally required.

### 6.2 Possible Professional-Credential Revocation Handling

A named professional-credential profile may require a credential-status update after a revocation record from its declared issuing authority passes that profile's checks.

This document does not define a universal enforcement window. Different domains and jurisdictions may require different procedures.

### 6.3 Legal Status Remains External

ARC assigns no legal status, contracting capacity, or allocation of responsibility. Those questions remain external and jurisdiction-specific. The credential layer records claims and delegated scope; it does not create legal standing.

### 6.4 Profile Scope Defaults

A named professional application profile may default to minimum necessary scope and require each supported professional domain to be declared and reviewed. Base ARC does not select professional-practice scope.

### 6.5 Identity and Reputation Are Circular Without Care

Identity helps decide which reputation records are meaningful.

A named reputation Projection may provide an evidence-linked signal for a new or lightly evidenced participant.

This creates a circular dependency. ARC does not define a complete solution. A named identity/reputation profile may use limited transaction scope, explicit uncertainty, probation, rate limits, or reviewable records; these are application-policy options, not base requirements.

---

## 7. Privacy Considerations

Professional license numbers and verification details are sensitive. Possible named-profile practices include:

- Store credential hashes, not raw license numbers, in public agent profiles
- Provide evidence URLs that let authorized observers apply the declared checks without exposing unnecessary raw data
- Allow professionals to control visibility of credential details beyond community governance
- Avoid exposing more identity evidence than is necessary for the named application's decision
- Apply local retention and deletion rules where legally required

---

## 8. Optional Commerce Identity and Discovery-Profile Considerations

Not all service providers hold formal licenses. A plumber, welder, electrician, or carpenter may present experience, outcome claims, and counterparty evidence rather than a centrally issued professional credential.

Career evidence is an optional identity/application research area; base ARC defines no career-trust profile.

### 8.1 Portfolio and Experience Layer

Agents representing skilled tradespeople may *claim* a career portfolio that points at attributable supporting evidence:

```json
{
  "agent_id": "plumber_choi_001",
  "owner_type": "individual",
  "claimed_portfolio": {
    "type": "career_portfolio",
    "profession": "plumber",
    "portfolio_url": "https://arc.community/portfolio/choi"
  },
  "community": "seoul-home-services"
}
```

The profile's standing view is **not** a count stored in this record. Completed-job claims, community ratings, and dispute history are inputs to a named Projection over `ATTEST rep.outcome` and any relevant commons `ADJUDICATE`, scoped to context (see §4 and [object-model.md](./object-model.md) §4). A `completed_jobs` or `years_experience` number written into a profile block is a self-asserted claim; a named profile decides what weight, if any, to give attributable supporting records.

ARC does not define career-based standing as authoritative stored state. Portfolio claims, experience counts, and community endorsements may be exaggerated or imported across contexts. A named Projection can instead expose which available records and policies produced a view, without establishing the underlying outcomes as true.

### 8.2 New Entrant Protection

A Commerce deployment may consider how its discovery and governance policies affect new entrants and consumer choice. Base ARC selects no entry or ranking policy.

Optional profile mechanisms for new agents may include:

- temporary anti-fraud risk controls during probation, not zero access
- access to lower-risk job categories to accumulate initial evidence
- a "new member" badge visible to consumers
- voluntary incentives or discounts, where communities choose to support them
- protection from being permanently excluded by established providers

Any such mechanism is application policy and should disclose its criteria and effects.

Cold-start handling is an application design concern. A named discovery profile may surface clearly labeled entrants, require declared external evidence, impose probation, or use another documented policy. ARC does not establish that any one mechanism prevents Sybil attacks or provides fair exposure.

### 8.3 Healthy Competition / Discovery Diversity

A Commerce deployment may choose policies intended to support competition or discovery diversity; their effects require evaluation.

A named Commerce profile may review discovery concentration or offer optional alternatives. Base ARC neither selects trusted providers nor prescribes transaction caps or ranking defaults.

Possible community-level tools may include:

- making ranking concentration visible to users
- highlighting newer entrants with declared profile evidence as optional alternatives
- showing recent reliability signals alongside historical reputation
- supporting voluntary discounts or incentives for new entrants
- allowing users to switch discovery backends when they suspect bias

These are optional application-policy choices, not base ARC requirements or demonstrated outcomes.

### 8.4 Optional Recent Reliability Signals

Historical evidence may remain relevant, while consumers may also want a view over more recent records.

Communities may optionally make additional signals visible, such as:

- recent activity records that pass declared profile checks alongside historical claims
- clearly labeled reliability time windows
- user-selectable views that prioritize history or recent signals

Any use of these signals is application policy and should disclose how it affects ordering or eligibility to the relevant observer.

---

## 9. Current Status

The identity layer is a design proposal. Current probes include key and authority records, but no production identity-assurance profile or provider integration exists.

Possible future identity-profile work may include:

- key-pair generation under a declared security profile (Ed25519 in current reference fixtures)
- Basic identity provider integration (Google / Apple)
- Agent profile schema
- Clear distinction between account continuity, merchant legitimacy, and professional authority
- Key rotation and compromised-key handling notes

Where keys live — the signer boundary, key tiers, multi-device binding, compromise and root loss — is explored as a set of design decisions in [key-custody.md](./key-custody.md).

Professional credential binding is a later-stage design area and depends on community demand, jurisdiction, and regulatory review.

Contributions to the identity design are welcome. See [CONTRIBUTING.md](../CONTRIBUTING.md).
