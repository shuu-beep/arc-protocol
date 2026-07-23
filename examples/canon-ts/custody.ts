// ARC custody-shaped checks — local TypeScript probe (type-level only;
// NO runtime).
//
// canon.ts encodes three fixture-local type checks. This file applies the same
// approach to three custody-shaped checks related to docs/key-custody.md
// (§2, §3, §5) and the separate reference-client compromise fixture:
//
//   * CHECK A — the declared API rejects the demonstrated hot-key/root-slot and
//     category-widening calls; numeric attenuation is not checked;
//   * CHECK B — the honored slot rejects this module's revoked-key shape (§5):
//     key liveness is a phantom type; the model still permits construction after
//     its revoke marker, while the demonstrated call to the `"live"`-typed slot
//     fails this module's type check;
//   * CHECK C — the declared per-act void slot takes an ADJUDICATE shape (§5):
//     the demonstrated key-revocation and mandate-withdrawal values do not
//     satisfy that parameter type.
//
// Under `npx tsc --noEmit`, the file passes as written; uncommenting the
// demonstrated invalid calls produces local type errors.
// §8 states what the compiler cannot check.
//
// The configured command emits and executes no JavaScript. Every function is
// `declare`d and has no implementation in this file.

import type {
  Scope,
  KeyEvent,
  AttestEvent,
  AuthorizeEvent,
  AdjudicateEvent,
  GovernanceEvent,
} from "./canon";

// Same static-assertion helpers as canon.ts §7, redeclared locally.
type Assert<T extends true> = T;
type Equals<A, B> =
  (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2)
    ? true
    : false;

// ---------------------------------------------------------------------------
// 1. Local root-key and mandate-bearing key shapes
// ---------------------------------------------------------------------------
// A brand distinguishes the declared RootKey parameter from the HotKey shape in
// ordinary typed calls in this module. Assertions or different runtime code can
// bypass this distinction; it says nothing about physical custody.

declare const CEREMONY: unique symbol;

export interface RootKey {
  readonly key: string;
  // Not ordinarily constructible outside this module without a type assertion;
  // this fixture brand does not establish physical custody.
  readonly [CEREMONY]: "cold ceremonial root";
}

// The type-level mandate scope. It narrows canon's open `Scope` to the axes the
// compiler can actually see (§8 on the axes it cannot): a literal-typed
// category, a numeric ceiling, and whether the holder may mint sub-mandates.
export interface MandateScope extends Scope {
  category: string;
  max_total_krw: number;
  redelegatable: boolean;
}

// A mandate carries its scope as a phantom type parameter. The examples use
// `as const` to keep values such as "food" and `true` from widening.
export interface Mandate<S extends MandateScope> {
  readonly grant: AuthorizeEvent; // associated consent.mandate AUTHORIZE value
  readonly scope: S;
}

export type KeyStatus = "live" | "revoked";

// This module's HotKey shape includes a mandate and a phantom liveness state.
export interface HotKey<St extends KeyStatus = KeyStatus> {
  readonly key: string;
  readonly status: St;
  readonly mandate: Mandate<MandateScope>;
}

// Static assertion: HotKey does not satisfy the RootKey parameter shape.
type _HotKeyDoesNotSatisfyRoot = Assert<Equals<Extract<HotKey, RootKey>, never>>;

// ---------------------------------------------------------------------------
// 2. Check A — declared mandate-construction parameters
// ---------------------------------------------------------------------------
// This file declares two functions returning Mandate values. `redelegate`
// requires the child category to be assignable to the parent's literal category
// and the parent shape to carry `redelegatable: true`. It does not compare
// numeric ceilings or establish runtime authority.

export declare function mintFromRoot<S extends MandateScope>(
  root: RootKey,
  scope: S,
): Mandate<S>;

export declare function redelegate<
  P extends MandateScope & { redelegatable: true },
  C extends MandateScope & { category: P["category"] },
>(parent: Mandate<P>, child: C): Mandate<C>;

// Calls accepted by these declarations. (`as const` keeps the literals.)
declare const root: RootKey; // declared, never constructed in this module
declare const agentKey: HotKey<"live">; // declared fixture value

export const food50k = mintFromRoot(root, {
  category: "food",
  max_total_krw: 50000,
  redelegatable: true,
} as const);

// This call compiles because the category matches and redelegation is false.
// The compiler does not compare the numeric ceilings (§8).
export const courier20k = redelegate(food50k, {
  category: "food",
  max_total_krw: 20000,
  redelegatable: false,
} as const);

