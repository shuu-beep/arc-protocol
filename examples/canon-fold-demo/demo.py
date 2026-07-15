#!/usr/bin/env python3
"""
ARC canon fold demo — single file, stdlib only.

Purpose
-------
Test whether the ARC canon survives contact with code. Specifically:

  1. that a "Relationship" is recoverable as a *fold over a signed Event log*,
     with no stored score and no stored profile (object-model.md §4-§6);
  2. that the five canonical event types — KEY, ATTEST, AUTHORIZE, CHALLENGE,
     ADJUDICATE — plus a `nullifies` field are sufficient to express identity,
     an offer, an approval, a payment claim, a fulfillment claim, reputation
     signals, a dispute, and a governance decision (event-registry.md §4, §9);
  3. that injecting one governed dispute (CHALLENGE -> ADJUDICATE) makes the
     *same* fold produce a *different* projection — i.e. governance works by
     adding events, never by mutating stored state (authority-and-conflict.md).

This is an exploratory probe, not an implementation. Signatures are stubbed
(a hash, not real crypto). If the five types turn out to be insufficient, the
gap is meant to show up here — that is the point.

Run:  python3 demo.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Callable

# ---------------------------------------------------------------------------
# 1. The Event — the ONLY stored/transmitted/verifiable unit (object-model §2.2)
# ---------------------------------------------------------------------------
# The type set is closed and small. Application richness lives in `predicate`
# and `payload`, never in new top-level types (event-registry §2.1). Withdrawal
# is the `nullifies` field, never a per-domain revoke type (event-registry §4.6).

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


@dataclass(frozen=True)
class Event:
    id: str                       # content hash
    type: str                     # one of CANONICAL_TYPES
    signer: str                   # key id, resolvable via a prior KEY event
    predicate: str                # namespaced semantic tag (event-registry §6)
    timestamp: str
    refs: tuple[str, ...] = ()        # prior events / parties / resources
    nullifies: tuple[str, ...] = ()   # prior event ids withdrawn going forward
    scope: dict[str, Any] | None = None        # AUTHORIZE: budget/category/...
    contrary_to: tuple[str, ...] = ()          # AUTHORIZE: overridden warnings
    payload: dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    def signing_bytes(self) -> bytes:
        body = {
            "type": self.type, "signer": self.signer, "predicate": self.predicate,
            "timestamp": self.timestamp, "refs": self.refs, "nullifies": self.nullifies,
            "scope": self.scope, "contrary_to": self.contrary_to, "payload": self.payload,
        }
        return json.dumps(body, sort_keys=True, default=list).encode()


def stub_sign(signer: str, body: bytes) -> str:
    """STUB. Real ARC uses Ed25519; here a hash stands in so replay still works."""
    return "stub:" + hashlib.sha256(signer.encode() + body).hexdigest()[:16]


def make(type_: str, signer: str, predicate: str, ts: str, **kw) -> Event:
    assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r} — forbidden"
    partial = Event(id="", type=type_, signer=signer, predicate=predicate, timestamp=ts, **kw)
    body = partial.signing_bytes()
    return Event(
        id="ev:" + hashlib.sha256(body).hexdigest()[:12],
        type=type_, signer=signer, predicate=predicate, timestamp=ts,
        signature=stub_sign(signer, body), **kw,
    )


# ---------------------------------------------------------------------------
# 2. Verification IS replay (object-model §5)
# ---------------------------------------------------------------------------
# Before any fold is meaningful: verify each signature, and verify the signer
# was anchored by a prior KEY register event (key provenance). A KEY root is
# anchored from outside ARC by a cost gate, so it may self-anchor.

def verify_log(events: list[Event]) -> None:
    registered: set[str] = set()
    for ev in events:
        expected = stub_sign(ev.signer, ev.signing_bytes())
        if ev.signature != expected:
            raise ValueError(f"bad signature on {ev.id}")
        is_key_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        is_rotation = ev.type == "KEY" and ev.predicate == "id.key_rotate"
        if not is_key_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} has no prior KEY register ({ev.id})")
        if is_key_root:
            registered.add(ev.payload["key"])
        if is_rotation:
            # A rotation is signed by the OLD key (so only the controlling holder
            # can rotate) and anchors the NEW key. The new key's trust is carried
            # forward by that signature, not by a fresh external cost gate. Same
            # KEY type, new predicate — no sixth type (event-registry §4.1, §4.6).
            registered.add(ev.payload["new_key"])


def _rotation_successors(events: list[Event]) -> dict[str, set[str]]:
    """key -> every key downstream of it in the KEY rotation chain (§4.1).

    A rotation is signed by the OLD key and anchors the NEW one, so the holder's
    authority over a key's history carries FORWARD along the chain: whoever
    rotated k1 -> k2 still authors k1's statements through k2."""
    nxt: dict[str, str] = {}
    for ev in events:
        if ev.type == "KEY" and ev.predicate == "id.key_rotate":
            nxt[ev.signer] = ev.payload["new_key"]
    succ: dict[str, set[str]] = {}
    for k in nxt:
        chain: set[str] = set()
        cur = k
        while cur in nxt and nxt[cur] not in chain:
            cur = nxt[cur]
            chain.add(cur)
        succ[k] = chain
    return succ


def _may_nullify(nuller: str, author: str, successors: dict[str, set[str]]) -> bool:
    """The event-registry §4.6 nullifier-authority rule.

    Withdrawal is a self-domain act (authority-and-conflict §3): only the
    target's author — or a key downstream of it in the rotation lineage — may
    nullify it. Any other `nullifies` stays on the log as evidence but is not
    honored by the fold; invalidating another party's event is an ADJUDICATE
    (authority-and-conflict §9), never a `nullifies` side effect."""
    return nuller == author or nuller in successors.get(author, set())


def _revocations(events: list[Event]) -> dict[str, str]:
    """Revoked keys -> earliest revoke timestamp.

    A revocation is a `KEY` `id.key_revoke` whose `nullifies` names the key's
    register event — same KEY type, the existing `nullifies` field, no sixth
    type (event-registry §4.6). The revoked key is read from that register, and
    the revoke's timestamp is kept because withdrawal is *time-scoped*: "going
    forward" from the revoke, not retroactively over the key's whole history.
    Honored only from an authorized nullifier (§4.6): the revoked key itself or
    a key downstream of it in the rotation lineage."""
    by_id = {ev.id: ev for ev in events}
    succ = _rotation_successors(events)
    revs: dict[str, str] = {}
    for ev in events:
        if ev.type == "KEY" and ev.predicate == "id.key_revoke":
            for reg_id in ev.nullifies:
                reg = by_id.get(reg_id)
                if reg is not None and reg.type == "KEY" and "key" in reg.payload:
                    k = reg.payload["key"]
                    if not _may_nullify(ev.signer, k, succ):
                        continue  # §4.6: not the key's holder lineage -> not honored
                    revs[k] = ev.timestamp if k not in revs else min(revs[k], ev.timestamp)
    return revs


def active(events: list[Event]) -> list[Event]:
    """Drop events withdrawn by a later `nullifies` (event-registry §4.6).

    A `nullifies` is honored only from an AUTHORIZED nullifier — the target's
    author or a key downstream of it in the KEY rotation lineage (§4.6). Anyone
    else's withdrawal stays on the log as evidence but drops nothing here.

    An honored `nullifies` means "withdrawn going forward", read two ways from
    the SAME field:
      * an ordinary withdrawal (a withdrawn approval, a superseded offer) takes its
        target out of force however old the target is — this fold's
        current-standing reading drops it outright; whether a current reader
        continues to honor a COMPLETED act under the target is the authority-and-
        conflict §9 projection choice (see authority-revocation-demo);
      * a `KEY` `id.key_revoke` is time-scoped: the revoked key's register and
        everything it signed BEFORE the revoke stay readable, but anything it
        signs AT/AFTER the revoke timestamp is dropped. The register is kept, so
        the key's past history and its rotation lineage remain walkable.
    """
    revs = _revocations(events)
    by_id = {ev.id: ev for ev in events}
    succ = _rotation_successors(events)
    withdrawn = {
        ref for ev in events for ref in ev.nullifies
        if not (ev.type == "KEY" and ev.predicate == "id.key_revoke")
        and ref in by_id and _may_nullify(ev.signer, by_id[ref].signer, succ)
    }
    kept: list[Event] = []
    for ev in events:
        if ev.id in withdrawn:
            continue
        is_revoke = ev.type == "KEY" and ev.predicate == "id.key_revoke"
        rt = revs.get(ev.signer)
        if rt is not None and not is_revoke and ev.timestamp >= rt:
            continue  # signed by a revoked key, at/after revocation -> not honored
        kept.append(ev)
    return kept


def event_set_hash(events: list[Event]) -> str:
    """Stable digest of an ACTIVE event set — the identity of a replay input.

    A cached projection keyed by this hash is valid only while the *same* events
    replay; the moment the active set changes, the hash changes and the cache is
    stale. This is what lets a cache be event-bound instead of profile-like."""
    return "es:" + hashlib.sha256("\n".join(sorted(e.id for e in events)).encode()).hexdigest()[:16]


def as_of(events: list[Event], t: str) -> list[Event]:
    """Replay input restricted to events recorded at or before `t` — a
    point-in-time historical subset. It establishes what the event set contained
    then; it is not a same-events policy comparison. No new mechanism: a fold is
    over whatever event subset the reader holds (§5)."""
    return [e for e in events if e.timestamp <= t]


# ---------------------------------------------------------------------------
# 3. Projections — deterministic folds, NOTHING stored (object-model §4)
# ---------------------------------------------------------------------------
# Each projection takes the whole log and returns a view that the caller uses
# and discards. There is no profile object, no score field, no status column.

def project_identity_status(events: list[Event], key: str) -> str:
    """Fold KEY + credential ATTEST + commons ADJUDICATE -> status (identity §4).

    Status is NOT a stored field — it is recomputed here every call."""
    evs = active(events)
    if not any(e.type == "KEY" and e.payload.get("key") == key for e in evs):
        return "unverified"
    status = "verified"
    if any(e.type == "ATTEST" and e.predicate == "id.credential"
           and key in e.refs for e in evs):
        status = "credentialed"
    # Only an ADJUDICATE (commons authority) may suspend/revoke (authority §5).
    # Rulings fold in TIMESTAMP order — the same ordering project_merchant_standing
    # uses — so the two folds cannot diverge on an out-of-order log.
    rulings = (e for e in evs if e.type == "ADJUDICATE" and key in e.refs)
    for e in sorted(rulings, key=lambda e: e.timestamp):
        if e.predicate == "gov.suspension":
            status = "suspended"
        elif e.predicate == "gov.expulsion":
            status = "revoked"
        elif e.predicate == "gov.reinstatement":
            status = "verified"
    return status


