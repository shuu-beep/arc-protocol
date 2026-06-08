// ARC canon — TypeScript hardening probe (type-level only; NO runtime).
//
// The Python demo in ../canon-fold-demo tests SEMANTIC sufficiency: across ten
// scenarios, can five event types express identity, reputation, governance,
// disputes, approval, commerce, and delegation? (Answer so far: yes.)
//
// This file tests something narrower and stronger: COMPILER-ENFORCED invariants.
// It locks three of them as type-checker rules rather than conventions we promise
// to honor:
//   * closedness (§5–§6) — the five-type canon is a closed discriminated union,
//     so "no sixth event type" breaks the build the moment a sixth is added;
//   * governance is ADJUDICATE-only (§7–§8) — a probe finding (finding E, shown
//     at runtime in ../end-to-end-demo): commons standing moves only by an
//     ADJUDICATE, so the compiler refuses to let a CHALLENGE or ATTEST occupy a
//     verdict slot;
//   * revocation/delegation add no type (§9) — findings A and G: withdrawal,
//     key revocation, delegation, and capability are expressed through the
//     `nullifies` FIELD, a predicate, and the reader's fold policy — never a new
//     canonical type. The forbidden "sixth types" are proven non-members.
// `npx tsc --noEmit` is the whole test: it must PASS as written, and must FAIL
// the moment any invariant is violated.
//
// Nothing here executes. There is no signing, no fold, no I/O — only type-level
// constructs and `declare`d signatures the compiler checks but never runs.

// ---------------------------------------------------------------------------
// 1. The closed canonical type set
// ---------------------------------------------------------------------------
// This union IS the canon's entire top-level vocabulary. It is closed: the
// compiler knows these five and only these five. Application richness lives in
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
  id: string; // content hash
  signer: string; // key id, resolvable via a prior KEY event (except a KEY root)
  predicate: string; // namespaced semantic tag — richness grows HERE, not in `type`
  timestamp: string; // ISO 8601
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
// Each variant fixes one `type` literal. A variant may add its own fields
// (AUTHORIZE adds `scope` / `contrary_to`); none may add a new `type`.

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

// The closed set. Adding a member here is the ONLY way to add a type — and the
// exhaustive switch in §5 makes that addition fail to compile until handled.
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

// Richness extends by PREDICATE, not by TYPE: an entirely new flow is just a
// new predicate string on an existing type — `CanonicalType` does not change.
const novelFlow: AttestEvent = {
  type: "ATTEST",
  id: "ev:0007",
  signer: "k:merchant",
  predicate: "commerce.warranty_claim", // never seen before; compiles freely
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
// 5. Exhaustive switch — the closed-set guarantee, enforced by `never`
// ---------------------------------------------------------------------------
// Every canonical type is handled. In `default`, TypeScript has narrowed `e` to
// `never` precisely because the five cases above are exhaustive. If a sixth type
// is ever added to `Event`, `e` is no longer `never` here and `assertNever(e)`
// FAILS to compile — the compiler forces the new type to be handled (or removed).

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
      return assertNever(e); // ← closed-set tripwire
  }
}

// ---------------------------------------------------------------------------
// 6. The closed-set PROOF (commented out on purpose)
// ---------------------------------------------------------------------------
// Each block below is the kind of "sixth type" the canon forbids. As written
// (commented) the file compiles. Uncommenting ANY block must make
// `npx tsc --noEmit -p tsconfig.json` fail — the compiler, not a convention,
// is what rejects it.
//
// (a) A sixth type cannot be constructed as an `Event`:
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
// (b) Even if someone DECLARES a new variant and widens the union, the
//     exhaustive switch refuses to compile until the new case is handled:
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
// The lesson: closedness is no longer a promise in prose. Widening the canon
// breaks the build in at least two places. That is the graduation from
// philosophical closedness to language-level enforcement.

// ---------------------------------------------------------------------------
// 7. Governance is ADJUDICATE-only — enforced by the type system (finding E)
// ---------------------------------------------------------------------------
// ARC's authority invariant: commons governance standing moves ONLY when an
// ADJUDICATE is added. A CHALLENGE opens a dispute and an ATTEST records an
// outcome — neither is a verdict, and neither may change standing. The
// end-to-end probe (../end-to-end-demo) shows this holding at runtime, where the
// SAME standing projection is unmoved by a dispute and moves only on a ruling.
// Here the compiler refuses to let anything but an ADJUDICATE be a verdict.

// The governance-moving event type, extracted from the closed union. It is
// exactly AdjudicateEvent — by construction, not by promise. Narrow the union
// to "ADJUDICATE" and nothing else can stand in for a verdict.
export type GovernanceEvent = Extract<Event, { type: "ADJUDICATE" }>;

