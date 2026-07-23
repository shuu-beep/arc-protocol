# ARC Canon — local TypeScript type-shape probe

A tiny, dependency-free probe that encodes six fixture-local type-shape checks.
The TypeScript compiler checks this module; it does not enforce ARC at runtime
or across independent implementations.

[`canon.ts`](./canon.ts) exercises three **canon-shaped checks**:

1. **Local union exhaustiveness** — this module uses a five-member discriminated
   union, so adding a member here requires updating its exhaustive handlers.
2. **Local verdict-slot shape** — this module's declared verdict parameter
   accepts its `ADJUDICATE` variant and rejects the demonstrated `CHALLENGE` and
   `ATTEST` values.
3. **Revocation/delegation add no type** — findings A and G: withdrawal, key
   revocation, delegation, and capability are expressed through the `nullifies`
   *field*, a *predicate*, and the reader's *fold policy* — never a new
   canonical type in this module. The example pseudo-types (`REVOKE`,
   `KEY_REVOKE`, `DELEGATE`, `CAPABILITY`) are not members of its union.

[`custody.ts`](./custody.ts) exercises three **custody-shaped checks** related to
[`docs/key-custody.md`](../../docs/key-custody.md) and the separate
[`compromise_fixture.py`](../reference-client/compromise_fixture.py):

4. **The declared API separates root and hot-key paths** — branded types and
   literal categories reject the demonstrated invalid calls in this module;
   assertions or different runtime code can bypass those shapes.
5. **The declared honored slot rejects this module's revoked-key shape** — key
   liveness is a phantom type; the model still permits construction of bytes
   after its revoke marker, while the demonstrated call to the `"live"`-typed
   slot fails this module's type check.
6. **The declared per-act void slot accepts only the verdict shape** — the slot
   takes this module's `ADJUDICATE` variant; the demonstrated key-revocation and
   mandate-withdrawal values do not satisfy that parameter type.

## What this is (and is not)

- **Not a runtime implementation.** The configured command type-checks these
  files without emitting or executing JavaScript. The declared functions have
  no implementations here.
- **A local type-shape probe.** The test is `tsc --noEmit`: the files compile as
  written, and the commented invalid-call examples produce type errors when
  uncommented under this configuration.

It is the companion to the Python probe in [`../canon-fold-demo`](../canon-fold-demo/),
and the two test different things:

| Probe | Question | Mechanism |
| --- | --- | --- |
| `canon-fold-demo` (Python) | **Bounded scenario coverage** — do the eleven current fixtures use the five current event types? | folds a mock-signed Event log into authored projections |
| `canon-ts` (TypeScript) | **Fixture-local type checks** — can selected shapes be rejected within this module? | a local discriminated union + exhaustive `never` switch + typed fixture slots |

The Python demo shows that its current scenarios did not force a sixth type.
This probe shows only that this module's union is locally exhaustive and that its
demonstrated invalid calls fail its configured type check.

## Local union checks

1. **A closed union of literals.** `CanonicalType = "KEY" | "ATTEST" | "AUTHORIZE"
   | "CHALLENGE" | "ADJUDICATE"`. The discriminated `Event` union has exactly
   these five members.
2. **Open predicate and payload fields.** `predicate` and `payload` are open in
   this module; the example adds a predicate *string* on an existing type. The
   top-level `type` set changes only when this source is edited. `nullifies` is a withdrawal *field*, not a
   revoke type; a mandate/delegation is an `AUTHORIZE` with a wider `scope`.
3. **An exhaustive `never` switch.** `describe()` handles all five cases; in
   `default`, TypeScript has narrowed the value to `never`. Add a sixth type and
   that value is no longer `never`, so `assertNever()` fails to compile — the
   module requires the new type to be handled or removed before this check passes.
4. **Commented invalid examples.** `canon.ts` §6 contains a `CAPABILITY` / `DELEGATE`
   sixth-type example. As shipped it is commented, so the file compiles.
   Uncommenting it makes `tsc --noEmit` report a type error.

## Local verdict-slot checks

