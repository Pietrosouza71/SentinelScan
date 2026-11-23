from __future__ import annotations

import json
import sqlite3

from fastapi import APIRouter, Depends, Query

from backend.routes.targets import get_connection
from backend.schemas import AuditEventRead


router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=list[AuditEventRead])
def list_audit_events(
    limit: int = Query(default=50, ge=1, le=200),
    connection: sqlite3.Connection = Depends(get_connection),
) -> list[AuditEventRead]:
    rows = connection.execute(
        "SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    return [
        AuditEventRead(
            id=row["id"],
            event_type=row["event_type"],
            actor=row["actor"],
            details=json.loads(row["details_json"]),
            created_at=row["created_at"],
        )
        for row in rows
    ]
