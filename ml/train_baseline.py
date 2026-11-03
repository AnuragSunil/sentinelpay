"""SentinelPay baseline fraud model (PaySim dataset).

Run from the ml/ folder:
    python train_baseline.py --data data/PS_20174392719_1491204439457_log.csv
Outputs:
    models/fraud_xgb_v1.json   (the trained model)
    models/metrics_v1.json     (evaluation numbers + feature list)
"""
import argparse
import json
from pathlib import Path

import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)

FEATURES = [
    "type_is_transfer",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "errorBalanceOrig",
    "errorBalanceDest",
    "step_hour",
]
SPLIT_STEP = 600  # train on steps <= 600, test on the "future" (> 600)


def load_and_prepare(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # In PaySim, fraud only happens in TRANSFER and CASH_OUT. Other types are
    # left to the rules engine later (a deliberate modelling decision).
    df = df[df["type"].isin(["TRANSFER", "CASH_OUT"])].copy()
    df["type_is_transfer"] = (df["type"] == "TRANSFER").astype(int)
    df["errorBalanceOrig"] = df["newbalanceOrig"] + df["amount"] - df["oldbalanceOrg"]
    df["errorBalanceDest"] = df["oldbalanceDest"] + df["amount"] - df["newbalanceDest"]
    df["step_hour"] = df["step"] % 24
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    args = parser.parse_args()

    df = load_and_prepare(args.data)

    # Time-based split: a random split would leak the future into training.
    train = df[df["step"] <= SPLIT_STEP]
    test = df[df["step"] > SPLIT_STEP]
    x_train, y_train = train[FEATURES], train["isFraud"]
    x_test, y_test = test[FEATURES], test["isFraud"]

    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=neg / pos,  # fraud is very rare, so weight it up
        eval_metric="aucpr",
        tree_method="hist",
        n_jobs=-1,
    )
    model.fit(x_train, y_train, eval_set=[(x_test, y_test)], verbose=50)

    proba = model.predict_proba(x_test)[:, 1]
    pr_auc = average_precision_score(y_test, proba)

    # Threshold that gives the best F1 on the test period
    prec, rec, thr = precision_recall_curve(y_test, proba)
    f1 = (2 * prec * rec) / (prec + rec + 1e-12)
    best = int(f1[:-1].argmax())
    best_thr = float(thr[best])

    pred_default = (proba >= 0.5).astype(int)
    pred_best = (proba >= best_thr).astype(int)

    metrics = {
        "rows_train": int(len(train)),
        "rows_test": int(len(test)),
        "fraud_rate_train": float(y_train.mean()),
        "fraud_rate_test": float(y_test.mean()),
        "pr_auc": float(pr_auc),
        "at_0.5": {
            "precision": float(precision_score(y_test, pred_default, zero_division=0)),
            "recall": float(recall_score(y_test, pred_default)),
        },
        "at_best_f1": {
            "threshold": best_thr,
            "precision": float(precision_score(y_test, pred_best, zero_division=0)),
            "recall": float(recall_score(y_test, pred_best)),
        },
        "features": FEATURES,
    }

    out = Path("models")
    out.mkdir(exist_ok=True)
    model.save_model(out / "fraud_xgb_v1.json")
    (out / "metrics_v1.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()