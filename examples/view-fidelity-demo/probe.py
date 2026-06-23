#!/usr/bin/env python3
"""
ARC view fidelity probe — WYSINWYS: What You See Is Not What You Sign.

Single file, stdlib only, single process.

What this isolates
------------------
A signer is NOT malicious, the key is sound, and the signed canonical bytes B are
NOT tampered with. And yet, if the view-generator / summarizer / UI renderer between
the bytes and the eyes is lossy or adversarial, the view the signer SAW and the bytes
the signer SIGNED diverge.

  > A signature seals the signed bytes. It does not seal the displayed view.
  > Same bytes, different view. deterministic != faithful.

This is NOT a restatement of finding M. M is about the signer reading a mandate it
fully SAW and interpreting it unfaithfully — the failure is in interpretation. Here
the signer reads the mandate faithfully; the failure is one step EARLIER, in the
presentation/render layer: the view that reached the signer is not a faithful
rendering of B. M's signer is omniscient about B and varies in reading; this signer
is BLIND to B and sees only render(B).

Its relation to finding L
-------------------------
L (approval_seam_fixture) said the escalation return path is a second custody surface
and that the inbox owes the human a "sign what you saw" property — one projection used
for both human-review and signer-bytes; show less and you build a confused deputy. But
L's mitigation ASSUMES the projection/renderer is faithful. Bytes are not human-
cognizable (JSON, hashes, addresses), so SOME renderer is unavoidable, and L silently
trusted it. This probe pricks exactly that trust dependency: the renderer L relied on
is itself an unobservable, off-log party whose fidelity ARC cannot witness. So this is
the residue UNDER L's mitigation, not a restatement of it.

The one thing the log can check, and the one it cannot
------------------------------------------------------
ARC can bind a `view_hash` into the signed payload and let anyone recompute it from a
PINNED deterministic renderer. That folds: a careless attacker who shows a doctored
view but commits a hash that the pinned renderer would not produce is CAUGHT. But the
hash proves only CORRESPONDENCE to the pinned renderer's output — never the FIDELITY of
that renderer. A renderer that reproducibly OMITS a critical field is deterministic, its
output hashes consistently, the commitment is honest — and the view is still unfaithful.
deterministic != faithful. The pinned renderer's fidelity is a trust root the hash
cannot reach, and a human's actual perception is below even that.

The six readouts
----------------
  1. boundary            — the log proves B and id=hash(B); it does NOT carry the view.
  2. faithful control    — a faithful renderer shows the critical fields; sign-what-you-
                           saw holds, but ONLY under the faithful-renderer assumption.
  3. WYSINWYS attack     — the same signed action, an adversarial renderer rewrites the
                           payee; the signer sees a benign view and signs malicious B. verify ok.
  4. mitigation (half)   — view_hash commitment catches the CARELESS mismatch
                           (claimed_view_hash != recomputed_view_hash => CAUGHT).
  5. residue             — a careful deterministic renderer omits the field reproducibly;
                           claimed == recomputed, verify passes, view still unfaithful.
  6. mitigation price    — rendered_view ATTEST / signed preview / renderer attestation
                           are more records; they relocate trust into the renderer / a
                           runtime attestor and never prove human perception. (Mirrors
                           M's attested-signer, O's head-oracle, the world-axis oracle.)

Deliberately dirty and small. Explicitly:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519) — the point is the gap between bytes and
    view, not custody. But id and view_hash are REAL content hashes, so the recompute
    check genuinely bites: a careless view mismatch cannot pass for free;
  * the canonical types are reused as-is — no new type, no "view object", no view score.
    A rendered_view attestation is an ordinary ATTEST predicate, not a new primitive;
  * what each signer actually SAW (the view) and whether it was FAITHFUL live in an
    omniscient strip no observer and no fold can read — exactly the gap the probe is about;
  * this is a probe, not a protocol spec and not doctrine.

Run:  python3 probe.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}

# The fields a human MUST see to make an informed approval. The fold never reads this
# (it does not know which fields are semantically critical) — faithfulness is a human
# judgment, computed only in the omniscient strip.
CRITICAL_FIELDS = ("payee", "amount_krw")


# ---------------------------------------------------------------------------
# The Event and its mock signing — the same lean shape as the other probes. The
# canonical bytes B are what gets signed; the rendered view V is NOT in here.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Event:
    id: str
    type: str
    signer: str
    predicate: str
    timestamp: str
    refs: tuple[str, ...] = ()
    nullifies: tuple[str, ...] = ()
    scope: dict[str, Any] | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    def signing_bytes(self) -> bytes:
        body = {
            "type": self.type, "signer": self.signer, "predicate": self.predicate,
            "timestamp": self.timestamp, "refs": self.refs, "nullifies": self.nullifies,
            "scope": self.scope, "payload": self.payload,
        }
        return json.dumps(body, sort_keys=True, default=list).encode()


def stub_sign(signer: str, body: bytes) -> str:
    """MOCK. Real ARC uses Ed25519; a hash stands in so replay still verifies.

    The signature is a function of (signer, bytes). It is honest over WHATEVER bytes B
    were signed — and says nothing at all about the view the signer looked at. The whole
    finding lives in that silence: the signature seals B, never render(B).
    """
    return "stub:" + hashlib.sha256(signer.encode() + body).hexdigest()[:16]


def content_id(body: bytes) -> str:
    return "ev:" + hashlib.sha256(body).hexdigest()[:12]


def make(type_: str, signer: str, predicate: str, ts: str, **kw) -> Event:
    assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r} — forbidden"
    partial = Event(id="", type=type_, signer=signer, predicate=predicate, timestamp=ts, **kw)
    body = partial.signing_bytes()
    return Event(id=content_id(body), type=type_, signer=signer, predicate=predicate,
                 timestamp=ts, signature=stub_sign(signer, body), **kw)


def verify_log(events: list[Event]) -> None:
    """Verification IS replay: id integrity + signature + signer anchored by a KEY.

    Note what verify_log CANNOT see: the view. Every event below verifies — the
    signature is honest over the canonical bytes B regardless of what was displayed.
    """
    registered: set[str] = set()
    for ev in events:
        body = ev.signing_bytes()
        if ev.id != content_id(body):
            raise ValueError(f"id does not match content on {ev.id} (post-signature mutation)")
        if ev.signature != stub_sign(ev.signer, body):
            raise ValueError(f"bad signature on {ev.id}")
        is_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} not anchored by a KEY register ({ev.id})")
        if is_root:
            registered.add(ev.payload["key"])


# ---------------------------------------------------------------------------
# Renderers. Each turns canonical bytes B into a human-readable view V. They are
# pure functions that run OFF-LOG, in the signer's local environment. ARC never
# sees them — it sees only the bytes B that come out the other side.
# ---------------------------------------------------------------------------

def _payload_of(action: Event) -> dict:
    return action.payload


def faithful_render(action: Event) -> str:
    """Shows every critical field with its true value. The renderer L assumes."""
    p = _payload_of(action)
    return (f"APPROVE PAYMENT\n"
            f"  pay: {p['amount_krw']} KRW\n"
            f"  to:  {p['payee']}\n"
            f"  for: {p.get('item','-')}")


def adversarial_render(action: Event) -> str:
    """Same bytes B, but rewrites the payee to a benign-looking name. Lies."""
    p = _payload_of(action)
    return (f"APPROVE PAYMENT\n"
            f"  pay: {p['amount_krw']} KRW\n"
            f"  to:  Merchant-A (trusted)\n"          # <-- not p['payee']
            f"  for: {p.get('item','-')}")


def careful_omit_render(action: Event) -> str:
    """Deterministic and reproducible — and reproducibly DROPS the payee line.
    Hashes consistently; an honest view_hash commitment over it will match on
    recompute. Still unfaithful: the human never sees where the money goes."""
    p = _payload_of(action)
    return (f"APPROVE PAYMENT\n"
            f"  pay: {p['amount_krw']} KRW\n"
            f"  for: {p.get('item','-')}")          # <-- payee line structurally omitted


def view_hash(view: str) -> str:
    """REAL content hash of the rendered view — this is what folds."""
    return "vh:" + hashlib.sha256(view.encode()).hexdigest()[:12]


def recompute_view_hash(action: Event, pinned_renderer: Callable[[Event], str]) -> str:
    """Anyone can recompute the view from the PINNED renderer and the on-log bytes.
    This is the foldable check — and its exact limit: it certifies correspondence to
    the pinned renderer's output, never the fidelity of the pinned renderer."""
    return view_hash(pinned_renderer(action))