1. **The verdict type is extracted from this union.** `GovernanceEvent =
   Extract<Event, { type: "ADJUDICATE" }>` resolves to exactly the `ADJUDICATE`
   variant. Static type assertions (`canon.ts` §7) check that it equals
   `AdjudicateEvent` and excludes the other variants in this module.
2. **A typed verdict slot.** `declare function applyVerdict(current, verdict:
   GovernanceEvent)` is a signature with no body and no emitted code (not a fold —
   folds live in the Python probe). Its role is to check the declared parameter.
3. **Commented invalid examples.** `canon.ts` §8 passes a `CHALLENGE` and an
   `ATTEST` to that parameter. As shipped both are commented. Uncommenting
   either makes `tsc --noEmit` fail (`ChallengeEvent` / `AttestEvent` is not
   assignable to `AdjudicateEvent`); only the `ADJUDICATE` line compiles.

## Local field/type examples

1. **Example pseudo-types are checked as non-members.** `canon.ts` §9 asserts that
   `Extract<CanonicalType, "REVOKE" | "KEY_REVOKE" | "DELEGATE" | "CAPABILITY">`
   resolves to `never` — each example string is absent from this union.
   Adding any of them to `CanonicalType` makes those assertions fail to compile.
2. **A commented invalid example.** §9 also represents a key withdrawal without a new
   type: it is a `KEY` event with predicate `id.key_revoke` carrying `nullifies`.
   The neighboring `const revokeType: CanonicalType = "REVOKE"` line is commented;
   uncommenting it fails (`"REVOKE"` is not assignable to `CanonicalType`).

## Local custody-shaped checks

1. **The tier line is represented by a brand.** `RootKey` carries a `unique symbol`,
   so ordinary typed calls in this module do not pass a `HotKey` to a root slot
   (`custody.ts` §1–§2). The `HotKey` shape also contains a mandate field. These
   are compile-time shapes, not evidence of physical key custody.
2. **Attenuation is structural subtyping.** `redelegate` requires the child
   scope's `category` to be assignable to the parent's, and a parent whose
   scope has `redelegatable: true`. Widening a category, changing it sideways,
   or using a parent with `redelegatable: false` produces the displayed type
   errors (§3 examples).
3. **Key liveness is a phantom type.** In this declared API, `revokeKey` returns
   the `"revoked"` shape and `honorAct` takes `SignedAct<"live">`. `signAct`
   deliberately accepts either shape, so this check does not model prevention
   of signing (§4–§5).
4. **The per-act slot takes this module's verdict type.** `voidAct(act, verdict)` reuses
   `GovernanceEvent` from `canon.ts` §7: a `KeyEvent` revocation or an
   `AUTHORIZE` withdrawal in that slot fails to compile (§6–§7).
5. **Explicit limits.** `custody.ts` §8 states what these types do not check:
   numeric ceilings and expiry ordering, custody provenance, runtime signature
   validation, or the delay between compromise and a recorded revocation.

## Run it

No install or `package.json` required; `npx` fetches TypeScript on demand:

```sh
npx -p typescript tsc --noEmit -p examples/canon-ts/tsconfig.json
```

Use `npx -p typescript tsc` so npx resolves the official TypeScript compiler
package (a bare `npx tsc` resolves to an unrelated, squatted `tsc` package).

Expected: **no output, exit 0** (the module passes its configured type check). To
see the demonstrated type errors,
uncomment a block in `canon.ts` §6 (closedness — fails on `CanonicalType` or
`never`), §8 (governance — fails because a `CHALLENGE`/`ATTEST` is not an
`AdjudicateEvent`), or §9 (field discipline — fails because `"REVOKE"` is not a
`CanonicalType`) and run again. The custody examples work the same way: uncomment
a block in `custody.ts` §3 (attenuation — a widened scope or a hot key in the
root slot), §5 (a post-revoke act in the honored slot), or §7 (a revocation in
the per-act void slot).

## Summary

The current five types covered the eleven authored Python scenarios. This probe
checks a narrower set of invalid calls in one TypeScript module. Editing the
union or passing the demonstrated wrong shapes requires corresponding source
changes or breaks this module's type check; it is not runtime or protocol-wide
conformance enforcement. `custody.ts` §8 lists the numeric, custody, and timing
checks that this module does not perform.
