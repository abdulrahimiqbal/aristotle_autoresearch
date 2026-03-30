import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import shutil
import tempfile
import unittest

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.experiment_generator import DEFAULT_LEAN_TOOLCHAIN, materialize_experiment


class ExperimentGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="experiment_generator_test_"))
        root = Path(__file__).resolve().parents[1]
        self.charter = load_charter(root / "examples" / "erdos_combinatorics_charter.json")
        self.erdos44 = load_conjecture(root / "examples" / "conjectures" / "erdos" / "erdos_44_sidon_extension.json")
        self.weighted_monotone = load_conjecture(root / "examples" / "conjectures" / "weighted_monotone.json")

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_mathlib_import_generates_mathlib_lake_dependency(self):
        brief = materialize_experiment(
            self.charter,
            self.erdos44,
            str(self.tempdir),
            experiments=[],
            recurring_lemmas=[],
        )
        workspace = Path(brief.workspace_dir)

        self.assertEqual((workspace / "lean-toolchain").read_text(encoding="utf-8"), DEFAULT_LEAN_TOOLCHAIN + "\n")
        self.assertIn('name = "mathlib"', (workspace / "lakefile.toml").read_text(encoding="utf-8"))

    def test_non_mathlib_statement_omits_mathlib_lake_dependency(self):
        brief = materialize_experiment(
            self.charter,
            self.weighted_monotone,
            str(self.tempdir),
            experiments=[],
            recurring_lemmas=[],
        )

        self.assertNotIn(
            'name = "mathlib"',
            (Path(brief.workspace_dir) / "lakefile.toml").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
