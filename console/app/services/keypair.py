"""Console keypair — get-or-create the Ed25519 signing key."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_core.jwt import ConsoleKeypair

from app.models.db import ConsoleKeypairRow


async def get_or_create_keypair(db: AsyncSession) -> ConsoleKeypair:
    """Load the Console keypair from the DB, creating it on first call."""
    row = (await db.execute(select(ConsoleKeypairRow))).scalar_one_or_none()
    if row is not None:
        return ConsoleKeypair.from_private_pem(row.private_pem)

    kp = ConsoleKeypair.generate()
    db.add(ConsoleKeypairRow(
        private_pem=kp.private_pem(),
        public_pem=kp.public_pem(),
    ))
    await db.commit()
    return kp
