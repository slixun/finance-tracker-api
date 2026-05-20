from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1.operations import router as operations_router
from app.api.v1.wallets import router as wallets_router
from app.api.v1.users import router as users_router
from app.api.v1.interest import router as interest_router
from app.database import Base, engine
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield

    engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(wallets_router, prefix="/api/v1", tags=["wallets"])
app.include_router(operations_router, prefix="/api/v1", tags=["operations"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(interest_router, prefix="/api/v1", tags=["interest"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
