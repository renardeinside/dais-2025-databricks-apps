import streamlit as st


def intro():
    # Hero section
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <img src="https://cdn.bfldr.com/9AYANS2F/at/k8bgnnxhb4bggjk88r4x9snf/databricks-symbol-color.svg?auto=webp&format=png" alt="Databricks Logo" width="200"/>
            <h1 style="margin-top: 1rem; font-size: 2.5rem;">🚀 Sample Databricks App</h1>
            <p style="font-size: 1.25rem;">
                Welcome to your sample Databricks Streamlit application!<br>
                Explore, analyze, and visualize your data with ease.
            </p>
            <p style="font-size: 1.25rem;">
               Please select a demo from the sidebar to get started.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
