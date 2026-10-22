# Task 6 — Numbers that did not match

## Item 1: "large" = 500 (Table II) vs 1000 (Section V)

Already consistent once checked: the setup bullet and Table II both use
small=10, medium=100, large=500, xlarge=1000, and Section V-F quotes raw
task counts. To make the mapping explicit, V-F now says "DAGs of 10,
100, and 1000 tasks (the small, medium, and extra-large scales of
Table II)".

## Item 2: small bound 1.637 (Table II) vs 1.41 (Fig. 5)

Different instances, already explained in two places: after Table II
("these use fixed seeded instances that differ from the replication
instances...") and in V-F ("generated per replication with different
seeds... about 1.41 at 10 tasks here vs. 1.637 on the small test
dataset"). Verified: mean bound at n=10 in size.csv = 1.409 ≈ 1.41;
small test-dataset score = 1.637 = bound.

## Item 3: MILP makespan longer than greedy's

Already in the text after Table II: "the MILP maximizes accuracy, not
makespan: on the medium dataset it and the greedy reach the same score
while their makespans differ (60.94 vs. 43.11)..." Verified against
test_runs.csv (60.939 vs 43.109).

## Verification

`check_numbers.py` compares 17 quoted numbers against the result CSVs;
all match. Output: `number_check.csv` (0 mismatches).
