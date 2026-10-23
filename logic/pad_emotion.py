from collections.abc import Sequence
from dataclasses import dataclass
from math import exp, sqrt

AROUSAL_BINS = (-1.00, -0.71, -0.43, -0.14, 0.14, 0.43, 0.71, 1.00)
VALENCE_BINS = AROUSAL_BINS
DOMINANCE_BINS = (-1.00, -0.60, -0.20, 0.20, 0.60, 1.00)

EMOTION_COLORS = {
    "happy": "#28A745",
    "neutral": "#6C757D",
    "sadness": "#007BFF",
    "angry": "#DC3545",
}


@dataclass(frozen=True)
class PADClassification:
    arousal_index: int
    valence_index: int
    dominance_index: int
    emotion: str


def find_bin_index(value: float, bins: Sequence[float]) -> int:
    if value < bins[0] or value > bins[-1]:
        raise ValueError(f"Value {value} is outside the bin range [{bins[0]}, {bins[-1]}].")

    for index in range(len(bins) - 1):
        if bins[index] <= value < bins[index + 1]:
            return index

    return len(bins) - 2


def get_cube_emotion(arousal_index: int, valence_index: int, dominance_index: int) -> str:
    if not 0 <= arousal_index < 7:
        raise ValueError("Arousal index must be between 0 and 6.")
    if not 0 <= valence_index < 7:
        raise ValueError("Valence index must be between 0 and 6.")
    if not 0 <= dominance_index < 5:
        raise ValueError("Dominance index must be between 0 and 4.")

    if valence_index >= 4:
        return "happy"
    if valence_index == 3:
        return "neutral"
    if dominance_index <= 1:
        return "sadness"
    if dominance_index == 2:
        return "sadness" if arousal_index <= 2 else "angry"
    if dominance_index == 3:
        return "sadness" if arousal_index == 0 else "angry"
    return "angry"


def classify_point(arousal: float, valence: float, dominance: float) -> PADClassification:
    arousal_index = find_bin_index(arousal, AROUSAL_BINS)
    valence_index = find_bin_index(valence, VALENCE_BINS)
    dominance_index = find_bin_index(dominance, DOMINANCE_BINS)
    return PADClassification(
        arousal_index=arousal_index,
        valence_index=valence_index,
        dominance_index=dominance_index,
        emotion=get_cube_emotion(arousal_index, valence_index, dominance_index),
    )


def get_emotion_percentages(
    arousal: float,
    valence: float,
    dominance: float,
    sigma: float = 0.4,
) -> dict[str, float]:
    if sigma <= 0:
        raise ValueError("Sigma must be greater than zero.")

    category_distances = {emotion: [] for emotion in EMOTION_COLORS}
    for arousal_index in range(7):
        for valence_index in range(7):
            for dominance_index in range(5):
                emotion = get_cube_emotion(arousal_index, valence_index, dominance_index)
                center_a = (AROUSAL_BINS[arousal_index] + AROUSAL_BINS[arousal_index + 1]) / 2
                center_v = (VALENCE_BINS[valence_index] + VALENCE_BINS[valence_index + 1]) / 2
                center_d = (
                    DOMINANCE_BINS[dominance_index] + DOMINANCE_BINS[dominance_index + 1]
                ) / 2
                distance = sqrt(
                    (arousal - center_a) ** 2
                    + (valence - center_v) ** 2
                    + (dominance - center_d) ** 2
                )
                category_distances[emotion].append(distance)

    weights = {
        emotion: exp(-min(distances) / sigma)
        for emotion, distances in category_distances.items()
    }
    total_weight = sum(weights.values())
    return {
        emotion: weight / total_weight * 100
        for emotion, weight in weights.items()
    }
