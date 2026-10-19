import asyncio

# DEPRECATED-API: asyncio.get_event_loop() at import time with no running loop (deprecated 3.12)
LOOP = asyncio.get_event_loop()


def add(a: int, b: int) -> int:
    return a + b
