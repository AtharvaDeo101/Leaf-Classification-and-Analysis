
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

NON_FEATURE_COLS = ("image_id", "label", "margin_type", "seg_method")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path,
                    default=Path("data/processed/features_v1.csv"))
    ap.add_argument("--out", type=Path, default=Path("artifacts"))
    ap.add_argument("--test-size", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    feature_names = [c for c in df.columns if c not in NON_FEATURE_COLS]
    # A constant or all-NaN descriptor carries no signal and breaks scaling.
    X = np.nan_to_num(df[feature_names].to_numpy(dtype=np.float64),
                      nan=0.0, posinf=0.0, neginf=0.0)
    y = df["label"].astype(str).to_numpy()

    print(f"{len(df)} samples, {len(feature_names)} features, "
          f"{len(set(y))} classes")

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed, stratify=y)

    scaler = StandardScaler().fit(X_tr)
    X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)

    args.out.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("svm_bundle.joblib", SVC(C=10, gamma="scale", probability=True,
                                  random_state=args.seed), scaler),
        ("rf_bundle.joblib", RandomForestClassifier(
            n_estimators=500, n_jobs=-1, random_state=args.seed), None),
    ]

    for fname, model, sc in jobs:
        tr, te = (X_tr_s, X_te_s) if sc is not None else (X_tr, X_te)
        model.fit(tr, y_tr)
        pred = model.predict(te)
        metrics = {
            "accuracy": float(accuracy_score(y_te, pred)),
            "macro_f1": float(f1_score(y_te, pred, average="macro")),
            "n_train": len(y_tr),
            "n_test": len(y_te),
        }
        joblib.dump({"model": model, "scaler": sc,
                     "feature_names": feature_names,
                     "classes": list(model.classes_),
                     "metrics": metrics}, args.out / fname)
        print(f"{fname}: acc={metrics['accuracy']:.3f} "
              f"macro_f1={metrics['macro_f1']:.3f}")

        # Round-trip through the loader the API actually uses: catches a
        # feature-order or classes mismatch here instead of at inference.
        from backend.app.services.registry import LoadedModel
        loaded = LoadedModel(fname, "classical", joblib.load(args.out / fname))
        top = loaded.predict(dict(zip(feature_names, X_te[0])), top_k=1)
        assert top[0]["label"] == pred[0], f"{fname} round-trip mismatch"

    return 0


if __name__ == "__main__":
    sys.exit(main())
