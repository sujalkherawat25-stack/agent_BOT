import json
from collections.abc import AsyncIterator


def frame(event_type: str, run_id: str, payload: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps({'type': event_type, 'run_id': run_id, 'payload': payload}, default=str)}\n\n"


async def stream(events: list[tuple[str, dict]], run_id: str) -> AsyncIterator[str]:
    for event_type, payload in events:
        yield frame(event_type, run_id, payload)