def project_transaction_state(events: list[Event], tx_id: str) -> str:
    """Fold one transaction's events -> state (protocol §4, a projection)."""
    evs = [e for e in active(events) if tx_id in e.refs]
    state = "intent"
    has = lambda t, p: any(e.type == t and e.predicate == p for e in evs)
    if has("ATTEST", "commerce.offer"):
        state = "offer_received"
    if has("AUTHORIZE", "consent.approval"):
        state = "approved"
    if has("ATTEST", "commerce.payment_result"):
        state = "payment_confirmed"
    if has("ATTEST", "commerce.fulfillment"):
        state = "fulfilled"
    if has("CHALLENGE", "dispute.open"):
        state = "disputed"
    for e in evs:
        if e.type == "ADJUDICATE" and e.predicate.startswith("gov."):
            state = "resolved"
    return state


def _advisory_signal(positive: int, negative: int, disputes: int, distinct_raters: int) -> str:
    """The advisory-signal thresholds, factored out so a single-key fold and a
    lineage fold can share identical semantics. Behaviour is unchanged."""
    sig = "trusted" if positive >= 3 and disputes == 0 else \
          "limited"  if positive >= 1 and negative + disputes <= 2 else \
          "unproven"
    if distinct_raters < 2:
        sig = "unproven"  # too few independent counterparties to rely on
    return sig


def project_merchant_standing(events: list[Event], merchant: str, context: str) -> dict:
    """Fold -> a CONTEXT-SCOPED standing view for one merchant.

    Two clearly separated parts (authority-and-conflict §5):
      * advisory  — a risk signal folded from rep.outcome / dispute signals.
                    It may raise friction; it may NOT punish.
      * governance — commons standing, changed ONLY by ADJUDICATE.

    Non-aggregated and contextual: outcomes are filtered by `context`, so there
    is no single global score for the merchant (object-model §2.1, reputation §3.1).
    """
    evs = active(events)
    outcomes = [
        e for e in evs
        if e.type == "ATTEST" and e.predicate == "rep.outcome"
        and merchant in e.refs and e.payload.get("context") == context
    ]
    positive = sum(1 for e in outcomes if e.payload.get("result") == "positive")
    negative = sum(1 for e in outcomes if e.payload.get("result") == "negative")
    disputes = sum(
        1 for e in evs
        if e.type == "CHALLENGE" and e.predicate == "dispute.open" and merchant in e.refs
    )
    # Sybil down-weight lives in the fold (object-model §8): trust counts only
    # from *distinct* counterparties, so circular self-dealing does not inflate.
    distinct_raters = len({e.signer for e in outcomes})

    advisory = _advisory_signal(positive, negative, disputes, distinct_raters)

    rulings = [
        e for e in evs
        if e.type == "ADJUDICATE" and e.predicate.startswith("gov.") and merchant in e.refs
    ]
    governance = "in_good_standing"
    for e in sorted(rulings, key=lambda e: e.timestamp):
        governance = {
            "gov.warning": "warned",
            "gov.suspension": "suspended",
            "gov.expulsion": "expelled",
            "gov.reinstatement": "in_good_standing",
        }.get(e.predicate, governance)

    return {
        "merchant": merchant,
        "context": context,
        "advisory_signal": advisory,         # computed risk signal, not a verdict
        "governance_standing": governance,    # commons fact, ADJUDICATE-only
        "evidence": {
            "positive_outcomes": positive,
            "negative_outcomes": negative,
            "open_disputes": disputes,
            "distinct_counterparties": distinct_raters,
        },
        "_note": "recomputed on demand from the event log; nothing here is stored",
    }


def project_authority_context(events: list[Event], subject: str, authority: str) -> dict:
    """Governance standing for `subject` UNDER ONE authority context — counting
    only ADJUDICATE rulings signed by `authority` (authority-and-conflict §5).

    There is no global authority and no central arbiter: a reader chooses which
    community's rulings it honors, and this fold answers only "what does THAT
    authority say?". Two readers honoring two authorities can get two answers."""
    rulings = sorted(
        (e for e in active(events)
         if e.type == "ADJUDICATE" and e.predicate.startswith("gov.")
         and subject in e.refs and e.signer == authority),
        key=lambda e: e.timestamp,
    )
    standing = "in_good_standing"
    for e in rulings:
        standing = {
            "gov.warning": "warned",
            "gov.suspension": "suspended",
            "gov.expulsion": "expelled",
            "gov.reinstatement": "in_good_standing",
        }.get(e.predicate, standing)
    return {"subject": subject, "authority": authority,
            "governance_standing": standing, "rulings": [e.predicate for e in rulings]}


def project_conflicting_governance(events: list[Event], subject: str,
                                   authorities: list[str]) -> dict:
    """Read `subject`'s governance under EACH authority and report disagreement
    WITHOUT choosing a winner (authority-and-conflict §5: no single final
    authority by design).

    The five event types REPRESENT the conflict (each ruling is an ordinary
    ADJUDICATE, both valid, both replay). They cannot, by themselves, SELECT
    which authority governs — that needs a policy (authority selection /
    federation / bridge rule / human-community choice) OUTSIDE the event canon.
    `canonical_winner` is deliberately None: ARC does not auto-resolve this."""
    by_authority = {
        a: project_authority_context(events, subject, a)["governance_standing"]
        for a in authorities
    }
    return {
        "subject": subject,
        "by_authority": by_authority,
        "conflict": len(set(by_authority.values())) > 1,
        "canonical_winner": None,  # not expressible in the five types — left open
        "resolution_requires": ("an authority-selection / federation / bridge rule "
                                 "or human-community choice, outside the five event types"),
    }


# --- policy layer: OUTSIDE the event canon; ARC endorses NO single policy ----
# Scenario 8 showed the five types REPRESENT a conflict but do not RESOLVE it.
# These readers resolve it — but they are POLICY, not canon. Each consumes the
# per-authority projections (which ARE folded from events) and applies a choice
# the reader / community / federation makes. None is canonical: a different
# reader may pick a different policy and get a different — equally valid —
# answer. No event is added or changed; only the selection rule differs. A sixth
# event type would not help here, because the question is "whose ruling wins?",
# which is a choice, not a fact (authority-and-conflict §5).

_GOV_SEVERITY = {"in_good_standing": 0, "warned": 1, "suspended": 2, "expelled": 3}


def resolve_by_subscriber_choice(events: list[Event], subject: str,
                                 subscribed_authority: str) -> dict:
    """Policy: the reader honors the one authority it subscribes to / trusts."""
    v = project_authority_context(events, subject, subscribed_authority)
    return {"policy": "subscriber-choice", "honored_authority": subscribed_authority,
            "resolved_standing": v["governance_standing"]}


def resolve_by_most_restrictive(events: list[Event], subject: str,
                                authorities: list[str]) -> dict:
    """Policy: among valid rulings, the MORE RESTRICTIVE wins
    (expelled > suspended > warned > in_good_standing). A safety-biased reader
    policy — explicitly NOT ARC's recommendation, just one conservative choice."""
    views = {a: project_authority_context(events, subject, a)["governance_standing"]
             for a in authorities}
    winner = max(authorities, key=lambda a: _GOV_SEVERITY.get(views[a], 0))
    return {"policy": "most-restrictive-wins", "honored_authority": winner,
            "resolved_standing": views[winner]}


def resolve_by_explicit_precedence(events: list[Event], subject: str,
                                   precedence: list[str]) -> dict:
    """Policy: the reader supplies an ordered authority list; the first authority
    that has actually ruled on the subject wins."""
    for a in precedence:
        v = project_authority_context(events, subject, a)
        if v["rulings"]:  # this authority has issued a ruling
            return {"policy": "explicit-precedence", "honored_authority": a,
                    "resolved_standing": v["governance_standing"]}
    return {"policy": "explicit-precedence", "honored_authority": None,
            "resolved_standing": "in_good_standing"}


def project_overrides(events: list[Event], tx_id: str) -> dict:
    """Fold a transaction's `AUTHORIZE`s -> which approvals were made against a
    warning (event-registry §4.3, authority-and-conflict §7).

    An override is NOT a new type. It is an ordinary `consent.approval`
    `AUTHORIZE` carrying `contrary_to`, referencing the advisory it was made in
    spite of. It records that a human accepted risk over *their own action*; it
    grants no commons authority and changes no party's standing. Re-running this
    fold later still shows "this approval was made against a warning" — the fact
    is in the immutable event, not in any stored flag.
    """
    evs = active(events)
    warnings = {
        e.id: e for e in evs
        if e.type == "ATTEST" and e.predicate == "risk.advisory"
    }
    overrides = []
    for e in evs:
        if e.type == "AUTHORIZE" and tx_id in e.refs and e.contrary_to:
            overrides.append({
                "approval": e.id,
                "approver": e.signer,
                "overridden_warnings": [
                    {"warning": w,
                     "advisory": warnings[w].payload.get("advisory") if w in warnings else "unknown",
                     "reason": warnings[w].payload.get("reason") if w in warnings else "unknown"}
                    for w in e.contrary_to
                ],
            })
    return {
        "tx": tx_id,
        "override_detected": bool(overrides),
        "approvals_contrary_to_warning": overrides,
    }


def project_key_authority(events: list[Event], key: str) -> dict:
    """Fold KEY events -> may this key sign GOING FORWARD? (event-registry §4.6)

    Two separable facts, neither stored:
      * the key's PAST events stay valid and readable (the register is kept);
      * a `KEY` `id.key_revoke` withdraws the key's FORWARD authority from its
        timestamp on. This is the holder's authority over their own key (a
        rotation/revoke they signed), not a commons ADJUDICATE.
    Recomputed on demand; there is no stored key-status field.
    """
    evs = active(events)
    # Anchored either directly (id.key_register) or by a rotation that named it
    # (id.key_rotate, new_key) — the same provenance notion verify_log enforces.
    registered = any(
        e.type == "KEY" and (e.payload.get("key") == key or e.payload.get("new_key") == key)
        for e in evs
    )
    revoked_at = _revocations(events).get(key)
    return {
        "key": key,
        "registered": registered,
        "revoked": revoked_at is not None,
        "revoked_at": revoked_at,
        "honored_going_forward": registered and revoked_at is None,
    }