// The standings governance can hold. Vocabulary only: this names the possible
// RESULTS of a projection; ARC stores no standing field (object-model §4).
export type Standing =
  | "in_good_standing"
  | "warned"
  | "suspended"
  | "expelled";

// The one slot through which standing may change. `declare` means NO body and
// NO emitted code — this is a type signature, not a fold (folds live in the
// Python probe). Its only job is to make the compiler check what may be passed:
// the verdict parameter is a GovernanceEvent, so a non-ADJUDICATE event is
// rejected at the call site (see §8).
export declare function applyVerdict(
  current: Standing,
  verdict: GovernanceEvent,
): Standing;

// Static proofs (must compile). These resolve purely at the type level; if the
// governance-moving type ever drifted from "ADJUDICATE and only ADJUDICATE",
// the file would fail to compile.
type Assert<T extends true> = T;
type Equals<A, B> =
  (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2)
    ? true
    : false;

// (i) the verdict type is EXACTLY AdjudicateEvent — no wider, no narrower:
type _VerdictIsExactlyAdjudicate = Assert<Equals<GovernanceEvent, AdjudicateEvent>>;

// (ii) no non-verdict event qualifies as a GovernanceEvent (KEY/ATTEST/
//      AUTHORIZE/CHALLENGE are all excluded from the verdict slot):
type _NonVerdictsAreNotGovernance = Assert<
  Exclude<Event, AdjudicateEvent> extends GovernanceEvent ? false : true
>;

// ---------------------------------------------------------------------------
// 8. The governance PROOF (commented out on purpose)
// ---------------------------------------------------------------------------
// As written (commented) the file compiles. Uncommenting ANY block must make
// `npx tsc --noEmit -p tsconfig.json` fail — the compiler, not a convention, is
// what enforces that only an ADJUDICATE moves governance.
//
// (a) A CHALLENGE is not a verdict — it cannot move standing:
//
// applyVerdict("in_good_standing", dispute);
//   ❌ Argument of type 'ChallengeEvent' is not assignable to parameter of type
//      'AdjudicateEvent'. Types of property 'type' are incompatible.
//
// (b) Neither can an ATTEST outcome:
//
// applyVerdict("in_good_standing", offer);
//   ❌ Argument of type 'AttestEvent' is not assignable to 'AdjudicateEvent'.
//
// (c) Only an ADJUDICATE compiles in the verdict slot:
//
// const next: Standing = applyVerdict("in_good_standing", ruling); // ✅ ADJUDICATE
//
// The lesson, as in §6: the invariant stops being prose. "Governance moves only
// by ADJUDICATE" becomes something the build refuses to let you violate.

// ---------------------------------------------------------------------------
// 9. Revocation/delegation add no type — field discipline (findings A, G)
// ---------------------------------------------------------------------------
// The recurring temptation, every time the canon meets a hard case, is to add a
// "sixth type" — REVOKE, KEY_REVOKE, DELEGATE, CAPABILITY. The probes found this
// is never needed: withdrawal is the `nullifies` FIELD on an ordinary event
// (event-registry §4.6); a key revocation is a KEY event with predicate
// `id.key_revoke` carrying `nullifies`; a delegation/mandate is an AUTHORIZE with
// a wider `scope` (§4 `mandate`); and whether a revoke cascades over a completed
// act is a fold POLICY, not a type (finding G / ../authority-revocation-demo).
// So these "types" must NOT exist in the alphabet. Each is proven to be a
// non-member of CanonicalType — extracting it yields the empty type `never`.
// (Reuses the §7 `Assert` / `Equals` helpers.)

type _RevokeIsNotAType = Assert<Equals<Extract<CanonicalType, "REVOKE">, never>>;
type _KeyRevokeIsNotAType = Assert<Equals<Extract<CanonicalType, "KEY_REVOKE">, never>>;
type _DelegateIsNotAType = Assert<Equals<Extract<CanonicalType, "DELEGATE">, never>>;
type _CapabilityIsNotAType = Assert<Equals<Extract<CanonicalType, "CAPABILITY">, never>>;

// And collectively: none of the forbidden alphabet intersects the canon.
type ForbiddenType = "REVOKE" | "KEY_REVOKE" | "DELEGATE" | "CAPABILITY";
type _NoForbiddenTypeInCanon = Assert<Equals<Extract<CanonicalType, ForbiddenType>, never>>;

// A commented-out proof (parallel to §6/§8): treating a forbidden pseudo-type as
// canonical must fail to compile. As shipped it is commented, so the file builds.
//
// const revokeType: CanonicalType = "REVOKE";
//   ❌ Type '"REVOKE"' is not assignable to type 'CanonicalType'.
//
// The withdrawal it gropes for already exists without a new type — a KEY event
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
// The lesson: revocation, delegation, and capability are predicate/field/policy
// concerns. The canonical type alphabet stays exactly five.
