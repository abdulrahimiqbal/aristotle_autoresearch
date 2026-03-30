import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import json
import shutil
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from research_orchestrator.cli import cmd_campaign_status, cmd_start_campaign
from research_orchestrator.campaign_planner import synthesize_campaign
from research_orchestrator.db import Database
from research_orchestrator.orchestrator import run_one_cycle
from research_orchestrator.reporter import build_report


class CampaignStartTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = Path(tempfile.mkdtemp(prefix="campaign_start_test_"))
        self.db_path = self.tempdir / "state.sqlite"

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_start_campaign_from_prompt_persists_spec_and_questions(self):
        prompt = (
            "Study the hidden structure behind weighted monotone subsequence thresholds "
            "and discover which assumptions are truly necessary."
        )
        args = SimpleNamespace(db=str(self.db_path), prompt=prompt)
        with patch("sys.stdout", new=StringIO()) as stdout:
            cmd_start_campaign(args)
            output = stdout.getvalue()

        db = Database(self.db_path)
        db.initialize()
        try:
            payload = json.loads("\n".join(output.splitlines()[1:]))
            project_id = payload["project_id"]
            spec = db.get_campaign_spec(project_id)
            questions = db.list_discovery_questions(project_id, status="open")
            self.assertIsNotNone(spec)
            self.assertEqual(spec.raw_prompt, prompt)
            self.assertTrue(questions)
            self.assertIn("open_discovery_questions", payload)
        finally:
            db.close()

    def test_run_cycle_answers_discovery_question_and_updates_graph(self):
        prompt = (
            "Understand the boundary behavior of weighted monotone subsequence problems "
            "through formal verification and recurring subgoal discovery."
        )
        args = SimpleNamespace(db=str(self.db_path), prompt=prompt)
        with patch("sys.stdout", new=StringIO()):
            cmd_start_campaign(args)

        db = Database(self.db_path)
        db.initialize()
        try:
            project_id = db.conn.execute("SELECT project_id FROM projects LIMIT 1").fetchone()["project_id"]
            result = run_one_cycle(db, project_id, "mock", self.tempdir / "work")
            experiment = db.get_experiment(result["brief"].experiment_id)
            nodes = db.list_discovery_nodes(project_id)
            answered = db.list_discovery_questions(project_id, status="answered")
            report = build_report(db, project_id)
            self.assertTrue(experiment["discovery_question_id"])
            self.assertTrue(answered)
            self.assertTrue(nodes)
            self.assertIn("Discovery Graph", report)
            self.assertIn("discovery question", report)
        finally:
            db.close()

    def test_campaign_status_emits_discovery_state(self):
        prompt = "Map hidden lemmas in a combinatorics problem using verification as discovery."
        with patch("sys.stdout", new=StringIO()):
            cmd_start_campaign(SimpleNamespace(db=str(self.db_path), prompt=prompt))

        db = Database(self.db_path)
        db.initialize()
        try:
            project_id = db.conn.execute("SELECT project_id FROM projects LIMIT 1").fetchone()["project_id"]
        finally:
            db.close()

        with patch("sys.stdout", new=StringIO()) as stdout:
            cmd_campaign_status(SimpleNamespace(db=str(self.db_path), project=project_id))
            payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["project_id"], project_id)
        self.assertIn("open_questions", payload)
        self.assertIn("discovery_nodes", payload)

    def test_short_erdos_prompt_is_expanded_into_valid_campaign(self):
        spec, charter, conjectures, questions = synthesize_campaign("erdos problem 144")
        self.assertIn("Erdos problem 144.", spec.raw_prompt)
        self.assertEqual(charter.project_id, spec.project_id)
        self.assertTrue(conjectures)
        self.assertTrue(questions)
        self.assertIn("combinatorics", spec.domain_scope)


if __name__ == "__main__":
    unittest.main()
