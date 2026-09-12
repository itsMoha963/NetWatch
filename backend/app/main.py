from fastapi import FastAPI

app = FastAPI(title="NetWatch API")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
