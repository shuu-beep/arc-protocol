#!/usr/bin/env python3
"""ARC probe: the refusal-recording fold.

    Adoption does not fold. Refusals can.

The adoption frontier itself does not fold. ARC cannot prove why a party
will honor, join, or adopt the protocol; that incentive is off-ledger
(threat-model.md §18.1). This probe does not try. It demonstrates the
*other* half of that boundary: a refusal *record* is structured evidence
of what an actor said, and structured evidence folds.

A refusal record carries four fields (adoption-and-defection.md §6):

    actor      developer | company | merchant | user | community
    exit       WAIT | DEFECT | FORK | REJECT
    reason     the participant's own words
    mechanism  which §4 candidate they say would have changed the decision,
               or "none"

From a set of such records the fold computes a *falsification surface*:

  WHAT THIS FOLD COMPUTES
    - counts by actor, by exit, by named mechanism
    - per candidate, two qualities of evidence kept apart: NAMED (the refuser
      themselves pointed at it) and CELL-COINCIDENT (a `mechanism = none`
      refusal in an (actor, exit) cell the candidate claims — contradiction
      pressure, but the fold does not read the reason)
    - where a WAIT depends on another, still-missing side of the network
      (including mutual WAIT deadlock)
    - which exits no candidate mechanism even claims to address

  WHAT THIS FOLD CANNOT COMPUTE
    - whether a stated reason is true
    - whether the actor would actually change behavior later
    - whether adoption will or will not happen
    - whether a mechanism is valid in general (only: contradicted in *this*
      synthetic set, in the cells it claims)
    - whether a refusal was strategic, lazy, hostile, or honest
    - whether a CELL-COINCIDENT refuser ever weighed that candidate at all —
      reading the reason to decide would be the inference §6 forbids

A candidate mechanism is never VALIDATED here. The strongest a refusal can
say for a mechanism is "named as the gap" — and that party still declined,
so the lead is unproven. The fold can only contradict or weaken, never confirm.

Red-team note: the fold is only as precise as §4's claims, which are stated
by (actor, exit), not by reason. So a `mechanism = none` refusal contradicts
every candidate that claims its cell, even one its reason has nothing to do
with. That coarseness is reported honestly (NAMED vs CELL-COINCIDENT, "reason
unread") rather than hidden — and it is not fixable by making the fold read
reasons, because that is the forbidden inference. See README "Red-team notes".

The fixtures in `fixtures.json` are SYNTHETIC and illustrative. This is not
an adoption simulator and predicts nothing. Stdlib only; no network.
"""

import json
import sys
from collections import Counter
from pathlib import Path

ALL_ACTORS = ["developer", "company", "merchant", "user", "community"]
ALL_EXITS = ["WAIT", "DEFECT", "FORK", "REJECT"]

# The §4 candidate coordination mechanisms, each with the (actor, exit) cells
# it CLAIMS to address. `actors = None` means "any actor". These claims are
# transcribed from adoption-and-defection.md §4 — they are exactly what the
# refusals get to weaken or falsify.
CANDIDATES = {
    "4.1": {
        "name": "lower integration cost",
        "actors": None,
        "exits": {"WAIT", "REJECT"},
    },
    "4.2": {
        "name": "approval and audit overlay",
        "actors": {"user", "company"},
        "exits": {"REJECT"},
    },
    "4.3": {
        "name": "reputation portability",
        "actors": {"merchant"},
        "exits": {"REJECT", "DEFECT"},
    },
    "4.4": {
        "name": "replaceable / forkable discovery",
        "actors": None,
        "exits": {"FORK", "REJECT"},
    },
    "4.5": {
        "name": "governance transparency",
        "actors": {"community", "user"},
        "exits": {"DEFECT", "REJECT"},
    },
    "4.6": {
        "name": "open spec as latent counter-pressure",
        "actors": None,
        "exits": {"FORK"},
    },
}


