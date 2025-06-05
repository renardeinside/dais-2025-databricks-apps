from functools import partial
import streamlit as st
from dais_2025_databricks_apps.config import Config
import plotly.express as px

from dais_2025_databricks_apps.app_pages import dbsql_basics, intro, genie_chat

config = Config()  # type: ignore

# Set page config
st.set_page_config(
    page_title="Sample Databricks App",
    page_icon="🧱",
    layout="centered",
)

pg = st.navigation(
    [
        st.Page(
            intro,
            title="Introduction",
            url_path="/",
            icon="🏠",
        ),
        st.Page(
            partial(dbsql_basics, config=config),
            title="Databricks SQL Basics",
            url_path="/dbsql-basics",
            icon="📊",
        ),
        st.Page(
            partial(genie_chat, config=config),
            title="Genie Chat",
            url_path="/genie-chat",
            icon="💬",
        ),
    ]
)

pg.run()
