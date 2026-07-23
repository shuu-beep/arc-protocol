#!/usr/bin/env python3
"""
ARC reference-client viewer — build step (stdlib only, self-contained).

What this is
------------
An illustrative viewer, not a runtime or production implementation. Seven base
Commerce surfaces share one fixture log; additional bands use named independent
fixture logs. The selected UI surfaces are not one-to-one Canon requirements.

    each surface is a projection over its named fixture log, and
    a mandate is what this fixture permits an agent key to sign without another
    approval record.

Fixture scope
-------------------------
  * The Commerce log is programmatically generated from the hand-authored
    `examples/end-to-end-demo/flow.py` fixture and reused verbatim.
  * The write path (`run_proposals` / `evaluate`) uses the fixture's deterministic
    mock-signing scheme to show one mandate -> sign/route policy. Its mock-sign basis
    is an explicit consent.mandate minted for the write path; the base log's
    one-time consent.approval licenses only its own transaction (event-registry
    §6) and is never read as standing authority. This path does not model key
    custody. Proposals are scripted, not produced by a live runtime or an MCP wire.
  * The projections are computed by the probe's own fold
    (`project_merchant_standing`), not re-implemented here. The HTML renders the
    precomputed output.
  * The commerce log's delegation is single-level (one per-purchase AUTHORIZE),
    so the delegation-tree card is shallow. Multi-level delegation lives in the
    delegation-graph band, which uses a separate generated fixture log
    (`delegation_fixture.py`). Its Python fold is parameterized by an observer's
    local root and a revocation reading; the page toggles between pre-rendered
    outputs. In this fixture, an unrooted key has weight 0 and is not blocked.
  * The cold-start band folds a third generated fixture log
    (`coldstart_fixture.py`) through three illustrative observer policies. No
    composite score or protocol-level identity verification is inferred. Private
    generator stipulations are rendered separately and are not fold inputs.

Run:  python3 build.py    ->  writes client.html  (open it in a browser)
"""

from __future__ import annotations

import contextlib
import dataclasses
import html
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "end-to-end-demo"))

import flow  # the hand-authored executable fixture; reused, not copied

import delegation_fixture as fixture  # the multi-level delegation fixture (same dir)
import coldstart_fixture as coldstart  # the cold-start policy fixture (same dir)
import compromise_fixture as compromise  # stolen-hot-key fixture (illustrative Ed25519)
import federation_fixture as federation  # the cross-community bridge fixture (same dir)
import approval_seam_fixture as approval_return  # return-path fixture (illustrative Ed25519)

# key id -> display name (presentation only; the keys come from the probes' parties)
NAMES = {
    "k:human": "human",
    "k:consumer_agent": "consumer-agent",
    "k:merchant": "merchant-agent",
    "k:community": "community",
    **fixture.NAMES,
    **coldstart.NAMES,
    **federation.NAMES,
    **approval_return.NAMES,
}


def name(key: str) -> str:
    return NAMES.get(key, key)


def esc(x) -> str:
    return html.escape(str(x))


# ---------------------------------------------------------------------------
# Capture the generated Commerce fixture log (suppress narration).
# ---------------------------------------------------------------------------

def capture_log() -> list[flow.Event]:
    with contextlib.redirect_stdout(io.StringIO()):
        ledger = flow.run()
    return ledger.events


def capture_fixture_log() -> list[fixture.Event]:
    with contextlib.redirect_stdout(io.StringIO()):
        return fixture.generate_log()


def capture_coldstart_log() -> list[coldstart.Event]:
    with contextlib.redirect_stdout(io.StringIO()):
        return coldstart.generate_log()


def capture_compromise_log():
    """Capture the illustrative-Ed25519 compromise fixture."""
    with contextlib.redirect_stdout(io.StringIO()):
        return compromise.generate_log()


def capture_federation_log() -> list:
    with contextlib.redirect_stdout(io.StringIO()):
        return federation.generate_log()


def capture_approval_return():
    """Capture signer-boundary decisions, approval flow, attempts, and private
    fixture stipulations. The illustrative signature checks are rerun later."""
    with contextlib.redirect_stdout(io.StringIO()):
        return approval_return.band_data()


def project_at(events: list[flow.Event], upto_predicate: str) -> dict:
    """Fold the log up to and including the first event with this predicate,
    using the probe's own projection (not re-implemented here)."""
    cut = next(i for i, e in enumerate(events) if e.predicate == upto_predicate)
    sub = events[: cut + 1]
    return flow.project_merchant_standing(sub, flow.MERCHANT, flow.CONTEXT)


# ---------------------------------------------------------------------------
# Surface renderers — each returns an HTML fragment, each sourced from the log.
# ---------------------------------------------------------------------------

def render_delegation_tree(events) -> str:
    keys = [e for e in events if e.type == "KEY" and e.predicate == "id.key_register"]
    auth = next(e for e in events if e.type == "AUTHORIZE")
    grantees = sorted({name(e.signer) for e in events if auth.id in e.refs})
    scope = auth.scope or {}
    scope_str = ", ".join(f"{k}={v}" for k, v in scope.items())

    rows = []
    for k in keys:
        nm = name(k.signer)
        rows.append(f'<div class="node"><span class="who">{esc(nm)}</span>'
                    f'<span class="kid">{esc(k.signer)}</span></div>')
        if nm == name(auth.signer):
            for g in grantees:
                rows.append(
                    f'<div class="edge">└─ AUTHORIZE <code>{esc(auth.predicate)}</code> '
                    f'→ <span class="who">{esc(g)}</span>'
                    f'<span class="scope">scope: {esc(scope_str)}</span></div>')
    note = ('<p class="note">Four independently key-rooted participants. The only '
            'delegation edge in this log is one per-purchase AUTHORIZE — '
            'single-level by design of this probe. Multi-level delegation lives in '
            'the <strong>delegation graph</strong> band at the bottom, over its own '
            'fixture log.</p>')
    return "".join(rows) + note


def render_mandate(events) -> str:
    auth = next(e for e in events if e.type == "AUTHORIZE")
    scope = auth.scope or {}
    rows = "".join(f'<div class="kv"><span>{esc(k)}</span><code>{esc(v)}</code></div>'
                   for k, v in scope.items())
    return (
        f'<div class="mandate">'
        f'<div class="kv"><span>granted by</span><code>{esc(name(auth.signer))}</code></div>'
        f'<div class="kv"><span>predicate</span><code>{esc(auth.predicate)}</code></div>'
        f'{rows}'
        f'<div class="kv"><span>refs</span><code>{esc(", ".join(auth.refs))}</code></div>'
        f'</div>'
        f'<p class="note">This AUTHORIZE is a one-transaction '
        f'<code>consent.approval</code> — consent to a specific act, not standing '
        f'authority (event-registry §6). The fixture evaluates auto-sign vs '
        f'escalate against the write path\'s explicit '
        f'<code>consent.mandate</code> (see the live-proposal band below).</p>')


def render_approval_inbox(events, results=()) -> str:
    auth = next(e for e in events if e.type == "AUTHORIZE")
    items = [
        f'<div class="approval resolved">'
        f'<div class="head"><span class="tag ok">RESOLVED</span> '
        f'consumer-agent requested approval for an offer</div>'
        f'<div class="body">the consumer agent could not approve; the fixture root '
        f'emitted <code>AUTHORIZE {esc(auth.predicate)}</code> '
        f'<span class="evid">[{esc(auth.id)}]</span></div></div>']
    for p, decision, reason, _ev in results:
        if decision == "escalate":
            items.append(
                f'<div class="approval pending">'
                f'<div class="head"><span class="tag warn">PENDING</span> '
                f'{esc(name(p.proposer))} proposed <code>{esc(p.predicate)}</code> '
                f'<span class="origin">origin: runtime</span></div>'
                f'<div class="body">{esc(reason)} — routed for a root-side decision</div></div>')
    note = ('<p class="note">The request itself is transport, not a stored event — '
            'only the fixture root\'s AUTHORIZE is on the log. PENDING items are runtime '
            'proposals the boundary would not auto-sign (see the write path below).</p>')
    return "".join(items) + note


def render_commitments(events) -> str:
    preds = {"commerce.offer", "commerce.payment_result", "commerce.fulfillment"}
    items = []
    for e in events:
        if e.predicate in preds:
            summary = ", ".join(f"{k}={v}" for k, v in e.payload.items()
                                if k not in ("context",))
            items.append(
                f'<div class="commit"><div class="head">'
                f'<span class="who">{esc(name(e.signer))}</span> '
                f'<code>{esc(e.predicate)}</code> '
                f'<span class="evid">[{esc(e.id)}]</span></div>'
                f'<div class="body">{esc(summary)}</div></div>')
    return "".join(items)


def render_projection(snapshots) -> str:
    buttons, panels = [], []
    for i, (label, s) in enumerate(snapshots):
        active = " active" if i == 0 else ""
        buttons.append(
            f'<button class="snapbtn{active}" data-snap="{i}">{i+1}</button>')
        rows = (
            f'<div class="kv big"><span>governance_standing</span>'
            f'<code class="gov-{esc(s["governance_standing"])}">'
            f'{esc(s["governance_standing"])}</code></div>'
            f'<div class="kv"><span>advisory_signal</span>'
            f'<code>{esc(s["advisory_signal"])}</code></div>'
            f'<div class="kv"><span>open_disputes</span>'
            f'<code>{esc(s["open_disputes"])}</code></div>'
            f'<div class="kv"><span>outcomes</span>'
            f'<code>+{esc(s["positive_outcomes"])} / -{esc(s["negative_outcomes"])}</code></div>')
        panels.append(
            f'<div class="snap{active}" data-snap="{i}">'
            f'<div class="snaplabel">{esc(label)}</div>{rows}</div>')
    caption = ('<p class="note">Same fold, recomputed at three cuts of the same '
               'log. In this fixture, standing changes on the <code>ADJUDICATE</code>, '
               'not the <code>CHALLENGE</code>. The displayed projection is recomputed.</p>')
    return (f'<div class="snapnav">snapshot {"".join(buttons)}</div>'
            f'{"".join(panels)}{caption}')


