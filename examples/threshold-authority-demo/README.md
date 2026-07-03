# Threshold / joint-authority probe

A small, deliberately dirty probe that isolates one question `key-custody.md` §8
names but leaves open:

> Can **M-of-N joint authority** (a 2-of-3 board, a co-signed spend, an N-party
> committee) be represented with the existing five types — and if so, *where does
> the quorum rule live?*

Stdlib only, single process, mock signatures, no network, no storage. It reuses
the five canonical event types — `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`,
`ADJUDICATE` — and the `scope` / `refs` / `nullifies` fields, and adds **no sixth
type, no stored authority object, no "multisig" primitive.**

```
python3 probe.py
```

## The scenario

A 2-of-3 treasury board.

1. The **principal** grants an agent a spending mandate that is only honored with
   two-of-three board approval — recorded as `scope` on **one ordinary**
   `AUTHORIZE consent.joint_mandate`:
   `scope = {members:[m1,m2,m3], threshold:2, max_total_krw:30000}`. The member
   list and the threshold are *parameters*, exactly like `max_total_krw` in the
   [authority-revocation probe](../authority-revocation-demo/).
2. The **agent** proposes a candidate spend (`AUTHORIZE consent.execute`,
   referencing the mandate).
3. Board members approve by signing ordinary `ATTEST consent.approve` events that
   reference the candidate.
4. The **principal** later tries to withdraw member-2's approval (`AUTHORIZE
   consent.withdraw` carrying `nullifies` — the existing field). It is recorded
   but **not honored**: a fold honors a `nullifies` only from the target's
   author or its rotation lineage ([event-registry.md](../../docs/event-registry.md)
   §4.6).
5. **Member-2** then withdraws their **own** approval — the §4.6-authorized
   shape — and that one moves the fold.

"Did this candidate reach quorum?" is asked only as a **projection** — a fold that
counts approvals against the recorded threshold. It is never stored.

## What the probe prints

| # | check | result |
|---|-------|--------|
| 1 | **below threshold** — one approval | `authorized=False` (1/2) |
| 2 | **quorum satisfied** — two distinct members | `authorized=True` (2/2) |
| — | **guard:** candidate B over the ceiling at a full **3-of-3** | `authorized=False` (out of scope) |
| 3 | **nullifier authority** — the principal tries to void m2's approval | `authorized=True` (still 2/2 — not honored, §4.6) |
| 4 | **approval withdrawn after quorum** (by m2 itself) — current-log cascade | `authorized=False` (1/2) |
| 5 | **divergent readings** of the same withdrawn-approval log | see below |

The divergence on candidate A, after m2 withdraws its own approval:

| reading | counting | authorized? |
|---------|----------|-------------|
| as-of-act-time | strict (named members) | **True** — quorum stood at reliance |
| current-log, time-scoped | strict | **True** — withdrawal is "going forward" |
| current-log, retroactive cascade | strict | **False** — approval voided, 1/2 |
| current-log, retroactive cascade | **lenient** (any signer) | **True** — a non-member key restores 2/2 |

## What it exposes

- **Can M-of-N be represented in the five types?** Yes — joint set as `scope`,
  approvals as `ATTEST`, revocation as `nullifies`. No sixth type.
- **Where does the quorum *rule* live?** Not in any event. The threshold *number*
  is recorded; "did it reach quorum?" is a **fold**, and the counting rule
  (distinct? members-only? non-members?) is a **fold policy**.
- **Who may withdraw is not policy.** The fold honors a `nullifies` only from
  the target's author or its rotation lineage ([event-registry.md](../../docs/event-registry.md)
  §4.6). The principal's cross-party attempt is recorded evidence, not effect —
  voiding another party's event is `ADJUDICATE` business, never a `nullifies`
  side effect.
- **So joint authority is observer-relative on two axes:**
  - *revocation reading* (the finding-G axis): withdraw an approval after quorum
    and as-of-act-time / time-scoped preserve the act, while a retroactive cascade
    drops it below threshold — the same `nullifies`, two answers;
  - *counting policy* (new): a party holding **one** member key plus a **stray**
    key can manufacture a "valid" quorum against any counterparty whose fold uses
    the lenient rule. The threshold is itself an attack surface — not because a
    type is missing, but because the rule is policy.
- **Quorum does not widen scope.** Candidate B is unauthorized at 3-of-3 because
  it exceeds the mandate ceiling. Scope and quorum are separate gates, both folds.

## Honest limits

This is a **probe, not doctrine.** It does not define a multisig spec, does not
pick the "right" counting or revocation reading, does not solve federation, and
adds no stored authority object. The result is the same shape as findings B/C/D/G:
the hard case stays inside the five types, and what leaks out is a **fold-policy
choice, not a missing primitive** — here, a second observer-relative boundary that
lands on the count itself.
