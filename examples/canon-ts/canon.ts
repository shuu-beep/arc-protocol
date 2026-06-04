// ARC canon — TypeScript hardening probe (type-level only; NO runtime).
//
// The Python demo in ../canon-fold-demo tests SEMANTIC sufficiency: across ten
// scenarios, can five event types express identity, reputation, governance,
// disputes, approval, commerce, and delegation? (Answer so far: yes.)
//
// This file tests something narrower and stronger: COMPILER-ENFORCED closedness.
// The five-type canon is written as a closed TypeScript discriminated union, so
// that "no sixth event type" stops being a convention we promise to honor and
// becomes a rule the type-checker enforces. `npx tsc --noEmit` is the whole test:
// it must PASS as written, and must FAIL the moment a sixth type is introduced.
//
// Nothing here executes. There is no signing, no fold, no I/O.

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
