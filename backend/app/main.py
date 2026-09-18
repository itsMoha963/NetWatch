from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api.routes.alerts import router as alerts_router
from app.api.routes.devices import router as devices_router
from app.api.routes.metrics import router as metrics_router

app = FastAPI(title="NetWatch API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(devices_router)
app.include_router(metrics_router)
app.include_router(alerts_router)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "detail": "The request conflicts with an existing database record."
        },
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