// ---------------------------------------------------------------------------
// 3. Check A invalid-call examples (commented out on purpose)
// ---------------------------------------------------------------------------
// As written (commented) the file compiles. Uncommenting a displayed block
// produces a type error under `npx tsc --noEmit -p tsconfig.json`.
//
// (a) The demonstrated different category fails this parameter type:
//
// redelegate(food50k, {
//   category: "electronics", // ❌ '"electronics"' is not assignable to '"food"'
//   max_total_krw: 10000,
//   redelegatable: false,
// } as const);
//
// (b) The demonstrated union category is not assignable to the parent literal:
//
// declare const widened: MandateScope & { category: "food" | "electronics" };
// redelegate(food50k, widened);
//   ❌ '"food" | "electronics"' is not assignable to '"food"'.
//
// (c) This parent value does not satisfy `{ redelegatable: true }`:
//
// redelegate(courier20k, {
//   category: "food",
//   max_total_krw: 5000,
//   redelegatable: false,
// } as const);
//   ❌ courier20k's scope has `redelegatable: false`, which fails the parent
//      constraint `{ redelegatable: true }`.
//
// (d) This HotKey value lacks the RootKey brand required by the parameter:
//
// mintFromRoot(agentKey, {
//   category: "anything",
//   max_total_krw: 1,
//   redelegatable: true,
// } as const);
//   ❌ Argument of type 'HotKey<"live">' is not assignable to parameter of
//      type 'RootKey' — property '[CEREMONY]' is missing.
//
// These examples check only the displayed parameter relationships in this
// module. Type assertions and other APIs can bypass them.

// ---------------------------------------------------------------------------
// 4. Check B — local liveness-shaped parameter
// ---------------------------------------------------------------------------
// The phantom `KeyStatus` distinguishes two declared shapes. `revokeKey` returns
// the `"revoked"` shape, and this module's `honorAct` parameter takes `"live"`.
//
// `signAct` accepts either shape. These declarations neither sign bytes nor
// implement a runtime fold; they only exercise the displayed parameter types.

export interface SignedAct<St extends KeyStatus> {
  readonly event: AttestEvent; // value accepted regardless of phantom status
  readonly signedWith: HotKey<St>;
}

export declare function signAct<St extends KeyStatus>(
  key: HotKey<St>,
  event: AttestEvent,
): SignedAct<St>;

export interface HonoredAct {
  readonly act: SignedAct<"live">;
  readonly basis: string; // vocabulary only — the actual fold lives in Python
}

// A declared slot whose parameter uses the local `"live"` shape.
export declare function honorAct(act: SignedAct<"live">): HonoredAct;

// A declared shape transition. Its second parameter is a KEY event with
// predicate `id.key_revoke` carrying `nullifies` (canon.ts §9) — no new type.
export declare function revokeKey(
  key: HotKey<"live">,
  withdrawal: KeyEvent,
): HotKey<"revoked">;

const keyRevoke: KeyEvent = {
  type: "KEY",
  id: "ev:c1",
  signer: "k:root",
  predicate: "id.key_revoke",
  timestamp: "2026-06-12T16:09:00Z",
  nullifies: ["ev:c0"], // the device key's register — withdrawn going forward
  signature: "stub:c1",
};

// Two authored fixture values. Their names describe the scenario, but both have
// the same AttestEvent type and neither name establishes a world fact.
const purchase20000: AttestEvent = {
  type: "ATTEST",
  id: "ev:a1",
  signer: "k:agent_device",
  predicate: "commerce.purchase",
  timestamp: "2026-06-12T15:00:00Z",
  payload: { amount_krw: 20000, context: "market" },
  signature: "stub:a1",
};
const attackerAuthored25000: AttestEvent = {
  type: "ATTEST",
  id: "ev:a2",
  signer: "k:agent_device", // fixture value attributed to the same key id
  predicate: "commerce.purchase",
  timestamp: "2026-06-12T15:30:00Z",
  payload: { amount_krw: 25000, context: "market" },
  signature: "stub:a2",
};

// Both authored values have the same type and satisfy the same declared
// parameter. The type checker does not establish who controlled a signing key.
export const configuredAct = signAct(agentKey, purchase20000);
export const attackerAuthoredAct = signAct(agentKey, attackerAuthored25000);
export const h1 = honorAct(configuredAct);
export const h2 = honorAct(attackerAuthoredAct); // compiles under these shapes

// The returned value has a new `"revoked"` type. TypeScript has no linear types,
// so the earlier `agentKey` binding retains its `"live"` type.
export const revoked = revokeKey(agentKey, keyRevoke);

// This construction still compiles because `signAct` accepts either status:
export const postRevokeAttackerAuthored = signAct(revoked, attackerAuthored25000);

