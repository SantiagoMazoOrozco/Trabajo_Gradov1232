from sklearn.datasets import make_classification
import pandas as pd
import hashlib, json, time, os, argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-samples', type=int, default=3000, help='Número de filas a generar')
    ap.add_argument('--n-features', type=int, default=20, help='Número de columnas de atributos')
    ap.add_argument('--random-state', type=int, default=42, help='Semilla aleatoria')
    args = ap.parse_args()

    N_SAMPLES = args.n_samples
    N_FEATURES = args.n_features
    RANDOM_STATE = args.random_state

    X, y = make_classification(
        n_samples=N_SAMPLES,
        n_features=N_FEATURES,
        n_informative=8,
        n_redundant=4,
        n_repeated=0,
        n_classes=2,
        weights=[0.6, 0.4],
        class_sep=1.4,
        flip_y=0.01,
        random_state=RANDOM_STATE
    )

    df = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])])
    df["target"] = y

    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    csv_path = os.path.join(raw_dir, "synthetic_classification.csv")
    df.to_csv(csv_path, index=False)

    with open(csv_path, "rb") as fh:
        h = hashlib.sha256(fh.read()).hexdigest()

    meta = {
        "name": "synthetic_classification",
        "generator": "sklearn.make_classification",
        "params": {
            "n_samples": N_SAMPLES,
            "n_features": N_FEATURES,
            "n_informative": 8,
            "n_redundant": 4,
            "weights": [0.6, 0.4],
            "class_sep": 1.4,
            "flip_y": 0.01,
            "random_state": RANDOM_STATE
        },
        "rows": len(df),
        "cols": df.shape[1],
        "hash_sha256": h,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    with open(os.path.join(raw_dir, "synthetic_classification.meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print("Dataset congelado:")
    print(json.dumps(meta, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
