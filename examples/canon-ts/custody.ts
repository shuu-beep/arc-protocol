// ARC custody locks — TypeScript hardening probe, chapter two (type-level only;
// NO runtime).
//
// canon.ts locks three CANON invariants (closedness; governance is
// ADJUDICATE-only; revocation/delegation add no type). This file gives the same
// treatment to three CUSTODY invariants — the decisions in docs/key-custody.md
// (§2, §3, §5) after their adversarial probe on real Ed25519 keys
// (../reference-client/compromise_fixture.py, finding I):
//
//   * LOCK A — a hot key cannot mint authority beyond its ancestor's scope
//     (§2–§3): the only two paths to a mandate are a ceremonial root or an
//     attenuating redelegation; the compiler rejects a widened child scope and
//     a hot key in the root slot;
//   * LOCK B — a revoked key cannot produce honored post-revoke acts (§5):
//     key liveness is a phantom type; bytes signed after the revoke are still
//     CONSTRUCTIBLE (theft is not a type error — the log can hold a forgery)
//     but cannot occupy the honored slot;
//   * LOCK C — surgical invalidation requires adjudication (§5, finding I):
//     the only per-act void slot takes an ADJUDICATE; a key revocation or a
//     mandate withdrawal cannot unhonor a single act, only the wholesale
//     future. "Revocation is not surgical" becomes a compile-time refusal.
//
// As in canon.ts, `npx tsc --noEmit` is the whole test: the file must PASS as
// written and must FAIL the moment any lock is violated. §8 states what the
// compiler CANNOT hold — the honesty section; read it before trusting the rest.
//
// Nothing here executes. Every function is `declare`d: a signature the compiler
// checks but never runs. Folds live in the Python probes.

import type {
  Scope,
  KeyEvent,
  AttestEvent,
  AuthorizeEvent,
  AdjudicateEvent,
  GovernanceEvent,
} from "./canon";

// Same static-proof helpers as canon.ts §7 (redeclared locally; canon.ts keeps
// its own story intact).
type Assert<T extends true> = T;
type Equals<A, B> =
  (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2)
    ? true
    : false;

// ---------------------------------------------------------------------------
// 1. The tier line as types — cold ceremonial root, hot mandate-bounded key
// ---------------------------------------------------------------------------
// key-custody.md §3: a root key signs rarely and consequentially, through a
// human-present ceremony; an agent/device key signs often and boundedly, hot
// exactly as far as its mandate is narrow. Here the tier line is a BRAND: a
// unique symbol no hot key can fabricate, so no hot key fits a root slot.

declare const CEREMONY: unique symbol;

