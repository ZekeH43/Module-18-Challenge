# PyChain Ledger

Can you detect an edit to the **last** transaction, even though no later block points to it? This Python and Streamlit demo lets you mine a fictional transfer, inspect the resulting block, and try that edit on a copy.

## Run locally

Clone the repository and open its directory:

```sh
git clone https://github.com/ZekeH43/Module-18-Challenge.git
cd Module-18-Challenge
```

Use Python 3.11 or 3.12. On **Windows PowerShell**:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

On **WSL, Linux, or macOS**:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Stop the server with Ctrl+C. Your ledger lives in the current browser session; refreshing the page can reset it. No accounts, wallets, or keys are needed.

## A two-minute demonstration

1. Set **Leading zeros for the next block** to 2. Enter Alice, Bob, and 12.50, then choose **Mine block**.
2. Inspect **Block 1**. Its record contains the amount, its previous hash points to the genesis block, and its own digest begins with two zeros. The nonce shows which attempt succeeded, counting from zero.
3. Change the difficulty to 1 and add a second transfer. **Validate chain** still succeeds because each block retains its own difficulty.
4. Choose **Try changing the last record**. The app changes an amount on a copy and reports the hash mismatch. Validate the original again: it still passes.

## How it works

[ledger.py](ledger.py) defines the record, block, mining loop, and validator using only the Python standard library. The amount is parsed as a decimal and stored as fixed two-place text, so 12.5 and 12.50 have the same representation. Blocks use a UTC timestamp captured when a transaction is added. Mining stops after 100,000 attempts; an unsuccessful attempt leaves the ledger unchanged.

[app.py](app.py) handles the form, session state, inspector, and tamper demonstration. The [original classroom entry point](Starter_Code/Instructions/Starter_Code/pychain.py) also launches this interface. For the hashing algorithm, validation rules, and an interview exercise, see the [code walkthrough](docs/walkthrough.md).

## Run the checks

With the environment active, run:

```sh
python -m unittest discover -s tests -v
```

On Windows you can use `.\.venv\Scripts\python` in place of `python`. The tests cover record validation, mining, mixed difficulties, changed records, broken links, and the simulated Streamlit interface, including independent sessions. GitHub Actions runs the suite on Python 3.11 and 3.12.

## Scope and origin

This is a single-process classroom simulation. Validation tests the internal consistency of the blocks presented to it. A person who controls the ledger can discard a suffix or rewrite and re-mine a different history. There are no signatures, account balances, peer consensus, or real transfers.

The [original assignment and attribution](Starter_Code/Instructions/README.md) and [screenshots from the earlier interface](docs/original-screenshots.md) are retained for context.
