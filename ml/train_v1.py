"""SentinelPay fraud model v1: pre-transaction features only.

Run from the ml/ folder:
    python train_v1.py --data data\\paysim.csv
Outputs (in models/):
    fraud_xgb_v1.json       the trained model
    metrics_v1.json         final evaluation on the held-out future window
    feature_spec_v1.json    the contract: feature names, order, threshold
"""
import argparse
import json
from pathlib import Path

import xgboost as xgb
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)

from train_baseline import load_and_prepare

# Every feature here is known BEFORE the transaction completes.
FEATURES_V1 = [
    "type_is_transfer",
    "amount",
    "oldbalanceOrg",
    "oldbalanceDest",
    "step_hour",
    "amount_ratio",
    "drains_account",
]
TRAIN_END = 500  # train:      step <= 500
VAL_END = 600    # validation: 500 < step <= 600 (used to pick threshold)
                 # test:       step > 600 (touched once, for final numbers)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    args = parser.parse_args()

    df = load_and_prepare(args.data)
    df["amount_ratio"] = df["amount"] / (df["oldbalanceOrg"] + 1)
    df["drains_account"] = (df["amount"] >= df["oldbalanceOrg"]).astype(int)

    train = df[df["step"] <= TRAIN_END]
    val = df[(df["step"] > TRAIN_END) & (df["step"] <= VAL_END)]
    test = df[df["step"] > VAL_END]

    x_train, y_train = train[FEATURES_V1], train["isFraud"]
    x_val, y_val = val[FEATURES_V1], val["isFraud"]
    x_test, y_test = test[FEATURES_V1], test["isFraud"]

    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=neg / pos,
        eval_metric="aucpr",
        tree_method="hist",
        n_jobs=-1,
    )
    model.fit(x_train, y_train, verbose=False)

    # Pick the decision threshold on the validation window (best F1)
    val_proba = model.predict_proba(x_val)[:, 1]
    prec, rec, thr = precision_recall_curve(y_val, val_proba)
    f1 = (2 * prec * rec) / (prec + rec + 1e-12)
    threshold = float(thr[int(f1[:-1].argmax())])

    # Final, honest numbers on the untouched future window
    test_proba = model.predict_proba(x_test)[:, 1]
    pred = (test_proba >= threshold).astype(int)

    metrics = {
        "model_version": "v1",
        "rows": {"train": len(train), "val": len(val), "test": len(test)},
        "fraud_in": {
            "train": int(y_train.sum()),
            "val": int(y_val.sum()),
            "test": int(y_test.sum()),
        },
        "threshold_chosen_on_validation": threshold,
        "test": {
            "pr_auc": float(average_precision_score(y_test, test_proba)),
            "precision": float(precision_score(y_test, pred, zero_division=0)),
            "recall": float(recall_score(y_test, pred)),
        },
    }
    spec = {
        "model_version": "v1",
        "features": FEATURES_V1,
        "threshold": threshold,
        "notes": "All features available before the transaction completes.",
    }

    out = Path("models")
    out.mkdir(exist_ok=True)
    model.save_model(out / "fraud_xgb_v1.json")
    (out / "metrics_v1.json").write_text(json.dumps(metrics, indent=2))
    (out / "feature_spec_v1.json").write_text(json.dumps(spec, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()