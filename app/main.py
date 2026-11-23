from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.redis_client import init_redis, close_redis
from app.routers import auth, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables + init Redis
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_redis()
    yield
    # Shutdown
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title="Project Manager API",
    version="1.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(projects.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
