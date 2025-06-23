from contextlib import contextmanager
from typing import Any, Generator
import pandas as pd
import logging
from databricks.sdk import WorkspaceClient
from databricks import sql
from databricks.sql.client import Cursor
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass, field
import os

def get_logger() -> logging.Logger:
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

env_file_path = Path(__file__).parent.parent.parent / ".env"

if env_file_path.exists():
    logger.info(f"Loading environment variables from {env_file_path.absolute()}")
    load_dotenv(env_file_path)
else:
    logger.warning(
        f"Environment file {env_file_path.absolute()} does not exist. "
        "Make sure to create it with the necessary configurations."
    )

for env in os.environ:
    if env.startswith("DAIS_2025_APPS_"):
        logger.debug(f"Environment variable {env} is set to {os.environ[env]}")

@dataclass
class Config:
    logger: logging.Logger = field(default_factory=get_logger, repr=False)
    ws: WorkspaceClient = field(default_factory=WorkspaceClient, repr=False)
    catalog: str = "main"

    def __post_init__(self):
        self.logger.info(
            f"Running the app under user: {self.ws.current_user.me().user_name}",
        )
        self.logger.info(f"App config:{self}")

    @property
    def dbsql_http_path(self) -> str:
        return os.environ["DAIS_2025_APPS_DBSQL_HTTP_PATH"]

    @property
    def genie_space_id(self) -> str:
        genie_space_id = os.environ.get("DAIS_2025_APPS_GENIE_SPACE_ID")
        if not genie_space_id:
            raise ValueError(
                "Environment variable DAIS_2025_APPS_GENIE_SPACE_ID is not set."
            )
        return genie_space_id

    @property
    def user_id(self) -> str:
        user_id = self.ws.current_user.me().id
        assert user_id, "User ID should not be empty."
        return user_id

    @property
    def user_schema(self) -> str:
        return f"apps_{self.user_id}"

    @property
    def full_table_name(self) -> str:
        return "samples.nyctaxi.trips"

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
        with self.cursor() as cursor:
            self.logger.info(f"Executing query: {query}")
            cursor.execute(query)
            return cursor.fetchall_arrow().to_pandas()
