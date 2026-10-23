import unittest
from collections import Counter

from logic import (
    AROUSAL_BINS,
    DOMINANCE_BINS,
    VALENCE_BINS,
    classify_point,
    get_cube_emotion,
    get_emotion_percentages,
)


class PADEmotionTests(unittest.TestCase):
    def test_cube_counts_match_specification(self):
        emotion_counts = Counter(
            get_cube_emotion(arousal_index, valence_index, dominance_index)
            for arousal_index in range(7)
            for valence_index in range(7)
            for dominance_index in range(5)
        )

        self.assertEqual(
            emotion_counts,
            {"happy": 105, "neutral": 35, "sadness": 54, "angry": 51},
        )

    def test_bin_boundaries_are_unambiguous(self):
        for index, boundary in enumerate(AROUSAL_BINS[1:], start=1):
            self.assertEqual(classify_point(boundary, 0, 0).arousal_index, min(index, 6))
        for index, boundary in enumerate(VALENCE_BINS[1:], start=1):
            self.assertEqual(classify_point(0, boundary, 0).valence_index, min(index, 6))
        for index, boundary in enumerate(DOMINANCE_BINS[1:], start=1):
            self.assertEqual(classify_point(0, 0, boundary).dominance_index, min(index, 4))

        self.assertEqual(classify_point(1, 1, 1).arousal_index, 6)
        self.assertEqual(classify_point(0.14, 0.14, 0).emotion, "happy")
        self.assertEqual(classify_point(-0.14, -0.14, 0).emotion, "neutral")

    def test_emotion_percentages_are_normalized(self):
        percentages = get_emotion_percentages(0.2, -0.5, 0.0)

        self.assertEqual(set(percentages), {"happy", "neutral", "sadness", "angry"})
        self.assertAlmostEqual(sum(percentages.values()), 100.0)
        self.assertTrue(all(0 <= percentage <= 100 for percentage in percentages.values()))

    def test_invalid_values_and_temperature_raise_errors(self):
        with self.assertRaises(ValueError):
            classify_point(1.01, 0, 0)
        with self.assertRaises(ValueError):
            get_emotion_percentages(0, 0, 0, sigma=0)


if __name__ == "__main__":
    unittest.main()
