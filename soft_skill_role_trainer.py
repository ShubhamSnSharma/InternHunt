import argparse
import json
import re
from collections import Counter
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline


DEFAULT_CSV = "UpdatedResumeDataSet.csv"
DEFAULT_MODEL = "resume_classifier_v3_skills_mlp.pkl"
TEXT_COL = "Resume"
LABEL_COL = "Category"
RANDOM_STATE = 42
TEST_SIZE = 0.2
MIN_SAMPLES_PER_CLASS = 3

SKILL_HEADINGS = [
    "skills",
    "skill details",
    "technical skills",
    "technical proficiency",
    "technical expertise",
    "core competencies",
    "technologies",
    "tools & technologies",
    "software proficiency",
    "skill set",
]

STOP_HEADINGS = [
    "education",
    "education details",
    "experience",
    "work experience",
    "employment history",
    "professional experience",
    "company details",
    "projects",
    "project details",
    "certification",
    "certifications",
    "achievements",
    "responsibilities",
    "declaration",
    "personal details",
    "objective",
    "summary",
]


def clean_text(text: str) -> str:
    text = str(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_for_grouping(text: str) -> str:
    text = clean_text(text).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compile_heading_regex(headings):
    escaped = [re.escape(h) for h in headings]
    return re.compile(r"(?i)\b(?:%s)\b\s*:?" % "|".join(escaped))


SKILL_RE = compile_heading_regex(SKILL_HEADINGS)
STOP_RE = compile_heading_regex(STOP_HEADINGS)


def extract_skill_text(resume_text: str) -> str:
    text = clean_text(resume_text)
    lower_text = text.lower()
    snippets = []

    for match in SKILL_RE.finditer(lower_text):
        start = match.start()
        next_stop = STOP_RE.search(lower_text, match.end())
        end = next_stop.start() if next_stop else min(len(text), match.end() + 1200)
        chunk = text[start:end].strip(" :-")
        if chunk:
            snippets.append(chunk)

    if not snippets:
        boundary = STOP_RE.search(lower_text)
        fallback = text[: boundary.start()] if boundary else text[:1200]
        snippets.append(fallback)

    merged = " ".join(snippets)
    merged = re.sub(r"\bexprience\b", "experience", merged, flags=re.IGNORECASE)
    merged = re.sub(r"\bmonths?\b", " ", merged, flags=re.IGNORECASE)
    merged = re.sub(r"\bcompany details\b.*", " ", merged, flags=re.IGNORECASE)
    merged = re.sub(r"\s+", " ", merged).strip()
    return merged


def prepare_dataset(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)[[TEXT_COL, LABEL_COL]].dropna().copy()
    df["resume_clean"] = df[TEXT_COL].map(clean_text)
    df["group_key"] = df["resume_clean"].map(normalize_for_grouping)
    df["skills_text"] = df["resume_clean"].map(extract_skill_text)

    deduped = (
        df.sort_values([LABEL_COL, "group_key"])
        .drop_duplicates(subset=["group_key", LABEL_COL])
        .reset_index(drop=True)
    )

    counts = deduped[LABEL_COL].value_counts()
    valid_classes = counts[counts >= MIN_SAMPLES_PER_CLASS].index
    filtered = deduped[deduped[LABEL_COL].isin(valid_classes)].reset_index(drop=True)
    return filtered


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=2500,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95,
                    sublinear_tf=True,
                    stop_words="english",
                    lowercase=True,
                ),
            ),
            (
                "clf",
                MLPClassifier(
                    hidden_layer_sizes=(128, 64),
                    activation="relu",
                    solver="adam",
                    alpha=1e-4,
                    learning_rate_init=0.001,
                    max_iter=800,
                    tol=1e-4,
                    early_stopping=False,
                    n_iter_no_change=20,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def top_confusions(y_true, y_pred, labels):
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    pairs = []
    for i, actual in enumerate(labels):
        for j, predicted in enumerate(labels):
            if i != j and matrix[i, j] > 0:
                pairs.append(
                    {
                        "actual": actual,
                        "predicted": predicted,
                        "count": int(matrix[i, j]),
                    }
                )
    return sorted(pairs, key=lambda item: item["count"], reverse=True)[:10]


def train_and_evaluate(df: pd.DataFrame):
    X = df["skills_text"]
    y = df[LABEL_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    labels = sorted(y.unique())
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    min_class_size = int(y.value_counts().min())
    cv_folds = max(2, min(5, min_class_size))
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(build_pipeline(), X, y, cv=cv, scoring="f1_weighted")

    summary = {
        "rows_after_dedup": int(len(df)),
        "class_count": int(y.nunique()),
        "classes": dict(sorted(Counter(y).items())),
        "holdout_accuracy": float(report["accuracy"]),
        "holdout_weighted_f1": float(report["weighted avg"]["f1-score"]),
        "cv_folds": int(cv_folds),
        "cv_weighted_f1_mean": float(cv_scores.mean()),
        "cv_weighted_f1_std": float(cv_scores.std()),
        "top_confusions": top_confusions(y_test, y_pred, labels),
        "classification_report": report,
    }
    return pipeline, summary


def save_artifacts(model, summary, model_path: Path, report_path: Path):
    metadata = {
        "model": model,
        "sklearn_version": sklearn.__version__,
        "model_type": "MLPClassifier",
        "architecture": "skills_text -> TF-IDF(2500) -> MLP(128,64)",
        "training_mode": "deduplicated_skill_focused",
        "fuzzy_labels": {"High": ">0.70", "Medium": "0.40-0.70", "Low": "<0.40"},
        "metrics": {
            "holdout_accuracy": summary["holdout_accuracy"],
            "holdout_weighted_f1": summary["holdout_weighted_f1"],
            "cv_weighted_f1_mean": summary["cv_weighted_f1_mean"],
            "cv_weighted_f1_std": summary["cv_weighted_f1_std"],
        },
    }

    joblib.dump(metadata, model_path, compress=("zlib", 9))
    report_path.write_text(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Train a skill-focused soft-computing role classifier with MLPClassifier."
    )
    parser.add_argument("--csv", default=DEFAULT_CSV, help="Path to UpdatedResumeDataSet.csv")
    parser.add_argument("--model-out", default=DEFAULT_MODEL, help="Path to save the trained model")
    parser.add_argument(
        "--report-out",
        default="skill_role_validation_report.json",
        help="Path to save the evaluation report JSON",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    model_path = Path(args.model_out)
    report_path = Path(args.report_out)

    df = prepare_dataset(csv_path)

    print(f"Rows after deduplication: {len(df)}")
    print(f"Unique role labels kept: {df[LABEL_COL].nunique()}")
    print("Samples per class:")
    print(df[LABEL_COL].value_counts().sort_index().to_string())

    model, summary = train_and_evaluate(df)
    save_artifacts(model, summary, model_path, report_path)

    print("\nHoldout accuracy:", round(summary["holdout_accuracy"], 4))
    print("Holdout weighted F1:", round(summary["holdout_weighted_f1"], 4))
    print(
        "Cross-validation weighted F1:",
        round(summary["cv_weighted_f1_mean"], 4),
        "+/-",
        round(summary["cv_weighted_f1_std"], 4),
    )

    print("\nTop role confusions:")
    if summary["top_confusions"]:
        for item in summary["top_confusions"]:
            print(f"  {item['actual']} -> {item['predicted']}: {item['count']}")
    else:
        print("  None on the holdout split.")

    print(f"\nSaved model: {model_path}")
    print(f"Saved report: {report_path}")


if __name__ == "__main__":
    main()
