# Paired context length sensitivity

Compare 2, 4 and 8 known observations on EACH side of the same artificial outage.
This follow-up uses only chronological development and validation partitions.
No test data is used. Seed 3002 selects up to 30 nonoverlapping full-context masks
per sensor/split/duration. All contexts and methods share those masks.

## Distinct eligibility protocol

The hidden core and immediate bracketing intervals must be <=1.5 median cadences.
The wider observed context may have intervals <=3 median cadences and must provide
eight valid observations on each side. This is an explicit protocol change from
the original strict whole-context benchmark. Candidate selection uses timestamps
only. Compare contexts within this paired pool, not these errors against the old
benchmark as if they used the same cases.

## Validation mean MAE in deg C

| Gap min | Method | 2 nodes | 4 nodes | 8 nodes |
|---:|---|---:|---:|---:|
| 30 | forward_fill | 0.158333 | 0.158333 | 0.158333 |
| 30 | linear | 0.093457 | 0.093457 | 0.093457 |
| 30 | cubic | 0.115468 | 0.124258 | 0.125114 |
| 30 | pchip | 0.090570 | 0.090570 | 0.090570 |
| 60 | forward_fill | 0.277460 | 0.277460 | 0.277460 |
| 60 | linear | 0.147952 | 0.147952 | 0.147952 |
| 60 | cubic | 0.130941 | 0.147578 | 0.148020 |
| 60 | pchip | 0.117704 | 0.117704 | 0.117704 |

All four sensor/split/duration groups selected 30 windows. The mean MAEs of
forward fill and linear interpolation do not change because only their nearest
relevant nodes affect predictions. PCHIP interior slopes also depend locally on
neighbouring secants, already available with two nodes on each side. The natural
cubic spline depends on the full context and its outer boundary conditions, so
its predictions change. In this validation sample, increasing its context worsens
mean MAE rather than improving it. No statistical significance is claimed.

A practical design is to retain linear interpolation as the simple fast reference
and use local PCHIP when its error reduction justifies extra computation. Two
context nodes suffice for the PCHIP predictions in this study; this is a validated
configuration comparison, not new independent test confirmation. The primary
four-node benchmark remains unchanged for traceability.

Files in results/sensitivity record settings, coverage, each window score, summary
and context_comparison.png. Reproduce using python sensitivity_analysis.py after
preparing the original data.