def load_refusals(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["refusals"]


def claims_cell(cand, actor, exit_):
    """Does this candidate claim to address the (actor, exit) cell?"""
    if exit_ not in cand["exits"]:
        return False
    return cand["actors"] is None or actor in cand["actors"]


def claimed_cells(cand):
    actors = ALL_ACTORS if cand["actors"] is None else sorted(cand["actors"])
    return {(a, e) for a in actors for e in cand["exits"]}


# --------------------------------------------------------------------------
# Folds
# --------------------------------------------------------------------------

def summarize(refusals, field):
    return Counter(r[field] for r in refusals)


def candidate_verdicts(refusals):
    """Fold refusals into a per-candidate evidence picture.

    Two qualities of evidence, deliberately kept apart:

    - named           : the refuser themselves named this candidate as the
                        gap. Reason-relevant, because they chose it — but a
                        lead only, since they still declined.
    - cell_coincident : a `mechanism = none` refusal lands in an (actor, exit)
                        cell this candidate claims. It contradicts the
                        candidate's *claim* to address that cell, but the fold
                        does not read the reason and cannot say the refuser
                        ever weighed THIS candidate.

    The split matters: §4 specifies each candidate by (actor, exit), so the
    fold can only test at that grain. Matching by the refusal's reason would
    be the inference §6 forbids. Cell-coincident evidence is therefore
    contradiction *pressure*, never "the refuser rejected this mechanism".
    """
    out = {}
    for cid, cand in CANDIDATES.items():
        named = [r for r in refusals if r["mechanism"] == cid]
        cell_coincident = [
            r for r in refusals
            if r["mechanism"] == "none" and claims_cell(cand, r["actor"], r["exit"])
        ]

        if named and cell_coincident:
            verdict = "MIXED"
        elif named:
            verdict = "NAMED-RELEVANT (still declined)"
        elif cell_coincident:
            verdict = "CELL-CONTRADICTED (reason unread)"
        else:
            verdict = "UNTESTED"

        out[cid] = {
            "verdict": verdict,
            "named": named,
            "cell_coincident": cell_coincident,
        }
    return out


def wait_dependencies(refusals):
    """WAIT records and what each waits on; detect mutual-WAIT deadlock."""
    waits = [r for r in refusals if r["exit"] == "WAIT"]
    waits_on_actor = {}  # actor -> set of actor types it waits on
    for r in waits:
        target = r.get("waits_on_actor")
        if target:
            waits_on_actor.setdefault(r["actor"], set()).add(target)

    deadlocks = set()
    for a, targets in waits_on_actor.items():
        for b in targets:
            if b in waits_on_actor and a in waits_on_actor[b]:
                deadlocks.add(frozenset({a, b}))
    return waits, deadlocks


def unaddressed_cells(refusals):
    """Refusal cells that NO candidate mechanism even claims to address."""
    covered = set()
    for cand in CANDIDATES.values():
        covered |= claimed_cells(cand)
    out = []
    for r in refusals:
        if (r["actor"], r["exit"]) not in covered:
            out.append(r)
    return out


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def hr(title):
    return f"\n{title}\n" + "-" * len(title)


def main():
    here = Path(__file__).resolve().parent
    refusals = load_refusals(here / "fixtures.json")

    print("ARC — Refusal-Recording Fold  (synthetic data)")
    print("=" * 48)
    print("Adoption does not fold. Refusals can.\n")
    print(f"Loaded {len(refusals)} synthetic refusal records.")

    print(hr("[1] By actor"))
    for actor, n in summarize(refusals, "actor").most_common():
        print(f"  {actor:<10} {n}")

    print(hr("[2] By exit"))
    for exit_, n in summarize(refusals, "exit").most_common():
        print(f"  {exit_:<8} {n}")

    print(hr("[3] By mechanism named as decisive"))
    mech = summarize(refusals, "mechanism")
    for m in ["none"] + [c for c in CANDIDATES if mech.get(c)]:
        if mech.get(m):
            label = "no mechanism would have moved them" if m == "none" \
                else CANDIDATES[m]["name"]
            print(f"  {m:<5} {mech[m]}   ({label})")

    print(hr("[4] Candidate-mechanism evidence surface"))
    print("  No candidate is ever validated. Two evidence qualities, kept apart:")
    print("  NAMED (the refuser pointed at it) vs CELL-COINCIDENT (a 'none'")
    print("  refusal in a cell it claims — contradiction pressure, reason unread).")
    verdicts = candidate_verdicts(refusals)
    for cid, cand in CANDIDATES.items():
        v = verdicts[cid]
        actors = "any actor" if cand["actors"] is None else "/".join(sorted(cand["actors"]))
        print(f"\n  {cid} {cand['name']}  ->  {v['verdict']}")
        print(f"      claims: {actors} × {{{', '.join(sorted(cand['exits']))}}}")
        if v["named"]:
            ids = ", ".join(f"{r['id']}({r['actor']} {r['exit']})" for r in v["named"])
            print(f"      named as the gap (n={len(v['named'])}, still declined): {ids}")
        if v["cell_coincident"]:
            ids = ", ".join(f"{r['id']}({r['actor']} {r['exit']})" for r in v["cell_coincident"])
            print(f"      cell-coincident (n={len(v['cell_coincident'])}, reason unread): {ids}")

    print(hr("[5] WAIT dependency map"))
    waits, deadlocks = wait_dependencies(refusals)
    for r in waits:
        target = r.get("waits_on_actor") or "the network at large"
        mark = ""
        if r.get("waits_on_actor"):
            for d in deadlocks:
                if r["actor"] in d and r["waits_on_actor"] in d:
                    mark = "   <-- mutual"
        print(f"  {r['actor']:<10} waits on  {target}{mark}")
    if deadlocks:
        for d in deadlocks:
            print(f"  => mutual-WAIT deadlock: {{{', '.join(sorted(d))}}} "
                  f"(each rational to wait; neither moves first)")
    else:
        print("  (no mutual-WAIT deadlock in this set)")

    print(hr("[6] Exits no candidate mechanism even claims to address"))
    gaps = unaddressed_cells(refusals)
    if gaps:
        for r in gaps:
            print(f"  {r['actor']} / {r['exit']} : {r['id']}  \"{r['reason'][:60]}...\"")
        print("  (these refusals fall in cells the §4 set is silent on)")
    else:
        print("  (every refusal cell is claimed by some candidate)")

    print(hr("[7] What this fold cannot compute (standing residue)"))
    for line in [
        "whether any stated reason is true (a reason is testimony, not fact)",
        "whether a NAMED-RELEVANT party would actually adopt if the mechanism existed",
        "whether adoption will or will not happen",
        "whether a mechanism is valid in general (only: contradicted in this set)",
        "whether a refusal was strategic, lazy, hostile, or honest",
        "whether a CELL-COINCIDENT refuser ever weighed that candidate (the fold "
        "does not read reasons; matching by reason would be forbidden inference)",
    ]:
        print(f"  - {line}")
    print("\n  The fold seals what was said, never that it is so: the same wall")
    print("  as view/interpretation fidelity (a signature certifies the record,")
    print("  not its referent). A recorded \"no\" weakens a candidate; it does")
    print("  not explain the refuser, and adoption stays off-ledger.")


if __name__ == "__main__":
    sys.exit(main())