def project_cache_safety(entry: dict, live_hash: str) -> dict:
    """Classify a projection-CACHE entry by SHAPE, not by trust (object-model §10).

    A cache is a derived convenience. The risk is that it quietly becomes the
    stored profile / score / status object the model refuses to keep. The shape
    decides which it is — no event type is involved, this is about derived data:

      * not durable (scoped to one replay run)      -> safe optimization
      * durable, no event_set_hash binding          -> profile-like reintroduction
      * durable, event_set_hash, hint-only          -> conditionally safe

    A cache is *never* authority: whatever it stores, the authoritative answer is
    still the fold over the log, where an ADJUDICATE alone moves commons standing.
    """
    durable = entry.get("durable", False)
    bound = entry.get("event_set_hash")
    if not durable:
        classification = "safe optimization"
    elif bound is None:
        classification = "profile-like reintroduction"
    else:
        classification = "conditionally safe"
    matches_live = bound is not None and bound == live_hash
    return {
        "cache": entry.get("name"),
        "classification": classification,
        "event_bound": bound is not None,
        "matches_live_event_set": matches_live,
        "authoritative": entry.get("authoritative", False),  # must stay False
        # An event-bound cache may be reused only as a HINT, only while fresh:
        "reusable_as_hint": classification == "conditionally safe" and matches_live,
    }


def _rotation_links(events: list[Event]) -> dict[str, str]:
    """old_key -> new_key, read from KEY `id.key_rotate` events (no new type)."""
    return {
        e.payload["old_key"]: e.payload["new_key"]
        for e in active(events)
        if e.type == "KEY" and e.predicate == "id.key_rotate"
    }


def key_lineage(events: list[Event], key: str) -> set[str]:
    """All keys that are the same identity as `key`, walking KEY rotation links
    both directions. A lineage is just a chain of KEY events — no new primitive."""
    nxt = _rotation_links(events)
    prv = {v: k for k, v in nxt.items()}
    lineage = {key}
    cur = key
    while cur in nxt:
        cur = nxt[cur]; lineage.add(cur)
    cur = key
    while cur in prv:
        cur = prv[cur]; lineage.add(cur)
    return lineage


def project_identity_lineage(events: list[Event], key: str) -> dict:
    """Fold KEY `id.key_rotate` events into an ordered provenance chain.

    Pure KEY events read as a chain (event-registry §4.1, §4.6). This is the
    continuity record: it links old and new keys without a sixth type."""
    nxt = _rotation_links(events)
    prv = {v: k for k, v in nxt.items()}
    root = key
    while root in prv:
        root = prv[root]
    chain = [root]
    while chain[-1] in nxt:
        chain.append(nxt[chain[-1]])
    return {"key": key, "chain": chain, "root": chain[0],
            "current": chain[-1], "rotations": len(nxt)}


def project_lineage_standing(events: list[Event], key: str, context: str) -> dict:
    """ONE carry-forward reading: fold standing across the whole rotation lineage
    (full inheritance). Shown to demonstrate that continuity is *expressible*.

    Partial carry, standing-only, or no-auto-carry are equally expressible by
    changing what this fold counts. The demo links the identities; it does NOT
    declare which policy is correct.
    """
    evs = active(events)
    lineage = key_lineage(events, key)
    outcomes = [
        e for e in evs
        if e.type == "ATTEST" and e.predicate == "rep.outcome"
        and (set(e.refs) & lineage) and e.payload.get("context") == context
    ]
    positive = sum(1 for e in outcomes if e.payload.get("result") == "positive")
    negative = sum(1 for e in outcomes if e.payload.get("result") == "negative")
    disputes = sum(
        1 for e in evs
        if e.type == "CHALLENGE" and e.predicate == "dispute.open" and (set(e.refs) & lineage)
    )
    distinct_raters = len({e.signer for e in outcomes})
    root = project_identity_lineage(events, key)["root"]
    return {
        "lineage": sorted(lineage),
        "advisory_signal": _advisory_signal(positive, negative, disputes, distinct_raters),
        "identity_continuity": project_identity_status(events, root),
        "evidence": {
            "positive_outcomes": positive, "negative_outcomes": negative,
            "open_disputes": disputes, "distinct_counterparties": distinct_raters,
        },
    }


def _scope_covers(outer: dict | None, needed: dict) -> bool:
    """Does a mandate `outer` scope cover a `needed` {category, max_total_krw}?
    A sub-grant may only NARROW: same category (or "*" wildcard) and no more
    budget. Expiry is checked separately as a time-bound, not here."""
    if outer is None:
        return False
    cat_ok = outer.get("category") in (needed.get("category"), "*")
    amt_ok = needed.get("max_total_krw", 0) <= outer.get("max_total_krw", 0)
    return cat_ok and amt_ok


def _delegation_mandates_to(events: list[Event], grantee: str) -> list[Event]:
    """Active AUTHORIZE consent.mandate events that name `grantee` as the delegate.
    Revoked mandates are already gone — `active()` honors `nullifies` (§4.6)."""
    return [
        e for e in active(events)
        if e.type == "AUTHORIZE" and e.predicate == "consent.mandate"
        and e.payload.get("delegate") == grantee
    ]


def project_delegated_authority(events: list[Event], agent: str, needed: dict,
                                at_time: str, principal: str,
                                _seen: frozenset[str] = frozenset()) -> dict:
    """Fold the AUTHORIZE consent.mandate chain -> may `agent` authorize an action
    needing `needed` {category, max_total_krw} at `at_time`? (event-registry §4.3)

    Delegation is NOT a new type: it is AUTHORIZE + `scope` (+ expiry carried in
    scope) + `nullifies`. The chain bottoms out at the human principal, whose
    authority over their own action is inherent (authority-and-conflict §3) and
    needs no upstream grant. Scope-bounds, time-bounds, and the no-redelegation
    flag are all enforced HERE in the fold; nothing about authority is stored.
    Returns the validating chain, or the reason the request fails.
    """
    if agent == principal:
        return {"authorized": True, "chain": [principal], "via": None,
                "reason": "principal: inherent authority over own action"}
    if agent in _seen:
        return {"authorized": False, "chain": [], "via": None, "reason": "delegation cycle"}
    reason = "no mandate grants this agent the action"
    for m in _delegation_mandates_to(events, agent):
        sc = m.scope or {}
        if at_time > sc.get("expires_at", "9999-12-31T00:00:00Z"):
            reason = "mandate expired at query time"; continue
        if not _scope_covers(sc, needed):
            reason = "requested action not within granted scope"; continue
        grantor = m.payload.get("delegator")
        up = project_delegated_authority(events, grantor, needed, at_time,
                                         principal, _seen | {agent})
        if not up["authorized"]:
            reason = f"upstream authority broken ({up['reason']})"; continue
        # no-redelegation: if the grantor is not the principal, the mandate that
        # gave the GRANTOR its authority must itself have permitted redelegation.
        if grantor != principal:
            gm = up["via"]
            if gm is None or not (gm.scope or {}).get("redelegatable", False):
                reason = "grantor was not permitted to redelegate"; continue
        return {"authorized": True, "chain": up["chain"] + [agent], "via": m,
                "reason": "valid delegation chain"}
    return {"authorized": False, "chain": [], "via": None, "reason": reason}


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


# ---------------------------------------------------------------------------
#   Agent multiplication / root collapse (object-model §8 Sybil down-weight)
# ---------------------------------------------------------------------------
# ARC's event horizon is the commons boundary: an agent that only does local
# work — never signing a commons-visible event — is invisible to ARC and out of
# scope. The instant an agent signs a commons event (here a `rep.outcome`
# ATTEST) it becomes visible. That raises the probe's question: one actor can
# run many agents, so many signatures need not mean many independent
# counterparties. The standing fold already down-weights by DISTINCT signer
# (object-model §8); this asks whether that distinctness can be trusted when one
# actor holds many keys. Collapsing keys to a principal requires KNOWING the keys
# share a root — and the canon learns that only if the root DISCLOSES it. No new
# type: disclosure is `id.controls`, an open-namespace predicate (event-registry
# §6); nothing is stored, the link is re-read from the log each fold.

def _disclosed_control(events: list[Event]) -> dict[str, str]:
    """agent_key -> disclosed root_key, from ATTEST `id.controls` events.

    A root VOLUNTARILY discloses the agent keys it controls by signing an ATTEST
    `id.controls` naming those keys in `refs`. Nothing forces this: an attacker
    simply omits it. Undisclosed keys never appear here — which is the whole
    point of the probe."""
    control: dict[str, str] = {}
    for e in active(events):
        if e.type == "ATTEST" and e.predicate == "id.controls":
            for agent in e.refs:
                control[agent] = e.signer
    return control


def _principal_of(control: dict[str, str], key: str) -> str:
    """The disclosed root for a key, or the key itself if no disclosure links it.
    An undisclosed Sybil agent is therefore counted as its own principal."""
    return control.get(key, key)


def project_merchant_standing_root_aware(events: list[Event], merchant: str,
                                         context: str) -> dict:
    """The standing fold (object-model §8) with raters COLLAPSED to their
    disclosed root before counting distinct counterparties. Disclosed sibling
    agents count as ONE principal; undisclosed agents count as themselves. This
    is the only Sybil collapse the canon can do from events alone — and it bites
    exactly the actors who chose to disclose."""
    control = _disclosed_control(events)
    evs = active(events)
    outcomes = [e for e in evs if e.type == "ATTEST" and e.predicate == "rep.outcome"
                and merchant in e.refs and e.payload.get("context") == context]
    positive = sum(1 for e in outcomes if e.payload.get("result") == "positive")
    negative = sum(1 for e in outcomes if e.payload.get("result") == "negative")
    disputes = sum(1 for e in evs if e.type == "CHALLENGE"
                   and e.predicate == "dispute.open" and merchant in e.refs)
    raw_raters = len({e.signer for e in outcomes})
    principals = len({_principal_of(control, e.signer) for e in outcomes})
    return {
        "merchant": merchant,
        "advisory_signal": _advisory_signal(positive, negative, disputes, principals),
        "distinct_raters_raw": raw_raters,
        "distinct_principals": principals,
        "collapsed": raw_raters - principals,
    }


def project_correlation_suspicion(events: list[Event], merchant: str, context: str,
                                  window_minutes: int = 30, threshold: int = 3) -> dict:
    """Exit C made concrete: a LOCAL, PROBABILISTIC review trigger — not a verdict.

    It flags when `threshold`+ UNDISCLOSED raters endorse the same subject in the
    same context inside a `window_minutes` burst — a behavioral smell of one actor
    behind many keys. It changes NO standing and imposes NO penalty; it only
    suggests human/community review. It is fallible BY DESIGN: a genuinely popular
    merchant rated by real independent people in a burst trips it too (a false
    positive). This is the closest thing to ARC's actual Sybil stance: local,
    probabilistic, review-only — never automatic global dedup."""
    control = _disclosed_control(events)
    evs = active(events)
    undisclosed = sorted(
        (e for e in evs if e.type == "ATTEST" and e.predicate == "rep.outcome"
         and merchant in e.refs and e.payload.get("context") == context
         and e.signer not in control),
        key=lambda e: e.timestamp,
    )
    times = [_parse_ts(e.timestamp) for e in undisclosed]
    burst = 0
    for i, t0 in enumerate(times):  # tightest window holding the most raters
        n = sum(1 for t in times[i:] if (t - t0).total_seconds() <= window_minutes * 60)
        burst = max(burst, n)
    return {
        "merchant": merchant,
        "undisclosed_raters": len(undisclosed),
        "max_burst_in_window": burst,
        "review_suggested": burst >= threshold,
        "changes_standing": False,   # invariant: a trigger, never a penalty
        "fallible": True,            # would also flag a real popularity burst
    }


