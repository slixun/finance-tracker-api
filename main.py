from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.operations import router as operations_router
from app.api.v1.wallets import router as wallets_router
from app.api.v1.users import router as users_router
from app.api.v1.interest import router as interest_router
from app.database import Base, engine
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependency import get_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield

    engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wallets_router, prefix="/api/v1", tags=["wallets"])
app.include_router(operations_router, prefix="/api/v1", tags=["operations"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(interest_router, prefix="/api/v1", tags=["interest"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return {"status": "healthy"}
