#!/usr/bin/env python3
"""ARC probe: the refusal-recording fold.

This probe records and groups refusal records; it does not model adoption.

ARC records do not establish why a party will honor, join, or adopt a protocol
(threat-model.md §18.1). This fixture groups the declared fields of refusal
records without inferring motives or adoption.

A refusal record carries four fields (adoption-and-defection.md §6):

    actor      developer | company | merchant | user | community
    exit       WAIT | DEFECT | FORK | REJECT
    reason     the participant's own words
    mechanism  which §4 candidate they say would have changed the decision,
               or "none"

From a set of such records the fold computes a grouped summary:

  WHAT THIS FOLD COMPUTES
    - counts by actor, by exit, by named mechanism
    - per candidate, two qualities of evidence kept apart: NAMED (the refuser
      themselves pointed at it) and CELL-COINCIDENT (a `mechanism = none`
      refusal in an (actor, exit) cell the candidate claims — contradiction
      pressure, but the fold does not read the reason)
    - where a WAIT record names another still-missing side of the network
      (including reciprocal WAIT labels)
    - whether a candidate labeled counterparty-independent is mapped to a WAIT
      cell in a reciprocal-WAIT pair
    - which exits no candidate mechanism even claims to address

  WHAT THIS FOLD CANNOT COMPUTE
    - whether a stated reason is true
    - whether the actor would actually change behavior later
    - whether adoption will or will not happen
    - whether a mechanism is valid in general (only: contradicted in *this*
      synthetic set, in the cells it claims)
    - whether the stated reason matches private motivation
    - whether a CELL-COINCIDENT refuser ever weighed that candidate at all —
      reading the reason to decide would be the inference §6 forbids
    - whether a candidate carrying a solo or mixed label would change behavior

This fold does not validate a candidate mechanism. It reports authored candidate
labels, named mechanisms, and cell-coincident records without predicting behavior.

Red-team note: the fold is only as precise as §4's claims, which are stated
by (actor, exit), not by reason. So a `mechanism = none` refusal contradicts
every candidate that claims its cell, even one its reason has nothing to do
with. That coarseness is reported explicitly (NAMED vs CELL-COINCIDENT, "reason
unread") rather than hidden — and it is not fixable by making the fold read
reasons, because that is the forbidden inference. See README "Red-team notes".

The fixtures in `fixtures.json` are SYNTHETIC and illustrative. Real
refusals of ARC — collected under docs/first-refusal-protocol.md — live in
the sibling `fixtures_real.json`, and the same fold consumes both. A real
record additionally carries a provenance envelope (source, date, visibility,
stimulus; protocol §5). A real record whose vocabulary does not fit the schema
is reported as a SCHEMA-BREAK rather than silently discarded. This fixture is
not an adoption simulator and predicts nothing. Stdlib only; no network.
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
#   "network" — candidate is labeled as requiring a counterparty.
#   "solo"    — candidate is labeled counterparty-independent.
#   "mixed"   — candidate carries both labels.
#
# The fold compares these authored labels with reciprocal WAIT cells. It does not
# establish that a candidate would change behavior. See fold [6].
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
        # §4.5 PAIRS its claims — "DEFECT (governance), REJECT (user)" — so the
        # faithful cells are (community, DEFECT) and (user, REJECT), not the
        # cross-product of the actor and exit sets above. `cells` overrides the
        # cross-product wherever the doc pairs actor and exit.
        "cells": {("community", "DEFECT"), ("user", "REJECT")},
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


MECHANISM_VOCAB = set(CANDIDATES) | {"none"}

# The provenance envelope every REAL record must carry (protocol §5). It is
# metadata about where the record came from, never an interpretation of it.
PROVENANCE_FIELDS = ["source", "date", "visibility", "stimulus"]


def load_refusals(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["refusals"]


def load_sets(here):
    """Load synthetic fixtures, plus real records if the sibling file exists."""
    synthetic = load_refusals(here / "fixtures.json")
    real_path = here / "fixtures_real.json"
    real = load_refusals(real_path) if real_path.exists() else []
    for r in real:
        r["_real"] = True
    return synthetic, real


def validate_real(r):
    """Split a real record's problems into two kinds that mean opposite things.

    - breaks : a value outside the schema's vocabulary. Broken records are excluded from the folds
      (their cells are undefined) but reported prominently, never discarded.
    - gaps   : a missing reason or provenance field. This is a recording
      error by the interviewer, not a finding about the schema. Gapped
      records still fold (the fold needs only actor/exit/mechanism) but are
      flagged for repair.
    """
    breaks, gaps = [], []
    if r.get("actor") not in ALL_ACTORS:
        breaks.append(f"actor {r.get('actor')!r} not in vocabulary")
    if r.get("exit") not in ALL_EXITS:
        breaks.append(f"exit {r.get('exit')!r} not in WAIT/DEFECT/FORK/REJECT")
    if r.get("mechanism") not in MECHANISM_VOCAB:
        breaks.append(f"mechanism {r.get('mechanism')!r} not in 4.1..4.6/none")
    if r.get("waits_on_actor") is not None and r["waits_on_actor"] not in ALL_ACTORS:
        breaks.append(f"waits_on_actor {r['waits_on_actor']!r} not in vocabulary")
    if not r.get("reason"):
        gaps.append("reason missing or empty (verbatim capture failed)")
    for f in PROVENANCE_FIELDS:
        if not r.get(f):
            gaps.append(f"provenance field '{f}' missing (protocol §5)")
    return breaks, gaps


def rid(r):
    """Record id for report listings; real records are marked with '*'."""
    return r.get("id", "?") + ("*" if r.get("_real") else "")


def claims_cell(cand, actor, exit_):
    """Does this candidate claim to address the (actor, exit) cell?

    When the source doc PAIRS actor and exit (4.5), the pairing is authoritative
    (`cells`); the cross-product of `actors` x `exits` applies only where the
    doc itself claims the full product."""
    cells = cand.get("cells")
    if cells is not None:
        return (actor, exit_) in cells
    if exit_ not in cand["exits"]:
        return False
    return cand["actors"] is None or actor in cand["actors"]


def claimed_cells(cand):
    if cand.get("cells") is not None:
        return set(cand["cells"])
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
    """WAIT records and what each waits on; identify reciprocal-WAIT pairs."""
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
    """Compare reciprocal-WAIT cells with the supplied candidate and
    `value_locus` labels. For each pair, list candidates mapped to a WAIT cell and
    those additionally labeled solo or mixed. This is structural label coverage,
    not a prediction that a candidate would change behavior."""
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
    """Refusal cells that no candidate mechanism claims to address."""
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
    synthetic, real = load_sets(here)

    # Vocabulary-broken real records cannot enter the folds (their cells are
    # undefined) — but they are the headline of section [0], not discards.
    validated = [(r, *validate_real(r)) for r in real]
    broken = [(r, breaks) for r, breaks, _ in validated if breaks]
    foldable_real = [r for r, breaks, _ in validated if not breaks]
    refusals = synthetic + foldable_real

    label = "synthetic data" if not real else "synthetic + real data"
    print(f"ARC — Refusal-Recording Fold  ({label})")
    print("=" * 48)
    print("This probe groups refusal records; it does not model adoption.\n")
    print(f"Loaded {len(synthetic)} synthetic + {len(real)} real refusal records.")
    if real:
        print("Real records are marked '*' throughout the report.")

    print(hr("[0] Real records: provenance and schema survival"))
    if not real:
        print("  fixtures_real.json: 0 records.")
        print("  No public refusal records are currently present.")
    for r, breaks, gaps in validated:
        print(f"\n  {rid(r)}  {r.get('actor')} / {r.get('exit')} / "
              f"mechanism={r.get('mechanism')}")
        print(f"      source={r.get('source')}  date={r.get('date')}  "
              f"visibility={r.get('visibility')}")
        print(f"      stimulus: {r.get('stimulus')}")
        for b in breaks:
            print(f"      SCHEMA-BREAK: {b}")
        for g in gaps:
            print(f"      recording gap: {g}")
        if r.get("visibility") == "private":
            print("      CONSENT GATE: this file is a public artifact. A private")
            print("      verbatim reason must be de-identified or consented BEFORE")
            print("      it is committed here (protocol §6) — a render-time")
            print("      redaction cannot un-publish the repository.")
    if broken:
        print(f"\n  {len(broken)} record(s) broke the schema — excluded from the")
        print("  folds below; the schema mismatch is reported separately.")

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
            ids = ", ".join(f"{rid(r)}({r['actor']} {r['exit']})" for r in v["named"])
            print(f"      named as the gap (n={len(v['named'])}, still declined): {ids}")
        if v["cell_coincident"]:
            ids = ", ".join(f"{rid(r)}({r['actor']} {r['exit']})" for r in v["cell_coincident"])
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
            print(f"  => reciprocal-WAIT pair: {{{', '.join(sorted(d))}}} "
                  f"(reciprocal WAIT labels; rationality not inferred)")
    else:
        print("  (no reciprocal-WAIT pair in this set)")

    print(hr("[6] Candidate-label coverage of reciprocal-WAIT cells"))
    print("  This section compares reciprocal WAIT labels with the candidate")
    print("  coverage and `value_locus` labels encoded in this fixture.")
    deadlocks, reach = solo_value_reach(refusals)
    if not deadlocks:
        print("  (no reciprocal-WAIT pair in this set)")
    for res in reach:
        d = res["deadlock"]
        print(f"\n  pair {{{', '.join(sorted(d))}}}:")
        if res["reaching"]:
            for cid in res["reaching"]:
                cand = CANDIDATES[cid]
                print(f"      mapped to {cid} {cand['name']}  [{cand['value_locus']}]")
        else:
            print("      mapped to no candidate")
        if res["solo"]:
            print(f"      => candidates also labeled solo/mixed: {', '.join(res['solo'])}")
        else:
            print("      => no mapped candidate is labeled solo/mixed; the mapped")
            print("         candidates are labeled network in this fixture.")
    solo_ids = [cid for cid, c in CANDIDATES.items() if c["value_locus"] in SOLO_LOCI]
    if deadlocks and solo_ids:
        print("\n  Where the solo/mixed labels are mapped in this fixture:")
        for cid in solo_ids:
            cand = CANDIDATES[cid]
            has_wait = "incl. WAIT" if "WAIT" in cand["exits"] else "no WAIT cell"
            print(f"    {cid} {cand['name']} claims {{{', '.join(sorted(cand['exits']))}}}"
                  f"  ({has_wait})")
        print("  Under the candidates and `value_locus` labels coded here, the")
        print("  solo/mixed candidate is mapped to REJECT, not WAIT.")

    print(hr("[7] Exits no candidate mechanism even claims to address"))
    gaps = unaddressed_cells(refusals)
    if gaps:
        for r in gaps:
            print(f"  {r['actor']} / {r['exit']} : {rid(r)}  \"{r['reason'][:60]}...\"")
        print("  (the supplied candidate map has no matching cell for these refusals)")
    else:
        print("  (every refusal cell is claimed by some candidate)")

    print(hr("[8] What this fold cannot compute"))
    for line in [
        "whether any stated reason is true (a reason is testimony, not fact)",
        "whether a NAMED-RELEVANT party would actually adopt if the mechanism existed",
        "whether adoption will or will not happen",
        "whether a mechanism is valid in general (only: contradicted in this set)",
        "whether the stated reason matches private motivation",
        "whether a CELL-COINCIDENT refuser ever weighed that candidate (the fold "
        "does not perform reason matching)",
        "whether a candidate labeled solo or mixed would change behavior",
    ]:
        print(f"  - {line}")
    print("\n  The fold groups what the records say; it does not establish the reason")
    print("  or referent. Fixture record checks cover only the named fields. A")
    print("  recorded \"no\" contributes contradiction pressure under this fold; it does")
    print("  not explain the refuser, and adoption stays off-ledger.")


if __name__ == "__main__":
    sys.exit(main())
