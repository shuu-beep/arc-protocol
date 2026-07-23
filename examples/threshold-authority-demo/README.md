# Threshold / joint-authority probe

A small illustrative fixture for one question in `key-custody.md` §8:
names but leaves open:

> Can **M-of-N joint authority** (a 2-of-3 board, a co-signed spend, an N-party
> committee) be represented with the existing five types — and if so, *where does
> the quorum rule live?*

Stdlib only, single process, mock signatures, no network, no storage. It encodes
one 2-of-3 evidence-counting policy using the current Event types and fields.

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
3. Board members approve by signing ordinary `ATTEST quorum.approve` events that
   reference the candidate.
4. The **principal** later tries to withdraw member-2's approval (`AUTHORIZE
   consent.withdraw` carrying `nullifies` — the existing field). It is recorded
   but **not honored**. This fixture accepts a withdrawal only when its signer
   label exactly matches the target's signer label. It does not model or validate
   rotation lineage; the broader author/lineage rule is described in
   [event-registry.md](../../docs/event-registry.md) §4.6.
5. **Member-2** then withdraws their **own** approval — the §4.6 self-withdrawal
   shape — and that one moves the fold.

"Did this candidate reach quorum?" is asked only as a **projection** — a fold that
counts approvals against the recorded threshold. It is never stored.

## What the probe prints

| # | check | result |
|---|-------|--------|
| 1 | **below threshold** — one approval | `authorized=False` (1/2) |
| 2 | **quorum satisfied** — two distinct members | `authorized=True` (2/2) |
| — | **guard:** candidate B over the ceiling at a full **3-of-3** | `authorized=False` (out of scope) |
| 3 | **nullifier authority** — the principal tries to withdraw m2's approval after reliance | `candidate_honored_now=True` (still 2/2 — withdrawal not honored, §4.6) |
| 4 | **approval withdrawn after quorum** (by m2 itself) — full-current-log cascade | `candidate_honored_now=False` (1/2) |
| 5 | **divergent readings** of the same withdrawn-approval log | see below |

The historical baseline is an **earlier event subset** ending at reliance; it
prints `authorized_at_reliance=True`. It excludes the later withdrawal and is not
the same-events policy comparison.

Against the **same full current log**, current honoring diverges:

| policy | counting | candidate_honored_now |
|--------|----------|-----------------------|
| preserve | strict (named members) | **True** — later withdrawal does not reopen the relied-on candidate |
| cascade | strict | **False** — the withdrawn approval no longer counts in this projection, 1/2 |
| cascade | **lenient** (any signer) | **True** — a non-member key restores the current count to 2/2 |

## What it exposes

- **Can this fixture encode one M-of-N evidence policy with the five types?** Yes —
  joint set as `scope`, approvals as `ATTEST`, revocation as `nullifies`. This
  does not settle canonical joint-authority semantics or all threshold schemes.
- **Where does the quorum *rule* live?** Not in any event. The threshold *number*
  is recorded; "did it reach quorum?" is a **fold**, and the counting rule
  (distinct? members-only? non-members?) is a **fold policy**.
- **This fixture checks exact signer-label equality for withdrawal.** The
  principal's cross-party attempt is recorded evidence, not effect. The registry
  describes author or documented rotation lineage
  ([event-registry.md](../../docs/event-registry.md) §4.6), but this fixture has no
  rotation records or lineage traversal. Only an honored `ADJUDICATE` can
  explicitly void another party's event.
- **The fixture outputs depend on two configured policy axes:**
  - *revocation reading* (the finding-G axis): the earlier subset establishes
    `authorized_at_reliance=True`; against the same full current log, preserve
    yields `candidate_honored_now=True` while cascade yields `False`;
  - *counting policy* (new): a party holding **one** member key plus a **stray**
    key can satisfy the candidate gate under the lenient rule. This demonstrates
    that the counting rule is a named application-policy input.
- **Quorum does not widen scope.** Candidate B is unauthorized at 3-of-3 because
  it exceeds the mandate ceiling. Scope and quorum are separate gates, both folds.

## Limits

This is a **probe, not doctrine.** It does not define a multisig spec, does not
pick the "right" counting or revocation reading, does not solve federation, and
adds no stored authority object. It does not model or validate key-rotation
lineage. It also does not decide whether a quorum
approval is *evidence* or *consent*: approvals are modeled as `ATTEST
quorum.approve` — deliberately not `consent.*`, which the corpus reserves for
`AUTHORIZE` ([event-registry.md](../../docs/event-registry.md) §6) — and whether
a member's approval should ultimately be an authority-bearing `AUTHORIZE` is
the probe's declared open question, recorded in
[event-registry.md](../../docs/event-registry.md) §10. The fixture demonstrates
one encoding and does not settle joint-authority semantics.
