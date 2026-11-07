"""Launch from the repository root with: python -m streamlit run app.py."""

from dataclasses import asdict, replace

import streamlit as st

from ledger import PyChain, Record, validate


def main():
    st.title("PyChain Ledger")
    st.write(
        "Record a fictional transfer, mine a block, and inspect the proof. No money moves."
    )
    if "ledger" not in st.session_state:
        st.session_state.ledger = PyChain()
    ledger = st.session_state.ledger
    difficulty = st.sidebar.slider("Leading zeros for the next block", 1, 3, 2)
    with st.form("transfer"):
        sender = st.text_input("Sender", max_chars=80)
        receiver = st.text_input("Receiver", max_chars=80)
        amount = st.text_input(
            "Amount in demo units", placeholder="12.50", max_chars=12
        )
        submitted = st.form_submit_button("Mine block")
    if submitted:
        try:
            mined = ledger.add_record(Record(sender, receiver, amount), difficulty)
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.success(
                f"Added block {mined.height} after {mined.nonce + 1:,} attempts."
            )

    st.subheader("Ledger")
    st.caption(
        "This ledger is held in this session's memory. Reloading starts a new session."
    )
    rows = [
        {
            "Block": b.height,
            "Sender": b.record.sender if b.record else "Genesis",
            "Receiver": b.record.receiver if b.record else "—",
            "Amount": b.record.amount if b.record else "—",
            "Hash": b.digest,
        }
        for b in ledger.blocks
    ]
    st.dataframe(rows, hide_index=True)
    selected = st.selectbox(
        "Inspect a block", range(len(rows)), format_func=lambda n: f"Block {n}"
    )
    st.json(asdict(ledger.blocks[selected]))
    if st.button("Validate chain"):
        try:
            validate(ledger.blocks)
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.success(f"All {len(rows)} blocks passed validation.")
    if st.button("Try changing the last record", disabled=len(rows) == 1):
        blocks = list(ledger.blocks)
        tip = blocks[-1]
        amount = "2.00" if tip.record.amount == "1.00" else "1.00"
        blocks[-1] = replace(tip, record=replace(tip.record, amount=amount))
        try:
            validate(blocks)
        except ValueError as exc:
            st.info(f"Edit detected on a copy: {exc} Your ledger is unchanged.")


if __name__ == "__main__":
    main()
