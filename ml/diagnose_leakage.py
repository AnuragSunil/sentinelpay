"""Compare feature sets to find leakage in the SentinelPay baseline.

Run from the ml/ folder (next to train_baseline.py):
    python diagnose_leakage.py --data data\\paysim.csv
"""
import argparse
from pathlib import Path

import xgboost as xgb
from sklearn.metrics import (
    average_precision_score,
    precision_score,
    recall_score,
)

from train_baseline import FEATURES, SPLIT_STEP, load_and_prepare

# Information available BEFORE the transaction completes
PRE_TXN = [
    "type_is_transfer",
    "amount",
    "oldbalanceOrg",
    "oldbalanceDest",
    "step_hour",
]
# Pre-transaction features plus two derived only from old balances
PRE_TXN_PLUS = PRE_TXN + ["amount_ratio", "drains_account"]

FEATURE_SETS = {
    "A_full (uses post-transaction balances)": FEATURES,
    "B_pre_txn_only": PRE_TXN,
    "C_pre_txn_plus_derived": PRE_TXN_PLUS,
}


def evaluate(name, cols, train, test):
    x_train, y_train = train[cols], train["isFraud"]
    x_test, y_test = test[cols], test["isFraud"]
    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=neg / pos,
        eval_metric="aucpr",
        tree_method="hist",
        n_jobs=-1,
    )
    model.fit(x_train, y_train, verbose=False)

    proba = model.predict_proba(x_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    print(f"\n=== {name} ===")
    print(f"PR-AUC:    {average_precision_score(y_test, proba):.4f}")
    print(f"Precision: {precision_score(y_test, pred, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(y_test, pred):.4f}")
    ranked = sorted(zip(cols, model.feature_importances_), key=lambda p: -p[1])
    print("Top features:")
    for col, score in ranked[:5]:
        print(f"  {col:<20} {score:.3f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    args = parser.parse_args()

    df = load_and_prepare(args.data)
    df["amount_ratio"] = df["amount"] / (df["oldbalanceOrg"] + 1)
    df["drains_account"] = (df["amount"] >= df["oldbalanceOrg"]).astype(int)

    train = df[df["step"] <= SPLIT_STEP]
    test = df[df["step"] > SPLIT_STEP]
    print(f"Train rows: {len(train)}, fraud: {int(train['isFraud'].sum())}")
    print(f"Test rows:  {len(test)}, fraud: {int(test['isFraud'].sum())}")

    for name, cols in FEATURE_SETS.items():
        evaluate(name, cols, train, test)


if __name__ == "__main__":
    main()