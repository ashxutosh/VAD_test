from pathlib import Path

import streamlit as st

idea_file = Path(__file__).resolve().parents[1] / "idea.md"
st.markdown(idea_file.read_text(encoding="utf-8"))