// Static assertions over this module's declared parameter types.
type _HonorSlotTakesLiveOnly = Assert<
  Equals<Parameters<typeof honorAct>[0], SignedAct<"live">>
>;
type _RevokedActsAreNotHonorable = Assert<
  Equals<Extract<SignedAct<"revoked">, Parameters<typeof honorAct>[0]>, never>
>;

// ---------------------------------------------------------------------------
// 5. Check B invalid-call example (commented out on purpose)
// ---------------------------------------------------------------------------
// The construction above compiles. Uncommenting this call produces a type error:
//
// honorAct(postRevokeAttackerAuthored);
//   ❌ Argument of type 'SignedAct<"revoked">' is not assignable to parameter
//      of type 'SignedAct<"live">'. Types of property 'signedWith' are
//      incompatible — '"revoked"' is not assignable to '"live"'.
//
// This checks one declared parameter shape. It does not apply runtime revocation
// policy or distinguish the two authored values above.

// ---------------------------------------------------------------------------
// 6. Check C — local per-act verdict parameter
// ---------------------------------------------------------------------------
// This file declares `voidAct` with a GovernanceEvent parameter (canon.ts §7's
// local verdict type). The displayed KEY and AUTHORIZE values do not satisfy
// that parameter. This is not a runtime rule for legal or operational effects.

export interface VoidedAct {
  readonly was: HonoredAct; // fixture input value
  readonly voided_by: GovernanceEvent; // associated local verdict value
}

export declare function voidAct(
  act: HonoredAct,
  verdict: GovernanceEvent,
): VoidedAct;

// An authored mandate-withdrawal value used in the invalid-call example:
const withdrawal: AuthorizeEvent = {
  type: "AUTHORIZE",
  id: "ev:c2",
  signer: "k:root",
  predicate: "consent.withdraw",
  timestamp: "2026-06-12T16:09:00Z",
  nullifies: ["ev:m0"],
  signature: "stub:c2",
};

// An ADJUDICATE-shaped value accepted by the declared parameter:
const ruling: AdjudicateEvent = {
  type: "ADJUDICATE",
  id: "ev:c3",
  signer: "k:community",
  predicate: "gov.ruling",
  timestamp: "2026-06-13T09:00:00Z",
  refs: ["ev:a2"], // fixture reference to one act
  payload: { ruling: "void", finding: "holder attests the act is not theirs" },
  signature: "stub:c3",
};

export const surgical = voidAct(h2, ruling); // accepted by this declared slot

// Static assertions over the declared parameter and return shapes.
type _SurgicalSlotIsAdjudicateOnly = Assert<
  Equals<Parameters<typeof voidAct>[1], AdjudicateEvent>
>;
type _RevocationCannotOccupyTheSlot = Assert<
  Equals<Extract<KeyEvent, Parameters<typeof voidAct>[1]>, never>
>;
type _WithdrawalCannotOccupyTheSlot = Assert<
  Equals<Extract<AuthorizeEvent, Parameters<typeof voidAct>[1]>, never>
>;
type _RevocationIsNotSurgical = Assert<
  Equals<Extract<ReturnType<typeof revokeKey>, VoidedAct>, never>
>;

// ---------------------------------------------------------------------------
// 7. Check C invalid-call examples (commented out on purpose)
// ---------------------------------------------------------------------------
// (a) This KeyEvent does not satisfy the GovernanceEvent parameter:
//
// voidAct(h1, keyRevoke);
//   ❌ Argument of type 'KeyEvent' is not assignable to parameter of type
//      'AdjudicateEvent'. Types of property 'type' are incompatible.
//
// (b) This AuthorizeEvent also does not satisfy that parameter:
//
// voidAct(h1, withdrawal);
//   ❌ Argument of type 'AuthorizeEvent' is not assignable to 'AdjudicateEvent'.
//
// These examples establish only which declared values satisfy this module's
// parameter type.

// ---------------------------------------------------------------------------
// 8. What the compiler cannot check
// ---------------------------------------------------------------------------
// Limits on the local checks above:
//
//   * ORDERED AXES. Structural subtyping does not establish that 20000 ≤ 50000
//     or compare expiries. These declarations leave those checks to runtime code.
//
//   * CUSTODY PROVENANCE. `configuredAct` and `attackerAuthoredAct` in §4 type
//     identically. These declarations perform no signature, mandate, or
//     key-custody validation.
//
//   * TIME. The phantom status changes only in the return type of the declared
//     `revokeKey` call. These checks do not model clocks, detection, or chronology.
//
// Within those limits, the demonstrated invalid calls fail this module's type
// check. This is not runtime custody or protocol-conformance enforcement.