def project_root_collapse_summary(events: list[Event], disclosed_subject: str,
                                  hidden_subject: str, context: str) -> dict:
    """Make the disclosed/undisclosed ASYMMETRY explicit in one view. The honest
    cluster is deflated by the collapse; the hidden cluster is untouched, because
    the canon cannot prove undisclosed keys share a root without a stored identity
    graph or an external cost gate — both constitutional trade-offs."""
    d_raw = project_merchant_standing(events, disclosed_subject, context)
    d_col = project_merchant_standing_root_aware(events, disclosed_subject, context)
    h_raw = project_merchant_standing(events, hidden_subject, context)
    h_col = project_merchant_standing_root_aware(events, hidden_subject, context)
    return {
        "disclosed_root_detected": d_col["collapsed"] > 0,
        "local_collapse_possible": d_col["collapsed"] > 0,
        "hidden_root_detected": h_col["collapsed"] > 0,        # False: never disclosed
        "certain_global_dedup_possible": False,                # needs graph or cost gate
        "voluntary_disclosure_penalizes_honest_participants":
            d_col["advisory_signal"] != d_raw["advisory_signal"]
            and h_col["advisory_signal"] == h_raw["advisory_signal"],
    }


# ---------------------------------------------------------------------------
# 4. A hand-built event log (mock data — KRW local-food scenario)
# ---------------------------------------------------------------------------

CTX = "seoul-local-food/delivery"

def base_log() -> list[Event]:
    e: list[Event] = []
    # --- KEY: anchors (each anchored outside ARC by a cost gate) -------------
    e.append(make("KEY", "k:community", "id.key_register", "2026-01-01T00:00:00Z",
                  payload={"key": "k:community", "anchor": "community-charter"}))
    e.append(make("KEY", "k:merchant_bibimbap", "id.key_register", "2026-01-02T00:00:00Z",
                  payload={"key": "k:merchant_bibimbap", "anchor": "business-registration"}))
    for i in (1, 2, 3, 4):
        e.append(make("KEY", f"k:consumer_{i}", "id.key_register", f"2026-01-03T0{i}:00:00Z",
                      payload={"key": f"k:consumer_{i}", "anchor": "payment-account"}))

    # --- Four prior transactions, each: offer -> approval -> payment ---------
    #     -> fulfillment -> positive outcome. Builds context-scoped reputation.
    for i in (1, 2, 3):
        tx = f"tx_{i}"
        e.append(make("ATTEST", "k:merchant_bibimbap", "commerce.offer", f"2026-02-0{i}T10:00:00Z",
                      refs=(tx, "k:merchant_bibimbap"),
                      payload={"item": "vegetable bibimbap", "price_krw": 9800, "context": CTX}))
        e.append(make("AUTHORIZE", f"k:consumer_{i}", "consent.approval", f"2026-02-0{i}T10:01:00Z",
                      refs=(tx, "k:merchant_bibimbap"),
                      scope={"max_total_krw": 15000}, payload={"approved_total_krw": 12300}))
        e.append(make("ATTEST", f"k:consumer_{i}", "commerce.payment_result", f"2026-02-0{i}T10:02:00Z",
                      refs=(tx,), payload={"status": "confirmed", "amount_krw": 12300}))
        e.append(make("ATTEST", "k:merchant_bibimbap", "commerce.fulfillment", f"2026-02-0{i}T10:30:00Z",
                      refs=(tx,), payload={"status": "delivered"}))
        e.append(make("ATTEST", f"k:consumer_{i}", "rep.outcome", f"2026-02-0{i}T11:00:00Z",
                      refs=(tx, "k:merchant_bibimbap"),
                      payload={"result": "positive", "context": CTX}))
    return e


def disputed_tx_4(events: list[Event]) -> list[Event]:
    """Append a FOURTH transaction that goes wrong, then a governed dispute.

    Nothing already in the log is mutated — governance only adds events
    (authority-and-conflict §5). The same folds, re-run, yield new views.
    """
    tx = "tx_4"
    events.append(make("ATTEST", "k:merchant_bibimbap", "commerce.offer", "2026-03-01T10:00:00Z",
                       refs=(tx, "k:merchant_bibimbap"),
                       payload={"item": "vegetable bibimbap", "price_krw": 9800, "context": CTX}))
    events.append(make("AUTHORIZE", "k:consumer_4", "consent.approval", "2026-03-01T10:01:00Z",
                       refs=(tx, "k:merchant_bibimbap"),
                       scope={"max_total_krw": 15000}, payload={"approved_total_krw": 12300}))
    events.append(make("ATTEST", "k:consumer_4", "commerce.payment_result", "2026-03-01T10:02:00Z",
                       refs=(tx,), payload={"status": "confirmed", "amount_krw": 12300}))
    # paid, but never fulfilled -> consumer opens a dispute (CHALLENGE) ...
    events.append(make("CHALLENGE", "k:consumer_4", "dispute.open", "2026-03-01T12:00:00Z",
                       refs=(tx, "k:merchant_bibimbap"),
                       payload={"reason": "paid but not delivered"}))
    # negative outcome signal attached to the same context
    events.append(make("ATTEST", "k:consumer_4", "rep.outcome", "2026-03-01T12:05:00Z",
                       refs=(tx, "k:merchant_bibimbap"),
                       payload={"result": "negative", "context": CTX}))
    # ... and the community renders a decision (ADJUDICATE) — the ONLY event
    # that can change commons standing.
    events.append(make("ADJUDICATE", "k:community", "gov.suspension", "2026-03-03T09:00:00Z",
                       refs=(tx, "k:merchant_bibimbap"),
                       payload={"finding": "non-fulfillment after payment", "duration_days": 30}))
    return events


def override_against_warning(events: list[Event]) -> list[Event]:
    """Append a transaction where a projection raises a friction warning and the
    human approves anyway — recorded as `AUTHORIZE.contrary_to`, not a new type.

    Shows four canon points at once:
      * a projection can raise an advisory warning / friction signal;
      * a human may accept that risk over their *own* action and approve anyway;
      * the record is the existing `AUTHORIZE` event's `contrary_to` field;
      * this override changes NO commons standing — no `ADJUDICATE` is added, so
        the new merchant's governance standing stays `in_good_standing`.
    """
    tx = "tx_5"
    new_merchant = "k:merchant_new"
    # A brand-new merchant with no track record. Anchored by a KEY (cost gate),
    # so it is verifiable — but it has zero outcomes, so the standing fold yields
    # `unproven`: a thin-history / new-entrant friction signal, not a verdict.
    events.append(make("KEY", new_merchant, "id.key_register", "2026-03-10T00:00:00Z",
                       payload={"key": new_merchant, "anchor": "business-registration"}))
    events.append(make("ATTEST", new_merchant, "commerce.offer", "2026-03-10T10:00:00Z",
                       refs=(tx, new_merchant),
                       payload={"item": "vegetable bibimbap", "price_krw": 8900, "context": CTX}))
    # The consumer's agent folds the merchant's standing and surfaces the
    # friction to the human, recording what was shown as an ATTEST (evidence).
    standing = project_merchant_standing(events, new_merchant, CTX)
    warning = make("ATTEST", "k:consumer_1", "risk.advisory", "2026-03-10T10:00:30Z",
                   refs=(tx, new_merchant),
                   payload={"advisory": standing["advisory_signal"], "shown_to_human": True,
                            "reason": "no outcomes from distinct counterparties yet"})
    events.append(warning)
    # The human sees the warning and approves ANYWAY, accepting their own risk.
    # Override is not a type: it is this AUTHORIZE with `contrary_to` set.
    events.append(make("AUTHORIZE", "k:consumer_1", "consent.approval", "2026-03-10T10:01:00Z",
                       refs=(tx, new_merchant), contrary_to=(warning.id,),
                       scope={"max_total_krw": 15000}, payload={"approved_total_krw": 11400}))
    return events


def rotate_merchant_key(events: list[Event]) -> list[Event]:
    """A merchant rotates its signing key. Identity continuity and provenance
    carry-forward are expressed with KEY + ATTEST only — no KEY_ROTATION sixth
    type, no new primitive (event-registry §4.1, §4.6).

    A clean cafe merchant builds standing under `k:cafe_old`, then rotates to
    `k:cafe_new`. The rotation is a KEY `id.key_rotate` event signed by the OLD
    key (proving control) that names the new key. Past events keep referencing
    the old key and stay valid; the new key signs going forward.
    """
    old, new = "k:cafe_old", "k:cafe_new"
    events.append(make("KEY", old, "id.key_register", "2026-04-01T00:00:00Z",
                       payload={"key": old, "anchor": "business-registration"}))
    for i in (1, 2, 3):
        tx = f"tx_cafe_{i}"
        events.append(make("ATTEST", old, "commerce.offer", f"2026-04-0{i}T10:00:00Z",
                           refs=(tx, old),
                           payload={"item": "drip coffee", "price_krw": 4500, "context": CTX}))
        events.append(make("AUTHORIZE", f"k:consumer_{i}", "consent.approval", f"2026-04-0{i}T10:01:00Z",
                           refs=(tx, old), scope={"max_total_krw": 15000},
                           payload={"approved_total_krw": 4500}))
        events.append(make("ATTEST", old, "commerce.fulfillment", f"2026-04-0{i}T10:20:00Z",
                           refs=(tx,), payload={"status": "delivered"}))
        events.append(make("ATTEST", f"k:consumer_{i}", "rep.outcome", f"2026-04-0{i}T11:00:00Z",
                           refs=(tx, old), payload={"result": "positive", "context": CTX}))
    # ROTATE: old key signs a KEY id.key_rotate naming the new key. This both
    # proves control of the old key and anchors the new key (provenance carry).
    # No `nullifies` here: past events stay valid so the chain remains walkable;
    # revoking the old key going forward would be the KEY id.key_revoke /
    # `nullifies` instance, deliberately not applied (event-registry §4.6).
    events.append(make("KEY", old, "id.key_rotate", "2026-04-05T00:00:00Z",
                       refs=(old, new),
                       payload={"old_key": old, "new_key": new, "reason": "scheduled rotation"}))
    # After rotation the NEW key signs going forward.
    events.append(make("ATTEST", new, "commerce.offer", "2026-04-06T10:00:00Z",
                       refs=("tx_cafe_4", new),
                       payload={"item": "drip coffee", "price_krw": 4500, "context": CTX}))
    return events


