# ARC canon — TypeScript hardening probe

A tiny, dependency-free probe that encodes the ARC five-event canon as a **closed
TypeScript discriminated union**, so the compiler — not a convention — rejects a
sixth event type.

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
| `canon-ts` (TypeScript) | **Compiler-enforced closedness** — can the five-type set be *closed* so nothing can quietly add a sixth? | a closed discriminated union + an exhaustive `never` switch |

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

## Run it

No install or `package.json` required; `npx` fetches TypeScript on demand:

```sh
npx -p typescript tsc --noEmit -p examples/canon-ts/tsconfig.json
```

Use `npx -p typescript tsc` so npx resolves the official TypeScript compiler
package (a bare `npx tsc` resolves to an unrelated, squatted `tsc` package).

Expected: **no output, exit 0** (the canon compiles). To see the guarantee bite,
uncomment either block in `canon.ts` §6 and run again — it should fail with a
type error about `CanonicalType` or `never`.

## The point

> philosophical closedness → language-level enforcement

The five types held across every scenario the Python probe could throw at them.
This probe takes the next step: it makes the closed set something a compiler
defends, so adding a sixth type can no longer happen by accident — it breaks the
build.
