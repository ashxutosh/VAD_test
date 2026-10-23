import streamlit as st

st.set_page_config(page_title="PAD Emotion Space", layout="wide")

page = st.navigation(
    [
        st.Page("pages/pad_space.py", title="PAD Space", icon="🧊", url_path="", default=True),
        st.Page("pages/logic.py", title="Logic", icon="📘", url_path="logic"),
    ]
)
page.run()