export interface RootKey {
  readonly key: string;
  // Unforgeable outside this module — the type-level form of "cold, ceremonial,
  // never resident where any runtime can reach it".
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

// A mandate carries its scope as a PHANTOM type parameter: the lattice the
// locks operate on is made of literal types ("food", true), so examples below
// use `as const` to keep literals from widening to string/boolean.
export interface Mandate<S extends MandateScope> {
  readonly grant: AuthorizeEvent; // the AUTHORIZE that minted it (consent.mandate)
  readonly scope: S;
}

export type KeyStatus = "live" | "revoked";

// A hot key cannot exist without a mandate — the tier line IS the mandate line.
// Its liveness is the phantom state LOCK B pivots on.
export interface HotKey<St extends KeyStatus = KeyStatus> {
  readonly key: string;
  readonly status: St;
  readonly mandate: Mandate<MandateScope>;
}

// Static proof: the tiers do not intersect — no hot key is a root key.
type _HotKeyIsNotARoot = Assert<Equals<Extract<HotKey, RootKey>, never>>;

// ---------------------------------------------------------------------------
// 2. LOCK A — minting slots: authority only enters downward
// ---------------------------------------------------------------------------
// There are exactly two declared paths to a Mandate, and they are the only
// minting slots in this file:
//   (1) a ceremonial root mints freely — that is what the ceremony is FOR;
//   (2) a holder of a redelegatable mandate mints an ATTENUATION of it: the
//       child's category must be assignable to the ancestor's (narrow or equal,
//       never wider), and a non-redelegatable mandate fails the parent slot.
// Note what (2) does NOT forbid: redelegation itself. A hot key with a
// redelegatable mandate MAY mint — downward. What it cannot do is mint beyond
// its ancestor's scope; the compromise fixture's self-elevation forgery, which
// fell on the tier line at runtime, here has no slot to fall on at all.

export declare function mintFromRoot<S extends MandateScope>(
  root: RootKey,
  scope: S,
): Mandate<S>;

export declare function redelegate<
  P extends MandateScope & { redelegatable: true },
  C extends MandateScope & { category: P["category"] },
>(parent: Mandate<P>, child: C): Mandate<C>;

// Valid examples — the lattice working downward. (`as const` keeps the literals.)
declare const root: RootKey; // declared, never constructed: ceremonies happen off-page
declare const agentKey: HotKey<"live">; // the device key the mandate covers

export const food50k = mintFromRoot(root, {
  category: "food",
  max_total_krw: 50000,
  redelegatable: true,
} as const);

// Attenuation that compiles: same category, lower ceiling, redelegation
// surrendered. (The compiler holds the category and the surrender; the ceiling
// ORDER it cannot see — §8.)
export const courier20k = redelegate(food50k, {
  category: "food",
  max_total_krw: 20000,
  redelegatable: false,
} as const);

// ---------------------------------------------------------------------------
// 3. The LOCK A proof (commented out on purpose)
// ---------------------------------------------------------------------------
// As written (commented) the file compiles. Uncommenting ANY block must make
// `npx tsc --noEmit -p tsconfig.json` fail.
//
// (a) A child cannot change category — sideways is beyond the ancestor:
//
// redelegate(food50k, {
//   category: "electronics", // ❌ '"electronics"' is not assignable to '"food"'
//   max_total_krw: 10000,
//   redelegatable: false,
// } as const);
//
// (b) A child cannot WIDEN the category — covering more than the ancestor is
//     minting authority the ancestor never held:
//
// declare const widened: MandateScope & { category: "food" | "electronics" };
// redelegate(food50k, widened);
//   ❌ '"food" | "electronics"' is not assignable to '"food"'.
//
// (c) A non-redelegatable mandate cannot mint at all — courier20k surrendered
//     redelegation when it was minted:
//
// redelegate(courier20k, {
//   category: "food",
//   max_total_krw: 5000,
//   redelegatable: false,
// } as const);
//   ❌ courier20k's scope has `redelegatable: false`, which fails the parent
//      constraint `{ redelegatable: true }`.
//
// (d) The tier line: a hot key cannot occupy the root slot — there is no
//     ceremony brand to give it:
//
// mintFromRoot(agentKey, {
//   category: "anything",
//   max_total_krw: 1,
//   redelegatable: true,
// } as const);
//   ❌ Argument of type 'HotKey<"live">' is not assignable to parameter of
//      type 'RootKey' — property '[CEREMONY]' is missing.
//
// The lesson: "a hot key cannot mint authority beyond its ancestor's scope"
// stops being a sentence in key-custody.md §3 and becomes the absence of any
// well-typed call that does it.

// ---------------------------------------------------------------------------
// 4. LOCK B — revocation binds the future: no honored post-revoke act
// ---------------------------------------------------------------------------
// key-custody.md §5, first composed mechanism: a KEY revocation read
// time-scoped — what the key signed before the revoke stays readable; nothing
// it signs after is honored. The phantom `KeyStatus` carries that reading:
// `revokeKey` is the only transition, and the honored slot takes "live" only.
//
// Deliberately NOT locked: signing itself. An attacker who copied the secret
// can always make bytes — the compromise fixture's post-revoke forgery EXISTS
// in the log; it is the fold that refuses it. So `signAct` accepts a revoked
// key, and the refusal lands one step later, at `honorAct`.

export interface SignedAct<St extends KeyStatus> {
  readonly event: AttestEvent; // the bytes — constructible regardless of status
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

// The one slot through which an act is honored. "live" only, by type.
export declare function honorAct(act: SignedAct<"live">): HonoredAct;

// The one transition. Its witness is canon vocabulary: a KEY event with
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

// Two acts, in fixture vocabulary. The NAMES below are generator truth — the
// kind of fact the omniscient strip renders and no observer holds. To every
// fold, and to this type system, the two are the same type.
const purchase20000: AttestEvent = {
  type: "ATTEST",
  id: "ev:a1",
  signer: "k:agent_device",
  predicate: "commerce.purchase",
  timestamp: "2026-06-12T15:00:00Z",
  payload: { amount_krw: 20000, context: "market" },
  signature: "stub:a1",
};
const forgery25000: AttestEvent = {
  type: "ATTEST",
  id: "ev:a2",
  signer: "k:agent_device", // the thief signs AS the key — that is the theft
  predicate: "commerce.purchase",
  timestamp: "2026-06-12T15:30:00Z",
  payload: { amount_krw: 25000, context: "market" },
  signature: "stub:a2",
};

// Finding I, reproduced ON PURPOSE: while the key is typed "live", the holder's
// act and the thief's in-scope forgery are the SAME TYPE. Both compile; both
// are honorable. Custody provenance is not a type-level fact, exactly as it is
// not a log-level fact — the compiler shares the fold's blind spot, and this
// file refuses to pretend otherwise (§8).
export const honest = signAct(agentKey, purchase20000);
export const forged = signAct(agentKey, forgery25000);
export const h1 = honorAct(honest);
export const h2 = honorAct(forged); // ✅ deliberately compiles — the blind spot

// The revoke lands. Note the type system models this as a NEW fact (a new
// binding typed "revoked"), not a mutation of the old one — TypeScript has no
// linear types, so `agentKey` above keeps its "live" type. Accidentally apt:
// the stretch where stale bindings still type "live" is detection latency
// wearing a type system's clothes.
export const revoked = revokeKey(agentKey, keyRevoke);

// Bytes still happen after the revoke — this COMPILES, as it must (the log can
// hold the forgery):
export const postRevokeForgery = signAct(revoked, forgery25000);

// Static proofs: the honored slot takes exactly "live"-signed acts, and a
// revoked-signed act never qualifies.
type _HonorSlotTakesLiveOnly = Assert<
  Equals<Parameters<typeof honorAct>[0], SignedAct<"live">>
>;
type _RevokedActsAreNotHonorable = Assert<
  Equals<Extract<SignedAct<"revoked">, Parameters<typeof honorAct>[0]>, never>
>;

// ---------------------------------------------------------------------------
// 5. The LOCK B proof (commented out on purpose)
// ---------------------------------------------------------------------------
// The first line already compiled above (the bytes exist). The refusal is the
// second — uncommenting it must fail the build:
//
// honorAct(postRevokeForgery);
//   ❌ Argument of type 'SignedAct<"revoked">' is not assignable to parameter
//      of type 'SignedAct<"live">'. Types of property 'signedWith' are
//      incompatible — '"revoked"' is not assignable to '"live"'.
//
// The lesson: "nothing it signs after is honored" is no longer a reading we
// promise to apply; the honored slot cannot be handed a post-revoke act. What
// this lock does NOT do — distinguish `forged` from `honest` above — is the
// finding, not a gap (§8).

// ---------------------------------------------------------------------------
// 6. LOCK C — surgical invalidation requires adjudication
// ---------------------------------------------------------------------------
// key-custody.md §5, the probe's sharpening: revocation bounds future
// authority; it does not retroactively distinguish compromise from legitimate
// in-scope use. Voiding a SPECIFIC honored act needs a per-act dispute — a
// CHALLENGE and an honored ADJUDICATE. So the only per-act void slot in this
// file takes a GovernanceEvent (canon.ts §7's verdict type): a key revocation
// (KEY) or a mandate withdrawal (AUTHORIZE) cannot occupy it. Revocation's
// whole reach is the wholesale future via the "revoked" phantom in §4 — there
// is no typed path from a revocation to a single voided act.

export interface VoidedAct {
  readonly was: HonoredAct; // honored until the ruling — adjudication is
  readonly voided_by: GovernanceEvent; // specific-void, not truth-recovery
}

export declare function voidAct(
  act: HonoredAct,
  verdict: GovernanceEvent,
): VoidedAct;

// A mandate withdrawal — recovery's OTHER half (mandates die with the key),
// and still not a per-act void:
const withdrawal: AuthorizeEvent = {
  type: "AUTHORIZE",
  id: "ev:c2",
  signer: "k:root",
  predicate: "consent.withdraw",
  timestamp: "2026-06-12T16:09:00Z",
  nullifies: ["ev:m0"], // the mandate ends with the key (key-custody §5)
  signature: "stub:c2",
};

// The one thing that CAN void a single act — an honored ruling naming it:
const ruling: AdjudicateEvent = {
  type: "ADJUDICATE",
  id: "ev:c3",
  signer: "k:community",
  predicate: "gov.ruling",
  timestamp: "2026-06-13T09:00:00Z",
  refs: ["ev:a2"], // the SPECIFIC act — surgical, per-act, post-hoc
  payload: { ruling: "void", finding: "holder attests the act is not theirs" },
  signature: "stub:c3",
};

export const surgical = voidAct(h2, ruling); // ✅ only this compiles in the slot

// Static proofs: the surgical slot is exactly the verdict type, and neither a
// revocation nor a withdrawal qualifies; a revocation returns a key state,
// never a voided act.
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
// 7. The LOCK C proof (commented out on purpose)
// ---------------------------------------------------------------------------
// (a) A key revocation cannot void a specific act:
//
// voidAct(h1, keyRevoke);
//   ❌ Argument of type 'KeyEvent' is not assignable to parameter of type
//      'AdjudicateEvent'. Types of property 'type' are incompatible.
//
// (b) Neither can a mandate withdrawal:
//
// voidAct(h1, withdrawal);
//   ❌ Argument of type 'AuthorizeEvent' is not assignable to 'AdjudicateEvent'.
//
// The lesson: "revocation is not surgical" was the compromise probe's verdict;
// here it is the compiler's. The two blunt instruments (revoke the key, kill
// the mandate) act only on the future, wholesale; the scalpel slot exists, and
// only an ADJUDICATE fits its shape.

// ---------------------------------------------------------------------------
// 8. What the compiler CANNOT hold — the honesty section
// ---------------------------------------------------------------------------
// Three limits, stated so the locks above are not over-read:
//
//   * ORDERED AXES. Structural subtyping has no "≤": the compiler holds the
//     lattice's SHAPE (category narrows, redelegation surrenders, tiers don't
//     cross) but cannot see that 20000 ≤ 50000, nor compare expiries. Ceiling
//     arithmetic stays where key-custody §2 put it — in the signer's trusted
//     base, with the key, checked at proposal time.
//
//   * CUSTODY PROVENANCE. `honest` and `forged` in §4 type identically, and
//     LOCK B honors both. This is finding I as a type-level fact: signature
//     validity and mandate validity are checkable layers; custody integrity is
//     not — not by the log, not by the fold, and not by this compiler. A type
//     system that claimed to catch the in-scope forgery would be the lie this
//     repo keeps refusing to tell.
//
//   * TIME. The phantom flip from "live" to "revoked" happens where the
//     revocation LANDS, not where the theft happens. Detection latency — the
//     width term of the blast radius — is invisible here, exactly as it is in
//     the log. These locks bound what a key may do across the revocation edge;
//     they do not shorten the window before it.
//
// Within those limits, three sentences from docs/key-custody.md are now build
// failures instead of promises: a hot key minting beyond its ancestor's scope
// has no slot to call; a revoked key's later acts cannot be honored; and
// nothing short of an ADJUDICATE unhonors a single act.