# ---------------------------------------------------------------------------
# Omniscient faithfulness — readable by NO observer and NO fold. The fold does not
# know which fields are critical or what their true values are; faithfulness is a
# human-semantic judgment. Here only so the closing strip can show the gap.
# ---------------------------------------------------------------------------

def is_faithful(view: str, action: Event) -> bool:
    p = _payload_of(action)
    return all(str(p.get(fname)) in view for fname in CRITICAL_FIELDS)


def resolve_view_from_log(events: list[Event], action_id: str) -> dict:
    """What view did the signer see? Look only at the log. A rendered_view ATTEST, if
    present, carries a CLAIMED hash — itself only as good as its signer, and silent on
    whether that view was faithful or actually perceived. Absent one: UNKNOWN."""
    attest = next((e for e in events
                   if e.type == "ATTEST" and e.predicate == "view.rendered"
                   and e.payload.get("action") == action_id), None)
    if attest is None:
        return {"verdict": "UNKNOWN",
                "reason": "no event carries the rendered view; the log holds bytes, not what was shown"}
    return {"verdict": "CLAIMED", "view_hash": attest.payload.get("view_hash"), "by": attest.signer,
            "reason": f"{attest.signer} attests a view hash — a claim about what was shown, "
                      f"not proof it was faithful or perceived"}


