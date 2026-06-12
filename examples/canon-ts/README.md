# ARC canon — TypeScript hardening probe

A tiny, dependency-free probe that turns ARC invariants into rules the
TypeScript compiler — not a convention — enforces. Two files, six locks.

[`canon.ts`](./canon.ts) locks three **canon** invariants:

1. **Closedness** — the five-event canon is a **closed discriminated union**, so
   nothing can quietly add a sixth event type.
2. **Governance is ADJUDICATE-only** — a probe finding (finding E): commons
   standing moves only by an `ADJUDICATE`, so a `CHALLENGE` or `ATTEST` cannot
   occupy a verdict slot.
3. **Revocation/delegation add no type** — findings A and G: withdrawal, key
   revocation, delegation, and capability are expressed through the `nullifies`
   *field*, a *predicate*, and the reader's *fold policy* — never a new
   canonical type. The forbidden pseudo-types (`REVOKE`, `KEY_REVOKE`,
   `DELEGATE`, `CAPABILITY`) are proven non-members of `CanonicalType`.

[`custody.ts`](./custody.ts) locks three **custody** invariants — the decisions
in [`docs/key-custody.md`](../../docs/key-custody.md) after their adversarial
probe on real Ed25519 keys
([`compromise_fixture.py`](../reference-client/compromise_fixture.py)):

