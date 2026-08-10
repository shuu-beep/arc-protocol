# ARC Protocol: Identity and Root-Trust Boundaries

> **Status:** Non-normative identity and trust-boundary research
>
> ARC can validate and project records attributed to keys. It does not operate
> an identity provider, credential registry, trust root, account-recovery
> service, or legal-identity system.

## 1. Identity Claims Are Layered

An ARC-aware application should distinguish at least four claims:

1. **Key control:** a record verifies under a public key.
2. **Agent attribution:** an application associates that key with an agent or
   service account.
3. **Principal binding:** evidence associates the agent with a human,
   organization, or other principal.
4. **External status:** an issuer asserts a license, employment relationship,
   account status, business registration, or other credential.

Success at one layer does not prove the next. A signature proves control of key
material at signing time under the selected verification method; it does not
prove legal identity, beneficial ownership, independence, competence, or
authorization for the requested action.

The main terms are deliberately separate:

| Term | Meaning in this document | What it does not prove |
| --- | --- | --- |
| Principal | human, organization, or external entity on whose behalf authority is claimed | legal identity or beneficial ownership by itself |
| Agent | software or service acting under attributed authority | independent control, honesty, or mandate completeness |
| Signer/key | cryptographic key attributed as the author of signed bytes | that the signer is the principal or authorized Agent |
| Counterparty | independently represented participant in an interaction | that its advertised identity or authority is complete |
| Credential | external issuer claim about identity, role, account, or status | current authority for the exact action unless separately bound |
| External trust root | issuer, registry, platform, or institutional anchor selected by a profile | universal acceptance or infallibility |
| Attributable claim | claim whose signed bytes can be associated with a key under the declared check | truth, completeness, or real-world execution |
| Complete authority proof | evidence sufficient under a declared completeness contract and profile | a property ARC can infer from one signature or local Event set |

## 2. Principal and Agent Boundary

One principal may control many agents and keys. Conversely, one agent may be
operated through several services or rotated keys. ARC sees supplied records,
not the hidden real-world controller.

A profile that relies on principal identity must state:

- which identifier or external issuer is trusted;
- how the key-to-principal binding is obtained and verified;
- which agent/delegate is named by authority evidence;
- whether multiple keys belong to one lineage;
- what recovery, rotation, and revocation evidence is accepted; and
- what happens when the required evidence is missing or contested.

Self-assertion can be recorded but is not independent verification.

In a Buyer Agent/Seller Agent interaction, an attributable seller offer does
not automatically prove that Principal B authorized every term. Complete
seller-side authority would require the receiving profile to obtain and verify
the necessary principal binding, delegation, seller policy, key lineage, and
evidence-completeness inputs. The current ARC fixtures do not establish that
complete chain.

## 3. Key Lifecycle

Key lifecycle affects authority computation. Registration, rotation, and
revocation are represented with Canon `KEY` Events under declared predicates
and profile rules. The current key-revocation fixture uses a `KEY` Event with
the `id.key_revoke` predicate and `nullifies`; `KEY_REVOKE` is not a Canon Event
type.

Implementations must not assume that wall-clock timestamps alone establish that
a rotation or revocation causally precedes another Event. Reference Core keeps
ordering and lineage rules explicit and reports unsupported or contested cases.

Key revocation and authority withdrawal are different:

- key revocation changes whether records from a key remain acceptable under a
  security/profile rule;
- withdrawal seeks to nullify a particular authorization or mandate.

Neither automatically proves compromise, identifies the attacker, or restores
control to the correct principal.

## 4. Root Trust and External Credentials

Professional licenses, business registrations, employment status, payment
accounts, and government identifiers remain external to ARC. An application
may carry references or issuer-signed credentials, but it must decide:

- which issuer and credential format it trusts;
- how status and expiry are checked;
- whether online revocation or freshness is required;
- how scope in the credential relates to delegated action scope;
- how privacy and selective disclosure are handled; and
- what legal meaning, if any, follows from verification.

OAuth/OIDC, verifiable credentials, enterprise directories, cloud IAM, and
domain registries may supply these functions. ARC does not replace them.

## 5. Delegated Scope

Identity answers who or which key is involved; authority evidence answers what
that actor may do under a declared profile. Applications must still bind the
delegate and exact action or scoped mandate as described in
[delegation-and-spending-mandates.md](./delegation-and-spending-mandates.md).

A valid identity with tool access is not automatically authorized for an exact
consequential action. Conversely, ARC-shaped authority evidence is unusable if
the deployment cannot establish the required signer or delegate binding.

## 6. Custody and Runtime Compromise

If an agent runtime controls both the authority-signing key and the downstream
credential, compromise of that runtime can collapse both boundaries. A claim of
independent authority evidence requires relevant keys, approval channels,
authority state, and credentials to remain outside the compromised runtime's
control.

Key generation, secure storage, user presence, recovery, rotation, and incident
response are deployment responsibilities. See [key-custody.md](./key-custody.md)
and [threat-model.md](./threat-model.md).

## 7. Privacy and Data Minimization

Portable identity evidence can increase correlation and disclosure risk.
Implementations should minimize public identifiers, avoid placing sensitive
credentials directly in broadly replicated Events, disclose observer surfaces,
and separate audit needs from unnecessary permanent exposure.

ARC does not provide anonymity, unlinkability, selective disclosure, data
deletion, or regulatory compliance.

## 8. Commerce Counterparty Boundary

A receiver may combine ARC records with A2A/UCP profiles, verifiable
credentials, OpenID4VP presentations, OAuth/IAM identity, merchant registries,
or payment-network Agent trust. Those systems can strengthen identity and
attribution, but the receiver must still distinguish:

- the counterparty endpoint is authenticated;
- an offer is attributable to its signer;
- the signer is bound to an Agent and principal;
- the Agent has current authority for the offered terms; and
- the external transaction or fulfillment actually occurred.

No earlier statement proves a later one.

## 9. Historical Commerce Ideas

Earlier Commerce drafts explored professional-license binding, portfolio
signals, new-entrant discovery, and identity status labels. These are
application-policy ideas, not ARC authority primitives. They were not
implemented and are retained only as historical material.

## 10. Open Gaps

The current corpus does not settle:

- a normative key and signature profile for the Protocol;
- a universal key-to-principal binding;
- evidence-completeness discovery;
- multi-device recovery and compromise response;
- privacy-preserving credential presentation; or
- legal recognition of any ARC record.

Any production profile must choose and document those external trust roots.
