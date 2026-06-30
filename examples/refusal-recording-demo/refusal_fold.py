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
    - whether any §4 lever can break a detected mutual-WAIT from one side —
      i.e. whether a solo (counterparty-independent) lever even reaches it
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
    - whether a solo-value lever, where one reaches a deadlock, is large
      enough to seed adoption (its size is unmeasured; survey §114)

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
#
# `value_locus` records WHERE the mechanism's value accrues, and is also
# transcribed, not invented — each classification quotes the candidate's own
# §4 residue or the coordination-economics survey:
#
#   "network" — value requires a counterparty to also move; cannot make
#               moving-first rational from one side alone.
#   "solo"    — value accrues to a single adopter with zero counterparties
#               (a counterparty-independent / single-sided lever; survey §57).
#   "mixed"   — has a solo thread but its principal value is network.
#
# This matters for the WAIT deadlock: a mutual-WAIT is a standoff over
# *network* value (each waits for the other to move), so only a solo-value
# lever can break it from one side (survey §57, §109). See fold [6].
CANDIDATES = {
    "4.1": {
        "name": "lower integration cost",
        "actors": None,
        "exits": {"WAIT", "REJECT"},
        # §4.1 residue: a low cost "still buys nothing without demand on the
        # other side" — a cost-reducer, not a counterparty-independent value.
        "value_locus": "network",
    },
    "4.2": {
        "name": "approval and audit overlay",
        "actors": {"user", "company"},
        "exits": {"REJECT"},
        # survey §109: an ARC audit log has *some* solo value — a party can
        # record and recompute its own agent's approvals with no one else
        # participating. But transaction/dispute audit (§4.2) is network and
        # "felt mainly after a failure". Solo thread, network principal value.
        "value_locus": "mixed",
    },
    "4.3": {
        "name": "reputation portability",
        "actors": {"merchant"},
        "exits": {"REJECT", "DEFECT"},
        # §4.3: reputation is how counterparties see you; portability needs a
        # network to carry it across, and meaning needs Sybil resistance.
        "value_locus": "network",
    },
    "4.4": {
        "name": "replaceable / forkable discovery",
        "actors": None,
        "exits": {"FORK", "REJECT"},
        # §4.4: discovery ranks others' offers; "replaceability does not
        # create the alternative backend" and an empty network has nothing
        # to discover.
        "value_locus": "network",
    },
    "4.5": {
        "name": "governance transparency",
        "actors": {"community", "user"},
        "exits": {"DEFECT", "REJECT"},
        # §4.5: "exposure only bites if some other community is willing to
        # act on it" — value is contingent on another party.
        "value_locus": "network",
    },
    "4.6": {
        "name": "open spec as latent counter-pressure",
        "actors": None,
        "exits": {"FORK"},
        # §4.6: "the check only bites if a fork is viable, and viability needs
        # the very network effects that are missing."
        "value_locus": "network",
    },
}

# Loci that carry a counterparty-independent thread capable, in principle, of
# breaking a mutual-WAIT from one side.
SOLO_LOCI = {"solo", "mixed"}


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