def revoke_compromised_key(events: list[Event]) -> list[Event]:
    """A bakery merchant's signing key is compromised. The holder had already
    rotated to a fresh key; now the OLD key is revoked so nothing it signs
    *after* the revocation is honored. Revocation is a `KEY` `id.key_revoke`
    whose `nullifies` names the old key's register event — the same KEY type and
    the existing `nullifies` field, no `KEY_REVOKE` sixth type (event-registry
    §4.6).

    Three canon points:
      * revocation is APPENDED, never mutating a prior event;
      * "going forward" is time-scoped: past events by the old key stay readable,
        but anything it signs at/after the revoke timestamp drops out of the fold;
      * the new key, anchored by a rotation that happened BEFORE the revoke, keeps
        its lineage — revoking the old key does not orphan the new one.
    """
    old, new = "k:bakery_old", "k:bakery_new"
    reg = make("KEY", old, "id.key_register", "2026-05-01T00:00:00Z",
               payload={"key": old, "anchor": "business-registration"})
    events.append(reg)
    # Two clean transactions build a little history under the old key.
    for i in (1, 2):
        tx = f"tx_bakery_{i}"
        events.append(make("ATTEST", old, "commerce.offer", f"2026-05-0{i}T09:00:00Z",
                           refs=(tx, old),
                           payload={"item": "sourdough loaf", "price_krw": 7000, "context": CTX}))
        events.append(make("AUTHORIZE", f"k:consumer_{i}", "consent.approval", f"2026-05-0{i}T09:01:00Z",
                           refs=(tx, old), scope={"max_total_krw": 15000},
                           payload={"approved_total_krw": 7000}))
        events.append(make("ATTEST", old, "commerce.fulfillment", f"2026-05-0{i}T09:20:00Z",
                           refs=(tx,), payload={"status": "delivered"}))
        events.append(make("ATTEST", f"k:consumer_{i}", "rep.outcome", f"2026-05-0{i}T10:00:00Z",
                           refs=(tx, old), payload={"result": "positive", "context": CTX}))
    # ROTATE first, while the holder still controls the old key, anchoring `new`.
    events.append(make("KEY", old, "id.key_rotate", "2026-05-04T00:00:00Z",
                       refs=(old, new),
                       payload={"old_key": old, "new_key": new, "reason": "pre-emptive rotation"}))
    # The new key signs going forward — a legitimate post-rotation offer.
    events.append(make("ATTEST", new, "commerce.offer", "2026-05-05T09:00:00Z",
                       refs=("tx_bakery_3", new),
                       payload={"item": "sourdough loaf", "price_krw": 7000, "context": CTX}))
    # REVOKE: the old key is found compromised. The holder, now via the NEW key,
    # appends a KEY id.key_revoke that `nullifies` the old key's register event.
    # Same KEY type + `nullifies`; no sixth type. This is the holder's authority
    # over their own key, not a commons ADJUDICATE (authority-and-conflict §5).
    events.append(make("KEY", new, "id.key_revoke", "2026-05-07T00:00:00Z",
                       refs=(old,), nullifies=(reg.id,),
                       payload={"key": old, "reason": "old key compromised; withdraw forward authority"}))
    # FORGED attempts: whoever holds the leaked old key signs AFTER revocation.
    # verify_log still passes them (valid signature, key was once registered) —
    # the defense is that the FOLD no longer honors them.
    events.append(make("ATTEST", old, "commerce.offer", "2026-05-09T09:00:00Z",
                       refs=("tx_bakery_forged", old),
                       payload={"item": "sourdough loaf", "price_krw": 1000, "context": CTX,
                                "note": "post-revocation; must not be honored"}))
    events.append(make("AUTHORIZE", old, "consent.approval", "2026-05-09T09:01:00Z",
                       refs=("tx_bakery_forged", old), scope={"max_total_krw": 99999},
                       payload={"approved_total_krw": 99999, "note": "post-revocation forgery"}))
    return events


def conflicting_adjudication(events: list[Event]) -> list[Event]:
    """Two valid communities issue CONFLICTING governance rulings about the same
    subject. This is the adversarial probe: it may fail usefully.

    Both KEY roots are valid, both ADJUDICATE events are validly signed, and BOTH
    are present in the ONE shared log — so this is NOT the missing-event
    disagreement of the locality scenario (#4). The information is complete; the
    AUTHORITIES compete. Community A suspends the merchant; community B, reviewing
    the same merchant, issues only a warning. Neither is forged; neither is wrong
    in its own context.

    The five types REPRESENT the conflict (two ADJUDICATE events). They do not
    RESOLVE it: folding all gov.* together silently keeps the latest by timestamp
    — an accident, not a principle. Selecting which authority governs needs a
    policy outside the canon (authority-and-conflict §5: no single final authority
    by design). No sixth type is added, because the gap is not a type gap.
    """
    subject = "k:merchant_contested"
    a, b = "k:community_a", "k:community_b"
    events.append(make("KEY", a, "id.key_register", "2026-06-01T00:00:00Z",
                       payload={"key": a, "anchor": "community-charter"}))
    events.append(make("KEY", b, "id.key_register", "2026-06-01T00:01:00Z",
                       payload={"key": b, "anchor": "community-charter"}))
    events.append(make("KEY", subject, "id.key_register", "2026-06-01T00:02:00Z",
                       payload={"key": subject, "anchor": "business-registration"}))
    # Community A reviews a dispute and SUSPENDS (its commons ruling).
    events.append(make("ADJUDICATE", a, "gov.suspension", "2026-06-02T09:00:00Z",
                       refs=(subject,),
                       payload={"finding": "unresolved fulfillment complaints", "authority": a}))
    # Community B reviews the SAME merchant and issues only a WARNING (later ts,
    # so a naive whole-log fold would silently let B win — by accident).
    events.append(make("ADJUDICATE", b, "gov.warning", "2026-06-02T15:00:00Z",
                       refs=(subject,),
                       payload={"finding": "minor, first offense", "authority": b}))
    return events


def delegate_authority(events: list[Event]) -> list[Event]:
    """Probe: express DELEGATED authority with the existing canon only —
    AUTHORIZE `consent.mandate` + `scope` (+ expiry in scope) + `nullifies` — with
    no sixth type (CANONICAL_TYPES is untouched; no CAPABILITY / DELEGATE /
    AUTHORITY_TOKEN). A human delegates a scoped, time-bounded mandate to Agent A;
    A sub-delegates a narrower mandate to Agent B; B then attempts to grant Agent C.

    event-registry §4.3 already calls a mandate the SAME AUTHORIZE primitive with a
    wider scope. Redelegation is a scope flag; revocation is the existing
    `nullifies` field (§4.6). Each agent has its own anchored KEY (it can sign);
    the mandate is the separate grant of authority to act on the human's behalf.
    """
    P, A, B, C = "k:human_principal", "k:agent_a", "k:agent_b", "k:agent_c"
    for k, anchor, ts in ((P, "payment-account", "2026-06-10T00:00:00Z"),
                          (A, "agent-key", "2026-06-10T00:01:00Z"),
                          (B, "agent-key", "2026-06-10T00:02:00Z"),
                          (C, "agent-key", "2026-06-10T00:03:00Z")):
        events.append(make("KEY", k, "id.key_register", ts, payload={"key": k, "anchor": anchor}))
    # human -> A: a scoped, time-bounded, REDELEGATABLE food mandate.
    m1 = make("AUTHORIZE", P, "consent.mandate", "2026-06-11T00:00:00Z",
              refs=(A, P), scope={"category": "food", "max_total_krw": 50000,
                                  "expires_at": "2026-09-01T00:00:00Z", "redelegatable": True},
              payload={"delegator": P, "delegate": A})
    # human -> A: a SECOND, separate mandate (stationery) — for partial revocation.
    m_st = make("AUTHORIZE", P, "consent.mandate", "2026-06-11T00:05:00Z",
                refs=(A, P), scope={"category": "stationery", "max_total_krw": 10000,
                                    "expires_at": "2026-09-01T00:00:00Z", "redelegatable": False},
                payload={"delegator": P, "delegate": A})
    # A -> B: a NARROWER, NON-redelegatable sub-mandate (within A's food grant).
    m2 = make("AUTHORIZE", A, "consent.mandate", "2026-06-12T00:00:00Z",
              refs=(B, A), scope={"category": "food", "max_total_krw": 20000,
                                  "expires_at": "2026-09-01T00:00:00Z", "redelegatable": False},
              payload={"delegator": A, "delegate": B})
    # B -> C: the ATTEMPT. A validly signed AUTHORIZE, but B's mandate forbade
    # redelegation — so the fold REPRESENTS this event yet will not HONOR it.
    m3 = make("AUTHORIZE", B, "consent.mandate", "2026-06-13T00:00:00Z",
              refs=(C, B), scope={"category": "food", "max_total_krw": 10000,
                                  "expires_at": "2026-09-01T00:00:00Z", "redelegatable": False},
              payload={"delegator": B, "delegate": C})
    events += [m1, m_st, m2, m3]
    # PARTIAL revocation: withdraw ONLY the stationery mandate (its id in
    # `nullifies`). An ordinary AUTHORIZE carrying the FIELD, not a revoke type
    # (§4.6); `consent.withdraw` is an open-namespace predicate (§2.1, §6).
    events.append(make("AUTHORIZE", P, "consent.withdraw", "2026-08-05T00:00:00Z",
                       refs=(A, P), nullifies=(m_st.id,),
                       payload={"reason": "no longer delegating stationery purchases"}))
    # DOWNSTREAM revocation: later, withdraw A's food mandate (nullifies m1). This
    # is what collapses B's sub-authority, since B's chain ran through m1.
    events.append(make("AUTHORIZE", P, "consent.withdraw", "2026-08-10T00:00:00Z",
                       refs=(A, P), nullifies=(m1.id,),
                       payload={"reason": "revoke Agent A's food authority"}))
    return events


