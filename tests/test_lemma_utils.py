import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import unittest

from research_orchestrator.lemma_utils import normalize_lemma


class LemmaUtilsTest(unittest.TestCase):
    def test_normalization_collapses_simple_variable_renaming(self):
        a = "forall x, x <= x"
        b = "forall y, y <= y"
        self.assertEqual(normalize_lemma(a), normalize_lemma(b))


if __name__ == "__main__":
    unittest.main()
