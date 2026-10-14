"""Onboarding-sidan för Streamlits multipage-routing."""

import runpy
from pathlib import Path

import streamlit as st


st.session_state["_paxly_page"] = "Onboarding"

# Den gemensamma appfilen ansvarar för layout, datahämtning och rendering.
# run_path gör att appen renderas på nytt även efter en Streamlit-rerun.
runpy.run_path(Path(__file__).parents[1] / "app.py", run_name="__main__")
