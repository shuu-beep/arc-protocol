// ARC Canon — local TypeScript type-shape probe (type-level only; NO runtime).
//
// The Python demo in ../canon-fold-demo tests bounded scenario coverage: its
// eleven authored scenarios currently use five event types.
//
// This file tests something narrower: fixture-local type-shape checks.
// It encodes three selected constraints in this module:
//   * local exhaustiveness (§5–§6) — this module uses a closed discriminated
//     union, so adding a member here requires updating its handlers;
//   * local verdict-slot shape (§7–§8) — this declared parameter accepts the
//     module's ADJUDICATE variant and rejects the demonstrated CHALLENGE and
//     ATTEST values;
//   * revocation/delegation add no type (§9) — findings A and G: withdrawal,
//     key revocation, delegation, and capability are expressed through the
//     `nullifies` FIELD, a predicate, and the reader's fold policy — never a new
//     canonical type in this module. The example pseudo-types are non-members.
// The configured check is `npx tsc --noEmit`. It provides no runtime
// cryptography, custody, chronology, or repository-wide conformance enforcement.
//
// Nothing here executes. There is no signing, no fold, no I/O — only type-level
// constructs and `declare`d signatures the compiler checks but never runs.

// ---------------------------------------------------------------------------
// 1. The closed canonical type set
// ---------------------------------------------------------------------------
// This union models the current top-level vocabulary for this fixture. The
// compiler knows these five members here. Application richness lives in
// `predicate` and `payload` (open below), never in a new member here.

export type CanonicalType =
  | "KEY"
  | "ATTEST"
  | "AUTHORIZE"
  | "CHALLENGE"
  | "ADJUDICATE";

// JSON-shaped, open payload values. Predicates and payloads are where richness
// grows; the type set above does not.
export type Json =
  | null
  | boolean
  | number
  | string
  | Json[]
  | { [key: string]: Json };

// ---------------------------------------------------------------------------
// 2. The shared envelope
// ---------------------------------------------------------------------------
// Every event carries these fields. `predicate` and `payload` are the OPEN
// extension axis; `nullifies` is the withdrawal FIELD (not a revoke type).

interface EventBase {
  id: string; // identifier; this module does not validate content addressing
  signer: string; // declared key id; this module performs no key resolution
  predicate: string; // namespaced semantic tag — richness grows HERE, not in `type`
  timestamp: string; // timestamp string; this module performs no format check
  refs?: string[]; // prior events / parties / resources this event is about
  nullifies?: string[]; // prior event ids withdrawn going forward (the field, §4.6)
  payload?: { [key: string]: Json };
  signature: string;
}

// AUTHORIZE-only scope. A spending mandate / delegation is the SAME primitive
// with a wider scope (budget, category, duration, redelegation), not a new type.
export interface Scope {
  category?: string;
  max_total_krw?: number;
  expires_at?: string;
  redelegatable?: boolean;
  [key: string]: Json | undefined;
}

// ---------------------------------------------------------------------------
// 3. Event as a discriminated union (discriminant: `type`)
// ---------------------------------------------------------------------------
// Each variant fixes one `type` literal in this module. A variant may add its
// own fields (AUTHORIZE adds `scope` / `contrary_to`).

export interface KeyEvent extends EventBase {
  type: "KEY"; // predicate ∈ { id.key_register, id.key_rotate, id.key_revoke }
}

export interface AttestEvent extends EventBase {
  type: "ATTEST"; // offer, payment_result, fulfillment, credential, rep.outcome, ...
}

export interface AuthorizeEvent extends EventBase {
  type: "AUTHORIZE"; // approval, mandate/delegation, subkey binding
  scope?: Scope;
  contrary_to?: string[]; // override-friction record (an approval made vs a warning)
}

export interface ChallengeEvent extends EventBase {
  type: "CHALLENGE"; // dispute, fraud report, appeal
}

