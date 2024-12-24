from urllib.request import Request

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
import crimebot.chatbot.utils.loggers

app = FastAPI()
security = APIKeyHeader(name="X-API-Key")


@app.on_event("startup")
async def startup_event():
    utils.loggers.init_logger()


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    utils.loggers.logger.error(f"Unhandled exception: {exc}")
    raise HTTPException(status_code=500, detail=str(exc))


from api.router import router

app.include_router(router, prefix="/api", dependencies=[Depends(security)])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
