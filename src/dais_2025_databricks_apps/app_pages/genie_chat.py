from __future__ import annotations
import base64
import io
from typing import Any
from venv import logger
from pydantic import BaseModel, ConfigDict, field_serializer, field_validator
import streamlit as st
import pandas as pd


from dais_2025_databricks_apps.config import Config
from databricks.sdk.service.dashboards import GenieMessage


class Message(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, frozen=False, populate_by_name=True
    )

    role: str
    content: str | None = None
    data: pd.DataFrame | None = None
    code: str | None = None

    @field_serializer("data", return_type=str)
    def serialize_dataframe(self, df: pd.DataFrame) -> str:
        if df is None:
            return None
        buffer = io.BytesIO()
        df.to_feather(buffer)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    @field_validator("data", mode="before")
    def deserialize_dataframe(cls, v: Any) -> pd.DataFrame | None:
        if v is None or isinstance(v, pd.DataFrame):
            return v
        try:
            raw = base64.b64decode(v)
            return pd.read_feather(io.BytesIO(raw))
        except Exception as e:
            raise ValueError(f"Failed to deserialize DataFrame: {e}")

    def display(self) -> Message:
        """Display the message content in Streamlit."""
        with st.chat_message(self.role):
            if self.content:
                st.markdown(self.content)
            if self.data is not None:
                st.dataframe(self.data)
            if self.code:
                with st.expander("Show generated code"):
                    st.code(self.code, language="sql", wrap_lines=True)
        return self

    def persist(self) -> None:
        """Persist the message to session state."""
        MessageHistory.add_message(self)


def get_query_result(config: Config, statement_id: str) -> pd.DataFrame:
    # For simplicity, let's say data fits in one chunk, query.manifest.total_chunk_count = 1

    result = config.ws.statement_execution.get_statement(statement_id)
    if not result.result:
        st.warning("No result found for the query.")
        return pd.DataFrame()

    if (
        not result.manifest
        or not result.manifest.schema
        or not result.manifest.schema.columns
    ):
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
            message = Message(
                role="assistant",
                content=i.text.content,
            )
        elif i.query:
            if not i.query.statement_id:
                st.warning("No statement ID found for the query.")
                continue

            data = get_query_result(config, i.query.statement_id)
            message = Message(
                role="assistant",
                content=i.query.description,
                data=data,
                code=i.query.query,
            )
        else:
            st.warning("Unknown attachment type from Genie.")
            continue

        message.display()
        message.persist()


class MessageHistory:
    @classmethod
    def add_message(cls, message: Message) -> None:
        """Add a message to the session state."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append(message.model_dump())

    @classmethod
    def display_history(cls) -> None:
        """Display the message history in the chat interface."""
        if "messages" not in st.session_state:
            return

        for msg_data in st.session_state.messages:
            msg = Message.model_validate(msg_data)
            msg.display()


def genie_chat(config: Config) -> None:
    st.header("Genie Chat")
    st.markdown(
        """
        This page demonstrates how to interact with Genie using a chat interface.
        You can ask questions, and Genie will respond with relevant information or execute SQL queries.
        """
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.session_state.setdefault("conversation_id", None)

    # Display chat history if available
    MessageHistory.display_history()

    # Display chat messages from history on app rerun
    if prompt := st.chat_input("Ask your question..."):

        user_message = Message(
            role="user",
            content=prompt,
        )
        user_message.display()
        user_message.persist()

        with st.spinner("Processing Genie response...", show_time=True):
            if st.session_state.get("conversation_id"):
                conversation = config.ws.genie.create_message_and_wait(
                    config.genie_space_id, st.session_state.conversation_id, prompt
                )
            else:
                conversation = config.ws.genie.start_conversation_and_wait(
                    config.genie_space_id, prompt
                )

            process_genie_response(config, conversation)
