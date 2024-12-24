from fastapi import FastAPI, Depends, HTTPException, status
from .docker import start_containers, get_running_containers

router = FastAPI()


@router.post("/start", response_model=dict[str, str])
async def start_docker_containers(daemon_check: bool = Depends(check_docker_daemon)):
    start_containers()
    return {"message": "Docker Compose services started."}


@router.get("/health", response_model=dict[str, bool])
async def check_docker_health():
    running_containers = get_running_containers()
    if not running_containers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No Docker Compose services are running",
        )

    return {"healthy": True}
