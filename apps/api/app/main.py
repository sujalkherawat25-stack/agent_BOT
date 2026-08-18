from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_core.api import router
from storage.db import create_schema
from storage.settings import settings
from harnesses.tasks import tick_tasks


async def task_worker(stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            await tick_tasks()
        except Exception:
            pass
        try:
            await asyncio.wait_for(stop.wait(), timeout=5)
        except asyncio.TimeoutError:
            continue


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_schema()
    stop = asyncio.Event()
    worker = asyncio.create_task(task_worker(stop))
    try:
        yield
    finally:
        stop.set(); worker.cancel()
        await asyncio.gather(worker, return_exceptions=True)


app = FastAPI(title="Personal Agent API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/v1")
