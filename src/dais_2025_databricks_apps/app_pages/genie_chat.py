import streamlit as st
import pandas as pd

from dais_2025_databricks_apps.config import Config
from databricks.sdk.service.dashboards import GenieMessage


def display_message(message):
    if "content" in message:
        st.markdown(message["content"])
    if "data" in message:
        st.dataframe(message["data"])
    if "code" in message:
        with st.expander("Show generated code"):
            st.code(message["code"], language="sql", wrap_lines=True)


def get_query_result(config: Config, statement_id: str) -> pd.DataFrame:
    # For simplicity, let's say data fits in one chunk, query.manifest.total_chunk_count = 1

    result = config.ws.statement_execution.get_statement(statement_id)
    if not result.result:
        st.warning("No result found for the query.")
        return pd.DataFrame()

    if not result.manifest or not result.manifest.schema or not result.manifest.schema.columns:
        st.warning("No manifest or schema found for the query result.")
        return pd.DataFrame()

    return pd.DataFrame(
        result.result.data_array,
        columns=[i.name for i in result.manifest.schema.columns],
    )


def process_genie_response(config: Config, response: GenieMessage) -> None:
    if not response.attachments:
        st.warning("No response from Genie.")
        return

    for i in response.attachments:
        if i.text:
            message = {"role": "assistant", "content": i.text.content}
            display_message(message)
        elif i.query:
            if not i.query.statement_id:
                st.warning("No statement ID found for the query.")
                continue

            data = get_query_result(config, i.query.statement_id)
            message = {
                "role": "assistant",
                "content": i.query.description,
                "data": data,
                "code": i.query.query,
            }
            display_message(message)


def genie_chat(config: Config) -> None:
    st.header("Genie Chat")
    st.markdown(
        """
        This page demonstrates how to interact with Genie using a chat interface.
        You can ask questions, and Genie will respond with relevant information or execute SQL queries.
        """
    )

    st.session_state.setdefault("conversation_id", None)

    if prompt := st.chat_input("Ask your question..."):

        st.chat_message("user").markdown(prompt)

        with st.chat_message("assistant"):

            if st.session_state.get("conversation_id"):
                conversation = config.ws.genie.create_message_and_wait(
                    config.genie_space_id, st.session_state.conversation_id, prompt
                )
            else:
                conversation = config.ws.genie.start_conversation_and_wait(
                    config.genie_space_id, prompt
                )

            process_genie_response(config, conversation)
