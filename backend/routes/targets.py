from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from backend.database import connect, record_audit_event, utc_now
from backend.schemas import TargetCreate, TargetRead


router = APIRouter(prefix="/api/targets", tags=["targets"])


def get_connection(request: Request) -> Iterator[sqlite3.Connection]:
    connection = connect(Path(request.app.state.database_path))
    try:
        yield connection
    finally:
        connection.close()


def serialize_target(row: sqlite3.Row) -> TargetRead:
    return TargetRead(
        id=row["id"],
        name=row["name"],
        hostname=row["hostname"],
        scope_description=row["scope_description"],
        exclusions=json.loads(row["exclusions_json"]),
        authorization_reference=row["authorization_reference"],
        authorization_confirmed=bool(row["authorization_confirmed"]),
        is_active=bool(row["is_active"]),
        created_at=row["created_at"],
        deactivated_at=row["deactivated_at"],
    )


@router.get("", response_model=list[TargetRead])
def list_targets(
    active_only: bool = True,
    connection: sqlite3.Connection = Depends(get_connection),
) -> list[TargetRead]:
    where_clause = "WHERE is_active = 1" if active_only else ""
    rows = connection.execute(
        f"SELECT * FROM targets {where_clause} ORDER BY created_at DESC, id DESC"
    ).fetchall()
    return [serialize_target(row) for row in rows]


@router.post("", response_model=TargetRead, status_code=status.HTTP_201_CREATED)
def create_target(
    payload: TargetCreate,
    connection: sqlite3.Connection = Depends(get_connection),
) -> TargetRead:
    created_at = utc_now()
    try:
        cursor = connection.execute(
            """
            INSERT INTO targets (
                name, hostname, scope_description, exclusions_json,
                authorization_reference, authorization_confirmed, created_at
            ) VALUES (?, ?, ?, ?, ?, 1, ?)
            """,
            (
                payload.name,
                payload.target,
                payload.scope_description,
                json.dumps(payload.exclusions, ensure_ascii=False),
                payload.authorization_reference,
                created_at,
            ),
        )
        target_id = cursor.lastrowid
        record_audit_event(
            connection,
            "target.created",
            {"target_id": target_id, "hostname": payload.target},
        )
        connection.commit()
    except sqlite3.IntegrityError as error:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este alvo já está cadastrado no escopo ativo.",
        ) from error

    row = connection.execute("SELECT * FROM targets WHERE id = ?", (target_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=500, detail="O alvo foi salvo, mas não pôde ser recuperado.")
    return serialize_target(row)


@router.delete("/{target_id}", response_model=TargetRead)
def deactivate_target(
    target_id: int,
    connection: sqlite3.Connection = Depends(get_connection),
) -> TargetRead:
    row = connection.execute(
        "SELECT * FROM targets WHERE id = ? AND is_active = 1", (target_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alvo ativo não encontrado.")

    deactivated_at = utc_now()
    connection.execute(
        "UPDATE targets SET is_active = 0, deactivated_at = ? WHERE id = ?",
        (deactivated_at, target_id),
    )
    record_audit_event(
        connection,
        "target.deactivated",
        {"target_id": target_id, "hostname": row["hostname"]},
    )
    connection.commit()

    updated = connection.execute("SELECT * FROM targets WHERE id = ?", (target_id,)).fetchone()
    if updated is None:
        raise HTTPException(status_code=500, detail="O alvo foi desativado, mas não pôde ser recuperado.")
    return serialize_target(updated)
