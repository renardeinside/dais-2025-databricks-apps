from dais_2025_databricks_apps.app_pages.genie_chat import Message
import pandas as pd


def test_message_model():
    # Test initialization with valid data
    df = pd.DataFrame({"column1": [1, 2, 3], "column2": ["a", "b", "c"]})
    message = Message(role="user", content="Hello, Genie!", data=df, code="SELECT * FROM table;")

    # serialize to JSON
    as_dict = message.model_dump()
    assert isinstance(as_dict, dict)

    # deserialize from JSON
    message_loaded = Message.model_validate(as_dict)
    assert message_loaded.role == "user"
    assert message_loaded.content == "Hello, Genie!"
    assert isinstance(message_loaded.data, pd.DataFrame)
    assert message_loaded.data.equals(df)