def render_challenge(events) -> str:
    chal = next(e for e in events if e.type == "CHALLENGE")
    adj = next(e for e in events if e.type == "ADJUDICATE")
    return (
        f'<div class="challenge"><span class="tag warn">⚠ CHALLENGE</span> '
        f'<code>{esc(chal.predicate)}</code> by {esc(name(chal.signer))} '
        f'<span class="evid">[{esc(chal.id)}]</span><div class="body">'
        f'{esc(chal.payload.get("reason",""))}</div></div>'
        f'<div class="adjudication"><span class="tag verdict">⚖ ADJUDICATE</span> '
        f'<code>{esc(adj.predicate)}</code> by {esc(name(adj.signer))} '
        f'<span class="evid">[{esc(adj.id)}]</span><div class="body">'
        f'resolves <code>{esc(adj.payload.get("resolves",""))}</code></div></div>'
        f'<p class="note">In this fixture, a CHALLENGE opens a dispute and the '
        f'referencing ADJUDICATE resolves it and changes the displayed standing.</p>')


def render_event_log(events, proposed=()) -> str:
    rows = []
    for i, e in enumerate(events):
        rows.append(
            f'<tr data-i="{i}"><td>{i}</td><td class="t-{esc(e.type)}">{esc(e.type)}</td>'
            f'<td>{esc(name(e.signer))}</td><td><code>{esc(e.predicate)}</code></td>'
            f'<td class="evid">{esc(e.id)}</td></tr>')
    for j, e in enumerate(proposed):
        i = len(events) + j
        tag = ("write-path mandate · fixture-root-granted"
               if e.predicate == "consent.mandate" else "proposed · auto-signed")
        rows.append(
            f'<tr class="proposed" data-i="{i}"><td>{i}</td>'
            f'<td class="t-{esc(e.type)}">{esc(e.type)}</td>'
            f'<td>{esc(name(e.signer))}</td><td><code>{esc(e.predicate)}</code> '
            f'<span class="tag ok">{tag}</span></td>'
            f'<td class="evid">{esc(e.id)}</td></tr>')
    return ('<table class="log"><thead><tr><th>#</th><th>type</th><th>signer</th>'
            '<th>predicate</th><th>id</th></tr></thead><tbody>'
            + "".join(rows) + '</tbody></table>'
            '<div id="inspector"><div class="ins-empty">click an event to inspect '
            'its raw Event record</div></div>')


# ---------------------------------------------------------------------------
# The delegation graph band — renders the fixture fold's output, adds nothing.
# Both readings are pre-rendered here in Python; the page only toggles them.
# ---------------------------------------------------------------------------

STATUS_CLS = {"root": "ok", "active": "ok", "spent": "mut",
              "revoked": "warn", "severed": "warn", "unrooted": "mut"}


def render_graph_node(n: dict, depth: int = 0) -> str:
    nm, key = name(n["key"]), n["key"]
    tags = [f'<span class="tag {STATUS_CLS[n["status"]]}">{esc(n["status"].upper())}</span>']
    if n["ephemeral"]:
        tags.append('<span class="tag mut">EPHEMERAL · single use</span>')
    if n["overclaimed"]:
        tags.append('<span class="tag warn">OVERCLAIMED</span>')
    if n["status"] == "root":
        ceil = '<span class="ceil">grants authority; holds no mandate</span>'
    elif n["status"] == "unrooted":
        ceil = '<span class="ceil">weight 0 from this root — admissible, not blocked</span>'
    else:
        c = f'auto-sign &le; {esc(n["effective_ceiling"])} KRW'
        if n["overclaimed"]:
            c += (f' <em>(granted {esc(n["claimed_ceiling"])} — clamped by the '
                  f'inherited intersection)</em>')
        ceil = f'<span class="ceil">{c} · beyond &rarr; escalate to root</span>'

    edge = ""
    if n["grant_id"]:
        wd = (f' <span class="wd">— withdrawn by '
              f'<span class="evid fid" data-fid="{esc(n["grant_withdrawn_by"])}">'
              f'[{esc(n["grant_withdrawn_by"])}]</span></span>'
              if n["grant_withdrawn_by"] else "")
        cls = " withdrawn" if n["grant_withdrawn_by"] else ""
        edge = (f'<div class="gedge{cls}">&#9492;&#9472; <span class="m">AUTHORIZE '
                f'<code>consent.mandate</code></span> '
                f'<span class="evid fid" data-fid="{esc(n["grant_id"])}">'
                f'[{esc(n["grant_id"])}]</span>{wd}</div>')

    acts = []
    for a in n["acts"]:
        v = ('<span class="tag ok">HONORED</span>' if a["honored_now"]
             else '<span class="tag warn">NOT HONORED</span>')
        amt = f' {a["amount"]} KRW' if a["amount"] is not None else ""
        acts.append(
            f'<div class="gact"><code>ATTEST {esc(a["predicate"])}</code>{esc(amt)} '
            f'{v} <span class="basis">{esc(a["basis"])}</span> '
            f'<span class="evid fid" data-fid="{esc(a["id"])}">[{esc(a["id"])}]</span></div>')

    kids = "".join(render_graph_node(c, depth + 1) for c in n["children"])
    return (f'<div class="gnode">{edge}'
            f'<div class="ghead"><span class="who">{esc(nm)}</span>'
            f'<span class="kid">{esc(key)}</span> {"".join(tags)} {ceil}</div>'
            f'{"".join(acts)}{kids}</div>')


def render_delegation_graph(projections: dict, flips: list, fixture_events) -> str:
    labels = {"preserve": "preserve · full current log",
              "cascade": "cascade · full current log"}
    buttons, panels = [], []
    for i, (reading, proj) in enumerate(projections.items()):
        active = " active" if i == 0 else ""
        buttons.append(f'<button class="readbtn{active}" data-read="{i}">'
                       f'{esc(labels[reading])}</button>')
        tree = render_graph_node(proj["tree"])
        stray = "".join(render_graph_node(u) for u in proj["unrooted"])
        panels.append(
            f'<div class="greading{active}" data-read="{i}">{tree}'
            f'<div class="gsep">unrooted from <code>{esc(proj["local_root"])}</code> '
            f'— no grant chain to this observer\'s root</div>{stray}</div>')

    rows = []
    for f in flips:
        a, b = f["preserve"], f["cascade"]
        amt = f' {a["amount"]} KRW' if a["amount"] is not None else ""
        rows.append(
            f'<div class="gflip"><span class="who">{esc(name(a["signer"]))}</span> · '
            f'<code>ATTEST {esc(a["predicate"])}</code>{esc(amt)} '
            f'<span class="evid fid" data-fid="{esc(f["id"])}">[{esc(f["id"])}]</span>'
            f'<div class="body">fixture assumption: <strong>authorized_at_act=True</strong><br>'
            f'current honoring: preserve <strong>HONORED</strong> &middot; '
            f'cascade <strong>NOT HONORED</strong> — same full current log; the policy '
            f'differs</div></div>')
    flip_panel = (f'<div class="gflips"><div class="gsep">projection divergence — '
                  f'{len(flips)} completed act(s) differ between the readings; the '
                  f'descendant act emitted after withdrawal is not honored under either'
                  f'</div>{"".join(rows)}</div>')

    note = (
        '<p class="note">This band folds over its <strong>own generated fixture '
        'log</strong> (21 events, <code>delegation_fixture.py</code>) — a second log, '
        'separate from the commerce log above. The graph is not authoritative protocol '
        'state: the fixture computes it from the log and this generated HTML embeds the '
        'pre-rendered output. The fold is parameterized twice where the '
        'canon is silent. <strong>(1) Rooted-ness is computed from the selected observer\'s '
        'root</strong> — fold the same log from <code>k:stray</code> and the rooted '
        'classifications change; this fixture uses no global identity registry, and the '
        'stray key is rendered at weight 0, not blocked. '
        '<strong>(2) Current honoring after withdrawal is a fold reading</strong> '
        '(toggle above; both use the same full current log) — the fixture assigns '
        '<code>authorized_at_act=True</code> to the affected completed acts. Cascade does not '
        'honor the spent courier\'s already-delivered work. The escalated 40000 payment '
        'remains honored even under cascade because its basis is a direct root approval, not the withdrawn '
        'chain. This fixture encodes delegation, over-delegation, escalation, '
        'retirement, and revocation with KEY/ATTEST/AUTHORIZE and the existing '
        '<code>scope</code>, <code>refs</code>, and <code>nullifies</code> fields.</p>')

    inspector = ('<div id="ginspector"><div class="ins-empty">click any [ev:…] id in '
                 'this band to inspect its raw Event record</div></div>')
    return (f'<div class="readnav">fold reading {"".join(buttons)}</div>'
            f'{"".join(panels)}{flip_panel}{note}{inspector}')


# ---------------------------------------------------------------------------
# The cold-start band — renders the policy matrix the fixture fold computes.
# Both cuts are pre-rendered here in Python; the page only toggles them.
# ---------------------------------------------------------------------------

def render_policy_cell(c: dict) -> str:
    chips = [f'<span class="tag cat-{esc(c["category"])}">{esc(c["verdict"])}</span>']
    for r in c["rulings"]:
        cls = "warn" if r["label"] == "warned" else "ok"
        chips.append(f'<span class="tag {cls}">{esc(r["label"].upper())} '
                     f'<span class="evid cid" data-cid="{esc(r["id"])}">[{esc(r["id"])}]</span></span>')
    if c["open_disputes"]:
        chips.append(f'<span class="tag warn">{len(c["open_disputes"])} OPEN DISPUTE</span>')
    hinge = ""
    if c["hinge"]:
        hinge = (f'<div class="hinge">&#9888; hinges on one tie '
                 f'<span class="evid cid" data-cid="{esc(c["hinge"])}">[{esc(c["hinge"])}]</span>'
                 f' — remove that single event and this judgment is gone</div>')
    basis = ""
    if c["basis"]:
        links = " ".join(f'<span class="evid cid" data-cid="{esc(b)}">[{esc(b)}]</span>'
                         for b in c["basis"])
        basis = f'<div class="basis">rests on: {links}</div>'
    return (f'<td class="mcell cat-{esc(c["category"])}"><div class="chips">'
            f'{"".join(chips)}</div><div class="mdetail">{esc(c["detail"])}</div>'
            f'{hinge}{basis}</td>')


