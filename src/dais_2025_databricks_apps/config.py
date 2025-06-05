from contextlib import contextmanager
from typing import Any, Generator
import pandas as pd
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from databricks.sdk import WorkspaceClient
import logging
from databricks import sql
from databricks.sql.client import Cursor


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


class Config(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DAIS_2025_APPS_",  # for app-based configuration
        cli_parse_args=True,  # for command-line based configuration
        cli_ignore_unknown_args=True,  # ignore unknown command-line arguments
        extra="ignore",  # ignore unknown environment variables
    )

    logger: logging.Logger = Field(
        default_factory=get_logger,
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

    dbsql_http_path: str = Field(
        description="The HTTP path for the Databricks SQL endpoint.",
    )
    genie_space_id: str = Field(
        description="The Genie space ID for the application.",
    )

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