4. **A hot key cannot mint authority beyond its ancestor's scope** — the only
   two paths to a mandate are a ceremonial root (a branded type no hot key can
   fabricate) or an attenuating redelegation (the child scope must narrow the
   parent's; widening fails to compile).
5. **A revoked key cannot produce honored post-revoke acts** — key liveness is
   a phantom type; post-revoke bytes are still *constructible* (theft is not a
   type error — the log can hold a forgery) but cannot occupy the honored slot.
6. **Surgical invalidation requires adjudication** — the only per-act void slot
   takes an `ADJUDICATE`; a key revocation or mandate withdrawal cannot unhonor
   a single act. "Revocation is not surgical" becomes a compile-time refusal.

## What this is (and is not)

- **Not a runtime implementation.** Nothing here signs, folds, stores, or runs.
  There is no I/O. Both files are checked, never executed.
- **A type-level hardening probe.** The single test is `tsc --noEmit`: the files
  must compile as written, and must **fail to compile** the moment any locked
  invariant is violated.

It is the companion to the Python probe in [`../canon-fold-demo`](../canon-fold-demo/),
and the two test different things:

| Probe | Question | Mechanism |
| --- | --- | --- |
| `canon-fold-demo` (Python) | **Semantic sufficiency** — can five event types *express* identity, reputation, governance, disputes, approval, commerce, and delegation? | folds a signed event log into projections across ten scenarios |
| `canon-ts` (TypeScript) | **Compiler-enforced invariants** — can the canon's rules (closedness; governance is ADJUDICATE-only) be made into things a build *refuses to violate*? | a closed discriminated union + an exhaustive `never` switch, plus a typed verdict slot only an `ADJUDICATE` satisfies |

The Python demo shows the canon is *enough*. This probe shows the canon can be
made *closed* — that "no sixth event type" graduates from a philosophical claim
into a rule the type-checker enforces on every build.

## How closedness is enforced

1. **A closed union of literals.** `CanonicalType = "KEY" | "ATTEST" | "AUTHORIZE"
   | "CHALLENGE" | "ADJUDICATE"`. The discriminated `Event` union has exactly
   these five members.
2. **Richness extends by predicate, not by type.** `predicate` and `payload` are
   open; a brand-new flow is a new predicate *string* on an existing type. The
   top-level `type` set never grows. `nullifies` is a withdrawal *field*, not a
   revoke type; a mandate/delegation is an `AUTHORIZE` with a wider `scope`.
3. **An exhaustive `never` switch.** `describe()` handles all five cases; in
   `default`, TypeScript has narrowed the value to `never`. Add a sixth type and
   that value is no longer `never`, so `assertNever()` fails to compile — the
   compiler forces the new type to be handled or removed.
4. **A commented-out proof.** `canon.ts` §6 contains a `CAPABILITY` / `DELEGATE`
   sixth-type example. As shipped it is commented, so the file compiles.
   Uncommenting it makes `tsc --noEmit` fail — try it.

## How the governance invariant is enforced

1. **The verdict type is extracted, not promised.** `GovernanceEvent =
   Extract<Event, { type: "ADJUDICATE" }>` resolves to exactly the `ADJUDICATE`
   variant. Static type assertions (`canon.ts` §7) prove it is *exactly*
   `AdjudicateEvent` and that no other canonical event qualifies — if that ever
   drifted, the file would fail to compile.
2. **A typed verdict slot.** `declare function applyVerdict(current, verdict:
   GovernanceEvent)` is a signature with no body and no emitted code (not a fold —
   folds live in the Python probe). Its only role is to make the compiler check
   what may be presented as a verdict.
3. **A commented-out proof.** `canon.ts` §8 tries to move standing with a
   `CHALLENGE` and with an `ATTEST`. As shipped both are commented. Uncommenting
   either makes `tsc --noEmit` fail (`ChallengeEvent` / `AttestEvent` is not
   assignable to `AdjudicateEvent`); only the `ADJUDICATE` line compiles.

## How the field-discipline invariant is enforced

1. **Forbidden pseudo-types are proven non-members.** `canon.ts` §9 asserts that
   `Extract<CanonicalType, "REVOKE" | "KEY_REVOKE" | "DELEGATE" | "CAPABILITY">`
   resolves to `never` — each tempting "sixth type" is absent from the alphabet.
   Adding any of them to `CanonicalType` makes those assertions fail to compile.
2. **A commented-out proof.** §9 also shows that a key withdrawal needs no new
   type: it is a `KEY` event with predicate `id.key_revoke` carrying `nullifies`.
   The neighboring `const revokeType: CanonicalType = "REVOKE"` line is commented;
   uncommenting it fails (`"REVOKE"` is not assignable to `CanonicalType`).

## How the custody invariants are enforced

1. **The tier line is a brand.** `RootKey` carries a `unique symbol` no other
   code can fabricate, so a `HotKey` cannot occupy a root minting slot
   (`custody.ts` §1–§2). A hot key cannot exist without a mandate — the tier
   line *is* the mandate line ([key-custody.md](../../docs/key-custody.md) §3).
2. **Attenuation is structural subtyping.** `redelegate` requires the child
   scope's `category` to be assignable to the parent's, and a parent whose
   scope has `redelegatable: true`. Widening a category, changing it sideways,
   or re-minting from a surrendered mandate all fail to compile (§3 proofs).
3. **Key liveness is a phantom type.** `revokeKey` is the only
   `"live"` → `"revoked"` transition; `honorAct` takes `SignedAct<"live">`
   only. `signAct` deliberately accepts a revoked key — bytes can always be
   made; the refusal lands at the honored slot (§4–§5).
4. **The scalpel slot takes only a verdict.** `voidAct(act, verdict)` reuses
   `GovernanceEvent` from `canon.ts` §7: a `KeyEvent` revocation or an
   `AUTHORIZE` withdrawal in that slot fails to compile (§6–§7).
5. **An honesty section.** `custody.ts` §8 states what the compiler *cannot*
   hold: ordered axes (it cannot see that 20000 ≤ 50000 — ceiling arithmetic
   stays in the signer's trusted base), custody provenance (an in-scope
   pre-revoke forgery types identically to the honest act — finding I as a
   type-level fact, reproduced on purpose), and detection latency (the phantom
   flips where the revocation lands, not where the theft happens).

## Run it

No install or `package.json` required; `npx` fetches TypeScript on demand:

```sh
npx -p typescript tsc --noEmit -p examples/canon-ts/tsconfig.json
```

Use `npx -p typescript tsc` so npx resolves the official TypeScript compiler
package (a bare `npx tsc` resolves to an unrelated, squatted `tsc` package).

Expected: **no output, exit 0** (the canon compiles). To see the guarantees bite,
uncomment a block in `canon.ts` §6 (closedness — fails on `CanonicalType` or
`never`), §8 (governance — fails because a `CHALLENGE`/`ATTEST` is not an
`AdjudicateEvent`), or §9 (field discipline — fails because `"REVOKE"` is not a
`CanonicalType`) and run again. The custody locks bite the same way: uncomment
a block in `custody.ts` §3 (attenuation — a widened scope or a hot key in the
root slot), §5 (a post-revoke act in the honored slot), or §7 (a revocation in
the per-act void slot).

## The point

> philosophical closedness → language-level enforcement

The five types held across every scenario the Python probe could throw at them.
This probe takes the next step: it makes those findings something a compiler
defends, so violating them — adding a sixth type, letting a non-verdict move
governance, minting authority beyond an ancestor's scope, honoring a
post-revoke act, or unhonoring a single act without an `ADJUDICATE` — can no
longer happen by accident. It breaks the build. And where the compiler cannot
defend a custody fact (ceiling arithmetic, custody provenance, detection
latency), `custody.ts` §8 says so instead of pretending.