export interface AdjudicateEvent extends EventBase {
  type: "ADJUDICATE"; // warning, suspension, expulsion, reinstatement, ruling
}

// This module's closed set. Adding a member here also requires updating the
// exhaustive switch in §5 before the module passes its type check.
export type Event =
  | KeyEvent
  | AttestEvent
  | AuthorizeEvent
  | ChallengeEvent
  | AdjudicateEvent;

// ---------------------------------------------------------------------------
// 4. Valid examples — one per canonical type (+ that richness is by predicate)
// ---------------------------------------------------------------------------

const keyRegister: KeyEvent = {
  type: "KEY",
  id: "ev:0001",
  signer: "k:merchant",
  predicate: "id.key_register",
  timestamp: "2026-01-02T00:00:00Z",
  payload: { key: "k:merchant", anchor: "business-registration" },
  signature: "stub:0001",
};

const offer: AttestEvent = {
  type: "ATTEST",
  id: "ev:0002",
  signer: "k:merchant",
  predicate: "commerce.offer",
  timestamp: "2026-02-01T10:00:00Z",
  refs: ["tx_1", "k:merchant"],
  payload: { item: "vegetable bibimbap", price_krw: 9800 },
  signature: "stub:0002",
};

const approval: AuthorizeEvent = {
  type: "AUTHORIZE",
  id: "ev:0003",
  signer: "k:consumer",
  predicate: "consent.approval",
  timestamp: "2026-02-01T10:01:00Z",
  refs: ["tx_1", "k:merchant"],
  scope: { max_total_krw: 15000 },
  payload: { approved_total_krw: 12300 },
  signature: "stub:0003",
};

// A spending mandate / delegation: same AUTHORIZE primitive, wider scope.
const mandate: AuthorizeEvent = {
  type: "AUTHORIZE",
  id: "ev:0004",
  signer: "k:human_principal",
  predicate: "consent.mandate",
  timestamp: "2026-06-11T00:00:00Z",
  refs: ["k:agent_a", "k:human_principal"],
  scope: {
    category: "food",
    max_total_krw: 50000,
    expires_at: "2026-09-01T00:00:00Z",
    redelegatable: true,
  },
  payload: { delegator: "k:human_principal", delegate: "k:agent_a" },
  signature: "stub:0004",
};

const dispute: ChallengeEvent = {
  type: "CHALLENGE",
  id: "ev:0005",
  signer: "k:consumer",
  predicate: "dispute.open",
  timestamp: "2026-03-01T12:00:00Z",
  refs: ["tx_4", "k:merchant"],
  payload: { reason: "paid but not delivered" },
  signature: "stub:0005",
};

const ruling: AdjudicateEvent = {
  type: "ADJUDICATE",
  id: "ev:0006",
  signer: "k:community",
  predicate: "gov.suspension",
  timestamp: "2026-03-03T09:00:00Z",
  refs: ["tx_4", "k:merchant"],
  payload: { finding: "non-fulfillment after payment", duration_days: 30 },
  signature: "stub:0006",
};

// This example uses a predicate string not otherwise used in the file while
// retaining an existing local type member.
const novelFlow: AttestEvent = {
  type: "ATTEST",
  id: "ev:0007",
  signer: "k:merchant",
  predicate: "commerce.warranty_claim",
  timestamp: "2026-07-01T00:00:00Z",
  signature: "stub:0007",
};

export const examples: Event[] = [
  keyRegister,
  offer,
  approval,
  mandate,
  dispute,
  ruling,
  novelFlow,
];

// ---------------------------------------------------------------------------
// 5. Exhaustive switch — local exhaustiveness checked by `never`
// ---------------------------------------------------------------------------
// Every member of this module's union is handled. In `default`, TypeScript narrows `e` to
// `never` precisely because the five cases above are exhaustive. If a sixth type
// is ever added to `Event`, `e` is no longer `never` here and `assertNever(e)`
// fails to compile until the new type is handled or removed in this module.

