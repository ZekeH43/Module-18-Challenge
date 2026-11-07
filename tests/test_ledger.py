import unittest
from dataclasses import replace
from unittest.mock import patch

from ledger import PyChain, Record, genesis, validate


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.chain = PyChain()
        self.record = Record(" Alice ", "Bob", "12.5")

    def test_record_normalizes_only_valid_inputs(self):
        self.assertEqual(self.record, Record("Alice", "Bob", "12.50"))
        for amount in ("", "-1", "0.00", "12.345", "NaN", "Infinity", "1e4"):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                Record("Alice", "Bob", amount)
        for sender, receiver in [("", "B"), ("A", " "), ("A\nB", "C")]:
            with self.assertRaises(ValueError):
                Record(sender, receiver, "1")

    def test_mixed_difficulties_and_linked_proofs(self):
        one = self.chain.add_record(self.record, 1)
        two = self.chain.add_record(self.record, 2)
        self.assertEqual(one.previous_hash, genesis().digest)
        self.assertEqual(two.previous_hash, one.digest)
        self.assertTrue(one.digest.startswith("0") and two.digest.startswith("00"))
        validate(self.chain.blocks)

    def test_last_record_tampering(self):
        tip = self.chain.add_record(self.record, 1)
        altered = replace(tip, record=replace(self.record, amount="99"))
        with self.assertRaisesRegex(ValueError, "stored hash"):
            validate([genesis(), altered])
        validate(self.chain.blocks)

    def test_recomputed_hash_without_proof_is_rejected(self):
        block = self.chain.add_record(self.record, 1)
        while block.calculate_hash().startswith("0"):
            block = replace(block, nonce=block.nonce + 1)
        with self.assertRaisesRegex(ValueError, "proof of work"):
            validate([genesis(), replace(block, digest=block.calculate_hash())])

    def test_reordering_and_wrong_genesis(self):
        one = self.chain.add_record(self.record, 1)
        two = self.chain.add_record(self.record, 1)
        for altered in ([genesis(), two, one], [replace(genesis(), creator_id=42)], []):
            with self.assertRaises(ValueError):
                validate(altered)

    def test_bad_difficulty_does_not_append(self):
        for value in (True, 0, 4, 2.5):
            with self.assertRaises(ValueError):
                self.chain.add_record(self.record, value)
        self.assertEqual(self.chain.blocks, (genesis(),))

    def test_timestamp_is_read_for_each_new_block(self):
        with patch("ledger.datetime") as clock:
            clock.now.return_value.isoformat.side_effect = [
                "2026-01-01T00:00:00+00:00",
                "2026-01-02T00:00:00+00:00",
            ]
            first = self.chain.add_record(self.record, 1)
            second = self.chain.add_record(self.record, 1)
        self.assertNotEqual(first.timestamp, second.timestamp)
