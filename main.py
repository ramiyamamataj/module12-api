from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine
from app.models import Calculation, User  # noqa: F401
from app.routers import calculations, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="FastAPI User & Calculation BREAD API",
    description="REST API for user authentication and polymorphic calculation BREAD operations.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(calculations.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