function assertNever(x: never): never {
  throw new Error(`non-canonical event type: ${JSON.stringify(x)}`);
}

export function describe(e: Event): string {
  switch (e.type) {
    case "KEY":
      return `KEY ${e.predicate}`;
    case "ATTEST":
      return `ATTEST ${e.predicate}`;
    case "AUTHORIZE":
      // variant-specific field is available after narrowing
      return `AUTHORIZE ${e.predicate}${e.scope ? " (scoped)" : ""}`;
    case "CHALLENGE":
      return `CHALLENGE ${e.predicate}`;
    case "ADJUDICATE":
      return `ADJUDICATE ${e.predicate}`;
    default:
      return assertNever(e); // local exhaustiveness check
  }
}

// ---------------------------------------------------------------------------
// 6. Local closed-set examples (commented out on purpose)
// ---------------------------------------------------------------------------
// Each block below is a type this fixture's union excludes. As written
// (commented) the file compiles. Uncommenting either block produces a type error
// under `npx tsc --noEmit -p tsconfig.json`.
//
// (a) This CAPABILITY literal is not assignable to the local Event union:
//
// const capability: Event = {
//   type: "CAPABILITY", // ❌ error: Type '"CAPABILITY"' is not assignable to
//   id: "ev:x",         //    CanonicalType ("KEY" | "ATTEST" | "AUTHORIZE" |
//   signer: "k:x",      //    "CHALLENGE" | "ADJUDICATE").
//   predicate: "cap.grant",
//   timestamp: "2026-01-01T00:00:00Z",
//   signature: "stub:x",
// };
//
// (b) If a new variant widens the union, the exhaustive switch also needs a case:
//
// interface DelegateEvent extends EventBase { type: "DELEGATE"; }
// type EventPlus = Event | DelegateEvent;
// function describePlus(e: EventPlus): string {
//   switch (e.type) {
//     case "KEY": case "ATTEST": case "AUTHORIZE":
//     case "CHALLENGE": case "ADJUDICATE":
//       return e.predicate;
//     default:
//       return assertNever(e); // ❌ error: Argument of type 'DelegateEvent' is
//                              //    not assignable to parameter of type 'never'.
//   }
// }
//
// The lesson: widening this module's union requires updating its constructors
// and exhaustive handlers. This is a fixture-local maintenance check.

// ---------------------------------------------------------------------------
// 7. ADJUDICATE-only fixture slot (finding E)
// ---------------------------------------------------------------------------
// This declared slot models one policy in which the verdict parameter has the
// ADJUDICATE shape. It rejects this module's CHALLENGE and ATTEST variants. It
// does not implement a Projection or establish a runtime governance policy.

// The local verdict type, extracted from this module's closed union.
export type GovernanceEvent = Extract<Event, { type: "ADJUDICATE" }>;

// The standings governance can hold. Vocabulary only: this names the possible
// RESULTS of a projection; ARC stores no standing field (object-model §4).
export type Standing =
  | "in_good_standing"
  | "warned"
  | "suspended"
  | "expelled";

// A declared slot used to test the parameter shape. `declare` means no body and
// NO emitted code — this is a type signature, not a fold (folds live in the
// Python probe). Its only job is to make the compiler check what may be passed:
// the verdict parameter is a GovernanceEvent, so a non-ADJUDICATE event is
// rejected at the call site (see §8).
export declare function applyVerdict(
  current: Standing,
  verdict: GovernanceEvent,
): Standing;

// Static assertions. These resolve purely at the type level and check the
// relationships among this module's declared variants.
type Assert<T extends true> = T;
type Equals<A, B> =
  (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2)
    ? true
    : false;

// (i) the local verdict alias equals AdjudicateEvent:
type _VerdictIsExactlyAdjudicate = Assert<Equals<GovernanceEvent, AdjudicateEvent>>;

