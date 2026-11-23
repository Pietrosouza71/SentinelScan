from __future__ import annotations

import ipaddress
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator, model_validator


def normalize_host(value: str) -> str:
    host = value.strip().rstrip(".")
    if not host or len(host) > 253 or any(char in host for char in "/\\@?#"):
        raise ValueError("Informe somente um nome de host ou endereço IP, sem URL ou caminho.")
    if "%" in host:
        raise ValueError("Endereços IP com identificador de interface não são aceitos.")

    try:
        return ipaddress.ip_address(host).compressed
    except ValueError:
        pass

    try:
        hostname = host.encode("idna").decode("ascii").lower()
    except UnicodeError as error:
        raise ValueError("Nome de host inválido.") from error

    labels = hostname.split(".")
    label_pattern = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
    if len(hostname) > 253 or not all(label_pattern.fullmatch(label) for label in labels):
        raise ValueError("Nome de host inválido.")
    return hostname


class TargetCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    target: str = Field(min_length=1, max_length=253)
    scope_description: str = Field(min_length=1, max_length=1000)
    exclusions: list[str] = Field(default_factory=list, max_length=50)
    authorization_reference: str | None = Field(default=None, max_length=160)
    authorization_confirmed: StrictBool

    @field_validator("target")
    @classmethod
    def validate_target(cls, value: str) -> str:
        return normalize_host(value)

    @field_validator("exclusions")
    @classmethod
    def validate_exclusions(cls, values: list[str]) -> list[str]:
        normalized = [value.strip() for value in values]
        if any(not value or len(value) > 253 for value in normalized):
            raise ValueError("Cada exclusão deve conter de 1 a 253 caracteres.")
        return normalized

    @field_validator("authorization_reference")
    @classmethod
    def normalize_reference(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def require_authorization_confirmation(self) -> "TargetCreate":
        if not self.authorization_confirmed:
            raise ValueError("Confirme que possui autorização explícita para cadastrar este alvo.")
        return self


class TargetRead(BaseModel):
    id: int
    name: str
    hostname: str
    scope_description: str
    exclusions: list[str]
    authorization_reference: str | None
    authorization_confirmed: bool
    is_active: bool
    created_at: str
    deactivated_at: str | None


class AuditEventRead(BaseModel):
    id: int
    event_type: str
    actor: str
    details: dict[str, Any]
    created_at: str