def agent_multiplication(events: list[Event]) -> list[Event]:
    """Probe: agent multiplication / root collapse / agent-level Sybil
    amplification. One actor can run many agents; many signatures need not mean
    many independent counterparties. Adds NO new type, NO agent type, NO global
    one-human-one-agent rule, NO stored identity graph, NO cost gate.

    Two clusters each post three inflating `rep.outcome` ATTESTs at a target:
      * HONEST cluster — three agents whose root VOLUNTARILY discloses control of
        them via an ATTEST `id.controls`. The root-aware fold collapses them to
        one principal, deflating the inflated signal.
      * SYBIL cluster — three agents held by one HIDDEN actor that discloses
        nothing. The canon cannot prove they share a root, so the collapse never
        fires and the inflated signal stands.

    The asymmetry IS the finding: voluntary disclosure penalizes the honest and is
    simply omitted by the attacker.
    """
    root, da1, da2, da3 = "k:root_owner", "k:agent_d1", "k:agent_d2", "k:agent_d3"
    ha1, ha2, ha3 = "k:agent_h1", "k:agent_h2", "k:agent_h3"
    shop_d, shop_h = "k:shop_disclosed", "k:shop_hidden"
    # KEY registers. ARC enforces NO cost here, so spinning up keys is free —
    # that freeness is exactly what makes the farm cheap (the absent cost gate).
    for k, anchor, ts in (
        (root, "payment-account", "2026-06-15T00:00:00Z"),
        (da1, "agent-key", "2026-06-15T00:01:00Z"),
        (da2, "agent-key", "2026-06-15T00:02:00Z"),
        (da3, "agent-key", "2026-06-15T00:03:00Z"),
        (ha1, "agent-key", "2026-06-15T00:04:00Z"),
        (ha2, "agent-key", "2026-06-15T00:05:00Z"),
        (ha3, "agent-key", "2026-06-15T00:06:00Z"),
    ):
        events.append(make("KEY", k, "id.key_register", ts, payload={"key": k, "anchor": anchor}))
    # HONEST disclosure: the root signs ONE ATTEST id.controls naming its agents.
    # Open-namespace predicate (event-registry §6); no new type. This is the
    # moment the actor crosses ARC's event horizon and becomes collapsible.
    events.append(make("ATTEST", root, "id.controls", "2026-06-15T01:00:00Z",
                       refs=(da1, da2, da3),
                       payload={"note": "voluntary disclosure of common control"}))
    # Both clusters pump three positive outcomes at their target, in a tight burst.
    for agent, ts in ((da1, "2026-06-20T10:00:00Z"), (da2, "2026-06-20T10:05:00Z"),
                      (da3, "2026-06-20T10:10:00Z")):
        events.append(make("ATTEST", agent, "rep.outcome", ts, refs=("tx_pump_d", shop_d),
                           payload={"result": "positive", "context": CTX}))
    for agent, ts in ((ha1, "2026-06-21T10:00:00Z"), (ha2, "2026-06-21T10:05:00Z"),
                      (ha3, "2026-06-21T10:10:00Z")):
        events.append(make("ATTEST", agent, "rep.outcome", ts, refs=("tx_pump_h", shop_h),
                           payload={"result": "positive", "context": CTX}))
    return events


# ---------------------------------------------------------------------------
# 5. Run the probe: project before, then after the governed dispute.
# ---------------------------------------------------------------------------

def show(label: str, events: list[Event]) -> None:
    verify_log(events)  # replay: signatures + key provenance, before any fold
    print(f"\n{'=' * 66}\n{label}  ({len(events)} events in log)\n{'=' * 66}")
    standing = project_merchant_standing(events, "k:merchant_bibimbap", CTX)
    print("merchant standing  :", json.dumps(standing["evidence"]))
    print("  advisory signal   :", standing["advisory_signal"], "(risk signal — may raise friction, may not punish)")
    print("  governance standing:", standing["governance_standing"], "(commons fact — ADJUDICATE-only)")
    print("identity status     :", project_identity_status(events, "k:merchant_bibimbap"))
    print("tx_4 state          :", project_transaction_state(events, "tx_4"))


def show_override(events: list[Event]) -> None:
    verify_log(events)  # same replay discipline before folding
    print(f"\n{'=' * 66}\nOVERRIDE — human approves a new merchant against a warning"
          f"  ({len(events)} events in log)\n{'=' * 66}")
    standing = project_merchant_standing(events, "k:merchant_new", CTX)
    print("new merchant advisory   :", standing["advisory_signal"], "(friction signal shown to the human)")
    print("new merchant governance :", standing["governance_standing"], "(unchanged — no ADJUDICATE was added)")
    ov = project_overrides(events, "tx_5")
    print("override_detected       :", ov["override_detected"])
    for o in ov["approvals_contrary_to_warning"]:
        print(f"  approval {o['approval']} by {o['approver']}")
        for w in o["overridden_warnings"]:
            print(f"    contrary_to {w['warning']}  (advisory={w['advisory']}, reason={w['reason']})")


def community_view(events: list[Event], name: str) -> list[Event]:
    """Two communities hold different subsets of the same log.

    No new mechanism — just the observation that, under locality, not every
    community receives every event. Community A holds the full log. Community B
    received everything EXCEPT the suspension `ADJUDICATE` on the bibimbap
    merchant (the commons ruling never propagated to it). The demo does not say
    which subset is "right".
    """
    if name == "A":
        return list(events)
    if name == "B":
        return [
            e for e in events
            if not (e.type == "ADJUDICATE" and e.predicate == "gov.suspension"
                    and "k:merchant_bibimbap" in e.refs)
        ]
    raise ValueError(name)


def show_event_set_disagreement(events: list[Event]) -> None:
    merchant = "k:merchant_bibimbap"
    print(f"\n{'=' * 66}\nEVENT-SET DISAGREEMENT — same merchant, two event subsets"
          f"\n{'=' * 66}")
    for name in ("A", "B"):
        view = community_view(events, name)
        verify_log(view)  # each subset replays correctly ON ITS OWN
        st = project_merchant_standing(view, merchant, CTX)
        ident = project_identity_status(view, merchant)
        print(f"Community {name}: holds {len(view)} events")
        print(f"  advisory={st['advisory_signal']}  "
              f"governance={st['governance_standing']}  identity={ident}")


def show_key_rotation(events: list[Event]) -> None:
    old, new = "k:cafe_old", "k:cafe_new"
    verify_log(events)  # the rotated new key passes provenance via the old key
    lin = project_identity_lineage(events, new)
    print(f"\n{'=' * 66}\nKEY ROTATION / IDENTITY CONTINUITY — old key -> new key"
          f"\n{'=' * 66}")
    print("provenance chain        :", " -> ".join(lin["chain"]),
          f"({lin['rotations']} rotation)")
    # Existing single-key folds, UNCHANGED:
    so = project_merchant_standing(events, old, CTX)
    sn = project_merchant_standing(events, new, CTX)
    print(f"existing fold, old key  : advisory={so['advisory_signal']:<8} "
          f"identity={project_identity_status(events, old)}  (its history)")
    print(f"existing fold, new key  : advisory={sn['advisory_signal']:<8} "
          f"identity={project_identity_status(events, new)}  (a stranger if the link is ignored)")
    # One carry-forward reading, via the rotation chain:
    ls = project_lineage_standing(events, new, CTX)
    print(f"lineage fold,  new key  : advisory={ls['advisory_signal']:<8} "
          f"identity={ls['identity_continuity']}  (history carried forward via KEY id.key_rotate)")


def show_key_revocation(events: list[Event]) -> None:
    old, new = "k:bakery_old", "k:bakery_new"
    verify_log(events)  # the full log still verifies; revocation is a fold policy
    print(f"\n{'=' * 66}\nKEY REVOCATION — a compromised old key withdrawn going forward"
          f"\n{'=' * 66}")
    a_old = project_key_authority(events, old)
    a_new = project_key_authority(events, new)
    print(f"old key authority   : registered={a_old['registered']} revoked={a_old['revoked']} "
          f"(at {a_old['revoked_at']})  honored_going_forward={a_old['honored_going_forward']}")
    print(f"new key authority   : registered={a_new['registered']} revoked={a_new['revoked']}"
          f"                       honored_going_forward={a_new['honored_going_forward']}")
    # Past history of the old key is still readable (events before the revoke):
    st_old = project_merchant_standing(events, old, CTX)
    print("old key past history:", json.dumps(st_old["evidence"]), "(pre-revoke events still fold)")
    # Forged post-revocation events are present in the log but NOT honored:
    act = active(events)
    forged = [e for e in events if "tx_bakery_forged" in e.refs]
    honored = [e for e in forged if e in act]
    print(f"forged post-revoke  : {len(forged)} in log, {len(honored)} honored by the fold")
    print("  tx_bakery_forged state:", project_transaction_state(events, "tx_bakery_forged"),
          "(its forged offer/approval were dropped -> never leaves intent)")
    # The new key lineage is intact because the rotation preceded the revoke:
    lin = project_identity_lineage(events, new)
    ls = project_lineage_standing(events, new, CTX)
    print("new key lineage     :", " -> ".join(lin["chain"]),
          f"(advisory={ls['advisory_signal']}, identity={ls['identity_continuity']} — history carried)")


def show_replay_cache(events: list[Event]) -> None:
    """Caching is not in the canon — it is a derived-data hazard. This probe asks
    whether caching a projection re-introduces the stored profile/score/status
    object the model refuses to keep (object-model §10). No event is added."""
    subject, ctx = "k:merchant_bibimbap", CTX
    print(f"\n{'=' * 66}\nREPLAY COST / PROJECTION CACHE — does caching re-create a profile?"
          f"\n{'=' * 66}")
    act = active(events)
    live_hash = event_set_hash(act)
    # The authoritative answer: a fold computed by replay, kept by nobody.
    standing = project_merchant_standing(events, subject, ctx)
    result = {"advisory_signal": standing["advisory_signal"],
              "governance_standing": standing["governance_standing"]}
    print(f"live event set      : {live_hash}  ({len(act)} active events)")
    print(f"authoritative fold  : advisory={result['advisory_signal']} "
          f"governance={result['governance_standing']}  (recomputed, not stored)")

    # Three cache shapes wrapping that same result.
    ephemeral = {"name": "ephemeral", "durable": False, "event_set_hash": live_hash,
                 "authoritative": False, "computed_at": "2026-06-04T00:00:00Z", "result": result}
    durable_unbound = {"name": "durable-unbound", "durable": True, "event_set_hash": None,
                       "authoritative": True, "computed_at": "2026-06-04T00:00:00Z",
                       "result": {"advisory_signal": "trusted", "governance_standing": "in_good_standing"}}
    receipt = {"name": "event-bound-receipt", "durable": True, "event_set_hash": live_hash,
               "authoritative": False, "projection_name": "merchant_standing", "subject": subject,
               "context": ctx, "computed_at": "2026-06-04T00:00:00Z", "result": result}
    shapes = (ephemeral, durable_unbound, receipt)

    print("\nclassification (against the live event set):")
    for c in shapes:
        s = project_cache_safety(c, live_hash)
        print(f"  {s['cache']:<20} -> {s['classification']:<26} "
              f"event_bound={str(s['event_bound']):<5} reusable_as_hint={s['reusable_as_hint']}")

    # CHANGED event set: drop the suspension ADJUDICATE (locality view B). Its
    # hash differs, so any event-bound cache must self-invalidate.
    changed = active(community_view(events, "B"))
    changed_hash = event_set_hash(changed)
    print(f"\nchanged event set   : {changed_hash}  ({len(changed)} active; suspension ADJUDICATE absent)")
    print("re-check against the CHANGED set:")
    for c in shapes:
        s = project_cache_safety(c, changed_hash)
        verdict = ("self-invalidates -> recompute" if s["event_bound"]
                   else "cannot detect the change -> serves stale")
        print(f"  {s['cache']:<20} -> event_bound={str(s['event_bound']):<5} "
              f"matches_live={str(s['matches_live_event_set']):<5} {verdict}")

    # The hazard, made explicit: the durable-unbound cache cannot even notice the
    # change, and it is never authority over an ADJUDICATE.
    print("\ndurable-unbound read WITHOUT replay (the hazard):")
    print(f"  it serves its stored {durable_unbound['result']} to ANY caller,")
    print("  detached from the event set — a profile/score object by another name.")
    print(f"  yet the authoritative fold says governance={result['governance_standing']}: the cache")
    print("  cannot override the ADJUDICATE. Cache never changes commons standing.")


