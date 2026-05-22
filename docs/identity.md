# ARC Protocol: Identity

> **Status:** Exploratory draft
> **Purpose:** Agent identity model, verification layers, and professional credential binding
> For architecture overview, see [architecture.md](./architecture.md).

This document is a design proposal, not a finalized protocol rulebook.

Identity in ARC is intentionally incomplete at this stage. The goal is to describe the direction of the identity layer, identify trust boundaries, and make room for community review before implementation.

---

## 1. Why Identity Matters

Trust in agent commerce begins with identity.

Any agent can claim to be a reputable merchant, a licensed professional, or a verified logistics provider. Without a trustworthy identity layer, the entire reputation and governance model becomes fragile. Fake agents can accumulate false trust, impersonate legitimate providers, and exploit users who believe they are dealing with verified parties.

ARC's identity model starts from one principle:

> **Agent identity is derived from human identity. An agent cannot be more trusted than the human or organization behind it.**

---

## 2. Identity Layers

ARC explores three layers of agent identity.

### 2.1 Human Identity (Owner Layer)

Every agent should be owned by a verified human or legal entity.

Possible identity providers:

- Google Account
- Apple ID
- Microsoft Account
- National ID systems (country-specific)
- Business registration systems
- Verified payment accounts

The owner layer answers: **who is responsible for this agent?**

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
  "status": "verified",
  "created_at": "2026-01-01T00:00:00Z",
  "last_active": "2026-06-01T10:00:00Z"
}
```

Offers, approvals, and reputation events should be signed where manipulation resistance matters. Unsigned messages may still exist in early prototypes, but users should be able to distinguish verified records from unverified records.

### 2.3 Professional License Layer (Credential Layer)

For agents operating in regulated domains — law, medicine, finance, architecture — ARC may support an optional credential layer that binds professional licenses to agent identity.

The key idea is: **a licensed professional may delegate limited agent activity under their verified credential.**

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
    "verified": true,
    "verification_url": "https://www.koreanbar.or.kr/verify/example"
  },
  "agent_scope": ["legal_information", "contract_review_support", "dispute_summary"],
  "community": "seoul-legal-services",
  "status": "credentialed"
}
```

---

## 3. Professional License Binding

### 3.1 Core Principle

An agent's professional authority is derived from its owner's license.

- A lawyer's agent may support legal workflows within boundaries set by that lawyer, the relevant jurisdiction, and applicable professional rules.
- A doctor's agent may support medical information workflows only within boundaries permitted by the responsible professional and regulator.
- If the professional's license is suspended or revoked, the agent's credential status should be reviewed and restricted.

The agent does not hold the license. The human does. The agent inherits limited trust from the human.

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
Credential proof reviewed by community governance
          |
          v
Agent status updated to reflect credentialed scope
          |
          v
Credential expiry monitored or periodically rechecked
          |
          v
On expiry or revocation, agent scope is restricted or reviewed
```

Most licensing authorities may not provide public verification APIs. ARC should support layered verification: API verification where available, cryptographic credential issuance where supported, and community-reviewed manual verification as a pragmatic fallback.

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
| `unverified` | No identity verification completed |
| `basic` | Identity provider verified (Google, Apple, etc.) |
| `verified` | Community-verified identity |
| `credentialed` | Professional credential verified and active |
| `suspended` | Temporarily suspended by governance |
| `revoked` | Removed or no longer trusted by the community |

---

## 5. Agent Identity Lifecycle

```txt
Agent created by human owner
          |
          v
Identity provider verification
          |
          v
Community onboarding or probation period
          |
          v
Active verified agent
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

- Transaction volume is limited
- These temporary limits are intended as anti-fraud safeguards, not economic controls.
- Reputation score changes are rate-limited
- Community moderators may flag unusual activity

The goal is not to block newcomers. The goal is to let new agents build trust while limiting early fraud risk.

---

## 6. Key Design Decisions

### 6.1 Agents Cannot Self-Verify

No agent should verify its own identity or credentials. Verification should come from external identity providers, professional authorities, or community governance.

### 6.2 License Revocation Should Propagate

If a professional's license is revoked by the issuing authority, the agent's credential status should be updated through the relevant community or verification process.

This document does not define a universal enforcement window. Different domains and jurisdictions may require different procedures.

### 6.3 Agents Are Not Legal Entities

An agent is not a legal person. It cannot enter legally binding contracts on its own behalf. All legal responsibility remains with the human owner or legal entity behind the agent.

The credential layer reflects the owner's professional standing. It does not create new legal standing for the agent.

### 6.4 Scope Is Conservative by Default

Agents should default to the minimum necessary scope. A lawyer's agent does not automatically get permission to provide financial information, even if the lawyer holds dual qualifications. Scope should be explicitly declared and reviewed.

---

## 7. Privacy Considerations

Professional license numbers and verification details are sensitive. ARC recommends:

- Store credential hashes, not raw license numbers, in public agent profiles
- Provide verification URLs that allow third parties to confirm validity without exposing raw data
- Allow professionals to control visibility of credential details beyond community governance

---

## 8. Career-Based Trust (Non-Licensed Professionals)

Not all service providers hold formal licenses. A plumber, welder, electrician, or carpenter builds trust through experience and track record — not through a credential issued by a central authority.

ARC treats career-based trust as an important identity design area.

### 8.1 Portfolio and Experience Layer

Agents representing skilled tradespeople may attach verified career records:

```json
{
  "agent_id": "plumber_choi_001",
  "owner_type": "individual",
  "credential": {
    "type": "career_portfolio",
    "profession": "plumber",
    "years_experience": 8,
    "completed_jobs": 312,
    "portfolio_url": "https://arc.community/portfolio/choi",
    "community_verified": true
  },
  "reputation_score": 4.7,
  "community": "seoul-home-services"
}
```

Verified completed jobs, community ratings, and dispute history may form the trust basis — not a license number.

### 8.2 New Entrant Protection

A community that blocks new entrants can become a monopoly. ARC governance should protect against this.

New agents entering a community may receive:

- A probation period with reduced transaction limits, not zero access
- Access to lower-risk job categories to build initial reputation
- A "new member" badge visible to consumers, with optional discount incentives
- Protection from being systematically excluded by established providers

Communities should avoid entry requirements that prevent new participants from ever building reputation.

### 8.3 Healthy Competition / Anti-Monopoly Discovery Principles

ARC encourages open and competitive local discovery ecosystems.

ARC governance may support transparent discovery diversity policies, such as:

- Preventing a single provider from dominating a local category
- Making ranking concentration visible to communities and users
- Giving consumers clear choice among trusted providers, including newer entrants
- Allowing communities to review discovery patterns when local markets become too concentrated

This should not hide the best provider from consumers or enforce rigid economic control. It is an optional community review principle for keeping discovery open, transparent, and resistant to monopoly capture.

### 8.4 Optional Reputation Decay

Established agents with high reputation scores should not permanently block new entrants simply by existing.

Communities may optionally apply reputation decay mechanisms, such as:

- Lower discovery weight for agents with low recent activity
- Recent reliability signals alongside historical reputation
- Community-defined decay policies that reflect local conditions

The goal: **reputation should reflect current reliability, not just historical dominance.**

---

## 9. Current Status

The identity layer is a design proposal. No implementation exists.

Priority for Stage 2 implementation may include:

- Ed25519 key pair generation per agent
- Basic identity provider integration (Google / Apple)
- Agent profile schema

Professional credential binding is a later-stage design area and depends on community demand, jurisdiction, and regulatory review.

Contributions to the identity design are welcome. See [CONTRIBUTING.md](../CONTRIBUTING.md).
