# Follow one transfer through PyChain

**Start at the form.** Alice enters Bob and 12.50. The interface constructs a frozen `Record`. Blank names, nonpositive amounts, and amounts with more than two decimal places are rejected before mining. Free-text names are labels; they do not authenticate users.

**Build the candidate.** `PyChain.add_record` takes the last accepted digest as the previous hash, captures a fresh UTC timestamp, and records the difficulty selected for this block. The creator ID of 42 is an illustrative value retained from the assignment.

**Find a proof.** `Block.calculate_hash` serializes named fields as compact JSON with sorted keys and hashes the encoded bytes with SHA-256. The digest itself is omitted from that input. Mining changes the nonce, starting at zero, until the hexadecimal digest begins with the requested number of zero characters. The first successful candidate is appended. A higher difficulty generally needs more trials, but any individual search can get lucky.

**Check the result.** Validation first compares the genesis block with the agreed starting block. For each following block, it checks its position, link to the previous digest, record and difficulty, recomputed hash, and required zero prefix. Comparing against the stored digest catches an ordinary edit even at the tip. Checking the prefix separately also catches a replacement digest that no longer proves the required work.

**Trace the regression.** Imagine changing the last amount from 12.50 to 1.00. Its link to the previous block still matches; a validator that checks links alone can accept it. Its contents now hash to a different value. Try the edit in the app, then open [the ledger tests](../tests/test_ledger.py) to see how the same failure is reproduced independently of the interface.

**Explain the limit.** If someone changes a record, re-mines it and every affected successor, their replacement chain can pass these local checks. Even a valid earlier prefix can pass. Detecting that a whole consistent history has been substituted requires a trusted reference outside this in-memory ledger.

For interview practice, explain why the last-block edit is detectable, why two sessions should have separate ledgers, and why neither result proves that Alice authorized a payment.
