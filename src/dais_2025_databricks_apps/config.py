from contextlib import contextmanager
from typing import Any, Generator
import pandas as pd
from pydantic import BaseModel, Field, computed_field
from databricks.sdk import WorkspaceClient
import logging
from databricks import sql
from databricks.sql.client import Cursor
from pathlib import Path
from dotenv import load_dotenv


def get_logger() -> logging.Logger:
    """
    Returns a logger instance for the application.
    """
    logger = logging.getLogger("databricks.dais.2025.apps")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger


logger = get_logger()

# to the project root directory
env_file_path = Path(__file__).parent.parent.parent / ".env"

if env_file_path.exists():
    logger.info(f"Loading environment variables from {env_file_path.absolute()}")
    load_dotenv(env_file_path)
else:
    logger.warning(
        f"Environment file {env_file_path.absolute()} does not exist. "
        "Make sure to create it with the necessary configurations."
    )


import os 

for env in os.environ:
    if env.startswith("DAIS_2025_APPS_"):
        logger.debug(f"Environment variable {env} is set to {os.environ[env]}")

class Config(BaseModel):

    logger: logging.Logger = Field(
        default=logger,
        repr=False,
        exclude=True,
        description="Logger instance for the application.",
    )

    ws: WorkspaceClient = Field(
        default_factory=lambda: WorkspaceClient(),
        repr=False,
        exclude=True,
        description="Databricks Workspace client instance.",
    )

    catalog: str = Field(
        default="main",
        description="The catalog to use for SQL queries. Defaults to the current catalog.",
    )

    @property
    def dbsql_http_path(self) -> str:
        return os.environ["DAIS_2025_APPS_DBSQL_HTTP_PATH"]

    @property
    def genie_space_id(self) -> str:
        """
        Returns the Genie space ID for the application.
        This is set in the environment variable DAIS_2025_APPS_GENIE_SPACE_ID.
        """
        genie_space_id = os.environ.get("DAIS_2025_APPS_GENIE_SPACE_ID")
        if not genie_space_id:
            raise ValueError(
                "Environment variable DAIS_2025_APPS_GENIE_SPACE_ID is not set."
            )
        return genie_space_id

    @computed_field(repr=False, description="User ID of the current user.")
    @property
    def user_id(self) -> str:
        """
        Returns the user ID of the current user.
        This is computed from the WorkspaceClient's current user.
        """
        user_id = self.ws.current_user.me().id
        assert user_id, "User ID should not be empty."
        return user_id

    @computed_field(repr=False, description="user schema")
    @property
    def user_schema(self) -> str:
        """
        Returns the user schema for the current user.
        This is computed from the user ID.
        """
        user_schema = f"apps_{self.user_id}"
        return user_schema

    @computed_field(repr=False, description="Full table name for the sample dataset.")
    @property
    def full_table_name(self) -> str:
        """
        Returns the full table name for the sample dataset.
        This is computed from the catalog and user schema.
        """
        full_table_name = "samples.nyctaxi.trips"
        return full_table_name

    def model_post_init(self, context: Any) -> None:
        super().model_post_init(context)
        self.logger.info(
            f"Running the app under user: {self.ws.current_user.me().user_name}",
        )
        self.logger.info(f"App config:{self}")

    @contextmanager
    def cursor(self) -> Generator[Cursor, None, None]:
        with sql.connect(
            server_hostname=self.ws.config.host,
            http_path=self.dbsql_http_path,
            credentials_provider=lambda: self.ws.config.authenticate,
        ) as connection:
            with connection.cursor() as cursor:
                yield cursor
            self.logger.info("Cursor closed successfully.")

        self.logger.info("Connection closed successfully.")

    def execute_query(
        self,
        query: str,
    ) -> pd.DataFrame:
        """
        Executes a SQL query and returns the results as a list of dictionaries.
        """
        with self.cursor() as cursor:
            self.logger.info(f"Executing query: {query}")
            cursor.execute(query)
            return cursor.fetchall_arrow().to_pandas()
