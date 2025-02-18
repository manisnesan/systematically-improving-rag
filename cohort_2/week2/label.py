import streamlit as st
import json
import pandas as pd
from streamlit_shortcuts import button
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Optional
from textwrap import dedent


categories = json.load(open("./data/categories.json"))
category_names = [category["category"] for category in categories]


class Transaction(BaseModel):
    merchant_name: str
    merchant_category: list[str]
    department: str
    location: str
    amount: float
    spend_program_name: str
    trip_name: Optional[str] = None
    expense_category: str


def load_transactions():
    transactions = []
    try:
        with open("./data/generated_transactions.jsonl", "r") as f:
            for line in f:
                transactions.append(json.loads(line))
        return pd.DataFrame(transactions)
    except FileNotFoundError:
        st.error("transactions.jsonl file not found")
        return pd.DataFrame()


def save_transaction(transaction):
    with open("./data/cleaned.jsonl", "a") as f:
        transaction["merchant_category"] = eval(transaction["merchant_category"])
        f.write(Transaction(**transaction).model_dump_json() + "\n")


def main():
    st.title("Transaction Annotation Queue")

    # Initialize session state for tracking reviewed transactions
    if "reviewed_indices" not in st.session_state:
        st.session_state.reviewed_indices = set()

    # Load data
    df = load_transactions()

    if df.empty:
        st.write("No transactions to review")
        return

    # Filter out reviewed transactions
    remaining_indices = [
        i for i in range(len(df)) if i not in st.session_state.reviewed_indices
    ]

    if not remaining_indices:
        st.write("All transactions have been reviewed!")
        return

    # Sidebar selection
    st.sidebar.header("Transaction Queue")

    # Get transaction IDs or another unique identifier to select from
    selected_index = st.sidebar.selectbox(
        "Select Transaction to Review",
        remaining_indices,
        format_func=lambda x: f"Transaction {x + 1}",
    )

    # Display selected transaction
    # st.header(f"Transaction {selected_index + 1} Review")

    # Get the selected transaction
    selected_transaction = df.iloc[selected_index]

    print(selected_transaction)

    # Display transaction details in text fields with editing enabled
    edited_transaction = {}

    edited_transaction["merchant_name"] = st.text_input(
        "Transaction Name", selected_transaction["merchant_name"]
    )
    edited_transaction["merchant_category"] = st.text_input(
        "MCCs", selected_transaction["merchant_category"]
    )
    edited_transaction["department"] = st.text_input(
        "Department", selected_transaction["department"]
    )
    edited_transaction["location"] = st.text_input(
        "Location", selected_transaction["location"]
    )
    edited_transaction["amount"] = st.text_input(
        "Amount", selected_transaction["amount"]
    )
    edited_transaction["spend_program_name"] = st.text_input(
        "Spend Program Name", selected_transaction["spend_program_name"]
    )
    edited_transaction["trip_name"] = st.text_input(
        "Trip Name", selected_transaction["trip_name"]
    )

    edited_transaction["expense_category"] = st.selectbox(
        "Category",
        options=category_names,
        index=category_names.index(selected_transaction["expense_category"]),
    )

    # Add approve/reject buttons
    col1, col2 = st.columns(2)

    with col1:
        if button(
            "✅ Approve",
            "ctrl+e",
            on_click=lambda: st.success("Transaction approved and saved!"),
        ):
            save_transaction(edited_transaction)  # Save the edited version instead
            st.session_state.reviewed_indices.add(selected_index)  # Mark as reviewed
            st.rerun()  # Rerun to update the interface

    with col2:
        if button(
            "❌ Skip",
            "ctrl+r",
            on_click=lambda: st.info("Moving to next transaction..."),
        ):
            st.session_state.reviewed_indices.add(selected_index)  # Mark as reviewed
            st.rerun()

    # Show progress in the sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Review Progress")
    st.sidebar.write(f"Remaining to Review: {len(remaining_indices)}")
    st.sidebar.write("""
    We've provided hotkeys for you to use in this case

    1. ctrl + e to approve
    2. ctrl + r to reject
                     
    All of the approved transactions will be saved to `cleaned.jsonl` and we'll use these to generate a new set of transactions that are more challenging.
    """)


if __name__ == "__main__":
    main()
