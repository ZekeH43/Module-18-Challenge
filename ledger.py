"""A local teaching ledger. Hashing and validation need only the standard library."""

import hashlib
import json
import re
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal


@dataclass(frozen=True)
class Record:
    sender: str
    receiver: str
    amount: str

    def __post_init__(self):
        for field in ("sender", "receiver"):
            value = getattr(self, field)
            if (
                not isinstance(value, str)
                or not (1 <= len(value.strip()) <= 80)
                or not value.strip().isprintable()
            ):
                raise ValueError(
                    f"{field.title()} must contain 1–80 printable characters."
                )
            object.__setattr__(self, field, value.strip())
        if not isinstance(self.amount, str) or not re.fullmatch(
            r"[0-9]{1,9}(\.[0-9]{1,2})?", self.amount.strip()
        ):
            raise ValueError(
                "Enter a positive amount with at most nine whole digits and two decimal places."
            )
        value = Decimal(self.amount.strip())
        if value <= 0:
            raise ValueError("Amount must be greater than zero.")
        object.__setattr__(self, "amount", format(value, ".2f"))


@dataclass(frozen=True)
class Block:
    height: int
    record: Record | None
    creator_id: int
    previous_hash: str
    timestamp: str
    difficulty: int
    nonce: int
    digest: str

    def payload(self):
        """The digest itself is excluded to avoid a circular definition."""
        return {
            "height": self.height,
            "record": asdict(self.record) if self.record else None,
            "creator_id": self.creator_id,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
        }

    def calculate_hash(self):
        encoded = json.dumps(
            self.payload(), sort_keys=True, separators=(",", ":")
        ).encode()
        return hashlib.sha256(encoded).hexdigest()


def genesis():
    """The agreed starting block has no transaction or mining requirement."""
    block = Block(0, None, 0, "0" * 64, "1970-01-01T00:00:00+00:00", 0, 0, "")
    return replace(block, digest=block.calculate_hash())


def validate(blocks):
    """Raise ValueError on the first broken invariant, including a changed tip."""
    if not blocks or blocks[0] != genesis():
        raise ValueError("Genesis block does not match the agreed starting block.")
    for height, block in enumerate(blocks[1:], 1):
        if block.height != height or block.previous_hash != blocks[height - 1].digest:
            raise ValueError(f"Block {height}: broken position or previous hash.")
        if (
            block.record is None
            or type(block.difficulty) is not int
            or not 1 <= block.difficulty <= 3
        ):
            raise ValueError(f"Block {height}: invalid record or difficulty.")
        if block.digest != block.calculate_hash():
            raise ValueError(f"Block {height}: contents do not match the stored hash.")
        if not block.digest.startswith("0" * block.difficulty):
            raise ValueError(
                f"Block {height}: proof of work does not meet its difficulty."
            )


class PyChain:
    def __init__(self):
        self._blocks = [genesis()]

    @property
    def blocks(self):
        return tuple(self._blocks)

    def add_record(self, record: Record, difficulty=2):
        """Mine first; append only after a successful proof. Never mutate old blocks."""
        if not isinstance(record, Record):
            raise ValueError("A validated Record is required.")
        if type(difficulty) is not int or not 1 <= difficulty <= 3:
            raise ValueError("Choose a difficulty from 1 through 3.")
        validate(self._blocks)
        block = Block(
            len(self._blocks),
            record,
            42,
            self._blocks[-1].digest,
            datetime.now(UTC).isoformat(),
            difficulty,
            0,
            "",
        )
        target = "0" * difficulty
        for nonce in range(100_000):
            candidate = replace(block, nonce=nonce)
            digest = candidate.calculate_hash()
            if digest.startswith(target):
                mined = replace(candidate, digest=digest)
                self._blocks.append(mined)
                return mined
        raise ValueError(
            "No proof found in 100,000 attempts. Retry or lower the difficulty."
        )
