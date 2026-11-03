# ADR-002: Why the scoring service only uses pre-transaction features

- Status: Accepted
- Date: 2026-11-03

## Context
Training time and decision time are different moments. At training time we hold the whole finished dataset, including what each transaction did to the balances afterwards. At decision time the transaction has not happened yet, so the scoring service can only see what exists before it: the type, the amount, the sender's and receiver's old balances, and the hour. Our first baseline used the new balances and two "balance error" features built from them. It scored a perfect 1.0 PR-AUC, precision and recall. That is not a great model, it is a leak: those columns record the outcome of the transaction, and the model reads the answer from them. A leakage check confirmed it. `errorBalanceOrig` and `newbalanceOrig` carried about 96% of the importance.

## Decision
Model v1 may only use features that are known before the transaction completes: `type_is_transfer`, `amount`, `oldbalanceOrg`, `oldbalanceDest`, `step_hour`, plus `amount_ratio` and `drains_account`, which are derived only from those old values. The exact list and order are saved in `feature_spec_v1.json` so the scoring service and training use the same contract. Training also uses a time-based split (train, then validation to choose the threshold, then a test window used once).

## Trade-offs
- Gain: the metrics are honest. v1 gets PR-AUC 0.997 and precision and recall of 0.98 on the held-out future window, instead of a fake 1.0.
- Gain: the model can actually be called before a payment is approved, which is the whole point of fraud detection.
- Cost: lower scores than the leaky baseline, and fewer signals to work with.
- Cost: `drains_account` and `amount_ratio` lean on a pattern in synthetic data (fraud empties the sender's account), so real-world performance is unproven.
- Cost: v1 only scores TRANSFER and CASH_OUT. Other transaction types are meant to go to a rules engine, which has not been built yet, so that traffic is currently unscored.
- Cost: every new feature needs a "was this known at decision time?" check, which is a review step we must keep doing.
