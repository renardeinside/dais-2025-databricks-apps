from contextlib import contextmanager
from typing import Any, Generator
import pandas as pd
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
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


logger = get_logger()


class Config(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DAIS_2025_APPS_",  # for app-based configuration
        cli_parse_args=True,  # for command-line based configuration
        cli_ignore_unknown_args=True,  # ignore unknown command-line arguments
        extra="ignore",  # ignore unknown environment variables
    )

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

    dbsql_http_path: str = Field(
        description="The HTTP path for the Databricks SQL endpoint.",
    )

    genie_space_id: str = Field(
        description="The Genie space ID for the application.",
    )

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

    def __prepare_schema(self) -> None:
        """
        Prepare the schema with sample datasets and configurations.
        This method is called during the initialization of the Config class.
        """

        # check if schema exists
        schemas = self.ws.schemas.list(catalog_name=self.catalog)
        if not any(schema.name == self.user_schema for schema in schemas):
            self.logger.info(
                f"Creating schema {self.user_schema} in catalog {self.catalog}"
            )
            self.ws.schemas.create(
                catalog_name=self.catalog,
                name=self.user_schema,
                comment="Schema for DAIS 2025 apps",
            )
        else:
            self.logger.info(
                f"Schema {self.user_schema} already exists in catalog {self.catalog}"
            )

        # create sample datasets

        if not self.ws.tables.exists(full_name=self.full_table_name).table_exists:
            self.logger.info(
                f"Creating sample dataset {self.full_table_name} in catalog {self.catalog} and schema {self.user_schema}"
            )
            with self.cursor() as c:
                c.execute(
                    f"""
                    CREATE TABLE {self.full_table_name} AS
                    SELECT * FROM delta.`/databricks-datasets/nyctaxi/tables/nyctaxi_yellow`
                    """
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