def show_conflicting_adjudication(events: list[Event]) -> None:
    """Adversarial probe: two valid authorities disagree on the same subject."""
    subject = "k:merchant_contested"
    a, b = "k:community_a", "k:community_b"
    verify_log(events)  # both community roots valid; both rulings validly signed
    print(f"\n{'=' * 66}\nCONFLICTING ADJUDICATE — two valid authorities, one subject"
          f"\n{'=' * 66}")
    # The naive whole-log fold folds ALL gov.* together -> last by timestamp wins.
    naive = project_merchant_standing(events, subject, CTX)["governance_standing"]
    print(f"naive whole-log fold : governance={naive}  (kept the latest ADJUDICATE by timestamp — an accident)")
    # Authority-scoped folds: each community's ruling read on its own.
    va = project_authority_context(events, subject, a)
    vb = project_authority_context(events, subject, b)
    print(f"under authority A    : governance={va['governance_standing']:<14} rulings={va['rulings']}  ({a})")
    print(f"under authority B    : governance={vb['governance_standing']:<14} rulings={vb['rulings']}  ({b})")
    conf = project_conflicting_governance(events, subject, [a, b])
    print(f"conflict detected    : {conf['conflict']}   canonical_winner={conf['canonical_winner']}")
    print(f"resolution requires  : {conf['resolution_requires']}")


def show_resolution_policies(events: list[Event]) -> None:
    """The same scenario-8 conflict, resolved by several illustrative reader
    policies — all OUTSIDE the canon, none endorsed by ARC."""
    subject = "k:merchant_contested"
    a, b = "k:community_a", "k:community_b"
    short = {a: "A", b: "B"}
    verify_log(events)  # same valid, replaying log as scenario 8 — nothing added
    print(f"\n{'=' * 66}\nILLUSTRATIVE RESOLUTION POLICIES — same conflict, reader's choice"
          f"\n{'=' * 66}")
    conf = project_conflicting_governance(events, subject, [a, b])
    print(f"unresolved (canon)   : by_authority={conf['by_authority']}  canonical_winner={conf['canonical_winner']}")
    print("\nillustrative reader policies (EXAMPLES ONLY — ARC endorses none):")
    rows = []
    for sub in (a, b):
        rows.append((f"subscriber-choice (subscribes to {sub})",
                     resolve_by_subscriber_choice(events, subject, sub)))
    rows.append(("most-restrictive-wins (safety-biased)",
                 resolve_by_most_restrictive(events, subject, [a, b])))
    for order in ([a, b], [b, a]):
        rows.append((f"explicit-precedence (order {'>'.join(short[x] for x in order)})",
                     resolve_by_explicit_precedence(events, subject, order)))
    for label, r in rows:
        print(f"  {label:<47} -> {r['resolved_standing']:<14} honors {r['honored_authority']}")


def show_delegated_authority(events: list[Event]) -> None:
    """Probe: can delegated authority live in AUTHORIZE + scope + expiry +
    `nullifies`, with no sixth type? Human -> Agent A -> Agent B (-> Agent C?)."""
    P, A, B, C = "k:human_principal", "k:agent_a", "k:agent_b", "k:agent_c"
    verify_log(events)  # all agent keys anchored; every mandate validly signed
    print(f"\n{'=' * 66}\nDELEGATED AUTHORITY — human -> Agent A -> Agent B (-> Agent C?)"
          f"\n{'=' * 66}")
    food = lambda amt: {"category": "food", "max_total_krw": amt}
    stat = lambda amt: {"category": "stationery", "max_total_krw": amt}
    t0, after_r1, after_r2 = ("2026-07-01T00:00:00Z", "2026-08-07T00:00:00Z",
                              "2026-08-15T00:00:00Z")
    base = as_of(events, t0)         # before any revocation
    mid = as_of(events, after_r1)    # stationery mandate revoked
    current = events                 # full current log; A's food mandate revoked too

    def q(label: str, agent: str, needed: dict, at_time: str, evset: list[Event]) -> None:
        r = project_delegated_authority(evset, agent, needed, at_time, P)
        chain = " -> ".join(s.split(":", 1)[1] for s in r["chain"]) if r["chain"] else "—"
        print(f"  {label:<52} {'AUTHORIZED' if r['authorized'] else 'denied':<10} "
              f"[{chain}]  {r['reason']}")

    print("scope-bounded (human -> A: food <= 50000):")
    q("A food 30000 (within scope)", A, food(30000), t0, base)
    q("A food 80000 (over budget)", A, food(80000), t0, base)
    q("A electronics 30000 (wrong category)", A,
      {"category": "electronics", "max_total_krw": 30000}, t0, base)
    print("time-bounded (mandate expires 2026-09-01):")
    q("A food 30000 at 2026-10-01 (expired)", A, food(30000), "2026-10-01T00:00:00Z", base)
    print("sub-delegation (A -> B: food <= 20000, redelegatable=False):")
    q("B food 15000 (within sub-scope)", B, food(15000), t0, base)
    q("B food 30000 (over A's grant to B)", B, food(30000), t0, base)
    print("no-redelegation (B tries to grant C):")
    q("C food 10000 via B's grant", C, food(10000), t0, base)
    print("partial revocation (human withdraws ONLY the stationery mandate):")
    q("A food 30000 (food mandate intact)", A, food(30000), after_r1, mid)
    q("A stationery 5000 (mandate withdrawn)", A, stat(5000), after_r1, mid)
    print("historical authority baseline (EARLIER event subset; before the revoke):")
    q("B food 15000 at 2026-07-01", B, food(15000), t0, base)
    print("current mandate force (FULL CURRENT LOG; after the revoke):")
    q("A food 30000 (mandate withdrawn)", A, food(30000), after_r2, current)
    q("B food 15000 (upstream chain broken)", B, food(15000), after_r2, current)
    print("  These are different event sets and two authority-state questions, not two")
    print("  policy answers about one completed act. No completed act event is emitted here;")
    print("  preserve/cascade honoring is isolated in authority-revocation-demo.")


def show_agent_multiplication(events: list[Event]) -> None:
    """Probe: many agents, one actor — can the canon collapse the influence?"""
    shop_d, shop_h = "k:shop_disclosed", "k:shop_hidden"
    verify_log(events)  # every agent key anchored; every outcome validly signed
    print(f"\n{'=' * 66}\nAGENT MULTIPLICATION — many agents, one actor (Sybil amplification)"
          f"\n{'=' * 66}")
    dr = project_merchant_standing(events, shop_d, CTX)
    hr = project_merchant_standing(events, shop_h, CTX)
    print("naive fold (distinct signers, no root awareness):")
    print(f"  disclosed-cluster target : advisory={dr['advisory_signal']:<8} "
          f"raters={dr['evidence']['distinct_counterparties']}  (3 agents -> looks trusted)")
    print(f"  hidden-cluster   target  : advisory={hr['advisory_signal']:<8} "
          f"raters={hr['evidence']['distinct_counterparties']}  (3 agents -> looks trusted)")
    dc = project_merchant_standing_root_aware(events, shop_d, CTX)
    hc = project_merchant_standing_root_aware(events, shop_h, CTX)
    print("root-aware fold (collapse raters to their DISCLOSED root):")
    print(f"  disclosed-cluster target : advisory={dc['advisory_signal']:<8} "
          f"principals={dc['distinct_principals']} (collapsed {dc['collapsed']})  -> influence DEFLATED")
    print(f"  hidden-cluster   target  : advisory={hc['advisory_signal']:<8} "
          f"principals={hc['distinct_principals']} (collapsed {hc['collapsed']})  -> NOT deflated")
    print("asymmetry:")
    for k, v in project_root_collapse_summary(events, shop_d, shop_h, CTX).items():
        print(f"  {k:<52} = {v}")
    sd = project_correlation_suspicion(events, shop_d, CTX)
    sh = project_correlation_suspicion(events, shop_h, CTX)
    print("exit C — local probabilistic review trigger (no penalty, fallible):")
    print(f"  disclosed-cluster target : undisclosed_raters={sd['undisclosed_raters']} "
          f"review_suggested={sd['review_suggested']}  (disclosed -> not a hidden burst)")
    print(f"  hidden-cluster   target  : undisclosed_raters={sh['undisclosed_raters']} "
          f"review_suggested={sh['review_suggested']}  (burst smell -> review, not a verdict)")


