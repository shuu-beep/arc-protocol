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
# fidelity checks, then the commerce catalog, then the adoption track.
CATALOG = [
    ("canon-fold", "examples/canon-fold-demo/demo.py",
     "authored scenarios fold a fixture log using the current five event types"),
    ("end-to-end", "examples/end-to-end-demo/flow.py",
     "scripted parties emit mock-signed records; one named standing fold reads ADJUDICATE"),
    ("coldstart", "examples/reference-client/coldstart_fixture.py",
     "three illustrative cold-start strategies under named observer policies"),
    ("approval-seam", "examples/reference-client/approval_seam_fixture.py",
     "in-process proposal binding on an escalation return path"),
    ("compromise", "examples/reference-client/compromise_fixture.py",
     "fixture-classified exposure after a modeled hot-key compromise"),
    ("threshold", "examples/threshold-authority-demo/probe.py",
     "one fixture-local M-of-N evidence-counting policy"),
    ("revocation", "examples/authority-revocation-demo/probe.py",
     "two current-honoring readings after a recorded withdrawal"),
    ("cache", "examples/cache-discipline-demo/probe.py",
     "stale and cross-context reuse under three cache-keying strategies"),
    ("federation", "examples/federation-fidelity-demo/probe.py",
     "matching recognition under binding, advisory, and ignored fixture readings"),
    ("temporal", "examples/temporal-fidelity-demo/probe.py",
     "the mock-signature check does not establish timestamp truth"),
    ("execution", "examples/execution-fidelity-demo/probe.py",
     "a mock-signed fulfillment claim does not establish its world referent"),
    ("view", "examples/view-fidelity-demo/probe.py",
     "a record commitment does not establish the view displayed or understood"),
    ("commerce", "examples/local-commerce-demo/episode.py",
     "eight fixture runs [A]-[H] under named Commerce review policies"),
    ("refusal", "examples/refusal-recording-demo/refusal_fold.py",
     "records and groups authored refusal records; does not validate adoption"),
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
