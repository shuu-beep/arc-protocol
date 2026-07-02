#!/usr/bin/env python3
"""ARC — one entry point for the executable probe catalog.

    python3 run_demos.py            run everything, one summary line each
    python3 run_demos.py --list     name, thesis, and path of every probe
    python3 run_demos.py <name>...  run the named probe(s), full output

Every probe is a single Python file, stdlib only, offline. The whole
catalog runs in roughly ten seconds. This runner adds nothing to any
probe — it only executes each file exactly as its own README says to,
so "run the demos" has one obvious front door.

Not included here (each for a stated reason, not an oversight):
  - examples/canon-ts               TypeScript compiler probe; needs tsc.
  - end-to-end-demo/agent_flow.py   optional live-model run; needs an API key.
  - reference-client/build.py       builds the browser client, not a probe.
"""

import subprocess
import sys
import time
from pathlib import Path

# (name, script path relative to repo root, one-line thesis)
# Ordered as a reading path: canon first, then authority/custody, then the
# fidelity wall, then the commerce catalog, then the adoption track.
CATALOG = [
    ("canon-fold", "examples/canon-fold-demo/demo.py",
     "scenarios fold a hand-built log; the five event types held"),
    ("end-to-end", "examples/end-to-end-demo/flow.py",
     "four parties sign their own events; standing moves only by ADJUDICATE"),
    ("coldstart", "examples/reference-client/coldstart_fixture.py",
     "legitimacy before anyone can know whom to trust"),
    ("approval-seam", "examples/reference-client/approval_seam_fixture.py",
     "the escalation return path as a custody surface"),
    ("compromise", "examples/reference-client/compromise_fixture.py",
     "a stolen hot key, and the exact size of the damage (real Ed25519)"),
    ("threshold", "examples/threshold-authority-demo/probe.py",
     "M-of-N joint authority — the question key-custody §8 leaves open"),
    ("revocation", "examples/authority-revocation-demo/probe.py",
     "what revocation does to an action that already completed"),
    ("cache", "examples/cache-discipline-demo/probe.py",
     "the anti-social-credit claim is contingent on cache shape"),
    ("federation", "examples/federation-fidelity-demo/probe.py",
     "does a federation bridge launder a drifted signer's act?"),
    ("temporal", "examples/temporal-fidelity-demo/probe.py",
     "a valid signature does not prove the stamped timestamp is true"),
    ("execution", "examples/execution-fidelity-demo/probe.py",
     "a signed fulfillment asserts the world; the log cannot recover its truth"),
    ("view", "examples/view-fidelity-demo/probe.py",
     "WYSINWYS — a signature seals the signed bytes, not the displayed view"),
    ("commerce", "examples/local-commerce-demo/episode.py",
     "eight failure runs [A]-[H]: a byte-valid record is not a legitimate one"),
    ("refusal", "examples/refusal-recording-demo/refusal_fold.py",
     "adoption does not fold; refusals can"),
]

HERE = Path(__file__).resolve().parent


def run_one(script, stream):
    """Run a probe exactly as its README does: python3 <file>, from its dir."""
    path = HERE / script
    return subprocess.run(
        [sys.executable, path.name],
        cwd=path.parent,
        capture_output=not stream,
        text=True,
    )


def main(argv):
    if "--list" in argv or "-l" in argv:
        for name, script, thesis in CATALOG:
            print(f"  {name:<14} {thesis}")
            print(f"  {'':<14} {script}")
        return 0

    names = [a for a in argv if not a.startswith("-")]
    unknown = [n for n in names if n not in {c[0] for c in CATALOG}]
    if unknown:
        print(f"unknown probe(s): {', '.join(unknown)}  (try --list)")
        return 2

    if names:
        # Full output, exactly what running the file by hand would show.
        failed = 0
        for name, script, _ in CATALOG:
            if name not in names:
                continue
            print(f"\n{'=' * 72}\n  {name}  ({script})\n{'=' * 72}\n")
            failed += run_one(script, stream=True).returncode != 0
        return 1 if failed else 0

    # Default: run the whole catalog, one line per probe.
    print("ARC — executable probe catalog")
    print(f"{len(CATALOG)} probes, stdlib only, offline. "
          "Full output: python3 run_demos.py <name>\n")
    failures = []
    for name, script, thesis in CATALOG:
        t0 = time.monotonic()
        proc = run_one(script, stream=False)
        dt = time.monotonic() - t0
        status = "ok  " if proc.returncode == 0 else "FAIL"
        print(f"  {status}  {name:<14} {dt:4.1f}s  {thesis}")
        if proc.returncode != 0:
            failures.append((name, proc))
    if failures:
        for name, proc in failures:
            tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-15:])
            print(f"\n--- {name} failed (exit {proc.returncode}), last lines ---")
            print(tail)
        return 1
    print("\nAll probes ran. Each is a single file; read it next to its README.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