// (ii) no non-verdict event qualifies as a GovernanceEvent (KEY/ATTEST/
//      AUTHORIZE/CHALLENGE are all excluded from the verdict slot):
type _NonVerdictsAreNotGovernance = Assert<
  Exclude<Event, AdjudicateEvent> extends GovernanceEvent ? false : true
>;

// ---------------------------------------------------------------------------
// 8. Governance-slot examples (commented out on purpose)
// ---------------------------------------------------------------------------
// As written (commented) the file compiles. Uncommenting the two invalid calls
// produces type errors because the parameter uses this module's ADJUDICATE shape.
//
// (a) This CHALLENGE value does not satisfy the declared parameter:
//
// applyVerdict("in_good_standing", dispute);
//   ❌ Argument of type 'ChallengeEvent' is not assignable to parameter of type
//      'AdjudicateEvent'. Types of property 'type' are incompatible.
//
// (b) This ATTEST value also does not satisfy the declared parameter:
//
// applyVerdict("in_good_standing", offer);
//   ❌ Argument of type 'AttestEvent' is not assignable to 'AdjudicateEvent'.
//
// (c) This ADJUDICATE value satisfies the declared verdict parameter:
//
// const next: Standing = applyVerdict("in_good_standing", ruling); // ✅ ADJUDICATE
//
// The configured slot rejects the demonstrated non-verdict
// shapes. It does not implement or enforce a runtime governance fold.

// ---------------------------------------------------------------------------
// 9. Revocation/delegation add no type — field discipline (findings A, G)
// ---------------------------------------------------------------------------
// These authored fixtures do not use separate REVOKE, KEY_REVOKE, DELEGATE, or
// CAPABILITY members. Withdrawal is the `nullifies` field on an ordinary event
// (event-registry §4.6); a key revocation is a KEY event with predicate
// `id.key_revoke` carrying `nullifies`; a delegation/mandate is an AUTHORIZE with
// a wider `scope` (§4 `mandate`); and whether a current reader continues to honor
// a completed act after revocation is a fold POLICY, not a type (finding G /
// ../authority-revocation-demo).
// In this module those example strings are non-members of CanonicalType, so
// extracting them yields the empty type `never`.
// (Reuses the §7 `Assert` / `Equals` helpers.)

type _RevokeIsNotAType = Assert<Equals<Extract<CanonicalType, "REVOKE">, never>>;
type _KeyRevokeIsNotAType = Assert<Equals<Extract<CanonicalType, "KEY_REVOKE">, never>>;
type _DelegateIsNotAType = Assert<Equals<Extract<CanonicalType, "DELEGATE">, never>>;
type _CapabilityIsNotAType = Assert<Equals<Extract<CanonicalType, "CAPABILITY">, never>>;

// Collective check for the same fixture-local non-members.
type ForbiddenType = "REVOKE" | "KEY_REVOKE" | "DELEGATE" | "CAPABILITY";
type _NoForbiddenTypeInCanon = Assert<Equals<Extract<CanonicalType, ForbiddenType>, never>>;

// A commented invalid example (parallel to §6/§8). As shipped it is commented,
// so the file builds; uncommenting it produces a local type error.
//
// const revokeType: CanonicalType = "REVOKE";
//   ❌ Type '"REVOKE"' is not assignable to type 'CanonicalType'.
//
// The corresponding fixture representation uses a KEY event
// whose predicate is `id.key_revoke` and whose `nullifies` names the register it
// withdraws:
//
// const keyRevoke: KeyEvent = {
//   type: "KEY",
//   id: "ev:r1",
//   signer: "k:merchant",
//   predicate: "id.key_revoke",
//   timestamp: "2026-08-01T00:00:00Z",
//   nullifies: ["ev:0001"], // the register from §4 — withdrawn going forward
//   signature: "stub:r1",
// };
//
// In this fixture, the corresponding examples use predicate, field, and policy
// values while the local type union retains five members.
