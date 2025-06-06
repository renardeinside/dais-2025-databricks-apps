from functools import partial
import streamlit as st
from dais_2025_databricks_apps.config import Config

from dais_2025_databricks_apps.app_pages import dbsql_basics, intro, genie_chat

# Set page config
st.set_page_config(
    page_title="DAIS 2025 | Databricks Apps",
    page_icon="🧱",
    layout="centered",
)

try:
    config = Config()  # type: ignore
except Exception as e:
    st.error(
        f"Failed to load configuration: {e}. Please check your environment variables or .env file."
    )
    st.stop()

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