def main() -> None:
    log = base_log()
    show("BEFORE — three clean transactions", log)

    log = disputed_tx_4(log)
    show("AFTER  — tx_4 disputed (CHALLENGE) and adjudicated (ADJUDICATE)", log)

    print(f"\n{'-' * 66}")
    print("What changed, and how:")
    print("  * Same fold functions, same merchant, same context — only the log grew.")
    print("  * advisory_signal moved (a negative outcome + an open dispute entered the fold).")
    print("  * governance_standing -> suspended ONLY because an ADJUDICATE was added;")
    print("    no projection and no ordinary key could have produced that effect.")
    print("  * identity status -> suspended, tx_4 state -> resolved: all recomputed,")
    print("    never stored. Verification was replay over signed events throughout.")

    log = override_against_warning(log)
    show_override(log)

    print(f"\n{'-' * 66}")
    print("What this override shows:")
    print("  * The projection raised a friction signal (advisory=unproven); the human")
    print("    saw it and approved anyway, over their OWN risk.")
    print("  * That approval is a plain AUTHORIZE with contrary_to set — NOT a new type.")
    print("  * The new merchant's governance standing stayed in_good_standing: an")
    print("    override grants no commons authority; only an ADJUDICATE could change it.")
    print("  * Re-folding later still surfaces override_detected=True from the immutable")
    print("    event, so the accepted-risk fact is auditable without any stored flag.")

    show_event_set_disagreement(log)

    print(f"\n{'-' * 66}")
    print("What this disagreement shows (observation, not a verdict):")
    print("  * Both communities replayed correctly: each subset passes signature and")
    print("    provenance checks on its own. Neither view is corrupt or forged.")
    print("  * They still disagree — B never received the suspension ADJUDICATE, so it")
    print("    reads the merchant as in_good_standing / verified while A reads suspended.")
    print("  * 'Verification is replay' guarantees agreement only over a SHARED event set;")
    print("    a different replay input is a different — still valid — projection.")
    print("  * The demo does not resolve this. Divergent views may be an error to")
    print("    reconcile OR the expected result of locality. ARC does not force one here.")

    log = rotate_merchant_key(log)
    show_key_rotation(log)

    print(f"\n{'-' * 66}")
    print("What this rotation shows (continuity is expressible, policy is not forced):")
    print("  * The new key is anchored by the old key's signed KEY id.key_rotate —")
    print("    provenance carries forward with no external cost gate and no sixth type.")
    print("  * Existing single-key folds are UNCHANGED: the old key still reads its")
    print("    history; the new key alone reads as a stranger (unproven / unverified).")
    print("  * Continuity is recovered by reading the KEY rotation chain. A lineage fold")
    print("    then inherits the old standing — but that is ONE policy (full carry-forward).")
    print("  * Partial carry, standing-only, or no auto-carry are all expressible by what")
    print("    the lineage fold counts. The demo links the identities; it picks no policy.")

    log = revoke_compromised_key(log)
    show_key_revocation(log)

    print(f"\n{'-' * 66}")
    print("What this revocation shows (no sixth type; same `nullifies` field):")
    print("  * Revocation is a KEY id.key_revoke whose `nullifies` names the old key's")
    print("    register event — appended, never mutating any prior event.")
    print("  * 'Going forward' is time-scoped: the old key's past events stay readable, but")
    print("    anything it signs AT/AFTER the revoke timestamp drops out of the fold. The")
    print("    two forged post-revoke events verify (valid signature) yet are not honored.")
    print("  * The new key keeps its lineage because the rotation preceded the revoke —")
    print("    revoking the old key did not orphan the new one. Had the rotation come after,")
    print("    the old key's rotation event would itself fall after the cutoff and drop out.")

    show_replay_cache(log)

    print(f"\n{'-' * 66}")
    print("What this cache probe shows (caching is allowed, but only one shape is safe):")
    print("  * Caching is NOT in the canon and adds no event type — it is derived data.")
    print("    The question is whether a cache quietly becomes the stored profile/score/")
    print("    status object the model refuses to keep (object-model §10).")
    print("  * An ephemeral cache (scoped to one replay, discarded) is a safe optimization.")
    print("  * A durable cache with NO event_set_hash is profile-like reintroduction: it is")
    print("    read without replay, cannot notice the event set change, and detaches from")
    print("    the log — a score/status store by another name.")
    print("  * An event-bound receipt (event_set_hash + projection + subject + context +")
    print("    computed_at) is conditionally safe: reusable only as a HINT while its hash")
    print("    matches the live set; it self-invalidates the instant the events change.")
    print("  * No cache is authority: even the durable one asserting in_good_standing cannot")
    print("    override the ADJUDICATE — the authoritative fold still reads suspended.")

    log = conflicting_adjudication(log)
    show_conflicting_adjudication(log)

    print(f"\n{'-' * 66}")
    print("What this conflict shows (the probe finds a LIMIT — honestly):")
    print("  * Not the locality case (#4): no event is missing. BOTH ADJUDICATE rulings are")
    print("    in the one shared log, both validly signed, both replay. The issue is not")
    print("    missing information — it is two communities claiming authority at once.")
    print("  * The five types REPRESENT the conflict fine: each ruling is an ordinary")
    print("    ADJUDICATE. No sixth type is needed (or added) to record competing rulings.")
    print("  * But the five types do NOT RESOLVE it. The naive whole-log fold returns one")
    print("    answer only by keeping the latest ruling by timestamp — an accident, not a")
    print("    principle. Scope by authority and there are two valid, conflicting answers.")
    print("  * ARC does not auto-pick a winner (canonical_winner=None). Choosing one needs")
    print("    an authority-selection / federation / bridge rule or a human-community choice")
    print("    — a policy OUTSIDE the event canon. This is an authority-policy gap, NOT an")
    print("    event-type gap: adding a sixth type would not tell you which authority wins.")

    show_resolution_policies(log)

    print(f"\n{'-' * 66}")
    print("What these policies show (the gap is real; it just isn't an event-type gap):")
    print("  * The SAME conflicting log resolves to different standings under different")
    print("    reader policies — suspended under one, warned under another — all valid.")
    print("  * Resolution happened entirely in the POLICY layer, reading the per-authority")
    print("    projections; the events were untouched and NO sixth type was added.")
    print("  * ARC endorses none of them. subscriber-choice, most-restrictive-wins, and")
    print("    explicit-precedence just illustrate that the choice belongs to a reader /")
    print("    community / federation / bridge rule — not to the canon.")
    print("  * This does NOT dissolve scenario 8's limit: the canon still cannot pick a")
    print("    winner, and a sixth event type still would not say whose ruling is right.")

    log = delegate_authority(log)
    show_delegated_authority(log)

    print(f"\n{'-' * 66}")
    print("What this delegation probe shows (no sixth type; AUTHORIZE + scope + `nullifies`):")
    print("  * Delegation is an ordinary AUTHORIZE consent.mandate carrying a scope (category")
    print("    + budget), an expiry, and a redelegatable flag — event-registry §4.3 already")
    print("    calls a mandate the same AUTHORIZE primitive with a wider scope. CANONICAL_TYPES")
    print("    is unchanged; no CAPABILITY / DELEGATE / AUTHORITY_TOKEN was added.")
    print("  * The fold walks the mandate chain back to the human principal, whose authority")
    print("    over their own action is inherent (authority-and-conflict §3) and needs no")
    print("    upstream grant. Scope- and time-bounds are ENFORCED in the fold: over-budget,")
    print("    wrong-category, and expired requests are denied; a sub-grant may only narrow.")
    print("  * No-redelegation is just a scope flag: A->B was issued redelegatable=False, so")
    print("    B's attempt to grant C is REPRESENTED (a valid AUTHORIZE) but NOT HONORED.")
    print("  * Revocation is the existing `nullifies` field: withdrawing ONE of A's mandates")
    print("    leaves the others intact (partial revocation), and withdrawing A's food mandate")
    print("    collapses B's downstream authority — B's chain no longer reaches the principal.")
    print("  * The earlier subset establishes only a historical authority baseline; the full")
    print("    current log establishes that A's mandate and B's downstream authority are no")
    print("    longer in force. This scenario emits no completed B act, so it makes no claim")
    print("    about current honoring. The same-full-log preserve/cascade comparison lives in")
    print("    authority-revocation-demo. That residue is policy, not a missing event type.")

    log = agent_multiplication(log)
    show_agent_multiplication(log)

    print(f"\n{'-' * 66}")
    print("What this multiplication probe shows (event horizon + an honest asymmetry):")
    print("  * ARC's event horizon is the commons boundary. Agents doing only local work")
    print("    sign no commons event and are invisible to ARC; they enter the model only")
    print("    when they sign a commons-visible event (here a rep.outcome ATTEST). The")
    print("    problem is not multiple agents existing — it is unbounded active influence")
    print("    crossing that boundary.")
    print("  * Many signatures need not mean many independent counterparties. The standing")
    print("    fold already down-weights by distinct signer (object-model §8) — but one")
    print("    actor holding many keys defeats that unless the keys can be collapsed.")
    print("  * Collapse needs to KNOW the keys share a root. The canon learns that only")
    print("    from a VOLUNTARY ATTEST id.controls — no new type, no stored identity graph.")
    print("  * So the collapse is asymmetric: the honest cluster that discloses is deflated")
    print("    (trusted -> unproven); the hidden cluster that discloses nothing keeps its")
    print("    inflated signal. Voluntary disclosure penalizes the honest and is simply")
    print("    omitted by the attacker — it is NOT a sufficient Sybil defense.")
    print("  * Three design exits, each a constitutional trade-off OUTSIDE the canon:")
    print("      A. global+certain dedup via a STORED identity graph — stronger collapse,")
    print("         but violates the no-stored-relationship / anti-social-credit discipline.")
    print("      B. global+certain dedup via an external COST GATE on keys — stronger Sybil")
    print("         resistance, but introduces economic exclusion / value or provider")
    print("         dependency (event-registry §10: ARC custodies no value).")
    print("      C. local + PROBABILISTIC behavioral review — fallible, local, review-only,")
    print("         no automatic penalty. This is closest to ARC's existing position.")
    print("  * Honest verdict: ARC does NOT solve agent-level Sybil resistance absolutely.")
    print("    Its position is local + probabilistic + fallible resistance, not global")
    print("    certain dedup. Agent multiplication is REPRESENTABLE; certain resolution")
    print("    would require a constitutional trade-off (A or B) outside the canon.")

    print(f"{'-' * 66}")
    print("Sufficiency: KEY, ATTEST, AUTHORIZE, CHALLENGE, ADJUDICATE + `nullifies`")
    print("covered identity, offer, approval, payment, fulfillment, reputation, dispute,")
    print("governance, override-against-warning (AUTHORIZE.contrary_to), key rotation /")
    print("identity continuity (KEY id.key_rotate + the rotation chain), AND key revocation")
    print("(KEY id.key_revoke + `nullifies`, time-scoped) — no sixth type.")
    print("Caching adds no type but is only safe when scoped or event-bound and never")
    print("authoritative; otherwise it re-introduces the stored profile (object-model §10).")
    print("Conflicting authorities are REPRESENTABLE in the five types but not RESOLVABLE by")
    print("them: selecting the governing authority is a policy gap outside the canon, not a")
    print("missing event type. The probe found a real limit — and did not paper it over.")
    print("That gap is fillable by an OUT-OF-CANON policy layer (illustrated: subscriber-")
    print("choice / most-restrictive-wins / explicit-precedence), ARC endorsing none — which")
    print("confirms it is a policy/federation choice, not a missing event type.")
    print("Delegated authority is REPRESENTABLE on the same canon: AUTHORIZE + scope + expiry")
    print("+ `nullifies` give scoped, time-bounded, non-redelegable, revocable delegation with")
    print("no sixth type. This demo shows historical authority and current mandate force;")
    print("authority-revocation-demo isolates current honoring of completed acts as the")
    print("remaining fold-policy choice, not a missing event type.")
    print("Agent multiplication is REPRESENTABLE too, but exposes a sharper edge: the canon")
    print("can collapse many agents to one principal ONLY when their shared root is")
    print("voluntarily disclosed (ATTEST id.controls), so the collapse penalizes honest")
    print("disclosers while a hidden actor evades it. Certain agent-level Sybil resistance")
    print("would need a stored identity graph or an external cost gate — both constitutional")
    print("trade-offs outside the canon. ARC's honest position is local + probabilistic +")
    print("fallible resistance, not global certain dedup — still no sixth event type.")
    print("(See README for the verdict.)")


if __name__ == "__main__":
    main()
