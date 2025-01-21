"""A sample implementation for BigQuery."""

from __future__ import annotations

import sqlalchemy
from singer_sdk import SQLConnector
from singer_sdk import typing as th  # JSON schema typing helpers
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector


class BigQueryConnector(SQLConnector):
    """Connects to the BigQuery SQL source."""

    def create_engine(self) -> Engine:
        """Creates and returns a new engine. Do not call outside of _engine.

        NOTE: Do not call this method. The only place that this method should
        be called is inside the self._engine method. If you'd like to access
        the engine on a connector, use self._engine.

        This method exists solely so that tap/target developers can override it
        on their subclass of SQLConnector to perform custom engine creation
        logic.

        Returns:
            A new SQLAlchemy Engine.
        """
        if self.config.get("client_secrets"):
            secrets_dict = self.config.get("client_secrets")
            return sqlalchemy.create_engine(
                self.sqlalchemy_url,
                echo=False,
                credentials_info={
                    "type": secrets_dict.get("type") or "service_account",  
                    "project_id": self.config.get("project_id"),
                    "private_key_id": secrets_dict.get("private_key_id"),
                    "private_key": secrets_dict.get("private_key"),
                    "client_email": secrets_dict.get("client_email"),
                    "client_id": secrets_dict.get("client_id"),
                    "auth_uri": secrets_dict.get("auth_uri") or "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": secrets_dict.get("token_uri") or "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": secrets_dict.get("auth_provider_x509_cert_url") or "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": secrets_dict.get("client_x509_cert_url") or "https://www.googleapis.com/robot/v1/metadata/x509/bigquery-access%40metabase-test-358815.iam.gserviceaccount.com",
                    "universe_domain": secrets_dict.get("universe_domain") or "googleapis.com",
                    },
            )
        if self.config.get("credentials_path"):
            return sqlalchemy.create_engine(
                self.sqlalchemy_url,
                echo=False,
                credentials_path=self.config.get("credentials_path"),
                # json_serializer=self.serialize_json,
                # json_deserializer=self.deserialize_json,
            )
        else:
            return sqlalchemy.create_engine(
                self.sqlalchemy_url,
                echo=False,
                # json_serializer=self.serialize_json,
                # json_deserializer=self.deserialize_json,
            )

    def get_sqlalchemy_url(self, config: dict) -> str:
        """Concatenate a SQLAlchemy URL for use in connecting to the source."""
        return f"bigquery://{config['project_id']}"

    def get_object_names(
        self,
        engine,
        inspected,
        schema_name: str,
    ) -> list[tuple[str, bool]]:
        """Return discoverable object names."""
        # Bigquery inspections returns table names in the form
        # `schema_name.table_name` which later results in the project name
        # override due to specifics in behavior of sqlalchemy-bigquery
        #
        # Let's strip `schema_name` prefix on the inspection

        return [
            (table_name.split(".")[-1], is_view)
            for (table_name, is_view) in super().get_object_names(
                engine,
                inspected,
                schema_name,
            )
        ]

    def get_schema_names(self, engine: Engine, inspected: Inspector) -> list[str]:
        """Return a list of schema names in DB, or overrides with user-provided values.

        Args:
            engine: SQLAlchemy engine
            inspected: SQLAlchemy inspector instance for engine

        Returns:
            List of schema names
        """
        if "filter_schemas" in self.config and len(self.config["filter_schemas"]) != 0:
            return self.config["filter_schemas"]
        return super().get_schema_names(engine, inspected)

__all__ = ["TapBigQuery", "BigQueryConnector", "BigQueryStream"]