# ---------------------------------------------------------------------------
# Participants and ledger. The ledger carries signed canonical bytes. What each
# signer actually SAW is tracked separately, omniscient — no fold reads it.
# ---------------------------------------------------------------------------

class Party:
    def __init__(self, ledger: "Ledger", name: str, key: str):
        self.ledger, self.name, self.key = ledger, name, key

    def emit(self, type_: str, predicate: str, ts: str, **kw) -> Event:
        ev = make(type_, self.key, predicate, ts, **kw)
        self.ledger.append(ev)
        print(f"    -> {self.name} {type_} {predicate}  [{ev.id}]")
        return ev


class Ledger:
    def __init__(self) -> None:
        self.events: list[Event] = []
        self.saw: dict[str, tuple[str, bool]] = {}   # action id -> (view shown, was_faithful) OMNISCIENT

    def append(self, ev: Event) -> None:
        self.events.append(ev)

    def record_view(self, action_id: str, view: str, action: Event) -> None:
        self.saw[action_id] = (view, is_faithful(view, action))


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


def show_view(label: str, view: str) -> None:
    print(f"    {label} the signer saw:")
    for line in view.splitlines():
        print(f"        | {line}")


# ---------------------------------------------------------------------------
# The flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def run() -> None:
    led = Ledger()
    principal = Party(led, "principal", "k:principal")   # grants the mandate
    signer    = Party(led, "signer",    "k:signer")      # honest, sound key; signs what it approves
    renderer  = Party(led, "renderer",  "k:renderer")    # the view-generator, used in the mitigation

    print("\n0. Identity + mandate")
    for p in (principal, signer, renderer):
        p.emit("KEY", "id.key_register", "2026-06-14T09:00:00Z", payload={"key": p.key})
    mandate = principal.emit("AUTHORIZE", "consent.mandate", "2026-06-14T10:00:00Z",
                             refs=("k:signer",),
                             scope={"category": "market", "max_total_krw": 100000})

    # The canonical bytes B everyone below will sign or render: a payment whose true
    # payee is the attacker. B itself is never tampered with; only the VIEW varies.
    def action_payload(view_hash_value: str | None = None) -> dict:
        p = {"payee": "wallet:attacker", "amount_krw": 50000, "item": "electronics"}
        if view_hash_value is not None:
            p["view_hash"] = view_hash_value
        return p

    # -- Readout 1: boundary ---------------------------------------------------
    print("\n1. Readout 1 — THE BOUNDARY (the log proves bytes, not the view)")
    b1 = signer.emit("AUTHORIZE", "consent.execute", "2026-06-14T11:00:00Z",
                     refs=(mandate.id,), payload=action_payload())
    print("    verify_log: ", end=""); verify_log(led.events); print("passes.")
    print(f"    The log holds B and id=hash(B) [{b1.id}]. It carries NO record of the view.")
    r = resolve_view_from_log(led.events, b1.id)
    print(f"    resolve-view-from-log: {r['verdict']}  ({r['reason']})")

    # -- Readout 2: faithful render control ------------------------------------
    print("\n2. Readout 2 — FAITHFUL RENDER (control; sign-what-you-saw holds — by assumption)")
    v_faithful = faithful_render(b1)
    led.record_view(b1.id, v_faithful, b1)
    show_view("(faithful renderer)", v_faithful)
    print(f"    faithful? {is_faithful(v_faithful, b1)} — the critical fields (payee, amount) are shown.")
    print("    Under a FAITHFUL renderer the signer can decide informedly. The property holds")
    print("    only because the renderer was faithful — an assumption, not something the log checks.")

    # -- Readout 3: WYSINWYS attack --------------------------------------------
    print("\n3. Readout 3 — WYSINWYS ATTACK (same signed action, different view)")
    b3 = signer.emit("AUTHORIZE", "consent.execute", "2026-06-14T12:00:00Z",
                     refs=(mandate.id,), payload=action_payload())
    v_adv = adversarial_render(b3)
    led.record_view(b3.id, v_adv, b3)
    show_view("(adversarial renderer)", v_adv)
    say("signer", "the screen says Merchant-A — looks fine, I approve")
    print(f"    The same signed action (same payload shape, true payee = wallet:attacker)")
    print(f"    rendered differently — the renderer rewrote the payee. The signer signs B;")
    print(f"    verify_log: ", end="")
    verify_log(led.events); print("passes.")
    print(f"    faithful? {is_faithful(v_adv, b3)}. The signer is honest, the key is sound, B is")
    print(f"    untampered — and the money still goes to the attacker. NOT finding M: the signer")
    print(f"    did not misread B, it was shown a different thing. The fault is the render layer.")

    # -- Readout 4: mitigation half-success (careless caught) ------------------
    print("\n4. Readout 4 — view_hash MITIGATION (careless mismatch is CAUGHT)")
    pinned = faithful_render   # the system pins a renderer and commits its output hash
    print("    The signer commits a view_hash into the signed payload; anyone recomputes it")
    print("    from the PINNED renderer. A careless attacker shows the doctored view but")
    print("    commits the hash of THAT view:")
    claimed = view_hash(v_adv)                       # hash of the adversarial view it showed
    b4 = signer.emit("AUTHORIZE", "consent.execute", "2026-06-14T13:00:00Z",
                     refs=(mandate.id,), payload=action_payload(claimed))
    recomputed = recompute_view_hash(b4, pinned)
    print(f"    claimed_view_hash   = {claimed}")
    print(f"    recomputed (pinned) = {recomputed}")
    caught = claimed != recomputed
    print(f"    => {'CAUGHT' if caught else 'passes'} — the committed view does not match what the")
    print(f"       pinned renderer produces from B. The foldable half: a careless view lie bites.")

    # -- Readout 5: the residue (careful, deterministic, still unfaithful) ------
    print("\n5. Readout 5 — THE RESIDUE (deterministic != faithful)")
    pinned_careful = careful_omit_render   # the PINNED renderer is itself reproducibly lossy
    v_omit = careful_omit_render(b1)
    honest_commit = view_hash(v_omit)                # an HONEST commitment over the pinned output
    b5 = signer.emit("AUTHORIZE", "consent.execute", "2026-06-14T14:00:00Z",
                     refs=(mandate.id,), payload=action_payload(honest_commit))
    led.record_view(b5.id, v_omit, b5)
    show_view("(pinned deterministic renderer)", v_omit)
    recomputed5 = recompute_view_hash(b5, pinned_careful)
    print(f"    claimed_view_hash   = {honest_commit}")
    print(f"    recomputed (pinned) = {recomputed5}")
    print(f"    => {'MATCH' if honest_commit == recomputed5 else 'mismatch'}; verify_log: ", end="")
    verify_log(led.events); print("passes.")
    print(f"    faithful? {is_faithful(v_omit, b5)} — the payee line is reproducibly OMITTED.")
    print("    The hash certifies the view CAME FROM the pinned renderer; it cannot certify the")
    print("    pinned renderer is FAITHFUL. A deterministic renderer can deterministically mislead.")
    print("    deterministic != faithful. Same shape as finding M, on the render layer.")

    # -- Readout 6: mitigation price -------------------------------------------
    print("\n6. Readout 6 — MITIGATION PRICE (more records relocate trust; none prove perception)")
    rv = renderer.emit("ATTEST", "view.rendered", "2026-06-14T14:30:00Z",
                       refs=(b5.id,),
                       payload={"action": b5.id, "view_hash": honest_commit})
    rr = resolve_view_from_log(led.events, b5.id)
    print(f"    rendered_view ATTEST added [{rv.id}]. resolve-view-from-log now: {rr['verdict']}")
    print(f"      ({rr['reason']})")
    print("    A rendered_view ATTEST / signed preview / renderer attestation is one more signed")
    print("    record. It RELOCATES trust into the renderer (or a runtime attestor) — exactly")
    print("    finding M's attested-signer, finding O's head-oracle, the world-axis trusted-oracle.")
    print("    None of them proves the human's eyes received a faithful view. The renderer is a")
    print("    MANDATORY trust dependency: bytes are not human-cognizable, so for any human")
    print("    approval a renderer is always in the trusted base — and ARC does not govern it.")

    print(f"\nGenerated log: {len(led.events)} signed events. verify_log passes "
          f"(every signature is honest over its canonical bytes B).")
    verify_log(led.events)

    print("\n--- omniscient view — available to NO observer (folds never read this) ---")
    print(f"    true bytes B always pay  ->  wallet:attacker (50000 KRW)")
    for aid, (view, faithful) in led.saw.items():
        first = view.splitlines()[0]
        shown_payee = "Merchant-A" if "Merchant-A" in view else ("(omitted)" if "to:" not in view else "wallet:attacker")
        mark = "FAITHFUL" if faithful else "UNFAITHFUL"
        print(f"    [{aid}] view showed payee={shown_payee:<14} -> {mark}")
    print("    The log carries the bytes B; it does NOT carry the view. view_hash bounds the")
    print("    view only to the PINNED renderer's output, never to its fidelity, never to perception.")

    print_finding()


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * Can ARC prove what view the signer actually saw?
      No. render(B) runs off-log in the signer's environment; the log holds B and
      id=hash(B), never the view. A signature seals the signed bytes, not the displayed
      view. (The render-layer twin of the fidelity wall.)
  * Why is this not finding M?
      M's signer SEES B in full and interprets it unfaithfully — the fault is reading.
      Here the signer reads faithfully but is shown render(B) != B — the fault is one
      step earlier, in presentation. Same bytes, different view.
  * Why is this the residue under finding L?
      L's "sign what you saw" mitigation (one projection for review and signing) assumes
      a faithful renderer. Bytes are not human-cognizable, so a renderer is unavoidable
      and L silently trusted it. This probe pricks that trust dependency.
  * What CAN ARC check about the view?
      A view_hash committed into the payload and recomputed from a PINNED deterministic
      renderer. A careless attacker who shows a doctored view but commits a hash the
      pinned renderer would not produce is CAUGHT. The render-correspondence layer folds.
  * What CAN ARC NOT check?
      The FIDELITY of the pinned renderer. A renderer that reproducibly omits a critical
      field is deterministic, hashes consistently, and an honest commitment over it
      matches on recompute — yet the view is unfaithful. deterministic != faithful. And
      below even that: whether the human's eyes received the view at all.
  * Do the mitigations close it?
      No. rendered_view ATTEST / signed preview / renderer attestation are more signed
      records; they RELOCATE trust into the renderer or a runtime attestor (finding M's
      attested-signer, finding O's head-oracle, the world-axis trusted-oracle). The
      renderer is a MANDATORY trust dependency ARC does not govern.

Conclusion: ARC can PRESERVE a view claim — bind a view_hash into the bytes, recompute
it from a pinned renderer — but it cannot make the displayed view FAITHFUL, and it
cannot reach the human's perception. The signature seals the signed bytes, never the
displayed view. The render-correspondence layer folds; the renderer's fidelity and the
human's perception do not.

Standing (not promoted to a finding letter): this looks like a sharpening of findings L
and M with one narrow new wrinkle — the renderer as a mandatory, off-log, deterministic-
yet-unfaithful trust dependency at the presentation layer (a candidate "P", to be judged
after review, not asserted here). No new event type; a rendered_view attestation is an
ordinary ATTEST predicate. The gap is a fold-policy residue between the signed bytes and
the displayed view. This is a probe, not a protocol spec and not doctrine.
""")


if __name__ == "__main__":
    run()
