"""Unit tests for Essentia analysis helpers."""

import unittest

import numpy as np

from app.services.analysis_service import _mean_vector


class AnalysisServiceTests(unittest.TestCase):
    """Validate numpy-safe analysis helper behavior."""

    def test_mean_vector_accepts_numpy_matrices(self):
        matrix = np.array([[1.0, 2.0], [3.0, 4.0]])

        self.assertEqual(_mean_vector(matrix), [2.0, 3.0])

    def test_mean_vector_returns_none_for_empty_numpy_array(self):
        self.assertIsNone(_mean_vector(np.array([])))


if __name__ == "__main__":
    unittest.main()
