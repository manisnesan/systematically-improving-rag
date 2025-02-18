import streamlit as st
import json
import pandas as pd
from streamlit_shortcuts import button
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Optional
from textwrap import dedent


class Question(BaseModel):
    citation: str
    question: str
    answer: str
    category: str
    subcategory: str


def load_questions():
    questions = []
    try:
        with open("./data/synthetic_questions.jsonl", "r") as f:
            for line in f:
                questions.append(json.loads(line))
        return pd.DataFrame(questions)
    except FileNotFoundError:
        st.error("synthetic_questions.jsonl file not found")
        return pd.DataFrame()


def save_question(question):
    with open("./data/cleaned.jsonl", "a") as f:
        f.write(Question(**question).model_dump_json() + "\n")


def main():
    st.title("Transaction Annotation Queue")

    # Initialize session state for tracking reviewed transactions
    if "reviewed_indices" not in st.session_state:
        st.session_state.reviewed_indices = set()

    # Load data
    df = load_questions()

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
    st.sidebar.header("Question Queue")

    selected_index = st.sidebar.selectbox(
        "Select Question to Review",
        remaining_indices,
        format_func=lambda x: f"Question {x + 1}",
    )

    # Get the selected question
    selected_question = df.iloc[selected_index]

    # Display transaction details in text fields with editing enabled
    # Create text fields for editing each field
    edited_question = selected_question.copy()
    edited_question["question"] = st.text_area(
        "Edit Question", value=selected_question["question"]
    )

    st.write(f"Answer: {selected_question['answer']}")
    st.write(f"Category: {selected_question['category']}")
    st.write(f"Subcategory: {selected_question['subcategory']}")
    st.write(f"Citation: {selected_question['citation']}")

    # Add approve/reject buttons
    col1, col2 = st.columns(2)
    with col1:
        if button(
            "✅ Approve",
            "ctrl+e",
            on_click=lambda: st.success("Transaction approved and saved!"),
        ):
            save_question(edited_question)  # Save the edited version instead
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
