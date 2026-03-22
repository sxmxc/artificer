from __future__ import annotations

import json
from ipaddress import ip_network
from typing import Any

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    log_level: str = Field(default="info", validation_alias="API_LOG_LEVEL")
    app_version: str = Field(default="2.0.0-alpha.3", validation_alias="APP_VERSION")

    postgres_user: str = Field(default="mockadmin", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="mockpassword", validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="mockapi", validation_alias="POSTGRES_DB")
    postgres_host: str = Field(default="postgres", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")

    admin_bootstrap_username: str = Field(
        default="admin",
        validation_alias=AliasChoices("ADMIN_BOOTSTRAP_USERNAME", "ADMIN_USERNAME"),
    )
    admin_bootstrap_password: str | None = Field(
        default=None,
        validation_alias=AliasChoices("ADMIN_BOOTSTRAP_PASSWORD", "ADMIN_PASSWORD"),
    )
    admin_password_min_length: int = Field(default=12, validation_alias="ADMIN_PASSWORD_MIN_LENGTH")
    admin_login_max_attempts: int = Field(default=5, validation_alias="ADMIN_LOGIN_MAX_ATTEMPTS")
    admin_login_ip_max_attempts: int = Field(default=10, validation_alias="ADMIN_LOGIN_IP_MAX_ATTEMPTS")
    admin_login_window_seconds: int = Field(default=300, validation_alias="ADMIN_LOGIN_WINDOW_SECONDS")
    admin_login_lockout_seconds: int = Field(default=900, validation_alias="ADMIN_LOGIN_LOCKOUT_SECONDS")
    trusted_proxy_cidrs: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("TRUSTED_PROXY_CIDRS", "ADMIN_TRUSTED_PROXY_CIDRS"),
    )
    admin_session_ttl_hours: int = Field(default=12, validation_alias="ADMIN_SESSION_TTL_HOURS")
    admin_remember_me_ttl_days: int = Field(default=30, validation_alias="ADMIN_REMEMBER_ME_TTL_DAYS")
    credential_encryption_key: str | None = Field(default=None, validation_alias="CREDENTIAL_ENCRYPTION_KEY")

    enable_openapi: bool = Field(default=True, validation_alias="ENABLE_OPENAPI")

    @field_validator("trusted_proxy_cidrs", mode="before")
    @classmethod
    def _normalize_trusted_proxy_cidrs(cls, value: Any) -> list[str]:
        if value is None or value == "":
            return []

        raw_items: list[Any]
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                parsed = json.loads(stripped)
                if not isinstance(parsed, list):
                    raise ValueError("TRUSTED_PROXY_CIDRS must be a JSON array or comma-separated string.")
                raw_items = parsed
            else:
                raw_items = stripped.split(",")
        elif isinstance(value, (list, tuple, set)):
            raw_items = list(value)
        else:
            raise ValueError("TRUSTED_PROXY_CIDRS must be a JSON array or comma-separated string.")

        normalized: list[str] = []
        for item in raw_items:
            candidate = str(item).strip()
            if not candidate:
                continue
            ip_network(candidate, strict=False)
            normalized.append(candidate)

        return normalized

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
