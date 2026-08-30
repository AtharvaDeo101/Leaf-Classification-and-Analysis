# Leafprint

Identifies 32 plant species from a photograph of a single leaf, using 155
hand-engineered shape, texture and colour descriptors — no neural network.
Every number in a result traces back to something measurable on the leaf.

- **98.2%** held-out accuracy (SVM, RBF kernel), 95.8% (random forest)
- **1,906** reference scans across 32 species, from the Flavia dataset
- FastAPI backend, Next.js frontend

## How it works

A leaf goes through four stages, each consuming the previous one's output:

| # | Stage | What happens |
|---|-------|--------------|
| 01 | `original` | Resized to an 800px working frame |
| 02 | `mask_raw` | Leaf separated from background (Lab-a\* or excess-green threshold, whichever gives the cleaner border) |
| 03 | `mask_final` | Petiole removed, blade rotated so its major axis is horizontal |
| 04 | `descriptors` | Contour, convex hull, fitted ellipse and lobe notches |

155 descriptors are then extracted from the mask and contour:

| Family | Count | What it captures |
|--------|-------|------------------|
| `efd_` | 36 | Elliptic Fourier descriptors of the outline |
| `zernike_` | 25 | Zernike moments |
| `ccd_` | 18 | Centroid-distance profile |
| `color_` | 18 | Channel statistics inside the mask |
| `geo_` | 17 | Area, perimeter, solidity, elongation, circularity |
| `glcm_` | 11 | Grey-level co-occurrence texture |
| `lbp_` | 10 | Local binary patterns |
| `hu_` | 7 | Hu invariant moments |
| `vein_` | 7 | Vein density and branching |
| `margin_` | 6 | Tooth depth and periodicity along the edge |

### Refusing to guess

A 32-class model returns one of its 32 classes for *any* input, so without a
guard a photo of anything at all gets named a species. Each model bundle
carries a novelty check: the distance from a specimen to the nearest reference
leaf in standardised feature space. Past a threshold, the API measures the
image but declines to name it.

Measured on this dataset:

| Input | Distance | Outcome |
|-------|----------|---------|
| Held-out leaves (n=382) | median 4.3, max 21.8 | all accepted |
| A leaf *icon* (flat vector art) | 29.7 | refused |
| Star, hand, cat, text, bottle shapes | 59–82 | refused |
| Random noise | — | refused earlier, at segmentation |

The threshold sits at **26.3**. It is calibrated on Flavia's clean scans, where
leaves sit flat on plain white. A genuine leaf photographed on a busy
background scores higher and may be wrongly turned away — if that happens,
raise `NOVELTY_SLACK` in `src/training/train.py` and retrain. The training
output prints what fraction of held-out leaves the new value rejects.

## Setup

Requires Python 3.12 and Node with pnpm.

```bash
python -m venv .venv
```

```bash
.venv\Scripts\pip install -r requirements.txt
```

```bash
pnpm --dir frontend install
```

### Get the dataset

`archive/`, `data/`, `artifacts/`, `storage/` and `.env` are all gitignored, so
a fresh clone has no dataset and no trained models. Download the
[Flavia leaf dataset](https://flavia.sourceforge.net/) and place it so that
images and their labels sit at:

```
archive/Leaves/*.jpg
archive/Leaves/all.csv     # columns: id, y
```

### Configure

Create `.env` in the project root:

```
DATABASE_URL=sqlite:///./storage/leaf.db
STORAGE_DIR=./storage
ARTIFACTS_DIR=./artifacts
MAX_UPLOAD_MB=10
WORK_SIZE=800
CORS_ORIGINS=["http://localhost:3000"]
```

`CORS_ORIGINS` must list the frontend's origin, or the browser silently discards
every response — requests return 200 and the UI still shows a connection error.

## Build the model

Extract features for the whole dataset (~30 min for 1,907 images):

```bash
python -m src.training.extract_dataset
```

Writes `data/processed/features_v1.csv`. Freeze it — re-running after editing
descriptor code produces a file that is not comparable with earlier
experiments, so bump the version in the filename when features change
deliberately. One scan (`2347.jpg`) fails segmentation and is excluded;
failures are listed in `features_v1.failures.csv`.

Then train:

```bash
python -m src.training.train
```

Writes `artifacts/svm_bundle.joblib` and `artifacts/rf_bundle.joblib`, prints
held-out accuracy and the novelty threshold. Each bundle round-trips through
the API's own loader before finishing, so a feature-order or class mismatch
fails here rather than at inference.

## Run

```bash
uvicorn backend.app.main:app --port 8000
```

```bash
pnpm --dir frontend dev
```

Frontend at http://localhost:3000, interactive API docs at
http://localhost:8000/docs. Watch the startup log for
`Loaded model 'svm' (32 classes)` — if it says the artifact was not found, run
the training step above.



## Notes

- Species names and their file ranges come from the
  [official Flavia table](https://flavia.sourceforge.net/), cross-checked
  against the image-number ranges in `all.csv`. The `family` and `margin_type`
  fields in `backend/app/data/species.json` were filled in separately and are
  descriptive rather than authoritative.
- Class labels in `all.csv` are **not** in image-number order — label 2 is
  images 1552–1616, label 9 is 1438–1496. Don't assume a monotonic mapping.
- `to_vector` reorders features by the names saved in the bundle rather than by
  dict order. That is what stops a silent accuracy collapse when the pipeline
  gains a new descriptor.