def render_policy_matrix(projs: list) -> str:
    heads = []
    for p in projs:
        heads.append(
            f'<th><div class="who">{esc(p["observer"])}</div>'
            f'<div class="obsmeta">root <code>{esc(name(p["root"]))}</code> · '
            f'honors <code>{esc(name(p["honors"]))}</code><br>{esc(p["blurb"])}</div></th>')
    rows = []
    for s in coldstart.SUBJECTS:
        cells = "".join(render_policy_cell(p["cells"][s]) for p in projs)
        rows.append(f'<tr><th class="rowhead"><span class="who">{esc(name(s))}</span>'
                    f'<span class="kid">{esc(s)}</span></th>{cells}</tr>')
    return (f'<table class="matrix"><thead><tr><th></th>{"".join(heads)}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def render_coldstart_band(cut_matrices: dict, moves: list) -> str:
    buttons, panels = [], []
    for i, (label, projs) in enumerate(cut_matrices.items()):
        active = " active" if i == 0 else ""
        buttons.append(f'<button class="cutbtn{active}" data-cut="{i}">{esc(label)}</button>')
        panels.append(f'<div class="creading{active}" data-cut="{i}">'
                      f'{render_policy_matrix(projs)}</div>')

    move_rows = []
    for m in moves:
        move_rows.append(
            f'<div class="gflip"><span class="who">{esc(m["observer"])}</span> on '
            f'<span class="who">{esc(name(m["subject"]))}</span>: '
            f'<code>{esc(m["before"])}</code> &rarr; <code>{esc(m["after"])}</code></div>')
    moves_panel = (
        f'<div class="gsep">what moved between the cuts — observer-P and observer-H '
        f'return different readings for pre-authorized after the withdrawal</div>'
        f'{"".join(move_rows)}')

    stipulations = "".join(
        f'<div class="truth">{esc(t)}</div>' for t in coldstart.FIXTURE_STIPULATIONS)
    stipulation_panel = (
        f'<div class="gsep">generator-only stipulations — not inputs to the observer '
        f'folds</div><div class="omni">{stipulations}</div>')

    note = (
        '<p class="note">A third generated fixture log (30 events, '
        '<code>coldstart_fixture.py</code>). Each cell is one illustrative policy\'s '
        'categorical reading plus the Events used by that policy, with single-tie '
        'paths flagged. The visible records distinguish authored history, volume, '
        'and path patterns; they do not establish hidden operator identity or '
        'real-world outcome quality. Vouch/retraction are fixture predicates '
        '(<code>rep.vouch</code>, <code>rep.retraction</code> + <code>nullifies</code>) '
        'over the five canonical Event types.</p>')

    inspector = ('<div id="cinspector"><div class="ins-empty">click any [ev:…] id in '
                 'this band to inspect its raw Event record</div></div>')
    return (f'<div class="readnav">cut {"".join(buttons)}</div>{"".join(panels)}'
            f'{moves_panel}{stipulation_panel}{note}{inspector}')


# ---------------------------------------------------------------------------
# The compromise band — a stipulated stolen hot key with illustrative Ed25519.
# (just-after-revoke / after the dispute) x two revoke readings (time-scoped /
# cascade) are all pre-folded in Python; the page only toggles between them.
# The attacker-authored classification is generator-only — the honoring tables
# do not receive it. Different events can receive the same selected
# fold verdict; no payment or exact damage is established.
# ---------------------------------------------------------------------------

def render_honor_row(r: dict) -> str:
    honored = r["honored"]
    cls = "ok" if honored else "mut"
    label = "HONORED" if honored else "rejected"
    amt = f'{r["amount"]} KRW' if r["amount"] else "&mdash;"
    return (f'<tr class="{"hon" if honored else "rej"}">'
            f'<td><span class="tag verdict">SIG CHECK PASS</span></td>'
            f'<td><span class="tag {cls}">{label}</span></td>'
            f'<td><code>{esc(r["predicate"])}</code></td>'
            f'<td class="amt">{amt}</td>'
            f'<td class="basis">{esc(r["basis"])}</td>'
            f'<td><span class="evid xid" data-xid="{esc(r["id"])}">[{esc(r["id"])}]</span></td></tr>')


def render_compromise_band(moments: list, attacker_authored_ids: set, exposure: dict,
                           legit_id: str, forge_a_id: str, ceiling, revoke_ts) -> str:
    attacker_authored = set(attacker_authored_ids)

    # moment buttons x reading toggle, every combination pre-rendered
    mbtns, rbtns, grids = [], [], []
    for ri, reading in enumerate(compromise.READINGS):
        rbtns.append(f'<button class="xrbtn{" active" if ri == 0 else ""}" '
                     f'data-xr="{ri}">{esc(reading.replace("_", "-"))}</button>')
    for mi, m in enumerate(moments):
        mbtns.append(f'<button class="xmbtn{" active" if mi == 0 else ""}" '
                     f'data-xm="{mi}">{esc(m["label"])}</button>')
        for ri, reading in enumerate(compromise.READINGS):
            active = " active" if (mi == 0 and ri == 0) else ""
            rows = "".join(render_honor_row(r) for r in m["projs"][reading]["rows"])
            grids.append(
                f'<div class="xgrid{active}" data-xm="{mi}" data-xr="{ri}">'
                f'<table class="honor"><thead><tr><th>signature</th><th>fold</th>'
                f'<th>act</th><th>amount</th><th>why</th><th>event</th></tr></thead>'
                f'<tbody>{rows}</tbody></table></div>')

    # Two different records receive identical verdicts under both readings.
    pre = moments[0]["projs"]
    row = lambda reading, eid: next(r for r in pre[reading]["rows"] if r["id"] == eid)
    verd = lambda r: "HONORED" if r["honored"] else "rejected"
    twins = (
        '<div class="gsep">comparison just after withdrawal — the pre-compromise record and '
        'the in-scope attacker-authored record</div>'
        '<div class="twins">'
        f'<div class="twin"><div class="tlab">pre-compromise '
        f'<span class="evid xid" data-xid="{esc(legit_id)}">[{esc(legit_id)}]</span></div>'
        f'<div class="tval">time-scoped <b>{verd(row("time_scoped", legit_id))}</b> · '
        f'cascade <b>{verd(row("cascade", legit_id))}</b></div></div>'
        f'<div class="twin frg"><div class="tlab">ATTACKER-AUTHORED, in scope '
        f'<span class="evid xid" data-xid="{esc(forge_a_id)}">[{esc(forge_a_id)}]</span></div>'
        f'<div class="tval">time-scoped <b>{verd(row("time_scoped", forge_a_id))}</b> · '
        f'cascade <b>{verd(row("cascade", forge_a_id))}</b></div></div>'
        '</div>'
        '<div class="tnote">Identical verdicts for different records with different '
        'payloads, IDs, and bytes. Both pass the signature check, are in context, '
        'within ceiling, and precede withdrawal. Switch the '
        'moment toggle to <em>after the adjudication</em>: only then do they separate, '
        'after the fixture adds a <code>CHALLENGE</code> and honored '
        '<code>ADJUDICATE</code> voiding that one event. Three layers: fixture '
        'signature check passes (record) / scope honored (fold) / void (authority).</div>')

    # Fixture-classified honored exposure intersects the fold with private labels.
    b_ts, b_cas = exposure["time_scoped"], exposure["cascade"]
    exposure_panel = (
        '<div class="gsep">fixture-classified honored exposure — attacker-authored '
        'records this selected fold honors. No payment or exact damage is established.</div>'
        '<div class="exposure">'
        f'<div class="brow"><span class="blab">time-scoped revoke</span>'
        f'<span class="bval warn">{len(b_ts["honored_attacker_authored"])} honored · '
        f'{b_ts["honored_krw"]} KRW</span>'
        f'<span class="bnote">— one in-scope pre-withdrawal record remains honored</span>'
        f'</div>'
        f'<div class="brow"><span class="blab">cascade revoke</span>'
        f'<span class="bval">{len(b_cas["honored_attacker_authored"])} honored · '
        f'{b_cas["honored_krw"]} KRW</span>'
        f'<span class="bnote">— zero by excluding the pre-withdrawal records too</span>'
        f'</div>'
        f'<div class="bfind">scope ({esc(str(ceiling))} per act, context-bound) and '
        f'pre-withdrawal time (withdrawal @ {esc(revoke_ts[11:16])}) are two modeled '
        f'controls, not an exact general damage formula.</div></div>')

    # Generator-only authorship classifications; the grids never receive them.
    stipulation_rows = []
    for r in moments[0]["projs"]["time_scoped"]["rows"]:
        is_attacker_authored = r["id"] in attacker_authored
        amt = f'{r["amount"]} KRW' if r["amount"] else "&mdash;"
        stipulation_rows.append(
            f'<div class="otruth {"frg" if is_attacker_authored else "gen"}">'
            f'<span class="omark">{"ATTACKER-AUTHORED" if is_attacker_authored else "PRE-COMPROMISE"}</span> '
            f'<code>{esc(r["predicate"])}</code> <span class="oamt">{amt}</span> '
            f'<span class="evid xid" data-xid="{esc(r["id"])}">[{esc(r["id"])}]</span></div>')
    stipulations = (
        '<div class="gsep">generator-only authorship stipulations — the honoring '
        'grid does not receive this private classification. Each '
        'record passes the illustrative fixture signature check.</div>'
        f'<div class="omni">{"".join(stipulation_rows)}</div>')

    note = (
        '<p class="note">A fourth hand-authored fixture log (14 events, '
        '<code>compromise_fixture.py</code>) uses illustrative Ed25519. The fixture '
        'stipulates secret exfiltration; attacker-authored records pass the signature '
        'check. Under this fold, over-ceiling and out-of-context records fall '
        'to scope, the self-elevation to the tier line (the hot key does not control '
        'the cold-root key), and the post-revoke act to time. No new '
        'event type: theft is the absence of custody, revocation is '
        '<code>consent.withdraw</code> + <code>nullifies</code>, the dispute is '
        '<code>CHALLENGE</code> (the root, as disputant) + <code>ADJUDICATE</code> '
        '(the market community\'s key — the fold honors a per-act void only from an '
        'adjudicator the reader honors, so the disputant\'s own on-log ruling moves '
        'nothing; event-registry §4.5). See <code>docs/key-custody.md</code> '
        '§5/§8 for the broader topic.</p>')

    inspector = ('<div id="xinspector"><div class="ins-empty">click any [ev:…] id in '
                 'this band to inspect its raw record form and illustrative Ed25519 '
                 'signature</div></div>')

    return (
        f'<div class="readnav">moment {"".join(mbtns)}'
        f'&nbsp;&nbsp;&middot;&nbsp;&nbsp;revoke reading {"".join(rbtns)}</div>'
        f'{"".join(grids)}{exposure_panel}{twins}{stipulations}{note}{inspector}')


# ---------------------------------------------------------------------------
# The federation band — one log, two community authorities, five observers.
# Every (moment x severance reading) is pre-folded in Python by the fixture's
# own fold; the page only toggles between pre-rendered grids. CONTESTED is
# rendered as a split chip rather than an error state.
# ---------------------------------------------------------------------------

FED_STATUS_LABEL = {
    "local": "local authority",
    "imported": "imported as BINDING",
    "advisory": "imported as ADVISORY — moves nothing",
    "overridden": "imported, then OVERRIDDEN by the local ruling",
    "foreign": "foreign — weight 0",
}


def render_federation_cell(cell: dict) -> str:
    if cell["category"] == "contested":
        chip = ('<span class="tag fed-contested">'
                + " &#8741; ".join(esc(l.upper()) for l in cell["labels"])
                + '</span>')
    else:
        cls = {"good": "mut", "none": "mut", "affirm": "ok", "warn": "warn"}[cell["category"]]
        chip = f'<span class="tag {cls}">{esc(cell["standing"].upper())}</span>'
    chips = [chip]
    for v in cell["verdicts"]:
        if v["status"] == "advisory":
            chips.append(f'<span class="tag fed-adv">ADVISORY: {esc(v["label"].upper())}</span>')

    lines = []
    for v in cell["verdicts"]:
        via = (f' via bridge <span class="evid eid" data-eid="{esc(v["via"])}">'
               f'[{esc(v["via"])}]</span>' if v["via"] else "")
        lines.append(
            f'<div class="fverdict"><code>{esc(v["label"])}</code> by '
            f'<span class="who">{esc(name(v["by"]))}</span> '
            f'<span class="evid eid" data-eid="{esc(v["id"])}">[{esc(v["id"])}]</span>'
            f' — {esc(FED_STATUS_LABEL[v["status"]])}{via}</div>')

    hinge = ""
    if cell["hinge"]:
        hinge = (f'<div class="hinge">&#9888; this standing hinges on the bridge '
                 f'<span class="evid eid" data-eid="{esc(cell["hinge"])}">'
                 f'[{esc(cell["hinge"])}]</span> — fold without that one grant '
                 f'and it flips</div>')
    return (f'<td class="mcell fcell-{esc(cell["category"])}"><div class="chips">'
            f'{"".join(chips)}</div><div class="mdetail">{esc(cell["detail"])}</div>'
            f'{"".join(lines)}{hinge}</td>')


def render_federation_matrix(projs: list) -> str:
    rows = []
    for p in projs:
        prec = (f' · precedence: {p["precedence"].replace("_", "-")}'
                if p["precedence"] else "")
        rows.append(
            f'<tr><th class="rowhead frow"><div class="who">{esc(p["observer"])}</div>'
            f'<div class="obsmeta">root <code>{esc(name(p["root"]))}</code> · bridge: '
            f'{esc(p["bridge_reading"])}{esc(prec)}<br>{esc(p["blurb"])}</div></th>'
            f'{render_federation_cell(p["cell"])}</tr>')
    return (f'<table class="matrix fed"><thead><tr><th></th>'
            f'<th>the vendor&#8217;s standing, as this observer projects it</th>'
            f'</tr></thead><tbody>{"".join(rows)}</tbody></table>')


def render_federation_band(fed_matrices: dict, fed_moves: dict) -> str:
    mbtns, rbtns, grids = [], [], []
    for ri, reading in enumerate(federation.READINGS):
        rbtns.append(f'<button class="frbtn{" active" if ri == 0 else ""}" '
                     f'data-fr="{ri}">{esc(reading.replace("_", "-"))}</button>')
    for mi, (mlabel, _asof) in enumerate(federation.MOMENTS):
        mbtns.append(f'<button class="fmbtn{" active" if mi == 0 else ""}" '
                     f'data-fm="{mi}">{esc(mlabel)}</button>')
        for ri, reading in enumerate(federation.READINGS):
            active = " active" if (mi == 0 and ri == 0) else ""
            grids.append(f'<div class="fgrid{active}" data-fm="{mi}" data-fr="{ri}">'
                         f'{render_federation_matrix(fed_matrices[(mi, ri)])}</div>')

    move_panels = []
    for ri, reading in enumerate(federation.READINGS):
        rows = []
        for m in fed_moves[reading]:
            rows.append(
                f'<div class="gflip"><span class="who">{esc(m["observer"])}</span> '
                f'({esc(m["from_moment"])} &rarr; {esc(m["to_moment"])}): '
                f'<code>{esc(m["before"])}</code> &rarr; <code>{esc(m["after"])}</code></div>')
        if reading == "time_scoped":
            extra = ('<div class="gflip mutflip">under time-scoped, the severance '
                     'changes no earlier imported ruling; it bounds future imports. '
                     'The contested cell therefore remains unchanged.</div>')
        else:
            extra = ('<div class="gflip mutflip">under cascade the contested cell '
                     'becomes dismissed because the current projection excludes every '
                     'ruling previously imported through the severed '
                     'bridge. The original ADJUDICATE events remain intact.</div>')
        move_panels.append(
            f'<div class="fmoves{" active" if ri == 0 else ""}" data-fr="{ri}">'
            f'<div class="gsep">what moved between the moments · '
            f'{esc(reading.replace("_", "-"))}</div>{"".join(rows)}{extra}</div>')

    truth = "".join(f'<div class="truth">{esc(t)}</div>' for t in federation.FIXTURE_STIPULATIONS)
    truth_panel = (
        f'<div class="gsep">generator-only stipulations — not inputs to the observer '
        f'folds</div><div class="omni">{truth}</div>')

    note = (
        '<p class="note">A fifth generated fixture log (15 events, '
        '<code>federation_fixture.py</code>). Recognition is represented as a scoped <code>AUTHORIZE</code> '
        '(<code>fed.recognition</code>), severance is <code>nullifies</code>, and '
        'the preserve-vs-cascade divergence also appears here — severing a bridge '
        'bounds future imports without excluding earlier imports. A bridge reading is '
        'categorical (authority / advisory / ignore) in this authored policy. '
        'Override is a precedence choice inside a fold, not an event; and '
        'where a fold honors two conflicting authorities with no precedence rule, '
        '<strong>this fixture returns CONTESTED</strong>. A deployment may configure '
        'precedence or a final-authority topology. In this fixture, bridges are '
        'directional and route only authority the observer '
        'already grants. Why a community recognizes another in the first place is '
        'not in the log and no fold reads it. '
        'These are fixture-policy results.</p>')

    inspector = ('<div id="finspector"><div class="ins-empty">click any [ev:…] id in '
                 'this band to inspect its raw Event record</div></div>')

    return (
        f'<div class="readnav">moment {"".join(mbtns)}'
        f'&nbsp;&nbsp;&middot;&nbsp;&nbsp;severance reading {"".join(rbtns)}'
        f'<span class="frnote">(the readings differ only after the severance)</span>'
        f'</div>{"".join(grids)}{"".join(move_panels)}{truth_panel}{note}{inspector}')


# ---------------------------------------------------------------------------
# The approval-return band. Panel one shows
# signer decisions (the agent holds no key; the signer SIGNs / ROUTEs / REFUSEs);
# panel two binds an approval to reviewable proposal fields, then the same
# approval, in flight through the
# agent, is judged under two readings. The scope-only results are computed by the
# fixture. Generator-only authorship stipulations are not inputs to either reading.
# ---------------------------------------------------------------------------

APPROVAL_VERDICT = {"signed": ("ok", "SIGNED"), "routed": ("warn", "ROUTED"),
                    "refused": ("mut", "REFUSED")}


def render_signer_boundary_row(w: dict) -> str:
    cls, label = APPROVAL_VERDICT[w["verdict"]]
    amt = f'{w["amount"]} KRW' if w["amount"] else "&mdash;"
    drove = "configured operator" if w["by"] == "operator" else "attacker"
    return (f'<tr><td><span class="tag {cls}">{label}</span></td>'
            f'<td><code>{esc(w["label"])}</code></td>'
            f'<td class="amt">{amt}</td>'
            f'<td class="basis">{esc(w["reason"])}</td>'
            f'<td class="who">{esc(drove)}</td>'
            + (f'<td><span class="evid sid" data-sid="{esc(w["id"])}">[{esc(w["id"])}]</span></td>'
               if w["id"] else '<td class="basis">never an event</td>') + '</tr>')


def render_approval_attempt_row(a: dict, reading: str) -> str:
    r = a["readings"][reading]
    cls, label = APPROVAL_VERDICT[r["verdict"]]
    highlight = " counterfactual" if (
        reading == "scope_only" and r["verdict"] == "signed") else ""
    payee = a["payee"] or "&mdash;"
    amt = f'{a["amount"]} KRW' if a["amount"] else "&mdash;"
    return (f'<tr class="approval-attempt{highlight}"><td><span class="tag {cls}">{label}</span></td>'
            f'<td><code>{esc(a["label"])}</code></td>'
            f'<td class="amt">{esc(payee)} · {amt}</td>'
            f'<td class="basis">{esc(r["reason"])}</td></tr>')


def render_approval_return_band(approval_data: dict) -> str:
    # Panel one: signer-boundary outcomes.
    boundary_rows = "".join(
        render_signer_boundary_row(w) for w in approval_data["signer_boundary"])
    boundary = (
        '<div class="gsep">signer boundary — the fixture agent object holds no key '
        'and submits proposals to the signer object. The displayed '
        'out-of-scope proposals are routed or refused before Event creation.</div>'
        '<table class="honor"><thead><tr><th>signer</th><th>proposal</th>'
        '<th>amount</th><th>why</th><th>who drove it</th><th>event</th></tr></thead>'
        f'<tbody>{boundary_rows}</tbody></table>')

    # The simulated ceremony reviews fields for one routed proposal.
    e = approval_data["escalation"]
    match = "review fields match the proposal" if (
        e["review_payee"] == e["payee"] and e["review_amount"] == e["amount"]) else "DIVERGED"
    escalation = (
        '<div class="gsep">approval return path — a routed proposal is reviewed by '
        'the simulated cold-root ceremony before returning to the signer</div>'
        '<div class="returnflow">'
        f'<div class="sstep"><span class="tag warn">ROUTED</span> over-ceiling '
        f'{e["amount"]} KRW &rarr; the approval inbox</div>'
        f'<div class="sstep">the simulated ceremony pulls ticket <code>{esc(e["ticket"])}</code> and '
        f'sees <b>pay {e["review_amount"]} KRW to {esc(e["review_payee"])}</b> '
        f'<span class="smatch">({esc(match)})</span></div>'
        f'<div class="sstep">the ceremony emits a cold-key approval &rarr; '
        f'<span class="evid sid" data-sid="{esc(e["approval_id"])}">[{esc(e["approval_id"])}]</span> '
        f'<b>bound to that one proposal</b></div>'
        f'<div class="sstep"><span class="tag ok">SIGNED</span> '
        f'<span class="evid sid" data-sid="{esc(e["signed_id"])}">[{esc(e["signed_id"])}]</span> '
        f'— Event envelope fields are added by the signer</div>'
        '</div>')

    # The same approval under two readings.
    rbtns, grids, notes = [], [], []
    rlabel = {"proposal_bound": "proposal-bound (the signer)",
              "scope_only": "scope-only (a bearer token)"}
    for ri, reading in enumerate(approval_return.READINGS):
        rbtns.append(f'<button class="srbtn{" active" if ri == 0 else ""}" '
                     f'data-sr="{ri}">{esc(rlabel[reading])}</button>')
        rows = "".join(render_approval_attempt_row(a, reading)
                       for a in approval_data["attempts"])
        grids.append(
            f'<div class="sgrid{" active" if ri == 0 else ""}" data-sr="{ri}">'
            '<table class="honor"><thead><tr><th>verdict</th><th>attacker attempt</th>'
            '<th>payee · amount</th><th>why</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')
        if reading == "proposal_bound":
            notes.append('<div class="sgnote sgbound" data-sr="0">Bound to the '
                         'reviewable proposal-field hash: re-aim, in-process replay, and a '
                         'bare scope token are refused by the named signer checks.</div>')
        else:
            notes.append('<div class="sgnote sgcounterfactual" data-sr="1">embodiment_fixture\'s '
                         'approval was scope-only (context + amount). Under this computed '
                         'counterfactual, the three authored attempts are signed because '
                         'they satisfy the configured context and amount checks. '
                         'This grid is the fixture\'s <code>scope_only_would_sign()</code> — '
                         'a <strong>computed counterfactual</strong>, not an assertion. '
                         'The named binding and in-process consumption checks refuse these cases.</div>')
    comparison = (
        '<div class="gsep">the same approval returning through the agent under two '
        'fixture readings</div>'
        f'<div class="readnav">approval is {"".join(rbtns)}</div>'
        f'{"".join(grids)}{"".join(notes)}')

    # Generator-only authorship stipulations; the grids do not receive them.
    stipulation_rows = []
    for o in approval_data["generator_only"]:
        if "note" in o:
            stipulation_rows.append(f'<div class="truth">{esc(o["note"])}</div>')
        else:
            stipulation_rows.append(
                f'<div class="otruth gen"><span class="omark">{esc(o["who"])}</span> '
                f'<code>{esc(o["label"])}</code></div>')
    stipulations = (
        '<div class="gsep">generator-only authorship stipulations — not inputs to '
        'the signer checks or counterfactual</div>'
        f'<div class="omni">{"".join(stipulation_rows)}</div>')

    note = (
        '<p class="note">A sixth generated fixture log '
        '(<code>approval_seam_fixture.py</code>, illustrative Ed25519) exercises an '
        'approval return path. The hot secret remains in the signer object while the '
        'approval returns through the agent object. In the scope-only counterfactual, '
        'a context-and-amount token can be reused or re-aimed in the tested cases. Binding '
        'the approval to the content hash of reviewable proposal fields lets the '
        'signer refuse the tested re-aim and in-process replay cases. It does not '
        'establish what a person saw or understood, and consumption is not persistent. '
        'These are fixture-local signer checks.</p>')

    inspector = ('<div id="sinspector"><div class="ins-empty">click any [ev:…] id in '
                 'this band to inspect its raw record form and illustrative Ed25519 '
                 'signature</div></div>')

    return f'{boundary}{escalation}{comparison}{stipulations}{note}{inspector}'


# ---------------------------------------------------------------------------
# Page assembly.
# ---------------------------------------------------------------------------

CSS = """
:root{--ink:#1d2330;--mut:#6b7280;--line:#e3e6ee;--bg:#f7f8fb;--card:#fff;
--ok:#15803d;--warn:#b45309;--verdict:#6d28d9;--accent:#1f4ed8}
*{box-sizing:border-box}body{margin:0;font:13px/1.5 ui-monospace,SFMono-Regular,
Menlo,Consolas,monospace;color:var(--ink);background:var(--bg)}
header{padding:14px 20px;border-bottom:1px solid var(--line);background:var(--card)}
header h1{margin:0;font-size:15px;letter-spacing:.02em}
header .sub{color:var(--mut);font-size:12px;margin-top:3px}
.grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;padding:14px}
.col{display:flex;flex-direction:column;gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;
overflow:hidden}
.card>h2{margin:0;padding:9px 12px;font-size:12px;letter-spacing:.04em;
text-transform:uppercase;color:var(--mut);border-bottom:1px solid var(--line);
background:#fbfcfe}
.card>.in{padding:12px}
.note{color:var(--mut);font-size:11.5px;margin:10px 0 0;line-height:1.45}
code{background:#f0f2f7;padding:1px 5px;border-radius:4px;font-size:12px}
.who{font-weight:600}.kid{color:var(--mut);margin-left:8px;font-size:11px}
.node{padding:3px 0}.edge{padding:3px 0 3px 16px;color:#374151}
.edge .scope{display:block;color:var(--mut);font-size:11px;padding-left:18px}
.kv{display:flex;justify-content:space-between;gap:10px;padding:4px 0;
border-bottom:1px dashed var(--line)}.kv:last-child{border:0}
.kv span{color:var(--mut)}.kv.big code{font-size:13px}
.approval,.commit,.challenge,.adjudication{border:1px solid var(--line);
border-radius:6px;padding:9px;margin-bottom:8px}
.approval .head,.commit .head{font-weight:600;margin-bottom:4px}
.body{color:#374151}.evid{color:var(--mut);font-size:11px}
.tag{font-size:10px;font-weight:700;padding:1px 6px;border-radius:10px;
letter-spacing:.05em}.tag.ok{background:#dcfce7;color:var(--ok)}
.tag.warn{background:#fef3c7;color:var(--warn)}
.tag.verdict{background:#ede9fe;color:var(--verdict)}
.approval.pending{border-color:#f5d488;background:#fffdf5}
.origin{color:var(--mut);font-size:11px;font-weight:400;margin-left:6px}
.card.band>h2{color:var(--accent)}
.prop{border:1px solid var(--line);border-radius:6px;padding:9px 11px;margin-bottom:9px}
.prop .head{font-weight:600}.prop .ctx{color:var(--mut);font-weight:400}
.prop .intent{color:var(--mut);font-size:11.5px;margin:3px 0 6px}
.prop .decision{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.prop .route{color:var(--mut);font-size:11px;margin-left:auto}
table.log tr.proposed{background:#f3fbf5}table.log tr.proposed:hover{background:#e6f6ec}
.snapnav{color:var(--mut);margin-bottom:10px}
.snapbtn{font:inherit;border:1px solid var(--line);background:#fff;width:26px;
height:26px;border-radius:6px;margin-left:5px;cursor:pointer}
.snapbtn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.snap{display:none}.snap.active{display:block}
.snaplabel{font-size:11.5px;color:var(--mut);margin-bottom:6px;font-style:italic}
.gov-in_good_standing{color:var(--ok)}.gov-warned{color:var(--warn)}
.full{padding:0 14px 18px}
table.log{width:100%;border-collapse:collapse;background:var(--card);
border:1px solid var(--line);border-radius:8px;overflow:hidden}
table.log th,table.log td{text-align:left;padding:6px 10px;
border-bottom:1px solid var(--line);font-size:12px}
table.log th{color:var(--mut);text-transform:uppercase;font-size:10.5px;
letter-spacing:.04em;background:#fbfcfe}
table.log tbody tr{cursor:pointer}table.log tbody tr:hover{background:#f3f6ff}
table.log tbody tr.sel{background:#e8efff}
.t-KEY{color:#475569}.t-ATTEST{color:#0369a1}.t-AUTHORIZE{color:#15803d}
.t-CHALLENGE{color:#b45309}.t-ADJUDICATE{color:#6d28d9}
#inspector{margin-top:10px;background:#0f172a;color:#e2e8f0;border-radius:8px;
padding:12px;font-size:11.5px;white-space:pre;overflow:auto;max-height:280px}
.ins-empty{color:#64748b}
.tag.mut{background:#eef0f5;color:#475569}
.readnav{color:var(--mut);margin-bottom:10px}
.readbtn{font:inherit;font-size:11.5px;border:1px solid var(--line);background:#fff;
padding:4px 10px;border-radius:6px;margin-left:6px;cursor:pointer}
.readbtn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.greading{display:none}.greading.active{display:block}
.gnode{border-left:2px solid var(--line);margin:4px 0;padding:4px 0 2px 14px}
.ghead .ceil{display:block;color:var(--mut);font-size:11px;margin-top:1px}
.ghead .ceil em{font-style:normal;color:var(--warn)}
.gedge{color:var(--mut);font-size:11px;margin:1px 0 3px}
.gedge.withdrawn .m{text-decoration:line-through}
.gedge .wd{color:var(--warn)}
.gact{font-size:12px;padding:2px 0 2px 14px;color:#374151}
.gact .basis{color:var(--mut);font-size:11px}
.gsep{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.04em;
margin:12px 0 4px;padding-top:8px;border-top:1px dashed var(--line)}
.gflip{border:1px solid #f5d488;background:#fffdf5;border-radius:6px;
padding:8px 10px;margin:6px 0;font-size:12px}
.evid.fid{cursor:pointer;text-decoration:underline dotted}
#ginspector{margin-top:10px;background:#0f172a;color:#e2e8f0;border-radius:8px;
padding:12px;font-size:11.5px;white-space:pre;overflow:auto;max-height:280px}
.cutbtn{font:inherit;font-size:11.5px;border:1px solid var(--line);background:#fff;
padding:4px 10px;border-radius:6px;margin-left:6px;cursor:pointer}
.cutbtn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.creading{display:none}.creading.active{display:block}
table.matrix{width:100%;border-collapse:collapse}
table.matrix th,table.matrix td{border:1px solid var(--line);padding:8px 10px;
vertical-align:top;text-align:left;font-size:12px}
table.matrix thead th{background:#fbfcfe}
table.matrix .rowhead{background:#fbfcfe;white-space:nowrap}
table.matrix .rowhead .kid{display:block;margin-left:0}
.obsmeta{color:var(--mut);font-size:11px;font-weight:400;margin-top:3px;line-height:1.4}
.mcell .chips{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:5px}
.mcell .mdetail{color:#374151;font-size:11.5px;line-height:1.45}
.mcell .basis{color:var(--mut);font-size:10.5px;margin-top:5px}
.mcell .hinge{color:var(--warn);font-size:11px;margin-top:5px}
.tag.cat-affirm{background:#e0eaff;color:var(--accent)}
.tag.cat-thin{background:#fef3c7;color:var(--warn)}
.tag.cat-none{background:#eef0f5;color:#475569}
.tag.cat-dead{background:#fee2e2;color:#b91c1c}
td.mcell.cat-none{background:#fafbfd}td.mcell.cat-dead{background:#fff7f7}
.omni{border:1px dashed #94a3b8;border-radius:8px;background:#f8fafc;
padding:10px 12px}
.omni .truth{color:#475569;font-size:11.5px;padding:3px 0;line-height:1.5}
.evid.cid{cursor:pointer;text-decoration:underline dotted}
#cinspector{margin-top:10px;background:#0f172a;color:#e2e8f0;border-radius:8px;
padding:12px;font-size:11.5px;white-space:pre;overflow:auto;max-height:280px}
.xmbtn,.xrbtn{font:inherit;font-size:11.5px;border:1px solid var(--line);
background:#fff;padding:4px 10px;border-radius:6px;margin-left:6px;cursor:pointer}
.xmbtn.active,.xrbtn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.xgrid{display:none}.xgrid.active{display:block}
table.honor{width:100%;border-collapse:collapse;background:var(--card);
border:1px solid var(--line);border-radius:8px;overflow:hidden}
table.honor th,table.honor td{text-align:left;padding:6px 10px;
border-bottom:1px solid var(--line);font-size:12px;vertical-align:top}
table.honor th{color:var(--mut);text-transform:uppercase;font-size:10.5px;
letter-spacing:.04em;background:#fbfcfe}
table.honor tr.hon{background:#f3fbf5}table.honor tr.rej{background:#fafbfd}
table.honor .amt{white-space:nowrap}table.honor .basis{color:#374151;font-size:11.5px}
.exposure{border:1px solid var(--line);border-radius:8px;padding:10px 12px;background:#fff}
.brow{display:flex;align-items:center;gap:10px;padding:3px 0}
.brow .blab{font-weight:600;min-width:160px}
.bval{font-weight:700;color:var(--ok)}.bval.warn{color:#b91c1c}
.brow .bnote{color:var(--mut);font-size:11px}
.bfind{margin-top:8px;padding-top:8px;border-top:1px dashed var(--line);
color:#374151;font-size:12px;line-height:1.5}
.twins{display:flex;gap:10px;flex-wrap:wrap}
.twin{flex:1;min-width:220px;border:1px solid var(--line);border-radius:6px;
padding:8px 10px;background:#fbfcfe}
.twin.frg{border-color:#f5d488;background:#fffdf5}
.twin .tlab{font-weight:600;margin-bottom:3px}
.twin .tval{color:#374151;font-size:12px}
.tnote{color:var(--mut);font-size:11.5px;margin-top:8px;line-height:1.5}
.otruth{font-size:11.5px;padding:3px 0;line-height:1.5;color:#475569}
.otruth .omark{display:inline-block;min-width:62px;font-weight:700;font-size:10px;
letter-spacing:.05em}
.otruth.frg .omark{color:#b91c1c}.otruth.gen .omark{color:#475569}
.otruth .oamt{color:var(--mut)}
.evid.xid{cursor:pointer;text-decoration:underline dotted}
#xinspector{margin-top:10px;background:#0f172a;color:#e2e8f0;border-radius:8px;
padding:12px;font-size:11px;white-space:pre-wrap;word-break:break-all;
overflow:auto;max-height:300px}
.fmbtn,.frbtn{font:inherit;font-size:11.5px;border:1px solid var(--line);
background:#fff;padding:4px 10px;border-radius:6px;margin-left:6px;cursor:pointer}
.fmbtn.active,.frbtn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.frnote{font-size:10.5px;color:var(--mut);margin-left:8px}
.fgrid{display:none}.fgrid.active{display:block}
.fmoves{display:none}.fmoves.active{display:block}
table.matrix.fed .rowhead{white-space:normal;max-width:380px}
.tag.fed-contested{background:linear-gradient(90deg,#fee2e2 0 50%,#dcfce7 50% 100%);
color:#1d2330;border:1px solid #e5e7eb}
.tag.fed-adv{background:#e0f2fe;color:#0369a1}
td.mcell.fcell-contested{background:#fffbf5}
.fverdict{font-size:11.5px;color:#374151;padding:2px 0}
.gflip.mutflip{border-color:var(--line);background:#fbfcfe;color:#374151}
.evid.eid{cursor:pointer;text-decoration:underline dotted}
#finspector{margin-top:10px;background:#0f172a;color:#e2e8f0;border-radius:8px;
padding:12px;font-size:11.5px;white-space:pre;overflow:auto;max-height:280px}
.srbtn{font:inherit;font-size:11.5px;border:1px solid var(--line);
background:#fff;padding:4px 10px;border-radius:6px;margin-left:6px;cursor:pointer}
.srbtn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.sgrid{display:none}.sgrid.active{display:block}
.returnflow{border:1px solid var(--line);border-radius:8px;padding:6px 12px;background:#fff}
.sstep{padding:4px 0;font-size:12px;border-bottom:1px dashed var(--line)}
.sstep:last-child{border-bottom:0}
.smatch{color:var(--ok);font-size:11px}
.approval-attempt.counterfactual{background:#fef2f2}
.sgnote{display:none;margin-top:8px;padding:9px 11px;border-radius:6px;font-size:11.5px;
line-height:1.5}
.sgnote.active{display:block}
.sgnote.sgbound{background:#f3fbf5;border:1px solid #cdeed5;color:#14532d}
.sgnote.sgcounterfactual{background:#fef2f2;border:1px solid #f3c9c9;color:#7f1d1d}
.evid.sid{cursor:pointer;text-decoration:underline dotted}
#sinspector{margin-top:10px;background:#0f172a;color:#e2e8f0;border-radius:8px;
padding:12px;font-size:11px;white-space:pre-wrap;word-break:break-all;
overflow:auto;max-height:300px}
"""

JS = """
const EVENTS = JSON.parse(document.getElementById('arc-data').textContent);
document.querySelectorAll('.snapbtn').forEach(b=>b.onclick=()=>{
  const i=b.dataset.snap;
  document.querySelectorAll('.snapbtn').forEach(x=>x.classList.toggle('active',x===b));
  document.querySelectorAll('.snap').forEach(p=>p.classList.toggle('active',p.dataset.snap===i));
});
document.querySelectorAll('table.log tbody tr').forEach(tr=>tr.onclick=()=>{
  document.querySelectorAll('table.log tbody tr').forEach(x=>x.classList.remove('sel'));
  tr.classList.add('sel');
  const e=EVENTS[+tr.dataset.i];
  document.getElementById('inspector').textContent=JSON.stringify(e,null,2);
});
const FIX = JSON.parse(document.getElementById('arc-fixture').textContent);
const FIX_BY_ID = Object.fromEntries(FIX.map(e=>[e.id,e]));
document.querySelectorAll('.readbtn').forEach(b=>b.onclick=()=>{
  const i=b.dataset.read;
  document.querySelectorAll('.readbtn').forEach(x=>x.classList.toggle('active',x===b));
  document.querySelectorAll('.greading').forEach(p=>p.classList.toggle('active',p.dataset.read===i));
});
document.querySelectorAll('.evid.fid').forEach(el=>el.onclick=()=>{
  document.getElementById('ginspector').textContent=
    JSON.stringify(FIX_BY_ID[el.dataset.fid],null,2);
});
const COLD = JSON.parse(document.getElementById('arc-coldstart').textContent);
const COLD_BY_ID = Object.fromEntries(COLD.map(e=>[e.id,e]));
document.querySelectorAll('.cutbtn').forEach(b=>b.onclick=()=>{
  const i=b.dataset.cut;
  document.querySelectorAll('.cutbtn').forEach(x=>x.classList.toggle('active',x===b));
  document.querySelectorAll('.creading').forEach(p=>p.classList.toggle('active',p.dataset.cut===i));
});
document.querySelectorAll('.evid.cid').forEach(el=>el.onclick=()=>{
  document.getElementById('cinspector').textContent=
    JSON.stringify(COLD_BY_ID[el.dataset.cid],null,2);
});
const XCOMP = JSON.parse(document.getElementById('arc-compromise').textContent);
const XCOMP_BY_ID = Object.fromEntries(XCOMP.map(e=>[e.id,e]));
let xm='0', xr='0';
function xsync(){
  document.querySelectorAll('.xmbtn').forEach(b=>b.classList.toggle('active',b.dataset.xm===xm));
  document.querySelectorAll('.xrbtn').forEach(b=>b.classList.toggle('active',b.dataset.xr===xr));
  document.querySelectorAll('.xgrid').forEach(g=>g.classList.toggle('active',
    g.dataset.xm===xm && g.dataset.xr===xr));
}
document.querySelectorAll('.xmbtn').forEach(b=>b.onclick=()=>{xm=b.dataset.xm;xsync();});
document.querySelectorAll('.xrbtn').forEach(b=>b.onclick=()=>{xr=b.dataset.xr;xsync();});
document.querySelectorAll('.evid.xid').forEach(el=>el.onclick=()=>{
  document.getElementById('xinspector').textContent=
    JSON.stringify(XCOMP_BY_ID[el.dataset.xid],null,2);
});
const FED = JSON.parse(document.getElementById('arc-federation').textContent);
const FED_BY_ID = Object.fromEntries(FED.map(e=>[e.id,e]));
let fm='0', fr='0';
function fsync(){
  document.querySelectorAll('.fmbtn').forEach(b=>b.classList.toggle('active',b.dataset.fm===fm));
  document.querySelectorAll('.frbtn').forEach(b=>b.classList.toggle('active',b.dataset.fr===fr));
  document.querySelectorAll('.fgrid').forEach(g=>g.classList.toggle('active',
    g.dataset.fm===fm && g.dataset.fr===fr));
  document.querySelectorAll('.fmoves').forEach(g=>g.classList.toggle('active',g.dataset.fr===fr));
}
document.querySelectorAll('.fmbtn').forEach(b=>b.onclick=()=>{fm=b.dataset.fm;fsync();});
document.querySelectorAll('.frbtn').forEach(b=>b.onclick=()=>{fr=b.dataset.fr;fsync();});
document.querySelectorAll('.evid.eid').forEach(el=>el.onclick=()=>{
  document.getElementById('finspector').textContent=
    JSON.stringify(FED_BY_ID[el.dataset.eid],null,2);
});
const APPROVAL_EVENTS = JSON.parse(document.getElementById('arc-approval-return').textContent);
const APPROVAL_BY_ID = Object.fromEntries(APPROVAL_EVENTS.map(e=>[e.id,e]));
let sr='0';
function ssync(){
  document.querySelectorAll('.srbtn').forEach(b=>b.classList.toggle('active',b.dataset.sr===sr));
  document.querySelectorAll('.sgrid').forEach(g=>g.classList.toggle('active',g.dataset.sr===sr));
  document.querySelectorAll('.sgnote').forEach(g=>g.classList.toggle('active',g.dataset.sr===sr));
}
document.querySelectorAll('.srbtn').forEach(b=>b.onclick=()=>{sr=b.dataset.sr;ssync();});
ssync();
document.querySelectorAll('.evid.sid').forEach(el=>el.onclick=()=>{
  document.getElementById('sinspector').textContent=
    JSON.stringify(APPROVAL_BY_ID[el.dataset.sid]||{note:'not a logged event (e.g. a refused proposal or an off-log prop)'},null,2);
});
"""


# ---------------------------------------------------------------------------
# The write path — one proposal verb and a fixture evaluator that routes it.
# A scripted runtime proposes; this fixture checks the active mandate and either
# auto-signs in scope or routes out-of-scope proposals for a root-side decision.
# This mock-signing path does not model key custody.
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class Proposal:
    proposer: str          # key id of the mandated party, acting via a BYO runtime
    type: str
    predicate: str
    payload: dict
    intent: str


def evaluate(p: Proposal, mandate) -> tuple[str, str]:
    """Apply the write-path fixture policy; return an auto-sign or route decision."""
    scope = mandate.scope or {}
    # This fixture routes AUTHORIZE proposals for root-side handling.
    if p.type == "AUTHORIZE":
        return "escalate", "this fixture routes AUTHORIZE for root-side handling"
    ctx_ok = p.payload.get("context") == scope.get("context")
    amount = p.payload.get("amount_krw")
    amount_ok = amount is None or amount <= scope.get("max_total_krw", 0)
    if ctx_ok and amount_ok:
        return "auto_sign", "within mandate scope — no additional approval record required"
    if not ctx_ok:
        return "escalate", (f"context {p.payload.get('context')!r} is outside the "
                            f"mandate context {scope.get('context')!r}")
    return "escalate", f"amount {amount} exceeds the mandate ceiling {scope.get('max_total_krw')}"


def run_proposals(events) -> tuple[list, list]:
    # The base log's AUTHORIZE is a consent.approval — consent to one
    # transaction (event-registry §6). It is never standing authority, so the
    # boundary does not evaluate proposals against it. Auto-sign authority is
    # an explicit consent.mandate: the same fixture root that approved the lunch
    # transaction grants the agent a standing mandate with the same bounds,
    # and that is what evaluate() reads.
    approval = next(e for e in events if e.type == "AUTHORIZE")
    assert approval.predicate == "consent.approval"
    proposer = next((e.signer for e in events if approval.id in e.refs), approval.signer)
    mandate = flow.make("AUTHORIZE", approval.signer, "consent.mandate",
                        "2026-06-08T10:11:30Z", refs=(proposer,),
                        scope=dict(approval.scope or {}))
    proposals = [
        Proposal(proposer, "ATTEST", "rep.outcome",
                 {"result": "positive", "context": "lunch"},
                 "log a positive outcome within the authorized lunch context"),
        Proposal(proposer, "ATTEST", "commerce.payment_result",
                 {"result": "confirmed", "amount_krw": 20000, "context": "lunch"},
                 "pay 20000 KRW for a lunch order"),
        Proposal(proposer, "AUTHORIZE", "consent.approval",
                 {"context": "lunch"},
                 "grant itself a wider mandate"),
    ]
    results, signed = [], [mandate]   # the mandate itself enters the log first
    for p in proposals:
        decision, reason = evaluate(p, mandate)
        ev = None
        if decision == "auto_sign":
            ev = flow.make(p.type, p.proposer, p.predicate, "2026-06-08T10:12:00Z",
                           payload=dict(p.payload))
            signed.append(ev)
        results.append((p, decision, reason, ev))
    return results, signed


def render_proposal_flow(results, signed=()) -> str:
    badges = {"auto_sign": ("AUTO-SIGNED", "ok", "→ event log"),
              "escalate": ("ESCALATED", "warn", "→ approval inbox")}
    rows = []
    mandate = next((e for e in signed if e.predicate == "consent.mandate"), None)
    if mandate is not None:
        sc = mandate.scope or {}
        rows.append(
            f'<div class="prop"><div class="head">'
            f'<span class="who">{esc(name(mandate.signer))}</span> · '
            f'<code>AUTHORIZE consent.mandate</code> '
            f'<span class="ctx">({esc(sc.get("context", ""))} &le; '
            f'{esc(sc.get("max_total_krw"))} KRW)</span></div>'
            f'<div class="intent">basis: the fixture root grants standing auto-sign authority '
            f'for this window — the one-time <code>consent.approval</code> in the base '
            f'log licenses only its own transaction (event-registry §6) and is never '
            f'read as a mandate</div>'
            f'<div class="decision"><span class="tag ok">GRANTED</span> '
            f'<span class="evid">[{esc(mandate.id)}]</span> '
            f'<span class="route">→ event log</span></div></div>')
    for p, decision, reason, ev in results:
        label, cls, route = badges[decision]
        amt = p.payload.get("amount_krw")
        amt_s = f" {amt} KRW" if amt is not None else ""
        evid = f' <span class="evid">[{esc(ev.id)}]</span>' if ev else ""
        rows.append(
            f'<div class="prop"><div class="head">'
            f'<span class="who">{esc(name(p.proposer))}</span> · '
            f'<code>{esc(p.type)} {esc(p.predicate)}</code>{esc(amt_s)} '
            f'<span class="ctx">({esc(p.payload.get("context",""))})</span></div>'
            f'<div class="intent">intent: {esc(p.intent)}</div>'
            f'<div class="decision"><span class="tag {cls}">{label}</span> '
            f'{esc(reason)}{evid} <span class="route">{esc(route)}</span></div></div>')
    note = ('<p class="note">The fixture represents proposed records with one '
            '<code>Proposal</code> shape and routes them through <code>evaluate()</code>. Its '
            'basis is the explicit <code>consent.mandate</code> above: an approval is '
            'consent to one transaction, a mandate is standing scoped authority, and '
            'the write path uses them separately (event-registry §6). Signing here '
            'uses the fixture\'s deterministic mock scheme; key custody is not modeled. The base '
            'projection is left unchanged — this panel is the write path, not the read.</p>')
    return "".join(rows) + note


def build_html(events, snapshots, results, signed, projections, flips, fixture_events,
               cut_matrices, moves, coldstart_events, comp, fed, approval_data) -> str:
    data = json.dumps([dataclasses.asdict(e) for e in (list(events) + list(signed))],
                       default=list)
    fixdata = json.dumps([dataclasses.asdict(e) for e in fixture_events], default=list)
    colddata = json.dumps([dataclasses.asdict(e) for e in coldstart_events], default=list)
    compdata = json.dumps([dataclasses.asdict(e) for e in comp["events"]], default=list)
    feddata = json.dumps([dataclasses.asdict(e) for e in fed["events"]], default=list)
    approvaldata = json.dumps(
        [dataclasses.asdict(e) for e in approval_data["events"]], default=list)
    fed_band = render_federation_band(fed["matrices"], fed["moves"])
    approval_band = render_approval_return_band(approval_data)
    comp_band = render_compromise_band(comp["moments"], comp["attacker_authored"],
                                       comp["exposure"],
                                       comp["legit_id"], comp["forge_a_id"],
                                       comp["ceiling"], comp["revoke_ts"])
    card = lambda t, b: f'<div class="card"><h2>{t}</h2><div class="in">{b}</div></div>'
    left = card("delegation tree", render_delegation_tree(events)) + \
        card("authorization viewer", render_mandate(events))
    mid = card("approval inbox", render_approval_inbox(events, results)) + \
        card("signed commitments", render_commitments(events))
    right = card("projection viewer", render_projection(snapshots)) + \
        card("challenge / adjudication", render_challenge(events))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ARC reference client</title><style>{CSS}</style></head><body>
<header><h1>ARC reference client</h1>
<div class="sub">six generated fixture logs · the commerce log ({len(events)} events) feeds the seven
surfaces and the write path · a delegation fixture ({len(fixture_events)} events) feeds the
graph · a cold-start fixture ({len(coldstart_events)} events) feeds the policy matrix ·
a compromise fixture ({len(comp["events"])} events, illustrative Ed25519) feeds the exposure band ·
a federation fixture ({len(fed["events"])} events) feeds the bridge disagreement band ·
an approval-return fixture ({len(approval_data["events"])} events, illustrative Ed25519) feeds the approval-return band ·
each panel uses its named fixture log and declared reading</div></header>
<div class="grid">
<div class="col">{left}</div>
<div class="col">{mid}</div>
<div class="col">{right}</div>
</div>
<div class="full"><div class="card band"><h2>live proposal — scripted write-path evaluation</h2>
<div class="in">{render_proposal_flow(results, signed)}</div></div></div>
<div class="full"><div class="card"><h2>event log — the source the seven surfaces fold over</h2>
<div class="in">{render_event_log(events, signed)}</div></div></div>
<div class="full"><div class="card band"><h2>delegation graph — one fixture log, two readings</h2>
<div class="in">{render_delegation_graph(projections, flips, fixture_events)}</div></div></div>
<div class="full"><div class="card band"><h2>cold start — three illustrative observer policies (one fixture log, two cuts)</h2>
<div class="in">{render_coldstart_band(cut_matrices, moves)}</div></div></div>
<div class="full"><div class="card band"><h2>compromise — fixture-classified honored exposure (illustrative Ed25519; two moments, two revoke readings)</h2>
<div class="in">{comp_band}</div></div></div>
<div class="full"><div class="card band"><h2>federation — one log, two authorities, and what a bridge imports (five observers; three moments, two severance readings)</h2>
<div class="in">{fed_band}</div></div></div>
<div class="full"><div class="card band"><h2>approval return path — signer decisions and reviewable-field binding (illustrative Ed25519)</h2>
<div class="in">{approval_band}</div></div></div>
<script id="arc-data" type="application/json">{data}</script>
<script id="arc-fixture" type="application/json">{fixdata}</script>
<script id="arc-coldstart" type="application/json">{colddata}</script>
<script id="arc-compromise" type="application/json">{compdata}</script>
<script id="arc-federation" type="application/json">{feddata}</script>
<script id="arc-approval-return" type="application/json">{approvaldata}</script>
<script>{JS}</script>
</body></html>"""


def main() -> None:
    events = capture_log()
    snapshots = [
        ("after fulfillment", project_at(events, "commerce.fulfillment")),
        ("after dispute", project_at(events, "rep.outcome")),
        ("after adjudication", project_at(events, "gov.warning")),
    ]
    results, signed = run_proposals(events)
    fixture_events = capture_fixture_log()
    projections = {r: fixture.project_delegation_graph(fixture_events, reading=r)
                   for r in fixture.READINGS}
    flips = fixture.divergent_acts(fixture_events)
    coldstart_events = capture_coldstart_log()
    cut_matrices = {label: coldstart.matrix(coldstart_events, asof)
                    for label, asof in coldstart.CUTS}
    moves = coldstart.changed_cells(coldstart_events)

    # the compromise band: fold the stolen-key log at two moments x two readings.
    # The reader's policy honors the market community's adjudicating key — a
    # per-act void counts only from an honored adjudicator (registry §4.5), so
    # the disputant's own on-log ruling moves nothing in these grids.
    comp_events, comp_attacker_authored, _comp_kr, comp_meta = capture_compromise_log()
    c_root, c_agent = comp_meta["root"], comp_meta["agent"]
    c_honors = (comp_meta["community"],)
    comp_pre = [e for e in comp_events if e.type not in ("CHALLENGE", "ADJUDICATE")]
    proj = lambda log, r: compromise.project_compromise(
        log, root=c_root, agent=c_agent, reading=r, honored_adjudicators=c_honors)
    comp_moments = [
        {"label": "just after the revocation",
         "projs": {r: proj(comp_pre, r) for r in compromise.READINGS}},
        {"label": "after the adjudication",
         "projs": {r: proj(comp_events, r) for r in compromise.READINGS}},
    ]
    comp_exposure = {
        r: compromise.modeled_exposure(
            comp_pre, comp_attacker_authored, root=c_root, agent=c_agent,
            reading=r, honored_adjudicators=c_honors)
        for r in compromise.READINGS
    }
    base = comp_moments[0]["projs"]["time_scoped"]
    comp = {"events": comp_events, "attacker_authored": comp_attacker_authored,
            "moments": comp_moments, "exposure": comp_exposure,
            "legit_id": comp_meta["legit_id"],
            "forge_a_id": comp_meta["forge_a_id"], "ceiling": base["mandate_ceiling"],
            "revoke_ts": base["revoke_ts"]}

    # the federation band: every (moment x severance reading) pre-folded
    fed_events = capture_federation_log()
    fed_matrices = {(mi, ri): federation.matrix(fed_events, asof, reading)
                    for mi, (_label, asof) in enumerate(federation.MOMENTS)
                    for ri, reading in enumerate(federation.READINGS)}
    fed_moves = {reading: federation.moved_cells(fed_events, reading)
                 for reading in federation.READINGS}
    fed = {"events": fed_events, "matrices": fed_matrices, "moves": fed_moves}

    # Approval-return data is structured by its fixture; the viewer only renders it.
    approval_data = capture_approval_return()

    out = os.path.join(HERE, "client.html")
    with open(out, "w") as f:
        f.write(build_html(events, snapshots, results, signed,
                           projections, flips, fixture_events,
                           cut_matrices, moves, coldstart_events, comp, fed,
                           approval_data))
    print(f"captured {len(events)} mock-signed fixture Events from the end-to-end-demo")
    for label, s in snapshots:
        print(f"  [{label}] governance={s['governance_standing']} "
              f"open_disputes={s['open_disputes']}")
    print("write-path fixture decisions:")
    wp_mandate = next((e for e in signed if e.predicate == "consent.mandate"), None)
    if wp_mandate is not None:
        sc = wp_mandate.scope or {}
        print(f"  basis     AUTHORIZE consent.mandate [{wp_mandate.id}] — fixture-root-granted "
              f"standing authority ({sc.get('context')} <= {sc.get('max_total_krw')}); "
              f"the base log's consent.approval covers one transaction only (registry §6)")
    for p, decision, reason, ev in results:
        evid = f" [{ev.id}]" if ev else ""
        print(f"  {decision:9} {p.type} {p.predicate}{evid} — {reason}")
    # the write-path mandate and the auto-signed proposals verify against the
    # same log they extend
    flow.verify_log(events + signed)
    fixture.verify_log(fixture_events)  # the fixture log verifies independently
    coldstart.verify_log(coldstart_events)
    compromise.verify_log(comp_events)  # illustrative Ed25519 fixture check
    federation.verify_log(fed_events)
    approval_return.verify_log(approval_data["events"])
    print(f"delegation fixture: {len(fixture_events)} mock-signed Events; "
          f"{len(flips)} completed act(s) differ between the two fold readings")
    print(f"cold-start fixture: {len(coldstart_events)} mock-signed Events; "
          f"{len(moves)} matrix cell(s) move between the two cuts")
    print(f"compromise fixture: {len(comp_events)} illustrative-Ed25519 events; "
          f"fixture-classified honored exposure (time-scoped) = "
          f"{comp_exposure['time_scoped']['honored_krw']} KRW in "
          f"{len(comp_exposure['time_scoped']['honored_attacker_authored'])} "
          "attacker-authored record")
    n_sev_moves = sum(1 for m in fed_moves["time_scoped"]
                      if m["to_moment"] == federation.MOMENTS[2][0])
    print(f"federation fixture: {len(fed_events)} mock-signed Events; the severance changes "
          f"{n_sev_moves} cell(s) under time-scoped (earlier imports remain included) and "
          f"{sum(1 for m in fed_moves['cascade'] if m['to_moment'] == federation.MOMENTS[2][0])} "
          f"under cascade")
    n_scope_only = sum(
        1 for a in approval_data["attempts"]
        if a["readings"]["scope_only"]["verdict"] == "signed")
    print(f"approval-return fixture: {len(approval_data['events'])} "
          "illustrative-Ed25519 Events; under proposal-bound all "
          f"{len(approval_data['attempts'])} attacker attempts refuse at sign time; "
          f"under the scope-only counterfactual {n_scope_only} would sign")
    print(f"wrote {os.path.relpath(out)} — open it in a browser")


if __name__ == "__main__":
    main()