def solo_value_reach(refusals):
    """Does any §4 lever break a detected mutual-WAIT — from one side?

    A mutual-WAIT is a standoff over *network* value: each party waits for the
    other to move, so the value each wants is exactly the value the other is
    withholding. Lowering cost or sweetening a network benefit does not break
    it, because at zero counterparties the benefit is still zero. Only a
    *solo* lever — value that accrues to a single adopter with no counterparty
    — can make moving-first rational from one side (survey §57).

    This fold tests, per detected deadlock:
      - which candidates even REACH it (claim a WAIT cell of a deadlocked
        actor), and
      - whether any reaching candidate carries a solo-value thread.

    The survey names exactly one thin solo thread in ARC — the audit log's
    self-delegation audit (§4.2 / survey §109). This fold makes that prose
    claim load-bearing by checking whether it reaches the deadlock the
    chicken-and-egg actually turns on. It predicts nothing: even a reaching
    solo lever is a lead, not a path — its size is unmeasured (survey §114).
    """
    _, deadlocks = wait_dependencies(refusals)
    results = []
    for d in deadlocks:
        reaching = [
            cid for cid, cand in CANDIDATES.items()
            if any(claims_cell(cand, a, "WAIT") for a in d)
        ]
        solo = [cid for cid in reaching if CANDIDATES[cid]["value_locus"] in SOLO_LOCI]
        results.append({"deadlock": d, "reaching": reaching, "solo": solo})
    return deadlocks, results


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

    print(hr("[6] Does any §4 lever break a mutual-WAIT?"))
    print("  A mutual-WAIT is a standoff over NETWORK value — each waits for the")
    print("  other to move. Only a counterparty-independent (solo) lever breaks it")
    print("  from one side. ARC's one named solo thread is the audit log's")
    print("  self-delegation audit (4.2 / survey §109); the rest are network-value.")
    deadlocks, reach = solo_value_reach(refusals)
    if not deadlocks:
        print("  (no mutual-WAIT deadlock in this set; nothing to break)")
    for res in reach:
        d = res["deadlock"]
        print(f"\n  deadlock {{{', '.join(sorted(d))}}}:")
        if res["reaching"]:
            for cid in res["reaching"]:
                cand = CANDIDATES[cid]
                print(f"      reached by {cid} {cand['name']}  [{cand['value_locus']}]")
        else:
            print("      reached by no candidate at all")
        if res["solo"]:
            print(f"      => a solo-value lever reaches it: {', '.join(res['solo'])}")
            print("         (a lead only — solo value is unmeasured; survey §114,")
            print("         a hypothesis, not a path)")
        else:
            print("      => NO solo-value lever reaches it. The reaching candidates")
            print("         are network-value, so §4 does not break this deadlock")
            print("         from one side.")
    solo_ids = [cid for cid, c in CANDIDATES.items() if c["value_locus"] in SOLO_LOCI]
    if deadlocks and solo_ids:
        print("\n  Where ARC's solo thread actually sits:")
        for cid in solo_ids:
            cand = CANDIDATES[cid]
            has_wait = "incl. WAIT" if "WAIT" in cand["exits"] else "no WAIT cell"
            print(f"    {cid} {cand['name']} claims {{{', '.join(sorted(cand['exits']))}}}"
                  f"  ({has_wait})")
        print("  The only solo lever ARC has is aimed at REJECT, not the WAIT the")
        print("  chicken-and-egg turns on: the deadlock-breaking lever and the")
        print("  deadlock do not meet.")

    print(hr("[7] Exits no candidate mechanism even claims to address"))
    gaps = unaddressed_cells(refusals)
    if gaps:
        for r in gaps:
            print(f"  {r['actor']} / {r['exit']} : {r['id']}  \"{r['reason'][:60]}...\"")
        print("  (these refusals fall in cells the §4 set is silent on)")
    else:
        print("  (every refusal cell is claimed by some candidate)")

    print(hr("[8] What this fold cannot compute (standing residue)"))
    for line in [
        "whether any stated reason is true (a reason is testimony, not fact)",
        "whether a NAMED-RELEVANT party would actually adopt if the mechanism existed",
        "whether adoption will or will not happen",
        "whether a mechanism is valid in general (only: contradicted in this set)",
        "whether a refusal was strategic, lazy, hostile, or honest",
        "whether a CELL-COINCIDENT refuser ever weighed that candidate (the fold "
        "does not read reasons; matching by reason would be forbidden inference)",
        "whether a solo-value lever, where one reaches a deadlock, is large "
        "enough to seed adoption (unmeasured; survey §114, hypothesis not path)",
    ]:
        print(f"  - {line}")
    print("\n  The fold seals what was said, never that it is so: the same wall")
    print("  as view/interpretation fidelity (a signature certifies the record,")
    print("  not its referent). A recorded \"no\" weakens a candidate; it does")
    print("  not explain the refuser, and adoption stays off-ledger.")


if __name__ == "__main__":
    sys.exit(main())
