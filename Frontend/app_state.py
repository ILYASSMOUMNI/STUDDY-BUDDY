"""Shared state transitions for StudyBuddy pages."""

from __future__ import annotations

import streamlit as st


def reset_chat_state() -> None:
    st.session_state.chat_messages = []
    st.session_state.chat_display = []
    st.session_state.active_chat_session_id = None


def reset_quiz_state() -> None:
    st.session_state.quiz_data = None
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.wrong_answers_session = []


def open_chat(course_id: int | None = None, focus_concept: str | None = None,
              preset_message: str | None = None, chat_mode: str | None = None,
              reset: bool = False) -> None:
    if course_id is not None:
        st.session_state.selected_course_id = course_id
    st.session_state.current_page = "chat"
    st.session_state.focus_concept = focus_concept
    st.session_state.chat_preset = preset_message
    if chat_mode:
        st.session_state.chat_mode = chat_mode
    if reset:
        reset_chat_state()


def open_quiz(course_id: int | None = None, focus_concept: str | None = None,
              quick: bool = False, reset: bool = True) -> None:
    if course_id is not None:
        st.session_state.selected_course_id = course_id
    st.session_state.current_page = "quiz"
    st.session_state.focus_concept = focus_concept
    st.session_state.quick_quiz_mode = quick
    if reset:
        reset_quiz_state()
