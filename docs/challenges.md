# Challenges

Problems hit while building SentinelPay and how they were solved. This feeds the "challenges I hit" section of the demo. Newest at the top. Never record secrets here.

## Template

### <short title> (<YYYY-MM-DD>)
- Symptom:
- Root cause:
- Fix:
- What I learned:

---

### Baseline model scored a perfect 1.0 (2026-11-03)
- Symptom: `train_baseline.py` reported PR-AUC 1.0, precision 1.0 and recall 1.0 on the test window, and `aucpr` was 1.00000 from the very first training round. Real fraud models are never perfect.
- Root cause: data leakage. The features `newbalanceOrig`, `newbalanceDest`, `errorBalanceOrig` and `errorBalanceDest` are only known after the transaction completes. The model was reading the outcome. `diagnose_leakage.py` showed `errorBalanceOrig` (0.593) and `newbalanceOrig` (0.366) dominating.
- Fix: compared three feature sets with the same model and split. Using pre-transaction features only gave PR-AUC 0.974 (precision 0.706, recall 0.982 at threshold 0.5). Adding two derived features (`amount_ratio`, `drains_account`) gave 0.998. Built `train_v1.py` on the pre-transaction set with train, validation and test windows, and chose the threshold on validation only. Final test numbers in `metrics_v1.json`: PR-AUC 0.997, precision 0.98, recall 0.98. Decision recorded in ADR-002.
- What I learned: a result that looks too good is a bug until proven otherwise. Ask "would I know this value at decision time?" for every feature. Keep the threshold choice and the final test on different data.
