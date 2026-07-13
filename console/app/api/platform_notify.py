"""Platform → Console notifications endpoint."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class PlatformNotification(BaseModel):
    instance_id: str
    kind: str  # budget_alert | governance_alert | agent_stuck | cross_instance_invitation_received | upgrade_available
    payload: dict


@router.post("/notify")
async def platform_notify(notification: PlatformNotification, request: Request):
    # TODO: verify Platform's public key signature on the JWT in Authorization header
    # TODO: persist notification, fanout to Jarvis-Console if actionable
    return {"received": True, "kind": notification.kind}
