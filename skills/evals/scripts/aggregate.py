#!/usr/bin/env python3
"""Aggregate eval run results into metrics WITH variance — the number that matters.

LLM outputs are stochastic, so a single run of an eval is noise dressed up as a
result. This script takes the per-case, per-run scores your runner produced and
reports the mean, the spread (stdev), a 95% confidence interval, and the
pass-rate at a threshold — plus it flags the *flaky* cases whose score changes
from run to run, which a single-number report hides entirely.

The runner that actually calls your product is project-specific (its stack, its
API) so you write that; this aggregation is the same everywhere, so it's bundled.

Input — JSONL, one record per case-run:
  {"case": "ticket_042", "score": 1}            # score: 0/1 or a 0..1 float
  {"case": "ticket_042", "score": 0, "run": 2}  # repeat the case to add runs
  {"case": "ticket_017", "score": 0.5, "label": "partial"}

Usage:
  python aggregate.py results.jsonl [--threshold 0.5] [--json]
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

try:  # emit UTF-8 regardless of the console's default codepage (Windows cp1252)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


def load(path):
    rows = []
    text = Path(path).read_text(encoding="utf-8")
    for i, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            sys.exit(f"Bad JSON on line {i}: {e}")
    return rows


def stats(values):
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": 0.0, "stdev": 0.0, "ci95": 0.0}
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    sd = math.sqrt(var)
    sem = sd / math.sqrt(n) if n > 1 else 0.0
    return {"n": n, "mean": mean, "stdev": sd, "ci95": 1.96 * sem}


def aggregate(rows, threshold):
    by_case = defaultdict(list)
    for r in rows:
        if "case" not in r or "score" not in r:
            continue
        by_case[r["case"]].append(float(r["score"]))

    all_scores = [s for v in by_case.values() for s in v]
    overall = stats(all_scores)

    per_case = {}
    flaky = []
    for case, scores in by_case.items():
        cs = stats(scores)
        per_case[case] = cs
        # flaky = multiple runs that don't agree (some pass, some fail at threshold)
        passes = [s >= threshold for s in scores]
        if len(scores) > 1 and any(passes) and not all(passes):
            flaky.append((case, scores))

    case_means = [c["mean"] for c in per_case.values()]
    pass_rate = (sum(1 for m in case_means if m >= threshold) / len(case_means)
                 if case_means else 0.0)
    runs_per_case = sorted({c["n"] for c in per_case.values()})

    return {
        "cases": len(per_case),
        "runs_per_case": runs_per_case,
        "overall": overall,
        "pass_rate": pass_rate,
        "threshold": threshold,
        "flaky": flaky,
        "per_case": per_case,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Aggregate eval results with variance.")
    ap.add_argument("results")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    rows = load(args.results)
    agg = aggregate(rows, args.threshold)
    if not agg["cases"]:
        sys.exit("No usable records (need objects with 'case' and 'score').")

    if args.json:
        out = dict(agg)
        out["flaky"] = [{"case": c, "scores": s} for c, s in agg["flaky"]]
        print(json.dumps(out, indent=2))
        return 0

    o = agg["overall"]
    multi = max(agg["runs_per_case"]) > 1
    print(f"Cases: {agg['cases']}   Runs/case: {agg['runs_per_case']}")
    print(f"Mean score: {o['mean']:.3f}"
          + (f"  ±{o['ci95']:.3f} (95% CI)   stdev {o['stdev']:.3f}" if multi
             else "   (single run — variance unknown; run each case 3-5x)"))
    print(f"Pass-rate @ {agg['threshold']:.2f}: {agg['pass_rate']*100:.1f}% of cases")
    if not multi:
        print("\n⚠  One run per case. LLM scores are stochastic — a single run is "
              "noise. Re-run each case several times to get a trustworthy mean + CI.")
    if agg["flaky"]:
        print(f"\n⚠  Flaky cases ({len(agg['flaky'])}) — pass on some runs, fail on others:")
        for case, scores in agg["flaky"]:
            print(f"   • {case}: {scores}")
    worst = sorted(agg["per_case"].items(), key=lambda kv: kv[1]["mean"])[:5]
    print("\nLowest-scoring cases:")
    for case, cs in worst:
        print(f"   • {case}: {cs['mean']:.2f} (n={cs['n']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
