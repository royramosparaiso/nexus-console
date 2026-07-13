"""Platform → Console notifications endpoint.

Body is a signed JWT (compact form) — verified against the Platform pubkey
persisted on the InstanceRow at bootstrap time.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_core.contracts.notifications import (
    NotificationEnvelope, NotificationResult, NotificationStatus,
)
from nexus_core.jwt import ExpiredToken, InvalidSignature, verify_token

from app.db import get_db
from app.models.db import InstanceRow, NotificationRow

router = APIRouter()


@router.post("/notify", response_model=NotificationResult)
async def platform_notify(request: Request, db: AsyncSession = Depends(get_db)) -> NotificationResult:
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="empty body")
    token = body.decode() if isinstance(body, bytes) else str(body)

    # We don't know which instance sent this until we peek at the payload.
    try:
        import base64
        import json
        parts = token.split(".")
        raw = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(raw))
        instance_id = UUID(payload.get("instance_id"))
    except Exception:
        raise HTTPException(status_code=400, detail="malformed token")

    row = await db.get(InstanceRow, instance_id)
    if row is None or not row.platform_public_key_pem:
        raise HTTPException(status_code=404, detail="unknown or unbootstrapped instance")

    try:
        verified = verify_token(token, row.platform_public_key_pem)
    except ExpiredToken:
        return NotificationResult(
            notif_id=UUID(payload.get("notif_id", str(UUID(int=0)))),
            status=NotificationStatus.EXPIRED,
        )
    except InvalidSignature:
        return NotificationResult(
            notif_id=UUID(payload.get("notif_id", str(UUID(int=0)))),
            status=NotificationStatus.INVALID_SIGNATURE,
        )

    envelope = NotificationEnvelope.model_validate(verified)

    db.add(NotificationRow(
        instance_id=instance_id,
        kind=envelope.notification.kind.value,
        payload=envelope.notification.payload,
        verified=True,
    ))
    await db.commit()

    return NotificationResult(notif_id=envelope.notif_id, status=NotificationStatus.ACK)
