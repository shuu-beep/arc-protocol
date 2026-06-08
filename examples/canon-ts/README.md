# ARC canon — TypeScript hardening probe

A tiny, dependency-free probe that turns ARC canon invariants into rules the
TypeScript compiler — not a convention — enforces. It locks two so far:

1. **Closedness** — the five-event canon is a **closed discriminated union**, so
   nothing can quietly add a sixth event type.
2. **Governance is ADJUDICATE-only** — a probe finding (finding E): commons
   standing moves only by an `ADJUDICATE`, so a `CHALLENGE` or `ATTEST` cannot
   occupy a verdict slot.

## What this is (and is not)

- **Not a runtime implementation.** Nothing here signs, folds, stores, or runs.
  There is no I/O. `canon.ts` is checked, never executed.
- **A type-level hardening probe.** The single test is `tsc --noEmit`: the file
  must compile as written, and must **fail to compile** the moment a sixth type
  is introduced.

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

## Run it

No install or `package.json` required; `npx` fetches TypeScript on demand:

```sh
npx -p typescript tsc --noEmit -p examples/canon-ts/tsconfig.json
```

Use `npx -p typescript tsc` so npx resolves the official TypeScript compiler
package (a bare `npx tsc` resolves to an unrelated, squatted `tsc` package).

Expected: **no output, exit 0** (the canon compiles). To see the guarantees bite,
uncomment a block in `canon.ts` §6 (closedness — fails on `CanonicalType` or
`never`) or §8 (governance — fails because a `CHALLENGE`/`ATTEST` is not an
`AdjudicateEvent`) and run again.

## The point

> philosophical closedness → language-level enforcement

The five types held across every scenario the Python probe could throw at them.
This probe takes the next step: it makes those findings something a compiler
defends, so violating them — adding a sixth type, or letting a non-verdict move
governance — can no longer happen by accident. It breaks the build.
