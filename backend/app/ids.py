"""UUIDv7 generation — time-ordered UUIDs used as primary keys everywhere.

UUIDv7 embeds a millisecond timestamp in the high bits, so values sort in
creation order (great for DB indexes) while remaining globally unique and
safe to expose in URLs and APIs. This is the backbone of the "UUID-first"
architecture: every entity is addressable by one of these.
"""

import os
import time
import uuid


def uuid7() -> uuid.UUID:
    """Generate a UUIDv7 (RFC 9562) without external dependencies."""
    unix_ms = int(time.time() * 1000)
    timestamp = unix_ms.to_bytes(6, "big")
    rand = os.urandom(10)
    b = bytearray(timestamp + rand)
    # Set version (7) in the high nibble of byte 6.
    b[6] = (b[6] & 0x0F) | 0x70
    # Set the variant (10xx) in the two high bits of byte 8.
    b[8] = (b[8] & 0x3F) | 0x80
    return uuid.UUID(bytes=bytes(b))


def new_id() -> str:
    """Return a fresh UUIDv7 as a string (the storage form used by models)."""
    return str(uuid7())
