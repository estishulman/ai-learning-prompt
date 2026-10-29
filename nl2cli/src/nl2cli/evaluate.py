"""Run all scenarios against a prompt version and write results/iteration_N.csv
(ready to import as a sheet into Google Sheets).

Automatic columns: format_ok, syntax_ok, safety_status, safety_match.
Manual columns (fill by hand): correct (תקין/שגוי), notes.
"""
import argparse
import csv
from . import config
from .agent import to_command
from .safety import format_ok, syntax_plausible

FIELDS = ["id", "category", "input", "expected", "output", "format_ok", "syntax_ok",
          "safety_status", "expected_safety", "safety_match", "correct", "notes"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteration", type=int, required=True)
    ap.add_argument("--prompt", required=True, help="e.g. v1")
    ap.add_argument("--scenarios", default=str(config.SCENARIOS_DIR / "scenarios.csv"))
    args = ap.parse_args()

    out_path = config.RESULTS_DIR / f"iteration_{args.iteration}.csv"
    rows = []
    with open(args.scenarios, encoding="utf-8-sig", newline="") as f:
        for sc in csv.DictReader(f):
            try:
                res = to_command(sc["input"], args.prompt)
                raw, status = res["raw"], res["status"]
            except Exception as e:
                raw, status = f"ERROR: {e}", "ERROR"
            expected_safety = sc["expected_safety"]
            rows.append({
                "id": sc["id"], "category": sc["category"], "input": sc["input"],
                "expected": sc["expected"], "output": raw,
                "format_ok": int(format_ok(raw)),
                "syntax_ok": int(syntax_plausible(raw, config.TARGET_OS)),
                "safety_status": status, "expected_safety": expected_safety,
                "safety_match": int(status == expected_safety),
                "correct": "", "notes": "",
            })
            print(f"[{sc['id']}] {sc['input'][:50]!r} -> {raw!r} ({status})")

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    print(f"\nSaved {out_path}")
    for m in ("format_ok", "syntax_ok", "safety_match"):
        print(f"{m}: {sum(r[m] for r in rows)}/{n}")


if __name__ == "__main__":
    main()
