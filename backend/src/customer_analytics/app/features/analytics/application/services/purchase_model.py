"""Small dependency-free trainers for the purchase-repeat use case."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

FEATURE_NAMES = (
    "recency",
    "frequency",
    "monetary",
    "aov",
    "purchase_cycle",
    "interaction_score",
    "product_diversity",
    "review_score",
)


def _sigmoid(value: float) -> float:
    """Return a numerically stable logistic sigmoid."""
    if value >= 0:
        exponent = math.exp(-value)
        return 1.0 / (1.0 + exponent)
    exponent = math.exp(value)
    return exponent / (1.0 + exponent)


def _standardize(
    rows: Sequence[Sequence[float]],
) -> tuple[list[list[float]], list[float], list[float]]:
    """Standardize each feature and retain parameters for inference."""
    if not rows:
        return [], [], []
    width = len(rows[0])
    means = [sum(row[index] for row in rows) / len(rows) for index in range(width)]
    scales = []
    for index, mean in enumerate(means):
        variance = sum((row[index] - mean) ** 2 for row in rows) / len(rows)
        scales.append(math.sqrt(variance) or 1.0)
    normalized = [
        [(value - means[index]) / scales[index] for index, value in enumerate(row)]
        for row in rows
    ]
    return normalized, means, scales


def _probabilities(
    artifact: dict[str, Any], rows: Sequence[Sequence[float]]
) -> list[float]:
    """Score rows with a serialized logistic model or stump ensemble."""
    means = artifact["means"]
    scales = artifact["scales"]
    normalized = [
        [(value - means[index]) / scales[index] for index, value in enumerate(row)]
        for row in rows
    ]
    if artifact["model_type"] == "LOGISTIC_REGRESSION":
        weights = artifact["weights"]
        return [
            _sigmoid(
                artifact["intercept"]
                + sum(
                    weight * value for weight, value in zip(weights, row, strict=True)
                )
            )
            for row in normalized
        ]

    probabilities = []
    for row in normalized:
        votes = [
            1.0
            if (row[stump["feature"]] >= stump["threshold"])
            == stump["positive_if_high"]
            else 0.0
            for stump in artifact["stumps"]
        ]
        probabilities.append(sum(votes) / len(votes))
    return probabilities


def _roc_auc(labels: Sequence[int], probabilities: Sequence[float]) -> float:
    """Compute ROC-AUC using the probability ranking."""
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return 0.0
    order = sorted(range(len(labels)), key=lambda index: probabilities[index])
    rank_sum = sum(rank for rank, index in enumerate(order, start=1) if labels[index])
    return (rank_sum - positives * (positives + 1) / 2) / (positives * negatives)


def _pr_auc(labels: Sequence[int], probabilities: Sequence[float]) -> float:
    """Compute average precision for the positive class."""
    positives = sum(labels)
    if positives == 0:
        return 0.0
    order = sorted(
        range(len(labels)), key=lambda index: probabilities[index], reverse=True
    )
    hits = 0
    total = 0.0
    for rank, index in enumerate(order, start=1):
        if labels[index]:
            hits += 1
            total += hits / rank
    return total / positives


def _metrics(labels: Sequence[int], probabilities: Sequence[float]) -> dict[str, float]:
    """Return the metrics required by the scenario and model gates."""
    predictions = [1 if probability >= 0.5 else 0 for probability in probabilities]
    true_positive = sum(
        label == prediction == 1
        for label, prediction in zip(labels, predictions, strict=True)
    )
    false_positive = sum(
        label == 0 and prediction == 1
        for label, prediction in zip(labels, predictions, strict=True)
    )
    false_negative = sum(
        label == 1 and prediction == 0
        for label, prediction in zip(labels, predictions, strict=True)
    )
    accuracy = sum(
        label == prediction
        for label, prediction in zip(labels, predictions, strict=True)
    ) / len(labels)
    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    top_k = max(1, math.ceil(len(labels) * 0.1))
    top_indices = sorted(
        range(len(labels)), key=lambda index: probabilities[index], reverse=True
    )[:top_k]
    top_hits = sum(labels[index] for index in top_indices)
    precision_top10 = top_hits / top_k
    conversion = sum(labels) / len(labels)
    lift_top10 = precision_top10 / conversion if conversion else 0.0
    return {
        "accuracy": round(accuracy, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1_score": round(f1, 6),
        "roc_auc": round(_roc_auc(labels, probabilities), 6),
        "pr_auc": round(_pr_auc(labels, probabilities), 6),
        "precision_top10": round(precision_top10, 6),
        "overall_conversion": round(conversion, 6),
        "lift_top10": round(lift_top10, 6),
    }


def _train_logistic(
    rows: Sequence[Sequence[float]], labels: Sequence[int]
) -> dict[str, Any]:
    """Fit logistic regression with batch gradient descent."""
    normalized, means, scales = _standardize(rows)
    weights = [0.0] * len(FEATURE_NAMES)
    intercept = 0.0
    learning_rate = 0.08
    for _ in range(600):
        gradients = [0.0] * len(weights)
        intercept_gradient = 0.0
        for row, label in zip(normalized, labels, strict=True):
            probability = _sigmoid(
                intercept + sum(w * x for w, x in zip(weights, row, strict=True))
            )
            error = probability - label
            intercept_gradient += error
            for index, value in enumerate(row):
                gradients[index] += error * value
        scale = 1 / len(normalized)
        intercept -= learning_rate * intercept_gradient * scale
        for index, gradient in enumerate(gradients):
            weights[index] -= learning_rate * gradient * scale
    return {
        "model_type": "LOGISTIC_REGRESSION",
        "feature_names": list(FEATURE_NAMES),
        "means": means,
        "scales": scales,
        "weights": weights,
        "intercept": intercept,
    }


def _train_forest(
    rows: Sequence[Sequence[float]], labels: Sequence[int]
) -> dict[str, Any]:
    """Fit a deterministic ensemble of one-level classification trees."""
    normalized, means, scales = _standardize(rows)
    stumps: list[dict[str, Any]] = []
    for feature in range(len(FEATURE_NAMES)):
        values = sorted(row[feature] for row in normalized)
        for quantile in (0.2, 0.4, 0.6, 0.8):
            threshold = values[min(len(values) - 1, int((len(values) - 1) * quantile))]
            high_hits = sum(
                label == int(row[feature] >= threshold)
                for row, label in zip(normalized, labels, strict=True)
            )
            low_hits = sum(
                label == int(row[feature] < threshold)
                for row, label in zip(normalized, labels, strict=True)
            )
            stumps.append(
                {
                    "feature": feature,
                    "threshold": threshold,
                    "positive_if_high": high_hits >= low_hits,
                }
            )
    return {
        "model_type": "RANDOM_FOREST",
        "feature_names": list(FEATURE_NAMES),
        "means": means,
        "scales": scales,
        "stumps": stumps,
    }


def train_purchase_model(
    rows: Sequence[dict[str, Any]],
    model_type: str,
) -> tuple[dict[str, Any], dict[str, float]]:
    """Train and evaluate one supported purchase-repeat model."""
    if len(rows) < 4:
        raise ValueError("At least four labeled customers are required for training.")
    labels = [int(row["label"]) for row in rows]
    if len(set(labels)) < 2:
        raise ValueError(
            "Training data must contain both positive and negative labels."
        )
    features = [[float(row.get(name) or 0) for name in FEATURE_NAMES] for row in rows]
    normalized_type = model_type.upper()
    if normalized_type == "LOGISTIC_REGRESSION":
        artifact = _train_logistic(features, labels)
    elif normalized_type == "RANDOM_FOREST":
        artifact = _train_forest(features, labels)
    else:
        raise ValueError("model_type must be LOGISTIC_REGRESSION or RANDOM_FOREST.")
    probabilities = _probabilities(artifact, features)
    return artifact, _metrics(labels, probabilities)


def predict_purchase_probability(
    artifact: dict[str, Any], row: dict[str, Any]
) -> float:
    """Predict the purchase probability for one feature row."""
    values = [[float(row.get(name) or 0) for name in FEATURE_NAMES]]
    return round(_probabilities(artifact, values)[0], 4)
