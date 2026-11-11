#!/usr/bin/env python3
"""Score a Shot List Coverage report against the expected results.

Usage:
    python3 demo/score_report.py REPORT.md demo/expected/expected-full.csv

REPORT.md is the saved coverage report, or the report text copied from the
conversation into a file. The script reads the "All shots" table, compares the
status of each shot with the expected status, and checks the "Missing must-have
shots" section.

Exit code 0 when every shot passes, 1 when a shot fails, 2 on bad input.
"""
import csv
import re
import sys
from pathlib import Path

STATUSES = {"covered", "weak", "missing", "not checked"}


def parse_report(text):
    """Return ({shot: status}, set of shots listed under Missing must-have shots)."""
    statuses = {}
    header = None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            header = None if not line.strip() else header
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        lowered = [c.lower() for c in cells]
        if "status" in lowered and "#" in cells:
            header = lowered
            continue
        if header is None or set(line.replace("|", "").strip()) <= set("-: "):
            continue
        row = dict(zip(header, cells))
        num = re.sub(r"\D", "", row.get("#", ""))
        status = row.get("status", "").strip("*_ ").lower()
        if num and status in STATUSES:
            statuses[int(num)] = status
    flagged = set()
    section = re.search(r"#+\s*Missing must-have shots\s*\n(.*?)(?:\n#+\s|\Z)", text, re.S | re.I)
    if section:
        flagged = {int(m) for m in re.findall(r"^\s*[-*]\s*(\d+)\.", section.group(1), re.M)}
    return statuses, flagged


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    report_path, expected_path = Path(sys.argv[1]), Path(sys.argv[2])
    try:
        statuses, flagged = parse_report(report_path.read_text())
        expected = list(csv.DictReader(expected_path.open()))
    except OSError as err:
        print(f"Cannot read input: {err}")
        return 2
    if not statuses:
        print("No 'All shots' table with # and Status columns was found in the report.")
        return 2

    failures = 0
    false_covered = 0
    print(f"{'#':>3}  {'expected':<12} {'report':<12} result  shot")
    for row in expected:
        num = int(row["shot"])
        want = row["expected_status"]
        ok_set = {want} | ({row["also_ok"]} if row["also_ok"] else set())
        got = statuses.get(num, "absent")
        passed = got in ok_set
        if got == "covered" and want != "covered":
            false_covered += 1
        failures += not passed
        mark = "PASS" if passed else "FAIL"
        print(f"{num:>3}  {want:<12} {got:<12} {mark:<6}  {row['text']}")

    must_problems = {int(r["shot"]) for r in expected if r["must_have"] == "yes" and r["expected_status"] != "covered"}
    missing_flags = must_problems - flagged
    total = len(expected)
    print()
    print(f"Shots passed: {total - failures} of {total}")
    print(f"Shots marked covered that should not be: {false_covered}  (the most serious error)")
    if must_problems:
        print(f"Must-have problems listed at the top: {len(must_problems & flagged)} of {len(must_problems)}"
              + (f"  (not listed: {sorted(missing_flags)})" if missing_flags else ""))
    extra = sorted(set(statuses) - {int(r['shot']) for r in expected})
    if extra:
        print(f"Report has shots that are not in the expected file: {extra}")
    return 0 if failures == 0 and not missing_flags else 1


if __name__ == "__main__":
    sys.exit(main())
