from fastapi import FastAPI

from app.api.routes.devices import router as devices_router
from app.api.routes.metrics import router as metrics_router

app = FastAPI(title="NetWatch API")
app.include_router(devices_router)
app.include_router(metrics_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
