import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def launch(path="app.py"):
    return AppTest.from_file(str(ROOT / path), default_timeout=15).run()


def click(app, label):
    next(button for button in app.button if button.label == label).click()
    app.run()


class AppTests(unittest.TestCase):
    def test_submit_inspect_validate_and_tamper_without_changing_session(self):
        app = launch()
        app.slider[0].set_value(1)
        for field, value in zip(app.text_input, ("Alice", "Bob", "12.50"), strict=True):
            field.set_value(value)
        click(app, "Mine block")
        blocks = app.session_state["ledger"].blocks
        self.assertEqual((len(blocks), blocks[-1].difficulty), (2, 1))
        app.selectbox[0].set_value(1).run()
        self.assertIn(blocks[-1].digest, str(app.json[0].value))
        click(app, "Validate chain")
        self.assertIn("2 blocks passed", app.success[0].value)
        click(app, "Try changing the last record")
        self.assertIn("Edit detected", app.info[0].value)
        self.assertEqual(app.session_state["ledger"].blocks, blocks)
        self.assertEqual(len(launch().session_state["ledger"].blocks), 1)
        self.assertFalse(app.exception)

    def test_invalid_submission_leaves_only_genesis(self):
        app = launch()
        click(app, "Mine block")
        self.assertTrue(app.error)
        self.assertEqual(len(app.session_state["ledger"].blocks), 1)

    def test_classroom_entry_point(self):
        app = launch("Starter_Code/Instructions/Starter_Code/pychain.py")
        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, "PyChain Ledger")
